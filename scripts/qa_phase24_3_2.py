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
OUT = Path("tests/visual_baseline/phase24_3_2")
PASSWORD = "AdminPassword123!"

VIEWPORTS = [
    ("1920x1080", 1920, 1080),
    ("1600x900", 1600, 900),
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
        print("Server running on port 8599, starting Playwright QA for Phase 24.3.2...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(f"{BASE}/accounts/login/")
            page.fill("input[name=username]", admin.username)
            page.fill("input[name=password]", PASSWORD)
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")

            # 1. Verification at 1920x1080
            page.goto(f"{BASE}/reports/")
            page.wait_for_timeout(1000)

            items = page.locator(".venue-rank-item").all()
            print(f"\n--- VENUE UTILIZATION QA REPORT (1920x1080) ---")
            print(f"{'Venue':<12} | {'Displayed %':<11} | {'Track px':<10} | {'Fill px':<10} | {'Visual %':<10} | {'Status':<8}")
            print("-" * 75)

            all_passed = True

            for item in items:
                code = item.locator(".venue-code").inner_text().strip()
                val_text = item.locator(".progress-val").inner_text().strip()
                clean_val_str = val_text.replace("%", "").replace(",", ".").strip()
                displayed_pct = float(clean_val_str)

                track = item.locator(".progress-track")
                fill = item.locator(".progress-fill")

                track_width = track.evaluate("el => el.getBoundingClientRect().width")
                fill_width = fill.evaluate("el => el.getBoundingClientRect().width")

                visual_pct = (fill_width / track_width * 100.0) if track_width > 0 else 0.0

                if displayed_pct == 0.0:
                    status = "PASS" if fill_width == 0.0 else "FAIL"
                else:
                    deviation = abs(visual_pct - displayed_pct)
                    status = "PASS" if deviation <= 0.15 else "FAIL"

                if status == "FAIL":
                    all_passed = False

                row_str = f"{code:<12} | {val_text:<11} | {track_width:<10.2f} | {fill_width:<10.2f} | {visual_pct:<9.2f}% | {status:<8}"
                print(row_str)

            # 2. Capture Screenshots for Phase 24.3.2
            for vp_name, width, height in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": height})
                page.goto(f"{BASE}/reports/")
                page.wait_for_timeout(1000)
                screenshot_path = str(OUT / f"reports_{vp_name}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"Captured {vp_name} screenshot -> {screenshot_path}")

            browser.close()

            if not all_passed:
                print("\n[ERROR] QA FAILED: Some venue progress fills deviated from displayed percentages!")
                sys.exit(1)
            else:
                print("\n[SUCCESS] QA PASSED: All venue progress fills match displayed percentages perfectly!")

    finally:
        server.terminate()
        server.wait(timeout=5)

if __name__ == "__main__":
    main()
