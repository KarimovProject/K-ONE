import os
import secrets
import subprocess
import sys
import time
import urllib.request
from datetime import time as dt_time
from datetime import timedelta
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django

sys.path.insert(0, os.getcwd())
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.core.cache import cache  # noqa: E402
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventType  # noqa: E402
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()
PORT = 8571
BASE_URL = f"http://127.0.0.1:{PORT}"
OUTPUT = Path("tests/visual_baseline")
PASSWORD = secrets.token_urlsafe(24)


def cleanup():
    Event.objects.filter(title__startswith="[P11]").delete()
    EventType.objects.filter(code="p11-acceptance").delete()
    Venue.objects.filter(code__startswith="P11-").delete()
    User.objects.filter(username__startswith="p11_accept_").delete()


def prepare_data():
    cache.clear()
    cleanup()
    admin_user = User.objects.create_superuser(
        "p11_accept_admin", password=PASSWORD, email="p11-admin@example.test"
    )
    manager = User.objects.create_user(
        "p11_accept_manager",
        password=PASSWORD,
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )
    responsible = User.objects.create_user(
        "p11_accept_responsible",
        password=PASSWORD,
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )
    content_manager = User.objects.create_user(
        "p11_accept_content", password=PASSWORD, role=User.Role.CONTENT_MANAGER
    )
    reception = User.objects.create_user(
        "p11_accept_reception", password=PASSWORD, role=User.Role.RECEPTION_OPERATOR
    )
    event_type = EventType.objects.create(
        code="p11-acceptance",
        name_uz="Xalqaro uchrashuv",
        name_ru="Международная встреча",
        name_en="International meeting",
        color="#06B6D4",
    )
    venues = []
    for index, name in enumerate(("Grand Hall", "Diplomatic Room", "Forum Hall", "Media Hall"), 1):
        venues.append(
            Venue.objects.create(
                code=f"P11-{index}",
                name_uz=name,
                name_ru=name,
                name_en=name,
                capacity=80 + index * 20,
                working_start=dt_time(8),
                working_end=dt_time(20),
                sort_order=index,
            )
        )
    delete_venue = Venue.objects.create(
        code="P11-DEL",
        name_uz="O‘chirish testi",
        name_ru="Тест удаления",
        name_en="Delete test",
        capacity=10,
        working_start=dt_time(8),
        working_end=dt_time(18),
        sort_order=905,
    )
    now = timezone.localtime()
    starts = (9, 11, 14, 16)
    visibility = (
        Event.DisplayVisibility.FULL,
        Event.DisplayVisibility.GENERIC,
        Event.DisplayVisibility.HIDDEN,
        Event.DisplayVisibility.FULL,
    )
    for index, venue in enumerate(venues):
        Event.objects.create(
            title=f"[P11] International Health Partnership {index + 1}",
            event_type=event_type,
            venue=venue,
            planned_date=now.date() if index < 3 else now.date() + timedelta(days=1),
            start_time=dt_time(starts[index]),
            end_time=dt_time(starts[index] + 1),
            responsible_employee=responsible,
            management_responsible=manager,
            created_by=admin_user,
            status=Event.Status.PLANNED if index != 2 else Event.Status.APPROVED,
            display_visibility=visibility[index],
        )
    Event.objects.create(
        title="[P11] Awaiting leadership decision",
        event_type=event_type,
        venue=venues[0],
        planned_date=now.date() + timedelta(days=3),
        start_time=dt_time(15),
        end_time=dt_time(16),
        responsible_employee=responsible,
        management_responsible=manager,
        created_by=responsible,
        status=Event.Status.PENDING_APPROVAL,
    )
    return admin_user, manager, responsible, content_manager, reception, delete_venue


def wait_for_server():
    for _ in range(50):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=1) as response:
                return response.status == 200
        except Exception:
            time.sleep(0.25)
    return False


def login(page, username):
    page.goto(f"{BASE_URL}/accounts/login/")
    page.fill("input[name=username]", username)
    page.fill("input[name=password]", PASSWORD)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def shot(page, name, size, selector=None):
    if os.environ.get("IEMS_REGRESSION_NO_SHOTS") == "1":
        return
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.wait_for_timeout(300)
    if selector:
        page.locator(selector).screenshot(path=str(OUTPUT / name))
    else:
        page.screenshot(path=str(OUTPUT / name), full_page=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    admin_user, manager, responsible, content_manager, reception, delete_venue = prepare_data()
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_server():
            raise RuntimeError("Django acceptance server did not start")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/dashboard/")
            page.wait_for_selector("[data-dashboard]")
            assert page.locator("[data-metric]").count() == 5
            assert page.locator(".live-venue-card").count() == 4
            public_payload = page.evaluate(
                "async () => await (await fetch('/api/public/dashboard/')).json()"
            )
            serialized = str(public_payload)
            assert "[P11] International Health Partnership 1" in serialized
            assert "[P11] International Health Partnership 2" not in serialized
            assert "[P11] International Health Partnership 3" not in serialized
            shot(page, "phase11_01_public_dashboard_1920.png", (1920, 1080))
            shot(page, "phase11_02_public_dashboard_1366.png", (1366, 768))
            page.goto(f"{BASE_URL}/dashboard/calendar/")
            page.wait_for_selector(".calendar-grid")
            shot(page, "phase11_03_calendar_month.png", (1366, 900))
            page.locator(".calendar-event").first.click()
            assert page.locator("[data-event-dialog]").is_visible()
            page.click("[data-dialog-close]")
            page.click('[data-view="week"]')
            page.wait_for_timeout(300)
            shot(page, "phase11_04_calendar_week.png", (1366, 900))
            page.click('[data-view="day"]')
            page.wait_for_selector(".day-agenda")
            page.click('[data-view="list"]')
            page.wait_for_selector(".calendar-agenda")
            page.goto(f"{BASE_URL}/venues/live/")
            shot(page, "phase11_05_live_venues.png", (1366, 900))
            login(page, responsible.username)
            shot(page, "phase11_06_user_workspace.png", (1366, 900))
            page.context.clear_cookies()
            login(page, manager.username)
            shot(page, "phase11_07_management_workspace.png", (1366, 900))
            page.context.clear_cookies()
            login(page, content_manager.username)
            assert page.locator('a[href="/publications/"]').count() == 1
            assert page.locator('a[href="/master-data/venues/"]').count() == 0
            page.context.clear_cookies()
            login(page, reception.username)
            assert page.locator('a[href="/publications/"]').count() == 0
            assert page.locator('a[href="/master-data/venues/"]').count() == 0
            page.context.clear_cookies()
            login(page, admin_user.username)
            page.goto(f"{BASE_URL}/admin/")
            shot(page, "phase11_08_admin_home.png", (1366, 900))
            page.goto(f"{BASE_URL}/admin/events/event/")
            shot(page, "phase11_09_admin_event_list.png", (1366, 900))
            page.goto(f"{BASE_URL}/admin/venues/venue/{delete_venue.pk}/delete/")
            page.click("button[type=submit]")
            assert not Venue.objects.filter(pk=delete_venue.pk).exists()
            page.context.clear_cookies()
            page.goto(f"{BASE_URL}/dashboard/")
            page.set_viewport_size({"width": 768, "height": 1024})
            assert page.locator("body").evaluate("el => el.scrollWidth <= window.innerWidth")
            shot(page, "phase11_10_mobile_dashboard.png", (375, 812))
            assert page.locator("body").evaluate("el => el.scrollWidth <= window.innerWidth")
            browser.close()
        print("PASS — PHASE 11 UI ACCEPTANCE")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        cleanup()


if __name__ == "__main__":
    main()
