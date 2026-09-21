"""Phase 24.1 — Visual QA Screenshot Capture with Hard Guards"""
import os, sys, time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    os.system(f"{sys.executable} -m pip install playwright -q")
    os.system(f"{sys.executable} -m playwright install chromium")
    from playwright.sync_api import sync_playwright

BASE = "http://10.34.12.2:8012"
PASSWORD = os.environ.get("IEMS_ACCEPTANCE_PASSWORD", "Password123!")
OUT = r"C:\IEMS\tests\visual_baseline\phase24_3"
os.makedirs(OUT, exist_ok=True)

PAGES_AUTH = [
    ("workspace",  "/workspace/"),
    ("events",     "/events/"),
    ("calendar",   "/calendar/"),
    ("approvals",  "/events/approvals/"),
    ("moved_events", "/events/moved/"),
    ("internal_venues", "/master-data/venues/"),
    ("event_types", "/master-data/event-types/"),
    ("organizations", "/master-data/organizations/"),
    ("sponsors",   "/master-data/sponsors/"),
    ("speakers",   "/events/speakers/"),
    ("reports",    "/reports/"),
    ("leadership", "/leadership/"),
    ("profile",    "/profile/"),
]

PAGES_PUBLIC = [
    ("public_dashboard", "/dashboard/"),
    ("public_calendar",  "/dashboard/calendar/"),
    ("public_venues",    "/venues/live/"),
    ("login",            "/accounts/login/"),
]

VIEWPORTS_DESKTOP = [
    (1920, 1080, "1920"),
    (1600, 900,  "1600"),
    (1440, 900,  "1440"),
    (1366, 768,  "1366"),
]

VIEWPORTS_MOBILE = [
    (390, 844, "390"),
]

ERROR_STRINGS = [
    "Page not found (404)",
    "Server Error (500)",
    "Traceback",
    "Using the URLconf defined in",
    "You're seeing this error because you have DEBUG = True",
]

def login(page):
    response = page.goto(f"{BASE}/accounts/login/", wait_until="networkidle")
    page.wait_for_selector('input[name="username"]', state="visible", timeout=15000)
    page.fill('input[name="username"]', "acceptance_admin")
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    time.sleep(0.5)

def capture(page, name, url, label):
    target_url = f"{BASE}{url}"
    response = page.goto(target_url, wait_until="networkidle")
    time.sleep(0.8)
    
    if response.status != 200:
        print(f"  [FAILED] {name} @ {label} => HTTP {response.status} on {target_url}")
        return False
        
    content = page.content()
    for err in ERROR_STRINGS:
        if err in content:
            print(f"  [FAILED] {name} @ {label} => Django error page detected: '{err}' on {target_url}")
            return False
            
    if name == "reports" and "Hisobotlar va tahlil" not in content:
        print(f"  [FAILED] {name} @ {label} => Expected heading 'Hisobotlar va tahlil' missing on {target_url}")
        return False
        
    fname = f"{OUT}/{name}_{label}.png"
    page.screenshot(path=fname, full_page=True)
    print(f"  [OK] {name} @ {label}  =>  {fname}")
    return True

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        total = 0
        failed = 0

        # Authenticated Pages (All viewports)
        for w, h, label in VIEWPORTS_DESKTOP + VIEWPORTS_MOBILE:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            login(page)
            for name, url in PAGES_AUTH:
                # Only capture workspace, events, calendar on mobile
                if label == "390" and name not in ["workspace", "events", "calendar", "reports"]:
                    continue
                if capture(page, name, url, label):
                    total += 1
                else:
                    failed += 1
            context.close()

        # Public & Login Pages (All viewports)
        for w, h, label in VIEWPORTS_DESKTOP + VIEWPORTS_MOBILE:
            context = browser.new_context(viewport={"width": w, "height": h})
            page = context.new_page()
            for name, url in PAGES_PUBLIC:
                # Only capture login on mobile
                if label == "390" and name != "login":
                    continue
                if capture(page, name, url, label):
                    total += 1
                else:
                    failed += 1
            context.close()

        browser.close()
    print(f"\nDone. {total} screenshots captured in {OUT}, {failed} failed.")

if __name__ == "__main__":
    main()
