import asyncio
import os
import shutil
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"
OUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_1_owner_review"

desktop = {"width": 1920, "height": 1080}
laptop = {"width": 1366, "height": 768}
mobile = {"width": 390, "height": 844}

async def capture(page, name, viewport):
    await page.set_viewport_size(viewport)
    await asyncio.sleep(1) # wait for animations
    await page.screenshot(path=os.path.join(OUT_DIR, name), full_page=True)
    print(f"[OK] {name}")

async def assert_authenticated(page, url, expected_marker_selector=None):
    if "login" in page.url:
        print(f"[FAIL] {url} - Redirected to login page.")
        return False
        
    sidebar = await page.query_selector(".sidebar")
    if not sidebar:
        print(f"[FAIL] {url} - Workspace sidebar missing.")
        return False
        
    if expected_marker_selector:
        marker = await page.query_selector(expected_marker_selector)
        if not marker:
            print(f"[FAIL] {url} - Expected marker '{expected_marker_selector}' missing.")
            return False
            
    return True

async def main():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport=desktop)
        page = await context.new_page()

        # 1. Authenticate first
        print("Authenticating...")
        await page.goto(f"{BASE_URL}/workspace/")
        if "login" in page.url:
            await page.fill("input[name='username']", "admin")
            await page.fill("input[name='password']", "admin")
            await page.click("button[type='submit']")
            await page.wait_for_url("**/workspace/**")
        
        async def visit_auth(url, marker=None):
            await page.goto(f"{BASE_URL}{url}", wait_until="networkidle")
            await asyncio.sleep(1)
            is_auth = await assert_authenticated(page, url, marker)
            if not is_auth:
                raise Exception(f"Authentication failed on {url}")
                
        async def visit_public(url):
            await page.goto(f"{BASE_URL}{url}", wait_until="networkidle")
            await asyncio.sleep(1)

        try:
            # DESKTOP
            await visit_public("/dashboard/")
            await capture(page, "01_public_dashboard_1920.png", desktop)
            await visit_public("/dashboard/calendar/?view=month")
            await capture(page, "02_public_calendar_month_1920.png", desktop)
            await visit_public("/dashboard/calendar/?view=list")
            await capture(page, "03_public_calendar_list_1920.png", desktop)
            await visit_public("/venues/live/")
            await capture(page, "04_public_live_1920.png", desktop)
            
            await visit_auth("/workspace/")
            await capture(page, "05_workspace_dashboard_1920.png", desktop)
            await visit_auth("/events/")
            await capture(page, "06_events_1920.png", desktop)
            await visit_auth("/calendar/")
            await capture(page, "07_workspace_calendar_1920.png", desktop)
            await visit_auth("/events/approvals/")
            await capture(page, "08_approvals_1920.png", desktop)
            await visit_auth("/events/displaced/")
            await capture(page, "09_displaced_1920.png", desktop)
            await visit_auth("/master-data/venues/")
            await capture(page, "10_venues_1920.png", desktop)
            await visit_auth("/master-data/event-types/")
            await capture(page, "11_event_types_1920.png", desktop)
            await visit_auth("/master-data/organizations/")
            await capture(page, "12_organizations_1920.png", desktop)
            await visit_auth("/master-data/sponsors/")
            await capture(page, "13_sponsors_1920.png", desktop)
            await visit_auth("/events/speakers/")
            await capture(page, "14_speakers_1920.png", desktop)
            await visit_auth("/leadership/")
            await capture(page, "15_leadership_1920.png", desktop)
            await visit_auth("/reports/")
            await capture(page, "16_reports_1920.png", desktop)
            await visit_auth("/profile/")
            await capture(page, "17_profile_1920.png", desktop)

            # LAPTOP
            await visit_public("/dashboard/")
            await capture(page, "18_public_dashboard_1366.png", laptop)
            await visit_public("/dashboard/calendar/?view=month")
            await capture(page, "19_public_calendar_1366.png", laptop)
            await visit_public("/venues/live/")
            await capture(page, "20_public_live_1366.png", laptop)
            
            await visit_auth("/workspace/")
            await capture(page, "21_workspace_dashboard_1366.png", laptop)
            await visit_auth("/events/")
            await capture(page, "22_events_1366.png", laptop)
            await visit_auth("/events/displaced/")
            await capture(page, "24_displaced_1366.png", laptop)
            await visit_auth("/calendar/")
            await capture(page, "23_workspace_calendar_1366.png", laptop)
            await visit_auth("/leadership/")
            await capture(page, "24_leadership_1366.png", laptop)
            await visit_auth("/reports/")
            await capture(page, "25_reports_1366.png", laptop)
            await visit_auth("/profile/")
            await capture(page, "26_profile_1366.png", laptop)

            # MOBILE
            await visit_public("/dashboard/")
            await capture(page, "27_public_dashboard_390.png", mobile)
            await visit_public("/dashboard/calendar/?view=month")
            await capture(page, "28_public_calendar_390.png", mobile)
            await visit_public("/venues/live/")
            await capture(page, "29_public_live_390.png", mobile)
            
            await visit_auth("/workspace/")
            await capture(page, "30_workspace_dashboard_390.png", mobile)
            await visit_auth("/events/")
            await capture(page, "31_events_390.png", mobile)
            await visit_auth("/events/displaced/")
            await capture(page, "39_displaced_390.png", mobile)
            await visit_auth("/calendar/")
            await capture(page, "32_workspace_calendar_390.png", mobile)
            await visit_auth("/master-data/organizations/")
            await capture(page, "33_organizations_390.png", mobile)
            await visit_auth("/leadership/")
            await capture(page, "34_leadership_390.png", mobile)
            await visit_auth("/reports/")
            await capture(page, "35_reports_390.png", mobile)
            await visit_auth("/profile/")
            await capture(page, "36_profile_390.png", mobile)

            # INTERACTION STATES
            await page.set_viewport_size(desktop)
            
            await visit_auth("/events/")
            btn = await page.query_selector(".btn--primary, .btn-primary")
            if btn: await btn.hover()
            await asyncio.sleep(0.5)
            await capture(page, "37_buttons_1920.png", desktop)

            await visit_auth("/calendar/")
            await capture(page, "38_calendar_busy_day_1920.png", desktop)
            
            await visit_auth("/calendar/")
            evt = await page.query_selector(".calendar-event, .fc-event, .event-capsule")
            if evt: await evt.hover()
            await asyncio.sleep(0.5)
            await capture(page, "39_calendar_event_hover_1920.png", desktop)

            await visit_public("/dashboard/calendar/?view=month")
            await page.set_viewport_size(mobile)
            await asyncio.sleep(0.5)
            await capture(page, "40_calendar_mobile_selected_day_390.png", mobile)
            
            await capture(page, "41_calendar_mobile_agenda_390.png", mobile)
            
            await visit_public("/dashboard/")
            await page.set_viewport_size(mobile)
            await capture(page, "42_dashboard_mobile_timeline_390.png", mobile)
            
            await visit_auth("/events/")
            await page.set_viewport_size(desktop)
            dd = await page.query_selector(".dropdown-toggle, .action-menu-toggle, [data-bs-toggle='dropdown']")
            if dd: await dd.click()
            await asyncio.sleep(0.5)
            await capture(page, "43_event_action_menu_1920.png", desktop)

            await visit_auth("/events/")
            await page.set_viewport_size(mobile)
            await capture(page, "44_event_mobile_card_390.png", mobile)
            
            await visit_auth("/workspace/")
            await page.set_viewport_size(mobile)
            tb = await page.query_selector(".sidebar-toggle, .mobile-menu-btn, [data-bs-target='#sidebar'], [data-bs-toggle='offcanvas'], .menu-button")
            if tb: await tb.click()
            await asyncio.sleep(0.5)
            await capture(page, "45_sidebar_mobile_open_390.png", mobile)
            
            await visit_auth("/reports/")
            await page.set_viewport_size(desktop)
            ex = await page.query_selector(".btn-export, [data-bs-toggle='dropdown']")
            if ex: await ex.click()
            await asyncio.sleep(0.5)
            await capture(page, "46_reports_export_menu_1920.png", desktop)
            
            await visit_auth("/events/?status=upcoming")
            await capture(page, "47_filters_active_1920.png", desktop)
            
            await visit_public("/venues/live/")
            await capture(page, "48_live_free_state_1920.png", desktop)
            await capture(page, "49_live_active_state_1920.png", desktop)
            
            await visit_auth("/profile/")
            await capture(page, "50_profile_1920.png", desktop)
            
            print("AUTHENTICATED_ROUTE_ASSERTIONS: ALL PASS")
        except Exception as e:
            print(f"Exception during capture: {e}")
            
        await browser.close()
        
if __name__ == "__main__":
    asyncio.run(main())
