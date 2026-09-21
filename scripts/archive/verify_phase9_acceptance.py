import os
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
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.attendance.models import EventAttendance  # noqa: E402
from apps.audit.models import AuditEventLog  # noqa: E402
from apps.events.models import Event, EventType  # noqa: E402
from apps.notifications.models import TelegramDelivery  # noqa: E402
from apps.organizations.models import Organization, Sponsor  # noqa: E402
from apps.publications.models import Publication  # noqa: E402
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()
PORT = 8563
BASE_URL = f"http://127.0.0.1:{PORT}"
OUTPUT = Path("tests/visual_baseline")
OUTPUT.mkdir(parents=True, exist_ok=True)


def cleanup():
    Event.objects.filter(title__startswith="[P9]").delete()
    EventType.objects.filter(code="p9-acceptance").delete()
    Venue.objects.filter(code__in=("P9-A", "P9-B")).delete()
    Organization.objects.filter(name="[P9] International Partner").delete()
    Sponsor.objects.filter(name="[P9] Medical Sponsor").delete()
    User.objects.filter(username__startswith="p9_accept_").delete()


def prepare_data():
    cleanup()
    roles = {
        "leader": User.Role.LEADERSHIP_VIEWER,
        "manager": User.Role.MANAGEMENT_RESPONSIBLE,
        "reception": User.Role.RECEPTION_OPERATOR,
        "content": User.Role.CONTENT_MANAGER,
        "responsible": User.Role.RESPONSIBLE_EMPLOYEE,
    }
    users = {}
    for name, role in roles.items():
        users[name] = User.objects.create_user(
            f"p9_accept_{name}", password="Phase9-Safe-Test!", role=role
        )
    venues = []
    for code, name in (("P9-A", "International Hall"), ("P9-B", "Seminar Hall")):
        venues.append(
            Venue.objects.create(
                code=code,
                name_uz=name,
                name_ru=name,
                name_en=name,
                capacity=200,
                working_start=dt_time(8),
                working_end=dt_time(20),
            )
        )
    event_type = EventType.objects.create(
        code="p9-acceptance", name_uz="Forum", name_ru="Форум", name_en="Forum"
    )
    organization = Organization.objects.create(name="[P9] International Partner")
    sponsor = Sponsor.objects.create(name="[P9] Medical Sponsor")
    today = timezone.localdate()
    events = []
    for index in range(8):
        event = Event.objects.create(
            title=f"[P9] International Event {index + 1}",
            event_type=event_type,
            venue=venues[index % 2],
            planned_date=today + timedelta(days=index - 3),
            start_time=dt_time(9 + index % 4),
            end_time=dt_time(11 + index % 4),
            responsible_employee=users["responsible"],
            management_responsible=users["manager"],
            created_by=users["responsible"],
            status=Event.Status.COMPLETED if index < 3 else Event.Status.APPROVED,
            priority=Event.Priority.EMERGENCY if index == 7 else Event.Priority.NORMAL,
            expected_attendees=50 + index * 10,
        )
        event.organizing_organizations.add(organization)
        event.sponsors.add(sponsor)
        events.append(event)
    for index in range(25):
        EventAttendance.objects.create(
            event=events[0],
            attendee_identifier_hash=f"p9-accept-{index}",
            attendee_name="" if index < 5 else f"Guest {index}",
            checkin_method=(
                EventAttendance.Method.PUBLIC_QR
                if index < 18
                else EventAttendance.Method.STAFF_MANUAL
            ),
        )
    now = timezone.now()
    events[1].submitted_at = now - timedelta(hours=7)
    events[1].reviewed_at = now - timedelta(hours=2)
    events[1].save(update_fields=("submitted_at", "reviewed_at"))
    AuditEventLog.objects.create(action="event.submitted", target_id=str(events[1].pk))
    AuditEventLog.objects.create(action="event.approved", target_id=str(events[1].pk))
    for platform, status in (
        (Publication.Platform.TELEGRAM_CHANNEL, Publication.Status.PUBLISHED),
        (Publication.Platform.INSTAGRAM, Publication.Status.FAILED),
    ):
        Publication.objects.create(
            event=events[0],
            platform=platform,
            language="uz",
            headline=events[0].title,
            created_by=users["content"],
            status=status,
        )
    TelegramDelivery.objects.create(
        event=events[0],
        recipient_user=users["responsible"],
        notification_type="reminder_1d",
        scheduled_for=now,
        status=TelegramDelivery.Status.SENT,
    )
    return users, venues, event_type, organization, sponsor


def wait_for_server():
    for _ in range(40):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=1) as response:
                return response.status == 200
        except Exception:
            time.sleep(0.3)
    return False


def login(page, username):
    page.goto(f"{BASE_URL}/accounts/login/")
    page.fill("input[name=username]", username)
    page.fill("input[name=password]", "Phase9-Safe-Test!")
    page.click("button[type=submit]")


def shot(page, name, selector=None, size=(1440, 1000)):
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.wait_for_timeout(150)
    target = page.locator(selector) if selector else page
    target.screenshot(path=str(OUTPUT / name))


def main():
    users, venues, event_type, organization, sponsor = prepare_data()
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_server():
            raise RuntimeError("Django server did not start")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000}, accept_downloads=True)
            login(page, users["leader"].username)
            page.goto(f"{BASE_URL}/reports/")
            page.wait_for_selector("[data-testid=report-kpis]")
            shot(page, "phase9_01_reports_dashboard.png")
            shot(page, "phase9_02_event_trend.png", "[data-testid=event-trend]")
            shot(page, "phase9_03_venue_utilization.png", "[data-testid=venue-utilization]")
            shot(page, "phase9_04_attendance.png", "[data-testid=attendance-analytics]")
            shot(page, "phase9_05_approval_performance.png", "[data-testid=approval-performance]")
            shot(page, "phase9_06_publications.png", "[data-testid=publication-analytics]")

            page.select_option("select[name=venue]", str(venues[0].pk))
            page.select_option("select[name=event_type]", str(event_type.pk))
            page.select_option("select[name=organization]", str(organization.pk))
            page.select_option("select[name=sponsor]", str(sponsor.pk))
            page.click("[data-testid=report-filters] button[type=submit]")
            shot(page, "phase9_07_filters.png", "[data-testid=report-filters]")

            for suffix in ("csv", "xlsx", "pdf"):
                with page.expect_download() as download_info:
                    page.click(f'a[href*="export/{suffix}"]')
                assert Path(download_info.value.path()).stat().st_size > 100

            for language in ("uz", "ru", "en"):
                page.click(f"button[name=language][value={language}]")
                page.wait_for_selector("[data-testid=report-kpis]")
            for size in ((1920, 1080), (1366, 768), (768, 1024), (375, 812)):
                page.set_viewport_size({"width": size[0], "height": size[1]})
                assert page.locator("[data-testid=report-kpis]").is_visible()
            shot(page, "phase9_08_mobile_reports.png", size=(375, 812))

            for name in ("manager", "reception", "content", "responsible"):
                page.context.clear_cookies()
                login(page, users[name].username)
                assert page.goto(f"{BASE_URL}/reports/").status == 200
            body = page.locator("body").inner_text()
            assert "chat_id" not in body and "attendee_identifier_hash" not in body
            browser.close()
        print("PASS — Phase 9 Playwright acceptance")
    finally:
        server.terminate()
        server.wait(timeout=10)
        cleanup()


if __name__ == "__main__":
    main()
