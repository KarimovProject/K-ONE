import os
import subprocess
import sys
import time
import urllib.request
from datetime import date, timedelta
from datetime import time as dt_time

import django

# Setup Django Environment
sys.path.insert(0, os.getcwd())
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventProgramItem, EventType, Speaker  # noqa: E402
from apps.events.services.program import upload_program_pdf  # noqa: E402
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()

PORT = 8558
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


def cleanup_phase4_test_data():
    """Delete only records owned by this acceptance script."""
    usernames = ("p4_super_admin", "p4_resp_user")
    Event.objects.filter(created_by__username__in=usernames).delete()
    Speaker.objects.filter(full_name__startswith="[P4 Acceptance]").delete()
    Venue.objects.filter(code="P4-PALACE").delete()
    EventType.objects.filter(code="P4-SUMMIT").delete()
    User.objects.filter(username__in=usernames).delete()


def setup_phase4_test_data():
    """Create test users, venues, events, speakers, and PDF for Phase 4 acceptance."""
    super_admin, _ = User.objects.get_or_create(
        username="p4_super_admin",
        defaults={
            "email": "superadmin@iems.uz",
            "role": User.Role.SUPER_ADMIN,
            "is_superuser": True,
        },
    )
    super_admin.set_password("Password123!")
    super_admin.save()

    resp_user, _ = User.objects.get_or_create(
        username="p4_resp_user",
        defaults={
            "email": "resp_private@iems.uz",
            "role": User.Role.RESPONSIBLE_EMPLOYEE,
        },
    )
    resp_user.set_password("Password123!")
    resp_user.save()

    venue, _ = Venue.objects.get_or_create(
        code="P4-PALACE",
        defaults={
            "name_uz": "Xalqaro Anjumanlar Saroyi",
            "name_ru": "Дворец Международных Конференций",
            "name_en": "International Conference Palace",
            "working_start": "08:00",
            "working_end": "22:00",
            "capacity": 500,
        },
    )

    event_type, _ = EventType.objects.get_or_create(
        code="P4-SUMMIT",
        defaults={
            "name_uz": "Xalqaro Sammit",
            "name_ru": "Международный Саммит",
            "name_en": "International Summit",
            "color": "#06b6d4",
        },
    )

    planned_date = date.today() + timedelta(days=7)

    # Delete existing test events with these titles
    Event.objects.filter(
        title__in=[
            "Global Digital Innovations Summit 2026",
            "Private Internal Draft Workshop",
        ]
    ).delete()

    # 1. Approved Event for PDF & Manual testing
    pdf_event = Event.objects.create(
        title="Global Digital Innovations Summit 2026",
        event_type=event_type,
        venue=venue,
        planned_date=planned_date,
        start_time=dt_time(9, 0),
        end_time=dt_time(17, 0),
        responsible_employee=resp_user,
        management_responsible=super_admin,
        created_by=resp_user,
        status=Event.Status.APPROVED,
        zoom_url="https://zoom.us/j/123456789",
        registration_url="https://iems.uz/summit2026/register",
        description=(
            "Annual flagship international conference bringing together technology leaders."
        ),
        notes="CONFIDENTIAL: Internal security protocol notes.",
    )

    # Upload initial sample PDF
    sample_pdf = SimpleUploadedFile(
        "official_program.pdf",
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n",
        content_type="application/pdf",
    )
    upload_program_pdf(pdf_event, resp_user, sample_pdf)

    # 2. Draft Event (Must be hidden/404 publicly)
    draft_event = Event.objects.create(
        title="Private Internal Draft Workshop",
        event_type=event_type,
        venue=venue,
        planned_date=planned_date,
        start_time=dt_time(14, 0),
        end_time=dt_time(16, 0),
        responsible_employee=resp_user,
        management_responsible=super_admin,
        created_by=resp_user,
        status=Event.Status.DRAFT,
    )

    # 3. Speakers
    speaker1, _ = Speaker.objects.get_or_create(
        full_name="[P4 Acceptance] Dr. Alisher Navoiy",
        defaults={
            "title": "Lead Artificial Intelligence Architect",
            "organization": "National AI Center",
            "country": "Uzbekistan",
            "bio": "Pioneer in natural language processing and neural networks.",
            "email": "alisher.private@example.com",
            "public_profile_enabled": True,
        },
    )

    speaker2, _ = Speaker.objects.get_or_create(
        full_name="[P4 Acceptance] Prof. Elena Rostova",
        defaults={
            "title": "Director of Cyber Systems",
            "organization": "Eurasia Tech Academy",
            "country": "Kazakhstan",
            "bio": "Expert in distributed consensus and secure cloud infrastructure.",
            "email": "elena.private@example.com",
            "public_profile_enabled": True,
        },
    )

    # Add manual agenda items for pdf_event (for manual mode test)
    EventProgramItem.objects.create(
        event=pdf_event,
        title="Registration & Welcome Coffee",
        start_time=dt_time(9, 0),
        end_time=dt_time(9, 30),
        description="Guest check-in and networking.",
        sort_order=1,
    )
    EventProgramItem.objects.create(
        event=pdf_event,
        title="Opening Keynote: Future of AI & Digital Transformation",
        start_time=dt_time(9, 30),
        end_time=dt_time(10, 45),
        description="Keynote speech on sovereign AI deployment.",
        speaker=speaker1,
        sort_order=2,
    )
    EventProgramItem.objects.create(
        event=pdf_event,
        title="Panel Discussion: Cloud Infrastructure & Security",
        start_time=dt_time(11, 0),
        end_time=dt_time(12, 15),
        speaker=speaker2,
        sort_order=3,
    )

    return {
        "pdf_event_id": str(pdf_event.pk),
        "pdf_event_token": pdf_event.public_token,
        "draft_event_id": str(draft_event.pk),
        "draft_event_token": draft_event.public_token,
    }


