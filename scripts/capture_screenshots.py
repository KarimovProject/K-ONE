import os
import sys
from playwright.sync_api import sync_playwright

BASE_URL = "http://10.34.12.2:8012"
OUT_DIR = r"C:\IEMS\tests\visual_baseline\phase26_1"

PAGES = {
    "login": "/accounts/login/",
    "events": "/events/",
    "approvals": "/events/approvals/",
    "organizations": "/master-data/organizations/",
    "venues": "/master-data/venues/",
    "event_types": "/master-data/event-types/",
    "sponsors": "/master-data/sponsors/",
    "reports": "/reports/",
    "profile": "/profile/"
}

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1600, "height": 900},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1024, "height": 768},
    {"width": 390, "height": 844}
]

def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=VIEWPORTS[0])
        page = context.new_page()

        # Helper to take screenshots
        def take_shots(page_name, url):
            for vp in VIEWPORTS:
                page.set_viewport_size(vp)
                page.goto(url, wait_until="networkidle")
                # Handle possible 500
                if page.evaluate("document.title") == "Server Error (500)":
                    print(f"FAILED: 500 Error on {url}")
                page.screenshot(path=os.path.join(OUT_DIR, f"{page_name}_{vp['width']}.png"), full_page=True)



        print("Logging in to workspace...")
        page.goto(f"{BASE_URL}{PAGES['login']}")
        page.fill("input[name='username']", "admin")
        page.fill("input[name='password']", "admin123")
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")

        print("Capturing workspace pages...")
        for name, path in PAGES.items():
            if name not in ["public_dashboard", "public_calendar", "public_live", "login"]:
                print(f"Capturing {name}...")
                take_shots(name, f"{BASE_URL}{path}")

        browser.close()

if __name__ == "__main__":
    run()
