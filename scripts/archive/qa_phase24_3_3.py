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
OUT = Path("tests/visual_baseline/phase24_3_3")
PASSWORD = "AdminPassword123!"

VIEWPORTS = [
    ("1920x1080", 1920, 1080),
    ("1600x900", 1600, 900),
    ("1440x900", 1440, 900),
    ("1366x768", 1366, 768),
    ("1024x768", 1024, 768),
    ("390x844", 390, 844),
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
        print("Server running on port 8599, starting Playwright QA for Phase 24.3.3...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(f"{BASE}/accounts/login/")
            page.fill("input[name=username]", admin.username)
            page.fill("input[name=password]", PASSWORD)
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

            all_passed = True
            
            # 1. Capture Screenshots and check for clipping for Phase 24.3.3
            for vp_name, width, height in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": height})
                page.goto(f"{BASE}/reports/")
                page.wait_for_timeout(1000)
                
                # Check for horizontal overflow (clipping)
                scroll_width = page.evaluate("document.documentElement.scrollWidth")
                client_width = page.evaluate("document.documentElement.clientWidth")
                
                if scroll_width > client_width:
                    print(f"[{vp_name}] FAIL: Horizontal overflow detected! ScrollWidth: {scroll_width}, ClientWidth: {client_width}")
                    all_passed = False
                else:
                    print(f"[{vp_name}] PASS: No horizontal overflow.")
                
                screenshot_path = str(OUT / f"reports_{vp_name}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Captured {vp_name} screenshot -> {screenshot_path}")

            browser.close()

            if not all_passed:
                print("\n[ERROR] QA FAILED: Responsive defects found!")
                sys.exit(1)
            else:
                print("\n[SUCCESS] QA PASSED: All responsive quality gates met!")

    finally:
        server.terminate()
        server.wait(timeout=5)

if __name__ == "__main__":
    main()
