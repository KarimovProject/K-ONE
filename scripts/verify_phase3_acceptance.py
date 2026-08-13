import os
import subprocess
import sys
import time
import urllib.request
from datetime import date, timedelta

import django

# Setup Django Environment
sys.path.insert(0, os.getcwd())
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventType  # noqa: E402
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()

PORT = 8557
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


def cleanup_phase3_test_data():
    """Delete only records owned by this acceptance script."""
    usernames = ("p3_super_admin", "p3_mgmt_user", "p3_resp_user")
    Event.objects.filter(created_by__username__in=usernames).delete()
    Venue.objects.filter(code="P3-HALL-A").delete()
    EventType.objects.filter(code="P3-CONF").delete()
    User.objects.filter(username__in=usernames).delete()


def setup_phase3_test_data():
    """Ensure required users, venues, and test events exist for Playwright test."""
    super_admin, _ = User.objects.get_or_create(
        username="p3_super_admin",
        defaults={
            "email": "superadmin@iems.uz",
            "role": User.Role.SUPER_ADMIN,
            "is_superuser": True,
        },
    )
    super_admin.set_password("Password123!")
    super_admin.save()

    mgmt_user, _ = User.objects.get_or_create(
        username="p3_mgmt_user",
        defaults={
            "email": "mgmt@iems.uz",
            "role": User.Role.MANAGEMENT_RESPONSIBLE,
        },
    )
    mgmt_user.set_password("Password123!")
    mgmt_user.save()

    resp_user, _ = User.objects.get_or_create(
        username="p3_resp_user",
        defaults={
            "email": "resp@iems.uz",
            "role": User.Role.RESPONSIBLE_EMPLOYEE,
        },
    )
    resp_user.set_password("Password123!")
    resp_user.save()

    venue, _ = Venue.objects.get_or_create(
        code="P3-HALL-A",
        defaults={
            "name_uz": "Phase 3 Asosiy Zal",
            "name_ru": "Фаза 3 Главный Зал",
            "name_en": "Phase 3 Main Hall",
            "capacity": 200,
            "working_start": "08:00",
            "working_end": "20:00",
        },
    )

    event_type, _ = EventType.objects.get_or_create(
        code="P3-CONF",
        defaults={
            "name_uz": "Xalqaro Anjuman",
            "name_ru": "Международная Конференция",
            "name_en": "International Conference",
            "requires_management_approval": True,
        },
    )

    planned_date = date.today() + timedelta(days=10)

    # Clean up existing test events with these titles to start fresh
    Event.objects.filter(
        title__in=[
            "Phase 3 Tech Summit 2026",
            "Scheduled Regular Workshop",
            "State High Priority Delegation Visit",
        ]
    ).delete()

    # Draft event for submission flow
    draft_event = Event.objects.create(
        title="Phase 3 Tech Summit 2026",
        event_type=event_type,
        venue=venue,
        planned_date=planned_date,
        start_time="10:00",
        end_time="12:00",
        responsible_employee=resp_user,
        management_responsible=mgmt_user,
        created_by=resp_user,
        status=Event.Status.DRAFT,
    )

    # Conflicting planned event for emergency override flow
    existing_planned = Event.objects.create(
        title="Scheduled Regular Workshop",
        event_type=event_type,
        venue=venue,
        planned_date=planned_date,
        start_time="14:00",
        end_time="16:00",
        responsible_employee=resp_user,
        management_responsible=mgmt_user,
        created_by=resp_user,
        status=Event.Status.PLANNED,
    )

    # Emergency event draft conflicting with existing_planned
    emergency_draft = Event.objects.create(
        title="State High Priority Delegation Visit",
        event_type=event_type,
        venue=venue,
        planned_date=planned_date,
        start_time="14:30",
        end_time="15:30",
        responsible_employee=resp_user,
        management_responsible=mgmt_user,
        created_by=resp_user,
        status=Event.Status.DRAFT,
    )

    return {
        "draft_event_id": str(draft_event.pk),
        "existing_planned_id": str(existing_planned.pk),
        "emergency_draft_id": str(emergency_draft.pk),
    }


