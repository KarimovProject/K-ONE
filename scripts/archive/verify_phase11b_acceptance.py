"""Phase 11B visual and interaction acceptance using isolated local data."""

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, os.getcwd())

import django

django.setup()

from playwright.sync_api import sync_playwright  # noqa: E402

import scripts.verify_phase11_ui_acceptance as phase11  # noqa: E402
from apps.events.models import Event  # noqa: E402

PORT = 8572
BASE_URL = f"http://127.0.0.1:{PORT}"
OUTPUT = Path("tests/visual_baseline")


def wait_for_server():
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=1) as response:
                return response.status == 200
        except Exception:
            time.sleep(0.25)
    return False


def login(page, username):
    page.goto(f"{BASE_URL}/accounts/login/")
    page.fill("input[name=username]", username)
    page.fill("input[name=password]", phase11.PASSWORD)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


def shot(page, name, width=1366, height=900):
    if os.environ.get("IEMS_REGRESSION_NO_SHOTS") == "1":
        return
    page.set_viewport_size({"width": width, "height": height})
    page.wait_for_timeout(250)
    page.screenshot(path=str(OUTPUT / name), full_page=True)


def assert_no_overflow(page):
    assert page.locator("body").evaluate("el => el.scrollWidth <= window.innerWidth")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    admin, manager, responsible, _, _, delete_venue = phase11.prepare_data()
    editable = Event.objects.filter(title__startswith="[P11]").order_by("pk").first()
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_server():
            raise RuntimeError("Phase 11B acceptance server did not start")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(reduced_motion="no-preference")
            page = context.new_page()
            login(page, admin.username)

            page.goto(f"{BASE_URL}/admin/")
            page.wait_for_selector(".admin-kpis")
            assert page.locator(".admin-kpis article").count() == 5
            assert page.locator(".admin-quick a").count() >= 4
            assert page.locator(".admin-nav").is_visible()
            page.locator(".admin-profile summary").click()
            assert page.locator(".admin-profile a", has_text="Profil").is_visible()
            page.locator(".admin-profile summary").click()
            shot(page, "phase11b_01_admin_dashboard.png")

            page.goto(f"{BASE_URL}/admin/events/event/")
            page.wait_for_selector("#result_list")
            assert page.locator("#searchbar").is_visible()
            assert page.locator(".admin-filters").count() == 1
            shot(page, "phase11b_02_admin_events.png")

            page.goto(f"{BASE_URL}/admin/events/event/{editable.pk}/change/")
            page.wait_for_selector(".admin-modern-form")
            assert page.locator(".admin-fieldsets .module").count() >= 5
            assert page.locator(".admin-sticky-actions").is_visible()
            shot(page, "phase11b_03_admin_event_form.png")

            page.goto(f"{BASE_URL}/admin/accounts/user/")
            page.wait_for_selector("#result_list")
            shot(page, "phase11b_04_admin_users.png")
            page.goto(f"{BASE_URL}/admin/venues/venue/")
            page.wait_for_selector("#result_list")
            page.goto(f"{BASE_URL}/admin/venues/venue/{delete_venue.pk}/delete/")
            page.wait_for_selector(".delete-card")
            shot(page, "phase11b_05_admin_delete.png")

            page.goto(f"{BASE_URL}/admin/")
            page.locator('.admin-languages button[value="ru"]').click()
            page.wait_for_load_state("networkidle")
            assert page.locator("html").get_attribute("lang").startswith("ru")
            page.locator('.admin-languages button[value="uz"]').click()
            page.wait_for_load_state("networkidle")

            page.goto(f"{BASE_URL}/workspace/")
            page.wait_for_selector(".workspace-hero")
            shot(page, "phase11b_06_workspace.png")
            page.goto(f"{BASE_URL}/profile/")
            page.wait_for_selector(".profile-layout")
            shot(page, "phase11b_07_profile.png")

            context.clear_cookies()
            page.goto(f"{BASE_URL}/dashboard/")
            page.wait_for_selector("[data-dashboard]")
            shot(page, "phase11b_08_public_dashboard.png")
            page.goto(f"{BASE_URL}/dashboard/calendar/")
            page.wait_for_selector(".calendar-grid")
            shot(page, "phase11b_09_calendar_month.png")
            page.locator('[data-view="week"]').click()
            page.wait_for_selector(".week-scheduler")
            shot(page, "phase11b_10_calendar_week.png")
            page.goto(f"{BASE_URL}/venues/live/")
            page.wait_for_selector(".live-venue-card")
            shot(page, "phase11b_11_live_venues.png")

            login(page, admin.username)
            page.goto(f"{BASE_URL}/admin/")
            page.set_viewport_size({"width": 375, "height": 812})
            assert_no_overflow(page)
            page.locator("[data-sidebar-open]").click()
            assert page.locator(".admin-sidebar").is_visible()
            page.locator("[data-sidebar-close]").click()
            shot(page, "phase11b_12_mobile_admin.png", 375, 812)

            context.clear_cookies()
            page.goto(f"{BASE_URL}/dashboard/")
            assert_no_overflow(page)
            shot(page, "phase11b_13_mobile_public.png", 375, 812)

            reduced = browser.new_context(reduced_motion="reduce").new_page()
            reduced.goto(f"{BASE_URL}/dashboard/")
            assert reduced.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
            browser.close()
        print("PASS — PHASE 11B VISUAL ACCEPTANCE")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        phase11.cleanup()


if __name__ == "__main__":
    main()
