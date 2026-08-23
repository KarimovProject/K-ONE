import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path

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
OUT = Path("tests/visual_baseline/phase24_3")
PASSWORD = "AdminPassword123!"

VIEWPORTS = [
    ("1920x1080", 1920, 1080),
    ("1600x900", 1600, 900),
    ("1440x900", 1440, 900),
    ("1366x768", 1366, 768),
]

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
    OUT.mkdir(parents=True, exist_ok=True)
    admin = seed_data()

    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_server()
        print("Server running on port 8599, starting Playwright captures for Phase 24.3...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            auth_page = browser.new_page()
            auth_page.set_viewport_size({"width": 1920, "height": 1080})
            auth_page.goto(f"{BASE}/accounts/login/")
            auth_page.fill("input[name=username]", admin.username)
            auth_page.fill("input[name=password]", PASSWORD)
            auth_page.click("button[type=submit]")
            auth_page.wait_for_load_state("networkidle")

            for vp_name, width, height in VIEWPORTS:
                auth_page.set_viewport_size({"width": width, "height": height})
                auth_page.goto(f"{BASE}/reports/")
                auth_page.wait_for_timeout(1000)
                auth_page.screenshot(path=str(OUT / f"reports_{vp_name}.png"), full_page=True)

            auth_page.close()
            browser.close()
            print("All Phase 24.3 screenshots captured successfully!")

    finally:
        server.terminate()
        server.wait(timeout=5)

if __name__ == "__main__":
    main()
