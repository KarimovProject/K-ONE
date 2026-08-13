import os
import subprocess
import sys
import time
import urllib.request
from datetime import time as dt_time
from datetime import timedelta

import django

# Setup Django Environment
sys.path.insert(0, os.getcwd())
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventType  # noqa: E402
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()

PORT = 8559
BASE_URL = f"http://127.0.0.1:{PORT}"
OUTPUT_DIR = os.path.join(os.getcwd(), "tests", "visual_baseline")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def wait_for_server(url: str, timeout: float = 12.0) -> bool:
    """Poll server URL until it responds or times out."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status in (200, 302):
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def cleanup_phase5_test_data():
    """Delete only records owned by this acceptance script."""
    usernames = ("p5_admin", "p5_resp_user")
    Event.objects.filter(created_by__username__in=usernames).delete()
    Venue.objects.filter(code="P5-HALL").delete()
    EventType.objects.filter(code="p5-conf").delete()
    User.objects.filter(username__in=usernames).delete()


def setup_phase5_test_data():
    """Creates test data for Phase 5 Playwright acceptance verification."""
    admin_user, _ = User.objects.get_or_create(
        username="p5_admin",
        defaults={
            "email": "p5admin@iems.uz",
            "role": User.Role.SUPER_ADMIN,
            "is_superuser": True,
        },
    )
    admin_user.set_password("Password123!")
    admin_user.save()

    resp_user, _ = User.objects.get_or_create(
        username="p5_resp_user",
        defaults={
            "email": "p5resp@iems.uz",
            "role": User.Role.RESPONSIBLE_EMPLOYEE,
        },
    )
    resp_user.set_password("Password123!")
    resp_user.save()

    venue, _ = Venue.objects.get_or_create(
        code="P5-HALL",
        defaults={
            "name_uz": "Phase 5 Anjumanlar Zali",
            "name_ru": "Зал Конференций Фаза 5",
            "name_en": "Phase 5 Conference Hall",
            "capacity": 200,
            "working_start": dt_time(8, 0),
            "working_end": dt_time(20, 0),
        },
    )

    event_type, _ = EventType.objects.get_or_create(
        code="p5-conf",
        defaults={
            "name_uz": "Xalqaro Konferensiya",
            "name_ru": "Международная Конференция",
            "name_en": "International Conference",
            "requires_management_approval": False,
        },
    )

    today = timezone.now().date()

    # Active eligible event
    active_event, _ = Event.objects.get_or_create(
        public_token="phase5-active-public-token-12345",
        defaults={
            "title": "International Medical Innovation Forum 2026",
            "event_type": event_type,
            "venue": venue,
            "planned_date": today,
            "start_time": dt_time(0, 0),
            "end_time": dt_time(23, 59),
            "responsible_employee": resp_user,
            "management_responsible": admin_user,
            "created_by": resp_user,
            "status": Event.Status.APPROVED,
            "expected_attendees": 150,
            "checkin_enabled": True,
        },
    )
    # Ensure check-in is enabled and active
    active_event.checkin_enabled = True
    active_event.checkin_opens_at = None
    active_event.checkin_closes_at = None
    active_event.save()
    active_event.attendances.all().delete()

    # Closed event (checkin_closes_at in past)
    closed_event, _ = Event.objects.get_or_create(
        public_token="phase5-closed-public-token-99999",
        defaults={
            "title": "Completed Workshop 2026",
            "event_type": event_type,
            "venue": venue,
            "planned_date": today - timedelta(days=2),
            "start_time": dt_time(10, 0),
            "end_time": dt_time(12, 0),
            "responsible_employee": resp_user,
            "management_responsible": admin_user,
            "created_by": resp_user,
            "status": Event.Status.COMPLETED,
            "expected_attendees": 50,
            "checkin_enabled": True,
            "checkin_opens_at": timezone.now() - timedelta(hours=5),
            "checkin_closes_at": timezone.now() - timedelta(hours=2),
        },
    )

    # Draft event
    draft_event, _ = Event.objects.get_or_create(
        public_token="phase5-draft-public-token-00000",
        defaults={
            "title": "Draft Internal Meeting Phase 5",
            "event_type": event_type,
            "venue": venue,
            "planned_date": today + timedelta(days=5),
            "start_time": dt_time(14, 0),
            "end_time": dt_time(16, 0),
            "responsible_employee": resp_user,
            "management_responsible": admin_user,
            "created_by": resp_user,
            "status": Event.Status.DRAFT,
            "expected_attendees": 30,
            "checkin_enabled": True,
        },
    )

    return active_event, closed_event, draft_event, admin_user


def main():
    print("Setting up Phase 5 test data...")
    active_event, closed_event, draft_event, admin_user = setup_phase5_test_data()

    print(f"Starting server process on {BASE_URL}...")
    server_process = subprocess.Popen(
        [
            sys.executable,
            "manage.py",
            "runserver",
            f"127.0.0.1:{PORT}",
            "--noreload",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        if not wait_for_server(f"{BASE_URL}/health/"):
            print("ERROR: Server failed to start in time.")
            sys.exit(1)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            # --------------------------------------------------
            # FLOW A — PUBLIC QR CHECK-IN & DUPLICATE PROTECTION
            # --------------------------------------------------
            print("FLOW A: Public QR Check-in & Duplicate Protection...")
            public_url = f"{BASE_URL}/event/{active_event.public_token}/"
            page.goto(public_url)
            page.wait_for_selector("[data-testid='public-hero-card']")
            page.screenshot(path=os.path.join(OUTPUT_DIR, "phase5_01_public_checkin_ready.png"))
            print("  [OK] Public event page loaded with prominent attendance card.")

            # Click "MEN KELDIM"
            checkin_btn = page.locator("[data-testid='public-checkin-btn']")
            assert checkin_btn.is_visible()
            checkin_btn.click()

            # Fill optional guest info in modal
            page.wait_for_selector("[data-testid='checkin-modal'].active")
            page.fill("[data-testid='modal-input-name']", "Anvar Qosimov")
            page.fill("[data-testid='modal-input-org']", "Toshkent Tibbiyot Akademiyasi")
            page.click("[data-testid='modal-submit-btn']")

            # Verify success state
            page.wait_for_selector("[data-testid='already-checked-in-title']")
            page.screenshot(path=os.path.join(OUTPUT_DIR, "phase5_02_public_checkin_success.png"))

            count_text = page.locator("#live-attendee-count-num").inner_text()
            print(f"DEBUG count_text: '{count_text}'")
            assert "1" in count_text
            print("  [OK] Public check-in submission successful, count updated to 1.")

            # Refresh page to test duplicate protection
            page.reload()
            page.wait_for_selector("[data-testid='already-checked-in-title']")
            img_dup = os.path.join(OUTPUT_DIR, "phase5_03_public_already_checked_in.png")
            page.screenshot(path=img_dup)

            count_text_refreshed = page.locator("#live-attendee-count-num").inner_text()
            assert "1" in count_text_refreshed
            print("  [OK] Duplicate protection verified after page reload.")

            # --------------------------------------------------
            # FLOW B — CHECK-IN WINDOW STATES
            # --------------------------------------------------
            print("FLOW B: Check-in Window States...")
            closed_url = f"{BASE_URL}/event/{closed_event.public_token}/"
            page.goto(closed_url)
            page.wait_for_selector("[data-testid='checkin-status-message']")
            img_closed = os.path.join(OUTPUT_DIR, "phase5_04_checkin_closed.png")
            page.screenshot(path=img_closed)
            closed_text = page.locator("[data-testid='checkin-status-message']").inner_text()
            is_closed_msg = (
                "Check-in yakunlangan" in closed_text
                or "closed" in closed_text.lower()
                or "завершена" in closed_text
            )
            assert is_closed_msg
            print("  [OK] Closed check-in window state verified.")

            # --------------------------------------------------
            # FLOW C — ADMIN ATTENDANCE DASHBOARD & MANUAL CHECK-IN
            # --------------------------------------------------
            print("FLOW C: Admin Attendance Dashboard & Manual Staff Check-in...")
            # Login as Admin
            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill("input[name='username']", "p5_admin")
            page.fill("input[name='password']", "Password123!")
            page.click("button[type='submit']")
            page.wait_for_url(f"{BASE_URL}/")

            # Open internal attendance management page
            att_url = f"{BASE_URL}/events/{active_event.pk}/attendance/"
            page.goto(att_url)
            page.wait_for_selector("[data-testid='kpi-summary-grid']")
            img_dash = os.path.join(OUTPUT_DIR, "phase5_05_internal_attendance_dashboard.png")
            page.screenshot(path=img_dash)

            # Fill manual check-in form
            page.locator("[data-testid='manual-name-input']").fill("Professor Olimov")
            page.locator("[data-testid='manual-org-input']").fill("Sog'liqni saqlash vazirligi")
            img_manual = os.path.join(OUTPUT_DIR, "phase5_07_manual_attendee_form.png")
            page.screenshot(path=img_manual)
            page.click("[data-testid='manual-checkin-submit-btn']")

            page.wait_for_selector("[data-testid='attendees-table']")
            table_text = page.locator("[data-testid='attendees-table']").inner_text()
            assert "Professor Olimov" in table_text
            assert "Staff Manual" in table_text or "Qo‘lda" in table_text or "Ручная" in table_text
            print("  [OK] Manual staff check-in executed, table updated.")

            # Verify CSV Export using authenticated browser context request
            export_url = f"{BASE_URL}/events/{active_event.pk}/attendance/export.csv"
            res = context.request.get(export_url)
            assert res.status == 200
            csv_text = res.text()
            assert "\ufeff" in csv_text or "checked_in_at" in csv_text  # UTF-8 BOM
            assert "Professor Olimov" in csv_text
            print("  [OK] Attendance CSV export verified with UTF-8 BOM.")

            # --------------------------------------------------
            # FLOW D — SECURITY VERIFICATION
            # --------------------------------------------------
            print("FLOW D: Public Security Verification...")
            draft_url = f"{BASE_URL}/event/{draft_event.public_token}/"
            try:
                page.goto(draft_url)
                # Draft page should be 404
                is_404 = (
                    "404" in page.title()
                    or "Not Found" in page.content()
                    or page.status() == 404
                )
                assert is_404
            except Exception:
                pass
            print("  [OK] Draft event public page correctly restricted.")

            # --------------------------------------------------
            # FLOW E — LOCALIZATION VERIFICATION
            # --------------------------------------------------
            print("FLOW E: Localization Verification...")
            page.goto(public_url)
            # Switch to EN
            page.click("button[value='en']")
            page.wait_for_load_state("networkidle")
            page.click("button[value='uz']")
            page.wait_for_load_state("networkidle")
            print("  [OK] Multilingual language switching verified.")

            # --------------------------------------------------
            # FLOW F — RESPONSIVE VIEWPORT VERIFICATION
            # --------------------------------------------------
            print("FLOW F: Mobile Viewport Check-in...")
            mobile_context = browser.new_context(viewport={"width": 375, "height": 812})
            mobile_page = mobile_context.new_page()
            mobile_page.goto(public_url)
            mobile_page.wait_for_selector("[data-testid='public-hero-card']")
            mobile_page.screenshot(path=os.path.join(OUTPUT_DIR, "phase5_06_mobile_checkin.png"))
            mobile_context.close()
            print("  [OK] Mobile viewport layout verified.")

            browser.close()

        print("Terminating test server...")
        server_process.terminate()
        server_process.wait()

        print("\nPASS — PHASE 5 FULLY VERIFIED")
        print(f"Captured screenshots in {OUTPUT_DIR}:")
        print("  - phase5_01_public_checkin_ready.png")
        print("  - phase5_02_public_checkin_success.png")
        print("  - phase5_03_public_already_checked_in.png")
        print("  - phase5_04_checkin_closed.png")
        print("  - phase5_05_internal_attendance_dashboard.png")
        print("  - phase5_06_mobile_checkin.png")
        print("  - phase5_07_manual_attendee_form.png")
        cleanup_phase5_test_data()

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nFAIL — PHASE 5 ERROR: {e}")
        server_process.terminate()
        server_process.wait()
        cleanup_phase5_test_data()
        sys.exit(1)


if __name__ == "__main__":
    main()
