import os
import subprocess
import sys
import time
import urllib.request
from datetime import time as dt_time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, os.getcwd())

import django

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.core.exceptions import ValidationError  # noqa: E402
from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventType  # noqa: E402
from apps.venues.models import DisplayToken, Venue  # noqa: E402
from config.validators import validate_pdf_upload  # noqa: E402

PORT = 8565
BASE_URL = f"http://127.0.0.1:{PORT}"
PASSWORD = "Phase10-Readiness!"
User = get_user_model()


def cleanup():
    Event.objects.filter(title="[P10] Readiness Event").delete()
    DisplayToken.objects.filter(name="P10 readiness display").delete()
    EventType.objects.filter(code="p10-readiness").delete()
    Venue.objects.filter(code="P10-READY").delete()
    User.objects.filter(username="p10_readiness_admin").delete()


def prepare():
    cleanup()
    user = User.objects.create_user(
        "p10_readiness_admin", password=PASSWORD, role=User.Role.INTERNATIONAL_ADMIN
    )
    venue = Venue.objects.create(
        code="P10-READY",
        name_uz="Readiness Hall",
        name_ru="Readiness Hall",
        name_en="Readiness Hall",
        capacity=50,
        working_start=dt_time(8),
        working_end=dt_time(18),
    )
    event_type = EventType.objects.create(
        code="p10-readiness", name_uz="Readiness", name_ru="Readiness", name_en="Readiness"
    )
    event = Event.objects.create(
        title="[P10] Readiness Event",
        event_type=event_type,
        venue=venue,
        planned_date=timezone.localdate(),
        start_time=dt_time(10),
        end_time=dt_time(11),
        responsible_employee=user,
        management_responsible=user,
        created_by=user,
        status=Event.Status.APPROVED,
        expected_attendees=50,
        notes="PRIVATE-P10-NOTE",
        emergency_justification="PRIVATE-P10-EMERGENCY",
    )
    display = DisplayToken.objects.create(name="P10 readiness display")
    return user, event, display


def wait_for_server():
    for _ in range(50):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=1):
                return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("Readiness server did not start")


def main():
    user, event, display = prepare()
    try:
        try:
            validate_pdf_upload(SimpleUploadedFile("unsafe.pdf", b"not-pdf"))
            raise AssertionError("Unsafe PDF was accepted")
        except ValidationError:
            pass
        server = subprocess.Popen(
            [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            wait_for_server()
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1366, "height": 768})
                response = page.goto(f"{BASE_URL}/event/{event.public_token}/")
                assert response.status == 200
                assert "PRIVATE-P10" not in page.content()
                assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
                assert "no-store" in response.headers["cache-control"]
                assert page.locator("h1").count() == 1
                response = page.goto(f"{BASE_URL}/display/{display.token}/")
                assert response.status == 200 and "PRIVATE-P10" not in page.content()
                response = page.goto(f"{BASE_URL}/missing-phase10/")
                assert response.status == 404 and "Traceback" not in page.content()
                page.goto(f"{BASE_URL}/accounts/login/")
                assert page.locator("label").count() >= 2
                page.fill("input[name=username]", user.username)
                page.fill("input[name=password]", PASSWORD)
                page.click("button[type=submit]")
                page.goto(f"{BASE_URL}/reports/")
                assert page.locator("h1").count() == 1
                assert page.locator("form [name=period]").is_visible()
                page.set_viewport_size({"width": 375, "height": 812})
                assert page.locator("main").is_visible()
                browser.close()
        finally:
            server.terminate()
            server.wait(timeout=10)
    finally:
        cleanup()
    print("PASS — Phase 10 readiness acceptance")


if __name__ == "__main__":
    main()
