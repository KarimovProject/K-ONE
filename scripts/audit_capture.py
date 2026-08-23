"""Audit capture script to start server, seed QA data, and take screenshots across viewports."""

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
sys.path.insert(0, os.getcwd())

import django

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.core.cache import cache  # noqa: E402
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventProgramItem, EventType  # noqa: E402
from apps.organizations.models import Organization  # noqa: E402
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()
PORT = 8575
BASE = f"http://127.0.0.1:{PORT}"
OUT = Path("docs/audit_screenshots")
PASSWORD = "AuditPassword123!"
TAG = "AUDIT_QA_TAG"

VIEWPORTS = [
    ("1920x1080", 1920, 1080),
    ("1440x900", 1440, 900),
    ("1366x768", 1366, 768),
    ("768x1024", 768, 1024),
    ("390x844", 390, 844),
]

def cleanup():
    Event.objects.filter(description=TAG).delete()
    EventType.objects.filter(code__startswith="audit-").delete()
    Venue.objects.filter(code__startswith="AUD").delete()
    Organization.objects.filter(name__startswith="Audit QA").delete()
    User.objects.filter(username__startswith="audit_").delete()

def prepare():
    cache.clear()
    cleanup()
    now = timezone.localtime()

    admin = User.objects.create_superuser(
        "audit_admin",
        password=PASSWORD,
        first_name="Aziz",
        last_name="Karimov",
        role=User.Role.SUPER_ADMIN,
    )
    owner = User.objects.create_user(
        "audit_owner",
        password=PASSWORD,
        first_name="Dilnoza",
        last_name="Rasulova",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )

    org = Organization.objects.create(
        name="Audit QA International Oncology Institute", short_name="IOI"
    )

    types = [
        EventType.objects.create(
            code=f"audit-{code}", name_uz=name, name_ru=name, name_en=en, color=color, sort_order=i
        )
        for i, (code, name, en, color) in enumerate(
            (
                ("symposium", "Simpozium", "Symposium", "#087FDB"),
                ("board", "Konsilium", "Tumor Board", "#00A9B7"),
                ("seminar", "Seminar", "Seminar", "#08A17A"),
                ("workshop", "Ustaxona", "Workshop", "#F15A24"),
            ),
            1,
        )
    ]

    venues = [
        Venue.objects.create(
            code=f"AUD{i}",
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
                ("Klinik ta'lim markazi", "Clinical Education Center"),
            ),
            1,
        )
    ]

    titles = [
        "International Oncology Symposium",
        "Multidisciplinary Tumor Board",
        "International Research Seminar",
        "Clinical Protocol Workshop",
        "Central Asia Cancer Partnership Forum",
    ]

    events = []
    for i, title in enumerate(titles):
        day = now.date() + timedelta(days=i)
        hour = 9 + (i * 2) % 8
        event = Event.objects.create(
            title=title,
            description=TAG,
            event_type=types[i % len(types)],
            venue=venues[i % len(venues)],
            planned_date=day,
            start_time=dt_time(hour),
            end_time=dt_time(hour + 2, 0),
            responsible_employee=owner,
            management_responsible=admin,
            created_by=admin,
            status=Event.Status.APPROVED if i != 1 else Event.Status.PENDING_APPROVAL,
            priority=Event.Priority.HIGH if i == 0 else Event.Priority.NORMAL,
            display_visibility=Event.DisplayVisibility.FULL,
            is_public_enabled=True,
            public_token=f"audit-token-{i+1}"
        )
        event.organizing_organizations.add(org)
        events.append(event)

        EventProgramItem.objects.create(
            event=event,
            sort_order=1,
            start_time=dt_time(hour),
            end_time=dt_time(hour, 30),
            title=f"Opening Ceremony for {title}",
            speaker_name_override="Prof. Karimov"
        )

    return admin, owner, events

def wait_server():
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"{BASE}/health/", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Audit server did not start")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    admin, owner, events = prepare()

    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_server()
        print("Audit server started successfully!")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # Unauthenticated context
            page = browser.new_page()

            routes_anon = {
                "A_public_dashboard": "/dashboard/",
                "B_public_calendar": "/dashboard/calendar/",
                "C_live_venues": "/venues/live/",
                "D_login": "/accounts/login/",
                "M_tv_wallboard": "/display/venues/",
            }

            for key, path in routes_anon.items():
                page.goto(f"{BASE}{path}")
                page.wait_for_timeout(300)
                for vp_name, w, h in VIEWPORTS:
                    page.set_viewport_size({"width": w, "height": h})
                    page.screenshot(path=str(OUT / f"{key}_{vp_name}.png"), full_page=False)

            # Authenticated context
            auth_page = browser.new_page()
            auth_page.goto(f"{BASE}/accounts/login/")
            auth_page.fill("input[name=username]", admin.username)
            auth_page.fill("input[name=password]", PASSWORD)
            auth_page.click("button[type=submit]")
            auth_page.wait_for_load_state("networkidle")

            routes_auth = {
                "E_user_workspace": "/workspace/",
                "F_profile": "/profile/",
                "G_events_list": "/events/",
                "H_event_create_wizard": "/events/wizard/",
                "I_event_detail": f"/events/{events[0].id}/",
                "J_approvals": "/events/approvals/",
                "K_attendance": f"/events/{events[0].id}/attendance/",
                "L_leadership_dashboard": "/leadership/",
                "N_telegram_settings": "/notifications/telegram/",
                "O_publication_composer": "/publications/",
                "P_reports": "/reports/",
                "Q_django_admin": "/admin/",
            }

            for key, path in routes_auth.items():
                auth_page.goto(f"{BASE}{path}")
                auth_page.wait_for_timeout(300)
                for vp_name, w, h in VIEWPORTS:
                    auth_page.set_viewport_size({"width": w, "height": h})
                    auth_page.screenshot(path=str(OUT / f"{key}_{vp_name}.png"), full_page=False)

            browser.close()
        print("Audit screenshot capture complete!")
    finally:
        server.terminate()
        server.wait(timeout=5)

if __name__ == "__main__":
    main()
