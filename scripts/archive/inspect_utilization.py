import os
import sys
import time
import subprocess
import urllib.request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, os.getcwd())

import django
django.setup()

from django.contrib.auth import get_user_model
from playwright.sync_api import sync_playwright

User = get_user_model()
PORT = 8599
BASE = f"http://127.0.0.1:{PORT}"
PASSWORD = "AdminPassword123!"

def seed_data():
    admin, _ = User.objects.get_or_create(
        username="phase24_admin",
        defaults={"is_staff": True, "is_superuser": True, "first_name": "Aziz", "last_name": "Karimov"}
    )
    admin.set_password(PASSWORD)
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    return admin

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
    admin = seed_data()

    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_server()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(f"{BASE}/accounts/login/")
            page.fill("input[name=username]", admin.username)
            page.fill("input[name=password]", PASSWORD)
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

            page.goto(f"{BASE}/reports/")
            page.wait_for_timeout(1000)

            # Inspect venue ranking items
            items = page.locator(".venue-rank-item").all()
            print(f"Found {len(items)} venue rank items:")
            for item in items:
                code = item.locator(".venue-code").inner_text()
                name = item.locator(".venue-name").inner_text()
                val_text = item.locator(".progress-val").inner_text()
                track = item.locator(".progress-track")
                fill = item.locator(".progress-fill")
                
                track_box = track.bounding_box()
                fill_box = fill.bounding_box()
                fill_html = fill.evaluate("el => el.outerHTML")
                fill_computed_width = fill.evaluate("el => window.getComputedStyle(el).width")
                track_computed_width = track.evaluate("el => window.getComputedStyle(el).width")
                
                print(f"--- {code} ({name}) ---")
                print(f"  val_text: {val_text}")
                print(f"  fill outerHTML: {fill_html}")
                print(f"  track_box: {track_box}")
                print(f"  fill_box: {fill_box}")
                print(f"  track computed width: {track_computed_width}, fill computed width: {fill_computed_width}")

            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=5)

if __name__ == "__main__":
    main()
