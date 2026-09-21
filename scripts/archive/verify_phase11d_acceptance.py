"""Phase 11D premium institutional visual acceptance with isolated QA data."""

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
PORT = 8574
BASE = f"http://127.0.0.1:{PORT}"
OUT = Path("tests/visual_baseline")
PASSWORD = secrets.token_urlsafe(24)
TAG = "P11D_VISUAL_QA"


def cleanup():
    Event.objects.filter(description=TAG).delete()
    EventType.objects.filter(code__startswith="p11d-").delete()
    Venue.objects.filter(code__startswith="I11D").delete()
    Organization.objects.filter(name__startswith="P11D QA").delete()
    User.objects.filter(username__startswith="p11d_").delete()


def prepare():
    cache.clear()
    cleanup()
    now = timezone.localtime()
    admin = User.objects.create_superuser(
        "p11d_admin", password=PASSWORD, first_name="Aziz", last_name="Karimov"
    )
    owner = User.objects.create_user(
        "p11d_owner",
        password=PASSWORD,
        first_name="Dilnoza",
        last_name="Rasulova",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )
    organization = Organization.objects.create(
        name="P11D QA International Oncology Institute", short_name="IOI"
    )
    types = [
        EventType.objects.create(
            code=f"p11d-{code}", name_uz=name, name_ru=name, name_en=en, color=color, sort_order=i
        )
        for i, (code, name, en, color) in enumerate(
            (
                ("symposium", "Simpozium", "Symposium", "#087FDB"),
                ("board", "Konsilium", "Tumor Board", "#00A9B7"),
                ("seminar", "Seminar", "Seminar", "#08A17A"),
                ("workshop", "Ustaxona", "Workshop", "#F15A24"),
                ("visit", "Tashrif", "Visit", "#CF248F"),
            ),
            1,
        )
    ]
    venues = [
        Venue.objects.create(
            code=f"I11D{i}",
            name_uz=name,
            name_ru=en,
            name_en=en,
            capacity=80 + i * 30,
            working_start=dt_time(8),
            working_end=dt_time(20),
            sort_order=i,
        )
        for i, (name, en) in enumerate(
            (
                ("Xalqaro konferensiyalar zali", "International Conference Hall"),
                ("Multidisiplinar konsilium xonasi", "Tumor Board Room"),
                ("Ilmiy seminarlar zali", "Research Seminar Hall"),
                ("Klinik ta’lim markazi", "Clinical Education Center"),
            ),
            1,
        )
    ]
    titles = (
        "International Oncology Symposium",
        "Multidisciplinary Tumor Board",
        "International Research Seminar",
        "Clinical Protocol Workshop",
        "Visiting Professor Session",
        "Central Asia Cancer Partnership Forum",
        "Precision Oncology Leadership Meeting",
        "International Nursing Education Roundtable",
        "Radiotherapy Innovation Briefing",
        "Emergency Coordination Session",
    )
    events = []
    for i, title in enumerate(titles):
        day = now.date() + timedelta(days=0 if i < 4 else (i % 5) + 1)
        hour = max(8, min(18, (now.hour - 1 + i * 2) if i < 4 else 9 + (i % 6)))
        event = Event.objects.create(
            title=title,
            description=TAG,
            event_type=types[i % len(types)],
            venue=venues[i % 4],
            planned_date=day,
            start_time=dt_time(hour),
            end_time=dt_time(min(hour + 1 + (i % 2), 20), 30),
            responsible_employee=owner,
            management_responsible=admin,
            created_by=admin,
            status=Event.Status.EMERGENCY if i == 9 else Event.Status.APPROVED,
            priority=Event.Priority.EMERGENCY
            if i == 9
            else (Event.Priority.HIGH if i % 3 == 0 else Event.Priority.NORMAL),
            display_visibility=Event.DisplayVisibility.FULL,
            is_public_enabled=True,
        )
        event.organizing_organizations.add(organization)
        events.append(event)
    return admin, events[0]


