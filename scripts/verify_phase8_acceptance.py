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
os.environ["IEMS_BASE_URL"] = "http://127.0.0.1:8562"

import django

sys.path.insert(0, os.getcwd())
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.utils import timezone  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

from apps.events.models import Event, EventType  # noqa: E402
from apps.publications.models import Publication  # noqa: E402
from apps.publications.services import (  # noqa: E402
    approve_publication,
    prepare_publication,
    publish_publication,
    schedule_publication,
)
from apps.publications.testing import (  # noqa: E402
    FakeInstagramTransport,
    FakeTelegramChannelTransport,
)
from apps.venues.models import Venue  # noqa: E402

User = get_user_model()
PORT = 8562
BASE_URL = f"http://127.0.0.1:{PORT}"
OUTPUT = Path("tests/visual_baseline")
OUTPUT.mkdir(parents=True, exist_ok=True)


def cleanup():
    for publication in Publication.objects.filter(event__title__startswith="[P8]"):
        if publication.banner:
            publication.banner.delete(save=False)
    Event.objects.filter(title__startswith="[P8]").delete()
    EventType.objects.filter(code="p8-acceptance").delete()
    Venue.objects.filter(code="P8-ACC").delete()
    User.objects.filter(username__startswith="p8_accept_").delete()


def prepare_data():
    cleanup()
    admin = User.objects.create_user(
        "p8_accept_admin",
        password="Phase8-Safe-Test!",
        role=User.Role.INTERNATIONAL_ADMIN,
    )
    manager = User.objects.create_user(
        "p8_accept_manager",
        password="Phase8-Safe-Test!",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )
    viewer = User.objects.create_user(
        "p8_accept_viewer",
        password="Phase8-Safe-Test!",
        role=User.Role.LEADERSHIP_VIEWER,
    )
    venue = Venue.objects.create(
        code="P8-ACC",
        name_uz="Xalqaro konferensiya zali",
        name_ru="Международный конференц-зал",
        name_en="International Conference Hall",
        capacity=300,
        working_start=dt_time(8),
        working_end=dt_time(20),
    )
    event_type = EventType.objects.create(
        code="p8-acceptance",
        name_uz="Xalqaro forum",
        name_ru="Международный форум",
        name_en="International Forum",
    )
    event = Event.objects.create(
        title="[P8] Central Asian Medical Cooperation Forum",
        description="International cooperation, science and clinical exchange.",
        event_type=event_type,
        venue=venue,
        planned_date=(timezone.localtime() + timedelta(days=10)).date(),
        start_time=dt_time(10),
        end_time=dt_time(14),
        responsible_employee=admin,
        management_responsible=manager,
        created_by=admin,
        status=Event.Status.APPROVED,
        registration_url="https://register.example.test/forum",
    )
    return admin, manager, viewer, event


def wait_for_server():
    for _ in range(40):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=1) as response:
                return response.status == 200
        except Exception:
            time.sleep(0.3)
    return False


def login(page, username):
    page.goto(f"{BASE_URL}/accounts/login/")
    page.fill("input[name=username]", username)
    page.fill("input[name=password]", "Phase8-Safe-Test!")
    page.click("button[type=submit]")


def shot(page, name, selector=None, size=(1440, 1000)):
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.wait_for_timeout(150)
    if selector:
        page.wait_for_selector(selector, timeout=10_000)
    target = page.locator(selector) if selector else page
    target.screenshot(path=str(OUTPUT / name))


def main():
    admin, manager, viewer, event = prepare_data()
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
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            login(page, admin.username)
            page.goto(f"{BASE_URL}/publications/")
            shot(page, "phase8_01_publication_dashboard.png", "[data-testid=publication-dashboard]")

            page.goto(f"{BASE_URL}/publications/events/{event.pk}/new/")
            page.select_option("select[name=platform]", "telegram_channel")
            page.select_option("select[name=language]", "uz")
            page.fill(
                "textarea[name=caption]", "Markaziy Osiyo tibbiy hamkorlik forumiga taklif qilamiz."
            )
            shot(page, "phase8_02_telegram_composer.png", "[data-testid=publication-composer]")
            page.click(".composer-form button[type=submit]")
            telegram = Publication.objects.filter(event=event).latest("created_at")
            prepare_publication(telegram, admin)
            approve_publication(telegram, manager)
            publish_publication(telegram.pk, FakeTelegramChannelTransport())
            page.reload()
            shot(page, "phase8_03_telegram_preview.png", "[data-testid=publication-preview]")
            shot(page, "phase8_04_banner_telegram.png", "[data-testid=publication-banner]")

            instagram = Publication.objects.create(
                event=event,
                platform=Publication.Platform.INSTAGRAM,
                language="en",
                headline=event.title,
                caption="Join the international medical cooperation forum.",
                created_by=admin,
            )
            prepare_publication(instagram, admin)
            response = page.goto(f"{BASE_URL}/publications/{instagram.pk}/edit/")
            if response.status != 200:
                raise RuntimeError(f"Instagram composer returned HTTP {response.status}")
            shot(page, "phase8_05_instagram_composer.png", "[data-testid=publication-composer]")
            approve_publication(instagram, manager)
            publish_publication(instagram.pk, FakeInstagramTransport())
            page.goto(f"{BASE_URL}/publications/{instagram.pk}/")
            shot(page, "phase8_06_instagram_preview.png", "[data-testid=publication-preview]")

            scheduled = Publication.objects.create(
                event=event,
                platform=Publication.Platform.TELEGRAM_CHANNEL,
                language="ru",
                headline=event.title,
                caption="Приглашаем на международный медицинский форум.",
                created_by=admin,
            )
            prepare_publication(scheduled, admin)
            approve_publication(scheduled, manager)
            schedule_publication(scheduled, admin, timezone.now() + timedelta(hours=1))
            page.goto(f"{BASE_URL}/publications/{scheduled.pk}/")
            shot(page, "phase8_07_schedule.png")

            failed = Publication.objects.create(
                event=event,
                platform=Publication.Platform.TELEGRAM_CHANNEL,
                language="uz",
                headline="[P8] Retry-safe announcement",
                caption="Retry acceptance flow.",
                created_by=admin,
            )
            prepare_publication(failed, admin)
            approve_publication(failed, manager)
            fake = FakeTelegramChannelTransport(fail_once=True)
            try:
                publish_publication(failed.pk, fake)
            except Exception:
                failed.status = Publication.Status.FAILED
                failed.error_code = "network"
                failed.error_message = "Temporary test failure"
                failed.save()
            publish_publication(failed.pk, fake)
            assert len(fake.calls) == 2
            page.goto(f"{BASE_URL}/publications/{failed.pk}/")
            shot(page, "phase8_08_failed_retry.png")

            page.goto(f"{BASE_URL}/publications/events/{event.pk}/new/")
            shot(page, "phase8_09_mobile_composer.png", size=(375, 812))
            for size in ((1920, 1080), (1366, 768), (768, 1024), (375, 812)):
                page.set_viewport_size({"width": size[0], "height": size[1]})
                assert page.locator("[data-testid=publication-composer]").is_visible()

            page.context.clear_cookies()
            login(page, viewer.username)
            assert page.goto(f"{BASE_URL}/publications/{telegram.pk}/").status == 200
            assert page.locator("body").inner_text().find("TELEGRAM_BOT_TOKEN") == -1
            browser.close()
        print("PASS — Phase 8 Playwright acceptance")
    finally:
        server.terminate()
        server.wait(timeout=10)
        cleanup()


if __name__ == "__main__":
    main()
