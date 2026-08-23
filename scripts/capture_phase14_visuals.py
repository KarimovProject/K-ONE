"""
Phase 14 Visual Baseline Capture Script
Captures the 9 required visual screens for Owner Review:
1. dashboard_1920.png (1920x1080)
2. dashboard_1366.png (1366x768)
3. dashboard_mobile.png (390x844)
4. calendar_month_1920.png (1920x1080)
5. calendar_week_1920.png (1920x1080)
6. calendar_live.png (1920x1080)
7. calendar_inspector.png (1920x1080, event drawer open)
8. live_venues_1920.png (1920x1080)
9. workspace_1920.png (1920x1080, authenticated admin)
"""
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, r"C:\IEMS")

import django
django.setup()

from django.contrib.auth import get_user_model
from playwright.sync_api import sync_playwright

User = get_user_model()
BASE = "http://10.34.12.2:8012"
OUT = Path(r"C:\IEMS\tests\visual_baseline\phase14")
PASSWORD = "AdminPassword123!"

def ensure_user():
    admin, _ = User.objects.get_or_create(
        username="phase14_admin",
        defaults={
            "is_staff": True,
            "is_superuser": True,
            "first_name": "Aziz",
            "last_name": "Karimov",
            "email": "admin@iems.uz",
        }
    )
    admin.set_password(PASSWORD)
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    return admin

def capture():
    OUT.mkdir(parents=True, exist_ok=True)
    admin = ensure_user()
    print(f"[Phase 14] Capturing visual baselines to {OUT}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1. Dashboard 1920
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(f"{BASE}/dashboard/", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "dashboard_1920.png"), full_page=True)
        print(" -> Captured dashboard_1920.png")
        ctx.close()

        # 2. Dashboard 1366
        ctx = browser.new_context(viewport={"width": 1366, "height": 768})
        page = ctx.new_page()
        page.goto(f"{BASE}/dashboard/", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "dashboard_1366.png"), full_page=True)
        print(" -> Captured dashboard_1366.png")
        ctx.close()

        # 3. Dashboard Mobile 390x844
        ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        page = ctx.new_page()
        page.goto(f"{BASE}/dashboard/", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "dashboard_mobile.png"), full_page=True)
        print(" -> Captured dashboard_mobile.png")
        ctx.close()

        # 4. Calendar Month 1920
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(f"{BASE}/dashboard/calendar/?view=month", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "calendar_month_1920.png"), full_page=True)
        print(" -> Captured calendar_month_1920.png")
        ctx.close()

        # 5. Calendar Week 1920
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(f"{BASE}/dashboard/calendar/?view=week", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "calendar_week_1920.png"), full_page=True)
        print(" -> Captured calendar_week_1920.png")
        ctx.close()

        # 6. Calendar Live 1920
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(f"{BASE}/dashboard/calendar/?view=week&live=1", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "calendar_live.png"), full_page=True)
        print(" -> Captured calendar_live.png")
        ctx.close()

        # 7. Calendar Inspector Drawer (Open event dialog)
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(f"{BASE}/dashboard/calendar/?view=month", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.evaluate("() => { const el = document.querySelector('.calendar-event'); if (el) el.click(); }")
        page.wait_for_timeout(600)
        page.screenshot(path=str(OUT / "calendar_inspector.png"), full_page=True)
        print(" -> Captured calendar_inspector.png")
        ctx.close()

        # 8. Live Venues 1920
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(f"{BASE}/venues/live/", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "live_venues_1920.png"), full_page=True)
        print(" -> Captured live_venues_1920.png")
        ctx.close()

        # 9. Workspace 1920 (Authenticated Admin)
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(f"{BASE}/accounts/login/", wait_until="networkidle")
        page.fill("input[name='username']", "phase14_admin")
        page.fill("input[name='password']", PASSWORD)
        page.click("button[type='submit']")
        page.wait_for_timeout(800)
        page.goto(f"{BASE}/workspace/", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "workspace_1920.png"), full_page=True)
        print(" -> Captured workspace_1920.png")
        ctx.close()

        browser.close()

    print("[Phase 14] All 9 baseline screenshots captured successfully!")

if __name__ == "__main__":
    capture()
