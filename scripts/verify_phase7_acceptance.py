import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import time as dt_time
from datetime import timedelta
from pathlib import Path

os.environ["TELEGRAM_BOT_ENABLED"] = "true"
os.environ["TELEGRAM_BOT_TOKEN"] = "phase7-acceptance-only"
os.environ["TELEGRAM_BOT_USERNAME"] = "iems_phase7_test_bot"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # Script owns a single browser/DB thread.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django

sys.path.insert(0, os.getcwd())
django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventType  # noqa: E402
from apps.events.services.emergency import execute_emergency_override  # noqa: E402
from apps.events.services.workflow import reschedule_event  # noqa: E402
from apps.notifications.models import TelegramConnection, TelegramDelivery  # noqa: E402
from apps.notifications.telegram.client import UrlLibTelegramTransport  # noqa: E402
from apps.notifications.telegram.linking import consume_link_token  # noqa: E402
from apps.notifications.telegram.services import schedule_due_reminders  # noqa: E402
from apps.notifications.telegram.tasks import send_telegram_delivery  # noqa: E402
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()
PORT = 8561
BASE_URL = f"http://127.0.0.1:{PORT}"
OUTPUT = Path("tests/visual_baseline")
OUTPUT.mkdir(parents=True, exist_ok=True)


def cleanup():
    Event.objects.filter(title__startswith="[P7]").delete()
    EventType.objects.filter(code="p7-acceptance").delete()
    Venue.objects.filter(code="P7-ACC").delete()
    User.objects.filter(username__startswith="p7_accept_").delete()


def prepare_data():
    cleanup()
    admin = User.objects.create_user(
        "p7_accept_admin",
        password="Phase7-Safe-Test!",
        role=User.Role.INTERNATIONAL_ADMIN,
    )
    responsible = User.objects.create_user(
        "p7_accept_responsible",
        password="Phase7-Safe-Test!",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
        preferred_language="uz",
    )
    management = User.objects.create_user(
        "p7_accept_management",
        password="Phase7-Safe-Test!",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
        preferred_language="ru",
    )
    venue = Venue.objects.create(
        code="P7-ACC",
        name_uz="Phase 7 xalqaro zali",
        name_ru="Международный зал Phase 7",
        name_en="Phase 7 International Hall",
        capacity=120,
        working_start=dt_time(0),
        working_end=dt_time(23, 59),
    )
    event_type = EventType.objects.create(
        code="p7-acceptance", name_uz="Forum", name_ru="Форум", name_en="Forum"
    )
    target = timezone.localtime().replace(second=0, microsecond=0) + timedelta(minutes=30)
    event = Event.objects.create(
        title="[P7] International Staff Forum",
        event_type=event_type,
        venue=venue,
        planned_date=target.date(),
        start_time=target.time().replace(tzinfo=None),
        end_time=(target + timedelta(hours=1)).time().replace(tzinfo=None),
        responsible_employee=responsible,
        management_responsible=management,
        created_by=admin,
        status=Event.Status.APPROVED,
    )
    return admin, responsible, management, event, event_type, venue


def wait_for_server():
    for _ in range(40):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=1) as response:
                return response.status == 200
        except Exception:
            time.sleep(0.3)
    return False


def fake_post(self, url, payload, timeout):
    method = url.rsplit("/", 1)[-1]
    if method == "sendMessage":
        return {"ok": True, "result": {"message_id": 7001}}
    return {"ok": True, "result": {"id": 1, "username": "iems_phase7_test_bot"}}


def screenshot(page, filename, selector=None):
    page.set_viewport_size({"width": 1440, "height": 1000})
    target = page.locator(selector) if selector else page
    target.screenshot(path=str(OUTPUT / filename))


def login(page, username):
    page.goto(f"{BASE_URL}/accounts/login/")
    page.fill("input[name=username]", username)
    page.fill("input[name=password]", "Phase7-Safe-Test!")
    page.click("button[type=submit]")


def main():
    admin, responsible, _, event, event_type, venue = prepare_data()
    UrlLibTelegramTransport.post = fake_post
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=os.environ.copy(),
    )
    try:
        if not wait_for_server():
            raise RuntimeError("Django server did not start")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            login(page, responsible.username)
            page.goto(f"{BASE_URL}/notifications/telegram/")
            screenshot(
                page, "phase7_01_telegram_settings.png", "[data-testid=telegram-settings-card]"
            )
            page.click("[data-testid=connect-telegram]")
            href = page.locator("[data-testid=telegram-deep-link]").get_attribute("href")
            token = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)["start"][0]
            assert consume_link_token(token, "700100", 700100, "p7_responsible")
            page.reload()
            page.wait_for_selector("text=Connected")
            screenshot(page, "phase7_02_connected.png", "[data-testid=telegram-settings-card]")

            page.context.clear_cookies()
            login(page, admin.username)
            page.goto(f"{BASE_URL}/notifications/telegram/events/{event.pk}/")
            page.check("input[name=reminders_enabled]")
            page.click("button[type=submit]")
            page.goto(f"{BASE_URL}/notifications/telegram/events/{event.pk}/")
            screenshot(page, "phase7_03_event_reminders.png", "[data-testid=event-reminder-form]")

            settings.TELEGRAM_BOT_ENABLED = False
            assert schedule_due_reminders(event.start_datetime - timedelta(minutes=30)) == 2
            settings.TELEGRAM_BOT_ENABLED = True
            for delivery in event.telegram_deliveries.filter(status="pending"):
                send_telegram_delivery.run(delivery.pk)
            page.reload()
            screenshot(
                page, "phase7_04_delivery_status.png", "[data-testid=telegram-delivery-status]"
            )

            settings.TELEGRAM_BOT_ENABLED = False
            reschedule_event(
                event,
                admin,
                event.planned_date + timedelta(days=1),
                dt_time(10),
                dt_time(11),
            )
            emergency = Event.objects.create(
                title="[P7] Emergency Delegation",
                event_type=event_type,
                venue=venue,
                planned_date=event.planned_date,
                start_time=event.start_time,
                end_time=event.end_time,
                responsible_employee=responsible,
                management_responsible=event.management_responsible,
                created_by=admin,
                status=Event.Status.DRAFT,
            )
            execute_emergency_override(emergency, admin, "Acceptance-only authorized reason")
            settings.TELEGRAM_BOT_ENABLED = True
            for delivery in emergency.telegram_deliveries.filter(status="pending"):
                send_telegram_delivery.run(delivery.pk)
            page.goto(f"{BASE_URL}/notifications/telegram/events/{emergency.pk}/")
            screenshot(
                page,
                "phase7_05_emergency_notification.png",
                "[data-testid=telegram-delivery-status]",
            )

            TelegramConnection.objects.filter(user=responsible).delete()
            skipped = TelegramDelivery.objects.create(
                event=emergency,
                recipient_user=responsible,
                notification_type="disconnect-check",
                scheduled_for=timezone.now(),
                message_text="must not send",
            )
            assert send_telegram_delivery.run(skipped.pk) == "skipped"
            browser.close()
        print("PASS — Phase 7 Playwright acceptance")
    finally:
        server.terminate()
        server.wait(timeout=10)
        cleanup()


if __name__ == "__main__":
    main()
