"""
Phase 12 Visual QA Capture Script
Captures multi-viewport baseline for the 4 core experiences:
- /dashboard/
- /dashboard/calendar/?view=month
- /dashboard/calendar/?view=week
- /workspace/
plus event inspector modal, occupied venue state, upcoming venue state, and empty states.
"""
import os
import sys
import time
import subprocess
import urllib.request
from datetime import time as dt_time, timedelta
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, os.getcwd())

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from playwright.sync_api import sync_playwright

from apps.events.models import Event, EventType
from apps.organizations.models import Organization
from apps.venues.models import Venue

User = get_user_model()
PORT = 8599
BASE = f"http://127.0.0.1:{PORT}"
OUT = Path("tests/visual_baseline/phase12")
PASSWORD = "AdminPassword123!"

VIEWPORTS = [
    ("2560x1440", 2560, 1440),
    ("1920x1080", 1920, 1080),
    ("1440x900", 1440, 900),
    ("1366x768", 1366, 768),
    ("768x1024", 768, 1024),
    ("390x844", 390, 844),
]

def seed_data():
    admin, _ = User.objects.get_or_create(
        username="phase12_admin",
        defaults={"is_staff": True, "is_superuser": True, "first_name": "Aziz", "last_name": "Karimov"}
    )
    admin.set_password(PASSWORD)
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    owner, _ = User.objects.get_or_create(
        username="phase12_owner",
        defaults={"first_name": "Dilnoza", "last_name": "Rasulova"}
    )
    owner.set_password(PASSWORD)
    owner.save()

    etype, _ = EventType.objects.get_or_create(code="symposium", defaults={"name": "Simpozium"})
    org, _ = Organization.objects.get_or_create(name="Gustave Roussy International", defaults={"short_name": "GRI"})

    venues_data = [
        ("ICH", "International Conference Hall", 120),
        ("SSH", "Specialized Seminar Hall", 60),
        ("INR", "Interactive Network Room", 45),
        ("EMR", "Executive Multidisciplinary Room", 30),
    ]
    created_venues = []
    for code, name, cap in venues_data:
        v, _ = Venue.objects.get_or_create(code=code, defaults={"name": name, "capacity": cap, "is_active": True})
        created_venues.append(v)

    today = timezone.localdate()
    events = []

    # Active/Ongoing Event today on ICH
    e1, _ = Event.objects.get_or_create(
        title="International Oncology Symposium 2026",
        defaults={
            "event_type": etype,
            "venue": created_venues[0],
            "planned_date": today,
            "start_time": dt_time(8, 30),
            "end_time": dt_time(11, 30),
            "status": "in_progress",
            "priority": "high",
            "expected_attendees": 95,
            "responsible_employee": owner,
            "management_responsible": admin,
            "created_by": admin,
            "description": "Annual international symposium on precision oncology and clinical trial protocols.",
        }
    )
    e1.organizing_organizations.add(org)
    events.append(e1)

    # Upcoming Event today on SSH
    e2, _ = Event.objects.get_or_create(
        title="Clinical Trial Protocol Working Group",
        defaults={
            "event_type": etype,
            "venue": created_venues[1],
            "planned_date": today,
            "start_time": dt_time(13, 0),
            "end_time": dt_time(15, 30),
            "status": "approved",
            "priority": "normal",
            "expected_attendees": 40,
            "responsible_employee": owner,
            "management_responsible": admin,
            "created_by": admin,
            "description": "Cross-institutional harmonization of clinical study guidelines.",
        }
    )
    e2.organizing_organizations.add(org)
    events.append(e2)

    # Future events across the week
    for i in range(1, 5):
        ev, _ = Event.objects.get_or_create(
            title=f"Central Asia Research Workshop Session {i}",
            defaults={
                "event_type": etype,
                "venue": created_venues[i % len(created_venues)],
                "planned_date": today + timedelta(days=i),
                "start_time": dt_time(10, 0),
                "end_time": dt_time(12, 30),
                "status": "approved",
                "priority": "normal",
                "expected_attendees": 50,
                "responsible_employee": owner,
                "management_responsible": admin,
                "created_by": admin,
                "description": "Multi-center research coordination workshop.",
            }
        )
        ev.organizing_organizations.add(org)
        events.append(ev)

    return admin, events