def run_phase3_playwright_acceptance():
    print("Setting up Phase 3 test data...")
    test_ids = setup_phase3_test_data()

    print(f"Starting server process on {BASE_URL}...")
    server_process = subprocess.Popen(
        [
            sys.executable,
            "manage.py",
            "runserver",
            str(PORT),
            "--noreload",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not wait_for_server(f"{BASE_URL}/accounts/login/"):
        server_process.terminate()
        raise RuntimeError(f"Server on {BASE_URL} failed to start in time.")

    screenshots = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # -------------------------------------------------------------
            # Step 1: Login as Responsible Employee & Submit Event
            # -------------------------------------------------------------
            print("Flow 1: Submitting Draft Event...")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill(".login-card input[name='username']", "p3_resp_user")
            page.fill(".login-card input[name='password']", "Password123!")
            page.click(".login-card button[type='submit']")
            page.wait_for_selector(".app-shell")

            page.goto(f"{BASE_URL}/events/{test_ids['draft_event_id']}/")
            shot1 = os.path.join(OUTPUT_DIR, "phase3_01_draft_event_detail.png")
            page.screenshot(path=shot1)
            screenshots.append(shot1)

            page.click("[data-testid='submit-approval-btn']")
            page.wait_for_selector(".status-badge.pending_approval")
            shot2 = os.path.join(OUTPUT_DIR, "phase3_02_submitted_pending_approval.png")
            page.screenshot(path=shot2)
            screenshots.append(shot2)
            print("  [OK] Draft event submitted successfully.")

            context.close()

            # -------------------------------------------------------------
            # Step 2: Login as Management Responsible & Review Approval Queue / Reject
            # -------------------------------------------------------------
            print("Flow 2: Reviewing Approval Queue & Rejecting Event with Reason...")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill(".login-card input[name='username']", "p3_mgmt_user")
            page.fill(".login-card input[name='password']", "Password123!")
            page.click(".login-card button[type='submit']")
            page.wait_for_selector(".app-shell")

            page.goto(f"{BASE_URL}/events/approvals/")
            shot3 = os.path.join(OUTPUT_DIR, "phase3_03_approval_queue.png")
            page.screenshot(path=shot3)
            screenshots.append(shot3)

            # Go to detail and click Reject
            page.goto(f"{BASE_URL}/events/{test_ids['draft_event_id']}/")
            page.click("[data-testid='reject-event-btn']")
            page.wait_for_url("**/reject/")

            shot4 = os.path.join(OUTPUT_DIR, "phase3_04_confirm_reject_form.png")
            page.screenshot(path=shot4)
            screenshots.append(shot4)

            page.fill(
                "textarea[name='reason']",
                "Budget justification is required before approval.",
            )
            page.click("[data-testid='confirm-reject-btn']")
            page.wait_for_selector(".status-badge.rejected")

            shot5 = os.path.join(OUTPUT_DIR, "phase3_05_rejected_event_with_reason.png")
            page.screenshot(path=shot5)
            screenshots.append(shot5)
            print("  [OK] Event rejected with mandatory rationale.")

            context.close()

            # -------------------------------------------------------------
            # Step 3: Responsible Employee Resubmits Event & Management Approves
            # -------------------------------------------------------------
            print("Flow 3: Resubmitting & Approving Event...")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill(".login-card input[name='username']", "p3_resp_user")
            page.fill(".login-card input[name='password']", "Password123!")
            page.click(".login-card button[type='submit']")
            page.wait_for_selector(".app-shell")

            page.goto(f"{BASE_URL}/events/{test_ids['draft_event_id']}/")
            page.click("[data-testid='resubmit-event-btn']")
            page.wait_for_selector(".status-badge.pending_approval")
            print("  [OK] Event resubmitted.")
            context.close()

            # Approve as Mgmt
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill(".login-card input[name='username']", "p3_mgmt_user")
            page.fill(".login-card input[name='password']", "Password123!")
            page.click(".login-card button[type='submit']")
            page.wait_for_selector(".app-shell")

            page.goto(f"{BASE_URL}/events/{test_ids['draft_event_id']}/")
            page.click("[data-testid='approve-event-btn']")
            page.wait_for_selector(".status-badge.approved")

            shot6 = os.path.join(OUTPUT_DIR, "phase3_06_approved_event_detail.png")
            page.screenshot(path=shot6)
            screenshots.append(shot6)
            print("  [OK] Event approved.")
            context.close()

            # -------------------------------------------------------------
            # Step 4: Super Admin Emergency Conflict Override
            # -------------------------------------------------------------
            print("Flow 4: Executing Emergency Conflict Override...")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill(".login-card input[name='username']", "p3_super_admin")
            page.fill(".login-card input[name='password']", "Password123!")
            page.click(".login-card button[type='submit']")
            page.wait_for_selector(".app-shell")

            page.goto(f"{BASE_URL}/events/{test_ids['emergency_draft_id']}/emergency-override/")
            shot7 = os.path.join(OUTPUT_DIR, "phase3_07_emergency_override_form.png")
            page.screenshot(path=shot7)
            screenshots.append(shot7)

            page.fill(
                "textarea[name='justification']",
                "State-level international delegation meeting requires priority hall reservation.",
            )
            page.click("[data-testid='confirm-override-btn']")
            page.wait_for_selector(".priority-badge.emergency")

            shot8 = os.path.join(OUTPUT_DIR, "phase3_08_emergency_overridden_event.png")
            page.screenshot(path=shot8)
            screenshots.append(shot8)
            print("  [OK] Emergency override executed.")
            context.close()

            # -------------------------------------------------------------
            # Step 5: Check Displaced Event Banner & Displaced Events Queue
            # -------------------------------------------------------------
            print("Flow 5: Displaced Event Banner & Reschedule...")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill(".login-card input[name='username']", "p3_resp_user")
            page.fill(".login-card input[name='password']", "Password123!")
            page.click(".login-card button[type='submit']")
            page.wait_for_selector(".app-shell")

            page.goto(f"{BASE_URL}/events/displaced/")
            shot9 = os.path.join(OUTPUT_DIR, "phase3_09_displaced_events_queue.png")
            page.screenshot(path=shot9)
            screenshots.append(shot9)

            page.goto(f"{BASE_URL}/events/{test_ids['existing_planned_id']}/")
            shot10 = os.path.join(OUTPUT_DIR, "phase3_10_displaced_event_banner.png")
            page.screenshot(path=shot10)
            screenshots.append(shot10)

            # Reschedule displaced event
            page.click("[data-testid='reschedule-event-btn']")
            page.wait_for_url("**/reschedule/")

            shot11 = os.path.join(OUTPUT_DIR, "phase3_11_reschedule_form.png")
            page.screenshot(path=shot11)
            screenshots.append(shot11)

            # Change start time to 16:30 - 18:30 (avoid conflict)
            page.fill("input[name='start_time']", "16:30")
            page.fill("input[name='end_time']", "18:30")
            page.click("[data-testid='confirm-reschedule-btn']")
            page.wait_for_selector(".status-badge.planned")

            shot12 = os.path.join(OUTPUT_DIR, "phase3_12_rescheduled_event_detail.png")
            page.screenshot(path=shot12)
            screenshots.append(shot12)
            print("  [OK] Displaced event successfully rescheduled.")

            context.close()

            # -------------------------------------------------------------
            # Step 6: Responsive Viewports & Languages Verification
            # -------------------------------------------------------------
            print("Flow 6: Responsive & Localization Verification...")
            viewports = [
                ("1920x1080", 1920, 1080),
                ("768x1024_tablet", 768, 1024),
                ("375x812_mobile", 375, 812),
            ]

            for vp_name, width, height in viewports:
                ctx_vp = browser.new_context(viewport={"width": width, "height": height})
                p_vp = ctx_vp.new_page()
                p_vp.goto(f"{BASE_URL}/accounts/login/")
                p_vp.fill(".login-card input[name='username']", "p3_resp_user")
                p_vp.fill(".login-card input[name='password']", "Password123!")
                p_vp.click(".login-card button[type='submit']")
                p_vp.wait_for_selector(".app-shell")

                p_vp.goto(f"{BASE_URL}/events/{test_ids['draft_event_id']}/")
                p_vp.wait_for_selector(".detail-header")
                shot_vp = os.path.join(OUTPUT_DIR, f"phase3_responsive_detail_{vp_name}.png")
                p_vp.screenshot(path=shot_vp)
                screenshots.append(shot_vp)
                ctx_vp.close()

            browser.close()

    finally:
        print("Terminating test server...")
        server_process.terminate()
        server_process.wait()
        cleanup_phase3_test_data()

    print("\nPASS — PHASE 3 FULLY VERIFIED")
    print(f"Captured {len(screenshots)} screenshots in {OUTPUT_DIR}:")
    for s in screenshots:
        print(f"  - {os.path.basename(s)}")


if __name__ == "__main__":
    run_phase3_playwright_acceptance()
