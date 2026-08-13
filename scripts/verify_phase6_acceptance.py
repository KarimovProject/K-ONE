import os
import subprocess
import sys
import time
import urllib.request
from datetime import time as dt_time
from datetime import timedelta
from pathlib import Path

import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventType  # noqa: E402
from apps.venues.models import DisplayToken, Venue  # noqa: E402

User = get_user_model()
PORT = 8560
BASE_URL = f"http://127.0.0.1:{PORT}"
OUTPUT = Path("tests/visual_baseline")
OUTPUT.mkdir(parents=True, exist_ok=True)


def wait_for_server() -> bool:
    for _ in range(40):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=1) as response:
                return response.status == 200
        except Exception:
            time.sleep(0.3)
    return False


def prepare_data():
    leader, _ = User.objects.get_or_create(
        username="phase6_leader",
        defaults={"role": User.Role.LEADERSHIP_VIEWER, "is_active": True},
    )
    leader.set_password("Phase6-Safe-Test!")
    leader.save()
    event_type, _ = EventType.objects.get_or_create(
        code="phase6-briefing",
        defaults={
            "name_uz": "Rahbariyat uchrashuvi",
            "name_ru": "Встреча руководства",
            "name_en": "Leadership meeting",
        },
    )
    venues = []
    venue_states = []
    for index, code in enumerate(("ICH", "SSH", "INR", "EMR"), 1):
        venue, created = Venue.objects.get_or_create(
            code=code,
            defaults={
                "name_uz": f"Phase 6 xona {index}",
                "name_ru": f"Помещение Phase 6 {index}",
                "name_en": f"Phase 6 venue {index}",
                "capacity": 100,
                "working_start": dt_time(0),
                "working_end": dt_time(23, 59),
                "sort_order": index,
            },
        )
        venue_states.append((venue.pk, created, venue.is_active, venue.sort_order))
        venue.is_active = True
        venue.sort_order = index
        venue.save(update_fields=["is_active", "sort_order"])
        venues.append(venue)
    Event.objects.filter(title__startswith="[P6]").delete()
    now = timezone.localtime()
    current_start = (now - timedelta(minutes=30)).time().replace(second=0, microsecond=0)
    current_end = (now + timedelta(minutes=45)).time().replace(second=0, microsecond=0)
    upcoming_start = (now + timedelta(minutes=30)).time().replace(second=0, microsecond=0)
    upcoming_end = (now + timedelta(minutes=90)).time().replace(second=0, microsecond=0)

    def create(title, venue, start, end, visibility):
        return Event.objects.create(
            title=title,
            event_type=event_type,
            venue=venue,
            planned_date=now.date(),
            start_time=start,
            end_time=end,
            responsible_employee=leader,
            management_responsible=leader,
            created_by=leader,
            status=Event.Status.APPROVED,
            display_visibility=visibility,
            expected_attendees=80,
        )

    create("[P6] International Forum", venues[0], current_start, current_end, "full")
    create("[P6] Hidden Council", venues[1], current_start, current_end, "hidden")
    create("[P6] Upcoming Briefing", venues[2], upcoming_start, upcoming_end, "full")
    create("[P6] Confidential Board", venues[3], current_start, current_end, "generic")
    token, _ = DisplayToken.objects.get_or_create(name="Phase 6 acceptance display")
    token.is_active = True
    token.save(update_fields=["is_active"])
    return leader, token, venue_states


def cleanup_data(venue_states):
    Event.objects.filter(title__startswith="[P6]").delete()
    DisplayToken.objects.filter(name="Phase 6 acceptance display").delete()
    EventType.objects.filter(code="phase6-briefing").delete()
    User.objects.filter(username="phase6_leader").delete()
    for venue_id, created, was_active, sort_order in venue_states:
        if created:
            Venue.objects.filter(pk=venue_id).delete()
        else:
            Venue.objects.filter(pk=venue_id).update(
                is_active=was_active,
                sort_order=sort_order,
            )


def screenshot(page, name, width, height, selector=None):
    page.set_viewport_size({"width": width, "height": height})
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(250)
    target = page.locator(selector) if selector else page
    target.screenshot(path=str(OUTPUT / name))


def main():
    _, token, venue_states = prepare_data()
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
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill("input[name=username]", "phase6_leader")
            page.fill("input[name=password]", "Phase6-Safe-Test!")
            page.click("button[type=submit]")
            page.goto(f"{BASE_URL}/leadership/")
            page.wait_for_selector("[data-testid=leadership-dashboard-container]")
            screenshot(page, "phase6_01_leadership_dashboard.png", 1920, 1080)
            screenshot(
                page,
                "phase6_02_live_venue_cards.png",
                1920,
                1080,
                "[data-testid=live-venue-cards-grid]",
            )
            screenshot(
                page,
                "phase6_03_today_timeline.png",
                1920,
                1080,
                "[data-testid=today-timeline-panel]",
            )
            screenshot(
                page,
                "phase6_04_upcoming_events.png",
                1366,
                768,
                "[data-testid=upcoming-schedule-panel]",
            )
            screenshot(page, "phase6_08_mobile_leadership.png", 375, 812)
            for language in ("uz", "ru", "en"):
                page.click(f"button[name=language][value={language}]")
                page.wait_for_selector("[data-testid=leadership-dashboard-container]")

            wallboard = f"{BASE_URL}/display/{token.token}/"
            page.goto(wallboard)
            page.wait_for_selector("[data-testid=tv-venues-grid]")
            assert page.locator("[data-testid^=tv-venue-card]").count() >= 4
            body = page.locator("body").inner_text()
            assert "[P6] International Forum" in body
            assert "[P6] Confidential Board" not in body
            assert "[P6] Hidden Council" not in body
            assert "attendee_name" not in body and "email" not in body.lower()
            screenshot(page, "phase6_05_tv_1920.png", 1920, 1080)
            screenshot(page, "phase6_06_tv_4k.png", 3840, 2160)
            screenshot(page, "phase6_07_private_event_display.png", 1920, 1080)
            page.set_viewport_size({"width": 2560, "height": 1440})
            assert page.locator("body").evaluate("el => el.scrollHeight <= el.clientHeight")
            assert page.locator("#fullscreen").is_visible()
            browser.close()
        print("PASS — Phase 6 Playwright acceptance")
    finally:
        server.terminate()
        server.wait(timeout=10)
        cleanup_data(venue_states)


if __name__ == "__main__":
    main()