def wait_server():
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"{BASE}/health/", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Phase 11D server did not start")


def login(page, user):
    page.goto(f"{BASE}/accounts/login/")
    page.fill("input[name=username]", user.username)
    page.fill("input[name=password]", PASSWORD)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def shot(page, name, width=1366, height=900):
    page.set_viewport_size({"width": width, "height": height})
    page.wait_for_timeout(450)
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    admin, event = prepare()
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
            response = page.goto(f"{BASE}/dashboard/")
            assert response and response.status == 200, (
                page.url,
                response.status if response else None,
            )
            assert page.locator(".institutional-lockup").count() == 1, (page.url, page.title())
            assert page.locator(".institution-logo").count() == 2
            shot(page, "01_public_dashboard_1920", 1920, 1080)
            shot(page, "02_public_dashboard_1366", 1366, 768)
            page.goto(f"{BASE}/dashboard/calendar/?date=2034-01-01&view=month")
            page.wait_for_selector(".view-month")
            shot(page, "03_calendar_month")
            page.goto(f"{BASE}/dashboard/calendar/")
            page.wait_for_selector(".calendar-event")
            shot(page, "04_calendar_month_with_events")
            page.click('[data-view="week"]')
            page.wait_for_selector(".week-scheduler")
            assert page.locator(".week-event-wrap").count() > 0
            shot(page, "05_calendar_week")
            page.click('[data-view="day"]')
            page.wait_for_selector(".day-agenda")
            shot(page, "06_calendar_day")
            page.click('[data-view="list"]')
            page.wait_for_selector(".calendar-agenda")
            shot(page, "07_calendar_list")
            page.locator("[data-event-index]").first.click()
            assert page.locator(".event-drawer").is_visible()
            shot(page, "08_calendar_event_drawer")
            page.click("[data-dialog-close]")
            page.fill('[data-filter="search"]', "Oncology")
            page.wait_for_timeout(400)
            assert page.locator("[data-filter-chips] button").count() == 1
            shot(page, "09_calendar_filters")
            page.goto(f"{BASE}/venues/live/")
            shot(page, "10_live_venues_mixed_states")
            login(page, admin)
            page.goto(f"{BASE}/workspace/")
            shot(page, "11_workspace")
            page.goto(f"{BASE}/profile/")
            shot(page, "12_profile")
            page.goto(f"{BASE}/admin/")
            assert page.locator(".admin-brand .institution-logo").count() == 2
            shot(page, "13_admin_dashboard")
            page.goto(f"{BASE}/admin/events/event/")
            shot(page, "14_admin_events")
            page.goto(f"{BASE}/admin/events/event/{event.pk}/change/")
            shot(page, "15_admin_event_form")
            page.context.clear_cookies()
            page.goto(f"{BASE}/dashboard/")
            shot(page, "16_mobile_dashboard", 375, 812)
            assert page.evaluate("document.body.scrollWidth<=innerWidth")
            page.goto(f"{BASE}/dashboard/calendar/")
            page.wait_for_selector(".calendar-agenda")
            shot(page, "17_mobile_calendar", 375, 812)
            assert page.evaluate("document.body.scrollWidth<=innerWidth")
            page.set_viewport_size({"width": 768, "height": 1024})
            page.goto(f"{BASE}/dashboard/calendar/?view=month")
            page.wait_for_selector(".view-month")
            shot(page, "18_tablet_calendar", 768, 1024)
            reduced = browser.new_context(reduced_motion="reduce").new_page()
            reduced.goto(f"{BASE}/dashboard/")
            assert reduced.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
            assert TAG not in page.locator("body").inner_text()
            browser.close()
        print("PASS — PHASE 11D VISUAL ACCEPTANCE")
    finally:
        server.terminate()
        server.wait(timeout=5)
        cleanup()
        assert not Event.objects.filter(description=TAG).exists()


if __name__ == "__main__":
    main()
