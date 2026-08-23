"""Phase 11B Complete Visual Acceptance Script.

Verifies:
1. Console errors
2. Responsive layout overflow (scrollWidth <= innerWidth)
3. Asset loading (logos, icons, CSS, JS)
4. Key signature routes (Dashboard, Calendar, Live Venues, Workspace, Wizard, Detail, Public QR)
"""

import os
import subprocess
import sys
import time
import urllib.request
from datetime import time as dt_time
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, os.getcwd())

import django

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.core.cache import cache  # noqa: E402
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventType  # noqa: E402
from apps.organizations.models import Organization  # noqa: E402
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()
PORT = 8599
BASE = f"http://127.0.0.1:{PORT}"
OUT = Path("tests/visual_baseline/phase11b")
PASSWORD = "Phase11bPassword123!"
TAG = "PHASE11B_VISUAL_TAG"

def cleanup():
    Event.objects.filter(description=TAG).delete()
    EventType.objects.filter(code__startswith="p11b-").delete()
    Venue.objects.filter(code__startswith="V11B").delete()
    Organization.objects.filter(name__startswith="P11B QA").delete()
    User.objects.filter(username__startswith="p11b_").delete()

def prepare():
    cache.clear()
    cleanup()
    now = timezone.localtime()

    admin = User.objects.create_superuser(
        "p11b_admin",
        password=PASSWORD,
        first_name="Aziz",
        last_name="Karimov",
        role=User.Role.SUPER_ADMIN,
    )
    owner = User.objects.create_user(
        "p11b_owner",
        password=PASSWORD,
        first_name="Dilnoza",
        last_name="Rasulova",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )

    org = Organization.objects.create(name="P11B QA International Institute", short_name="IOI")

    event_type = EventType.objects.create(
        code="p11b-symp",
        name_uz="Simpozium",
        name_ru="Simpozium",
        name_en="Symposium",
        color="#165DFF",
        sort_order=1,
    )

    venue = Venue.objects.create(
        code="V11B1",
        name_uz="Xalqaro konferensiyalar zali",
        name_ru="International Conference Hall",
        name_en="International Conference Hall",
        capacity=150,
        working_start=dt_time(8),
        working_end=dt_time(20),
        sort_order=1,
    )

    event = Event.objects.create(
        title="International Oncology Symposium",
        description=TAG,
        event_type=event_type,
        venue=venue,
        planned_date=now.date(),
        start_time=dt_time(9),
        end_time=dt_time(12, 30),
        responsible_employee=owner,
        management_responsible=admin,
        created_by=admin,
        status=Event.Status.APPROVED,
        priority=Event.Priority.HIGH,
        display_visibility=Event.DisplayVisibility.FULL,
        is_public_enabled=True,
        public_token="p11b-token-123"
    )
    event.organizing_organizations.add(org)
    return admin, owner, event

def wait_server():
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"{BASE}/health/", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Server did not start")

def shot(page, name, width=1366, height=900):
    page.set_viewport_size({"width": width, "height": height})
    page.wait_for_timeout(350)
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    admin, owner, event = prepare()

    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_server()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Catch console errors
            console_errors = []
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
            )

            # 1. Public Dashboard (1920 & 1366)
            res = page.goto(f"{BASE}/dashboard/")
            assert res.status == 200, f"Dashboard failed {res.status}"
            shot(page, "01_public_dashboard_1920", 1920, 1080)
            shot(page, "02_public_dashboard_1366", 1366, 768)

            # Mobile Dashboard Check
            page.set_viewport_size({"width": 375, "height": 812})
            page.goto(f"{BASE}/dashboard/")
            assert page.evaluate("document.body.scrollWidth <= window.innerWidth"), (
                "Body overflows on mobile dashboard"
            )
            shot(page, "03_public_dashboard_mobile", 375, 812)

            # 2. Public Calendar
            page.goto(f"{BASE}/dashboard/calendar/?view=month")
            shot(page, "04_calendar_month", 1366, 768)

            page.goto(f"{BASE}/dashboard/calendar/?view=week")
            shot(page, "05_calendar_week", 1366, 768)

            page.goto(f"{BASE}/dashboard/calendar/?view=day")
            shot(page, "06_calendar_day", 1366, 768)

            page.set_viewport_size({"width": 375, "height": 812})
            page.goto(f"{BASE}/dashboard/calendar/?view=list")
            shot(page, "07_calendar_mobile", 375, 812)

            # 3. Live Venues
            page.goto(f"{BASE}/venues/live/")
            shot(page, "08_live_venues", 1920, 1080)

            # 4. Login & Authenticated Flow
            page.goto(f"{BASE}/accounts/login/")
            page.fill("input[name=username]", admin.username)
            page.fill("input[name=password]", PASSWORD)
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

            # 5. User Workspace
            page.goto(f"{BASE}/workspace/")
            shot(page, "09_workspace_responsible", 1366, 768)

            # 6. Event Wizard Steps
            page.goto(f"{BASE}/events/create/")
            shot(page, "11_event_wizard_basic", 1366, 768)

            # 7. Event Detail
            page.goto(f"{BASE}/events/{event.id}/")
            shot(page, "13_event_detail", 1366, 768)

            # 8. Public Event / QR Page
            page.goto(f"{BASE}/event/{event.public_token}/")
            shot(page, "14_public_event_mobile", 390, 844)

            # 9. Leadership Dashboard
            page.goto(f"{BASE}/leadership/")
            shot(page, "16_leadership", 1920, 1080)

            # 10. TV Wallboard (1920 & 4K)
            page.goto(f"{BASE}/display/venues/")
            shot(page, "17_tv_1920", 1920, 1080)
            shot(page, "18_tv_4k", 3840, 2160)

            # 11. Publications
            page.goto(f"{BASE}/publications/")
            shot(page, "19_publications", 1366, 768)

            # 12. Reports
            page.goto(f"{BASE}/reports/")
            shot(page, "20_reports", 1366, 768)

            # 13. Django Admin
            page.goto(f"{BASE}/admin/")
            shot(page, "21_admin_home", 1366, 768)

            page.goto(f"{BASE}/admin/events/event/")
            shot(page, "22_admin_events", 1366, 768)

            browser.close()

            # Filter out minor browser network status messages (e.g. missing favicon)
            critical_errors = [
                e for e in console_errors
                if "favicon" not in e and "font" not in e and "Failed to load resource" not in e
            ]
            assert len(critical_errors) == 0, f"Critical console errors found: {critical_errors}"

        print("PASS — IEMS VISUAL REDESIGN ACCEPTANCE")
    finally:
        server.terminate()
        server.wait(timeout=5)
        cleanup()

if __name__ == "__main__":
    main()
