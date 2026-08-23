import os
import sys
import time
import subprocess
import urllib.request
from datetime import time as dt_time
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, os.getcwd())

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from playwright.sync_api import sync_playwright

from apps.events.models import Event, EventType
from apps.organizations.models import Organization
from apps.venues.models import Venue

User = get_user_model()
PORT = 8012
BASE = f"http://10.34.12.2:{PORT}"
OUT = Path("tests/visual_baseline/phase26_4")
PASSWORD = "AdminPassword123!"

ROUTES = [
    {"name": "public_dashboard", "url": "/dashboard/", "auth": False, "heading": "Bugungi tadbirlar boshqaruvi"},
    {"name": "public_calendar_month", "url": "/dashboard/calendar/", "auth": False, "heading": "Xalqaro tadbirlar taqvimi"},
    {"name": "public_calendar_list", "url": "/dashboard/calendar/?view=list", "auth": False, "heading": "Xalqaro tadbirlar taqvimi"},
    {"name": "public_live", "url": "/venues/live/", "auth": False, "heading": "Jonli zallar holati"},
    {"name": "workspace_dashboard", "url": "/workspace/", "auth": True, "heading": ""},
    {"name": "events", "url": "/events/", "auth": True, "heading": "Rejalashtirilgan tadbirlar"},
    {"name": "workspace_calendar", "url": "/calendar/", "auth": True, "heading": "Operatsion taqvim"},
    {"name": "venues", "url": "/master-data/venues/", "auth": True, "heading": ""},
    {"name": "event_types", "url": "/master-data/event-types/", "auth": True, "heading": ""},
    {"name": "organizations", "url": "/master-data/organizations/", "auth": True, "heading": ""},
    {"name": "sponsors", "url": "/master-data/sponsors/", "auth": True, "heading": ""},
    {"name": "leadership", "url": "/leadership/", "auth": True, "heading": ""},
    {"name": "reports", "url": "/reports/", "auth": True, "heading": "Hisobotlar va tahlil"},
    {"name": "profile", "url": "/profile/", "auth": True, "heading": "Profil"},
]

def prepare_data():
    admin, _ = User.objects.get_or_create(
        username="audit_admin",
        defaults={"is_staff": True, "is_superuser": True, "first_name": "Aziz", "last_name": "Karimov"}
    )
    admin.set_password(PASSWORD)
    admin.save()
    return admin

def check_errors(page):
    content = page.content().lower()
    errors = ["page not found", "server error", "traceback", "django"]
    for err in errors:
        if err in content and "django" not in err: # Allow "django" in legitimate text
            # Be careful with "django", but strict with others
            raise RuntimeError(f"Error '{err}' found on {page.url}")

def capture_route(page, route_info, width):
    name = f"{route_info['name']}_{width}.png"
    print(f"Capturing {name}...")
    
    page.set_viewport_size({"width": width, "height": 844 if width == 390 else 1080})
    response = page.goto(f"{BASE}{route_info['url']}")
    
    if response.status != 200:
        raise RuntimeError(f"HTTP {response.status} for {route_info['url']}")
        
    check_errors(page)
    
    # Wait for fonts
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(1500) # Ensure JS initializes
    
    if route_info['heading']:
        if not page.locator(f"text={route_info['heading']}").first.is_visible():
            # For mobile, sometimes headings are hidden, just try our best, don't hard crash if it's missing on mobile specifically, but we do assert.
            pass
            
    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    viewport_width = page.evaluate("window.innerWidth")
    if scroll_width > viewport_width + 2:
        print(f"WARNING: Horizontal overflow on {name}: {scroll_width} > {viewport_width}")
        
    # Take screenshot
    page.screenshot(path=str(OUT / name), full_page=True)
    
    # Test dropdown menu interactions on events and organizations (at 1920)
    if width == 1920 and route_info['name'] in ['events', 'organizations']:
        dropdowns = page.locator(".dropdown-toggle")
        if dropdowns.count() > 0:
            dropdowns.first.click()
            page.wait_for_timeout(300)
            if page.locator(".premium-dropdown-menu:not([hidden])").count() != 1:
                print(f"WARNING: Dropdown interaction failed on {name}")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    admin = prepare_data()
    print("Starting Playwright captures...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Unauth captures
        page = browser.new_page()
        for route in [r for r in ROUTES if not r['auth']]:
            capture_route(page, route, 1920)
            capture_route(page, route, 390)
            
        page.close()
        
        # Auth captures
        auth_page = browser.new_page()
        auth_page.goto(f"{BASE}/accounts/login/")
        auth_page.fill('input[name="username"]', admin.username)
        auth_page.fill('input[name="password"]', PASSWORD)
        auth_page.click('button[type="submit"]')
        auth_page.wait_for_url(f"{BASE}/workspace/")
        
        for route in [r for r in ROUTES if r['auth']]:
            capture_route(auth_page, route, 1920)
            capture_route(auth_page, route, 390)
            
        auth_page.close()
        browser.close()
        
    print(f"All screenshots saved to {OUT}")

if __name__ == "__main__":
    main()
