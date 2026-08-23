import asyncio
import os
import shutil
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"
OUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_owner_review"

async def capture(page, name, viewport):
    await page.set_viewport_size(viewport)
    await asyncio.sleep(1) # wait for animations
    await page.screenshot(path=os.path.join(OUT_DIR, name), full_page=True)

async def main():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)
    
    desktop = {"width": 1920, "height": 1080}
    laptop = {"width": 1366, "height": 768}
    mobile = {"width": 390, "height": 844}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Helper to visit page
        async def visit(url):
            await page.goto(f"{BASE_URL}{url}", wait_until="networkidle")
            await asyncio.sleep(1)

        # ------------------------------------------------------------
        # 2. REQUIRED DESKTOP CAPTURES
        # ------------------------------------------------------------
        await visit("/dashboard/")
        await capture(page, "01_public_dashboard_1920.png", desktop)
        
        await visit("/dashboard/calendar/?view=month")
        await capture(page, "02_public_calendar_month_1920.png", desktop)
        
        await visit("/dashboard/calendar/?view=list")
        await capture(page, "03_public_calendar_list_1920.png", desktop)
        
        await visit("/venues/live/")
        await capture(page, "04_public_live_1920.png", desktop)
        
        response = await page.goto(f"{BASE_URL}/workspace/")
        if "login" in page.url:
            await page.fill("input[name='username']", "admin")
            await page.fill("input[name='password']", "admin")
            await page.click("button[type='submit']")
            await page.wait_for_url("**/workspace/**")

        await visit("/workspace/")
        await capture(page, "05_workspace_dashboard_1920.png", desktop)
        
        await visit("/events/")
        await capture(page, "06_events_1920.png", desktop)
        
        await visit("/calendar/")
        await capture(page, "07_workspace_calendar_1920.png", desktop)
        
        await visit("/events/approvals/")
        await capture(page, "08_approvals_1920.png", desktop)
        
        await visit("/events/rescheduled/")
        await capture(page, "09_rescheduled_1920.png", desktop)
        
        await visit("/master-data/venues/")
        await capture(page, "10_venues_1920.png", desktop)
        
        await visit("/master-data/event-types/")
        await capture(page, "11_event_types_1920.png", desktop)
        
        await visit("/master-data/organizations/")
        await capture(page, "12_organizations_1920.png", desktop)
        
        await visit("/master-data/sponsors/")
        await capture(page, "13_sponsors_1920.png", desktop)
        
        await visit("/speakers/")
        await capture(page, "14_speakers_1920.png", desktop)
        
        await visit("/leadership/")
        await capture(page, "15_leadership_1920.png", desktop)
        
        await visit("/reports/")
        await capture(page, "16_reports_1920.png", desktop)
        
        await visit("/profile/")
        await capture(page, "17_profile_1920.png", desktop)

        # ------------------------------------------------------------
        # 3. REQUIRED LAPTOP CAPTURES
        # ------------------------------------------------------------
        await visit("/dashboard/")
        await capture(page, "18_public_dashboard_1366.png", laptop)
        await visit("/dashboard/calendar/?view=month")
        await capture(page, "19_public_calendar_1366.png", laptop)
        await visit("/venues/live/")
        await capture(page, "20_public_live_1366.png", laptop)
        await visit("/workspace/")
        await capture(page, "21_workspace_dashboard_1366.png", laptop)
        await visit("/events/")
        await capture(page, "22_events_1366.png", laptop)
        await visit("/calendar/")
        await capture(page, "23_workspace_calendar_1366.png", laptop)
        await visit("/leadership/")
        await capture(page, "24_leadership_1366.png", laptop)
        await visit("/reports/")
        await capture(page, "25_reports_1366.png", laptop)

        # ------------------------------------------------------------
        # 4. REQUIRED MOBILE CAPTURES
        # ------------------------------------------------------------
        await visit("/dashboard/")
        await capture(page, "26_public_dashboard_390.png", mobile)
        await visit("/dashboard/calendar/?view=month")
        await capture(page, "27_public_calendar_390.png", mobile)
        await visit("/venues/live/")
        await capture(page, "28_public_live_390.png", mobile)
        await visit("/workspace/")
        await capture(page, "29_workspace_dashboard_390.png", mobile)
        await visit("/events/")
        await capture(page, "30_events_390.png", mobile)
        await visit("/calendar/")
        await capture(page, "31_workspace_calendar_390.png", mobile)
        await visit("/master-data/organizations/")
        await capture(page, "32_organizations_390.png", mobile)
        await visit("/leadership/")
        await capture(page, "33_leadership_390.png", mobile)
        await visit("/reports/")
        await capture(page, "34_reports_390.png", mobile)
        await visit("/profile/")
        await capture(page, "35_profile_390.png", mobile)

        # ------------------------------------------------------------
        # 5. CAPTURE IMPORTANT INTERACTION STATES
        # ------------------------------------------------------------
        await page.set_viewport_size(desktop)
        
        # 36_primary_buttons_hover.png
        await visit("/events/")
        button = await page.query_selector(".btn--primary, .btn-primary")
        if button:
            await button.hover()
            await asyncio.sleep(0.5)
        await capture(page, "36_primary_buttons_hover.png", desktop)

        # 37_event_action_menu.png
        await visit("/events/")
        dropdown = await page.query_selector(".dropdown-toggle, .action-menu-toggle, [data-bs-toggle='dropdown']")
        if dropdown:
            await dropdown.click()
            await asyncio.sleep(0.5)
        await capture(page, "37_event_action_menu.png", desktop)

        # 38_calendar_busy_day.png
        await visit("/calendar/")
        await capture(page, "38_calendar_busy_day.png", desktop)

        # 39_calendar_event_hover.png
        await visit("/calendar/")
        event = await page.query_selector(".calendar-event, .fc-event, .event-capsule")
        if event:
            await event.hover()
            await asyncio.sleep(0.5)
        await capture(page, "39_calendar_event_hover.png", desktop)

        # 40_live_room_states.png
        await visit("/venues/live/")
        await capture(page, "40_live_room_states.png", desktop)

        # 41_filters_active.png
        await visit("/events/?status=upcoming")
        await capture(page, "41_filters_active.png", desktop)

        # 42_sidebar_mobile_open.png
        await visit("/workspace/")
        await page.set_viewport_size(mobile)
        sidebar_toggle = await page.query_selector(".sidebar-toggle, .mobile-menu-btn, [data-bs-target='#sidebar'], [data-bs-toggle='offcanvas']")
        if sidebar_toggle:
            await sidebar_toggle.click()
            await asyncio.sleep(0.5)
        await page.screenshot(path=os.path.join(OUT_DIR, "42_sidebar_mobile_open.png"), full_page=True)

        # 43_public_mobile_navigation.png
        await visit("/dashboard/")
        await page.set_viewport_size(mobile)
        await page.screenshot(path=os.path.join(OUT_DIR, "43_public_mobile_navigation.png"), full_page=False)

        # 44_reports_export_menu.png
        await visit("/reports/")
        await page.set_viewport_size(desktop)
        export_btn = await page.query_selector(".btn-export, [data-bs-toggle='dropdown']")
        if export_btn:
            await export_btn.click()
            await asyncio.sleep(0.5)
        await capture(page, "44_reports_export_menu.png", desktop)

        # 45_empty_state.png
        await visit("/events/?q=xyznonexistent123")
        await capture(page, "45_empty_state.png", desktop)

        await browser.close()
        
    print(f"Screenshots captured: {len(os.listdir(OUT_DIR))}")
    for item in os.listdir(OUT_DIR):
        print(item)

if __name__ == "__main__":
    asyncio.run(main())