def run_phase4_playwright_acceptance():
    print("Setting up Phase 4 test data...")
    test_ids = setup_phase4_test_data()

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
            # FLOW A — PDF EVENT & QR GENERATION
            # -------------------------------------------------------------
            print("FLOW A: PDF Event, Admin Editor & QR Generation...")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill(".login-card input[name='username']", "p4_resp_user")
            page.fill(".login-card input[name='password']", "Password123!")
            page.click(".login-card button[type='submit']")
            page.wait_for_selector(".app-shell")

            # 1. Admin Program Editor (PDF Mode)
            page.goto(f"{BASE_URL}/events/{test_ids['pdf_event_id']}/program/")
            page.wait_for_selector("[data-testid='program-mode-card']")

            shot1 = os.path.join(OUTPUT_DIR, "phase4_01_admin_program_editor_pdf.png")
            page.screenshot(path=shot1)
            screenshots.append(shot1)

            # 2. Public Event Page (PDF Mode)
            page.goto(f"{BASE_URL}/event/{test_ids['pdf_event_token']}/")
            page.wait_for_selector("[data-testid='public-hero-card']")
            page.wait_for_selector("[data-testid='pdf-program-card']")

            shot2 = os.path.join(OUTPUT_DIR, "phase4_02_public_pdf_event.png")
            page.screenshot(path=shot2)
            screenshots.append(shot2)
            print("  [OK] Public event page (PDF mode) verified.")

            # 3. Printable QR Poster Page
            page.goto(f"{BASE_URL}/events/{test_ids['pdf_event_id']}/print-qr/")
            page.wait_for_selector("[data-testid='print-poster-card']")

            shot3 = os.path.join(OUTPUT_DIR, "phase4_04_printable_qr_poster.png")
            page.screenshot(path=shot3)
            screenshots.append(shot3)
            print("  [OK] Printable QR poster page verified.")

            context.close()

            # -------------------------------------------------------------
            # FLOW B — MANUAL AGENDA & SPEAKERS
            # -------------------------------------------------------------
            print("FLOW B: Switching to Manual Agenda Mode & Speakers...")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.goto(f"{BASE_URL}/accounts/login/")
            page.fill(".login-card input[name='username']", "p4_resp_user")
            page.fill(".login-card input[name='password']", "Password123!")
            page.click(".login-card button[type='submit']")
            page.wait_for_selector(".app-shell")

            page.goto(f"{BASE_URL}/events/{test_ids['pdf_event_id']}/program/")
            page.click("[data-testid='radio-program-manual']")
            page.click("[data-testid='save-program-mode-btn']")

            shot4 = os.path.join(OUTPUT_DIR, "phase4_05_admin_program_editor_manual.png")
            page.screenshot(path=shot4)
            screenshots.append(shot4)

            # Check Public Page (Manual Mode with Agenda Timeline & Speakers)
            page.goto(f"{BASE_URL}/event/{test_ids['pdf_event_token']}/")
            page.wait_for_selector("[data-testid='manual-agenda-card']")
            page.wait_for_selector("[data-testid='speakers-card']")

            shot5 = os.path.join(OUTPUT_DIR, "phase4_06_public_manual_event.png")
            page.screenshot(path=shot5)
            screenshots.append(shot5)

            shot6 = os.path.join(OUTPUT_DIR, "phase4_07_public_speaker_section.png")
            page.screenshot(path=shot6)
            screenshots.append(shot6)
            print("  [OK] Public manual agenda timeline and speaker cards verified.")

            context.close()

            # -------------------------------------------------------------
            # FLOW C — SECURITY & ELIGIBILITY
            # -------------------------------------------------------------
            print("FLOW C: Verifying Public Security & Eligibility...")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            # Draft event public URL must return HTTP 404
            res = page.goto(f"{BASE_URL}/event/{test_ids['draft_event_token']}/")
            assert res.status == 404
            print("  [OK] Draft event URL correctly returned 404 Not Found.")

            context.close()

            # -------------------------------------------------------------
            # FLOW D — RESPONSIVE VIEWPORTS
            # -------------------------------------------------------------
            print("FLOW D: Mobile & Tablet Viewport Verification...")

            # Mobile 375x812
            ctx_mob = browser.new_context(viewport={"width": 375, "height": 812})
            p_mob = ctx_mob.new_page()
            p_mob.goto(f"{BASE_URL}/event/{test_ids['pdf_event_token']}/")
            p_mob.wait_for_selector("[data-testid='public-hero-card']")
            shot_mob = os.path.join(OUTPUT_DIR, "phase4_08_mobile_public_event_page.png")
            p_mob.screenshot(path=shot_mob)
            screenshots.append(shot_mob)
            ctx_mob.close()

            # Tablet 768x1024
            ctx_tab = browser.new_context(viewport={"width": 768, "height": 1024})
            p_tab = ctx_tab.new_page()
            p_tab.goto(f"{BASE_URL}/event/{test_ids['pdf_event_token']}/")
            p_tab.wait_for_selector("[data-testid='public-hero-card']")
            shot_tab = os.path.join(OUTPUT_DIR, "phase4_09_tablet_public_event_page.png")
            p_tab.screenshot(path=shot_tab)
            screenshots.append(shot_tab)
            ctx_tab.close()

            browser.close()

    finally:
        print("Terminating test server...")
        server_process.terminate()
        server_process.wait()
        cleanup_phase4_test_data()

    print("\nPASS — PHASE 4 FULLY VERIFIED")
    print(f"Captured {len(screenshots)} screenshots in {OUTPUT_DIR}:")
    for s in screenshots:
        print(f"  - {os.path.basename(s)}")


if __name__ == "__main__":
    run_phase4_playwright_acceptance()