def wait_server():
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"{BASE}/health/", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Server did not start")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    admin, events = seed_data()

    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_server()
        print("Server running on port 8599, starting Playwright captures...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # --- 1. Multi-Viewport Captures for the 4 Core Screens ---
            for vp_name, width, height in VIEWPORTS:
                page = browser.new_page()
                page.set_viewport_size({"width": width, "height": height})

                # A. Dashboard
                page.goto(f"{BASE}/dashboard/")
                page.wait_for_timeout(500)
                page.screenshot(path=str(OUT / f"dashboard_{vp_name}.png"), full_page=False)

                # B. Calendar Month
                page.goto(f"{BASE}/dashboard/calendar/?view=month")
                page.wait_for_timeout(600)
                page.screenshot(path=str(OUT / f"calendar_month_{vp_name}.png"), full_page=False)

                # C. Calendar Week
                page.goto(f"{BASE}/dashboard/calendar/?view=week")
                page.wait_for_timeout(600)
                page.screenshot(path=str(OUT / f"calendar_week_{vp_name}.png"), full_page=False)

                page.close()

            # --- 2. Workspace Viewport Captures (Authenticated) ---
            auth_page = browser.new_page()
            auth_page.set_viewport_size({"width": 1920, "height": 1080})
            auth_page.goto(f"{BASE}/accounts/login/")
            auth_page.fill("input[name=username]", admin.username)
            auth_page.fill("input[name=password]", PASSWORD)
            auth_page.click("button[type=submit]")
            auth_page.wait_for_load_state("networkidle")

            for vp_name, width, height in VIEWPORTS:
                auth_page.set_viewport_size({"width": width, "height": height})
                auth_page.goto(f"{BASE}/workspace/")
                auth_page.wait_for_timeout(500)
                auth_page.screenshot(path=str(OUT / f"workspace_{vp_name}.png"), full_page=False)

            # --- 3. Calendar Event Inspector Modal Capture ---
            inspect_page = browser.new_page()
            inspect_page.set_viewport_size({"width": 1920, "height": 1080})
            inspect_page.goto(f"{BASE}/dashboard/calendar/?view=month")
            inspect_page.wait_for_timeout(600)
            first_event = inspect_page.locator(".calendar-event").first
            if first_event.count() > 0:
                first_event.click(force=True)
                inspect_page.wait_for_timeout(500)
            inspect_page.screenshot(path=str(OUT / "calendar_event_inspector.png"), full_page=False)
            inspect_page.close()

            # --- 4. Dashboard Occupied Venue & Upcoming Venue State ---
            dash_page = browser.new_page()
            dash_page.set_viewport_size({"width": 1920, "height": 1080})
            dash_page.goto(f"{BASE}/dashboard/")
            dash_page.wait_for_timeout(600)
            dash_page.screenshot(path=str(OUT / "dashboard_live_states.png"), full_page=False)
            dash_page.close()

            # --- 5. Empty Calendar State Capture ---
            empty_page = browser.new_page()
            empty_page.set_viewport_size({"width": 1920, "height": 1080})
            empty_page.goto(f"{BASE}/dashboard/calendar/?view=day&date=2028-01-01")
            empty_page.wait_for_timeout(500)
            empty_page.screenshot(path=str(OUT / "calendar_empty_state.png"), full_page=False)
            empty_page.close()

            auth_page.close()
            browser.close()
            print("All Phase 12 screenshots captured successfully!")

    finally:
        server.terminate()
        server.wait(timeout=5)

if __name__ == "__main__":
    main()
