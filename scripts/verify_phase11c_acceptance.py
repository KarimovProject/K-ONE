"""Phase 11C premium visual acceptance with clean, realistic fixtures."""

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
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()
PORT = 8573
BASE_URL = f"http://127.0.0.1:{PORT}"
OUTPUT = Path("tests/visual_baseline")
PASSWORD = secrets.token_urlsafe(24)


def cleanup():
    Event.objects.filter(description="P11C_VISUAL_FIXTURE").delete()
    EventType.objects.filter(code="p11c-forum").delete()
    Venue.objects.filter(code__startswith="I11C").delete()
    User.objects.filter(username__startswith="p11c_").delete()


def prepare_data():
    cache.clear()
    cleanup()
    admin = User.objects.create_superuser(
        "p11c_admin", password=PASSWORD, first_name="Aziz", last_name="Karimov"
    )
    responsible = User.objects.create_user(
        "p11c_coordinator",
        password=PASSWORD,
        first_name="Dilnoza",
        last_name="Rasulova",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )
    kind = EventType.objects.create(
        code="p11c-forum",
        name_uz="Xalqaro forum",
        name_ru="Международный форум",
        name_en="International forum",
        color="#0EA5E9",
        sort_order=1,
    )
    venue_names = (
        ("I11C1", "Xalqaro konferensiyalar zali", "International Conference Hall"),
        ("I11C2", "Diplomatik uchrashuvlar xonasi", "Diplomatic Meeting Room"),
        ("I11C3", "Ilmiy seminarlar zali", "Scientific Seminar Hall"),
        ("I11C4", "Rahbariyat majlislar xonasi", "Executive Meeting Room"),
    )
    venues = [
        Venue.objects.create(
            code=code,
            name_uz=uz,
            name_ru=en,
            name_en=en,
            capacity=120,
            working_start=dt_time(8),
            working_end=dt_time(20),
            sort_order=1 + index,
        )
        for index, (code, uz, en) in enumerate(venue_names)
    ]
    now = timezone.localtime()
    titles = (
        "Markaziy Osiyo onkologiya forumi",
        "Xalqaro klinik hamkorlik uchrashuvi",
        "Tibbiy ta’lim va innovatsiyalar seminari",
        "Yevropa delegatsiyasi bilan strategik muloqot",
        "Global sog‘liqni saqlash tashabbuslari konferensiyasi",
        "Ilmiy tadqiqotlar bo‘yicha hamkorlik sessiyasi",
        "Xalqaro rezidentura dasturlari taqdimoti",
        "Sog‘liqni saqlash diplomatiyasi davra suhbati",
        "Raqamli tibbiyot va sun’iy intellekt simpoziumi",
        "Favqulodda tashkiliy muvofiqlashtirish yig‘ilishi",
    )
    created = []
    for index, title in enumerate(titles):
        day = now.date() if index < 3 else now.date() + timedelta(days=index % 5 + 1)
        hour = 9 + (index % 6)
        created.append(
            Event.objects.create(
                title=title,
                description="P11C_VISUAL_FIXTURE",
                event_type=kind,
                venue=venues[index % 4],
                planned_date=day,
                start_time=dt_time(hour),
                end_time=dt_time(min(hour + 1, 19), 30),
                responsible_employee=responsible,
                management_responsible=admin,
                created_by=admin,
                status=Event.Status.EMERGENCY if index == 9 else Event.Status.APPROVED,
                priority=Event.Priority.EMERGENCY if index == 9 else Event.Priority.NORMAL,
                display_visibility=Event.DisplayVisibility.FULL,
                is_public_enabled=True,
            )
        )
    return admin, created[0], venues


def wait_server():
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=1) as response:
                return response.status == 200
        except Exception:
            time.sleep(.25)
    return False


def login(page, user):
    page.goto(f"{BASE_URL}/accounts/login/")
    page.fill("input[name=username]", user.username)
    page.fill("input[name=password]", PASSWORD)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def shot(page, name, width=1366, height=900):
    page.set_viewport_size({"width": width, "height": height})
    page.wait_for_timeout(250)
    page.screenshot(path=str(OUTPUT / name), full_page=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    admin, event, venues = prepare_data()
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_server():
            raise RuntimeError("Phase 11C server did not start")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/dashboard/")
            page.wait_for_selector(".public-metrics article")
            assert "ACCEPTANCE_DEMO" not in page.locator("body").inner_text()
            assert "Test Zali" not in page.locator("body").inner_text()
            shot(page, "phase11c_01_dashboard_1920.png", 1920, 1080)
            shot(page, "phase11c_02_dashboard_1366.png")

            page.goto(f"{BASE_URL}/dashboard/calendar/")
            page.wait_for_selector(".view-month")
            assert page.locator(".calendar-event").count() > 0
            shot(page, "phase11c_03_calendar_month.png")
            page.click('[data-view="week"]')
            page.wait_for_selector(".week-scheduler")
            shot(page, "phase11c_04_calendar_week.png")
            page.click('[data-view="day"]')
            page.wait_for_selector(".day-agenda")
            shot(page, "phase11c_05_calendar_day.png")
            page.click('[data-view="list"]')
            page.wait_for_selector(".calendar-agenda")
            shot(page, "phase11c_06_calendar_list.png")
            page.locator(".agenda-row button").first.click()
            assert page.locator(".event-drawer").is_visible()
            shot(page, "phase11c_07_calendar_drawer.png")
            page.click("[data-dialog-close]")
            page.goto(f"{BASE_URL}/venues/live/")
            assert "ACCD" not in page.locator("body").inner_text()
            shot(page, "phase11c_08_live_venues.png")

            login(page, admin)
            page.goto(f"{BASE_URL}/workspace/")
            assert "Planned Events" not in page.locator("body").inner_text()
            assert "p11c_coordinator" not in page.locator("body").inner_text()
            shot(page, "phase11c_09_workspace.png")
            page.goto(f"{BASE_URL}/admin/")
            shot(page, "phase11c_10_admin_dashboard.png")
            page.goto(f"{BASE_URL}/admin/events/event/")
            shot(page, "phase11c_11_admin_events.png")
            page.goto(f"{BASE_URL}/admin/events/event/{event.pk}/change/")
            shot(page, "phase11c_12_admin_event_form.png")
            page.goto(f"{BASE_URL}/profile/")
            shot(page, "phase11c_13_profile.png")

            page.context.clear_cookies()
            page.goto(f"{BASE_URL}/dashboard/")
            shot(page, "phase11c_14_mobile_dashboard.png", 390, 844)
            assert page.locator("body").evaluate("el => el.scrollWidth <= innerWidth")
            page.goto(f"{BASE_URL}/dashboard/calendar/")
            page.wait_for_selector(".calendar-agenda")
            shot(page, "phase11c_15_mobile_calendar.png", 375, 812)
            assert page.locator("body").evaluate("el => el.scrollWidth <= innerWidth")

            reduced = browser.new_context(reduced_motion="reduce").new_page()
            reduced.goto(f"{BASE_URL}/dashboard/")
            assert reduced.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
            browser.close()
        print("PASS — PHASE 11C VISUAL ACCEPTANCE")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        cleanup()


if __name__ == "__main__":
    main()
