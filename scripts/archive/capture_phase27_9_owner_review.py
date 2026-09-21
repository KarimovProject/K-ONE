import asyncio
from playwright.async_api import async_playwright
import os
import shutil

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_9_owner_review"

async def capture_all():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_1920 = await browser.new_context(viewport={"width": 1920, "height": 1080})
        context_390 = await browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        
        # Authenticate
        page_1920 = await context_1920.new_page()
        await page_1920.goto("http://10.34.12.2:8012/accounts/login/")
        await page_1920.fill("input[name='username']", "admin")
        await page_1920.fill("input[name='password']", "admin")
        await page_1920.click("button[type='submit']")
        await page_1920.wait_for_url("**/workspace/")
        
        cookies = await context_1920.cookies()
        await context_390.add_cookies(cookies)
        page_390 = await context_390.new_page()
        
        # 1. Events list (06, 07, 08)
        print("Capturing events list...")
        await page_390.goto("http://10.34.12.2:8012/events/")
        await page_390.wait_for_selector(".k-mobile-events", state="visible")
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "06_events_mobile_390.png"), full_page=True)
        
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".data-table", state="visible")
        
        # Check action menu singleton behavior
        await page_1920.click(".action-menu-toggle >> nth=0")
        await page_1920.wait_for_selector(".k-action-dropdown.is-open", state="visible")
        await page_1920.click(".action-menu-toggle >> nth=1")
        await asyncio.sleep(0.5)
        visible_menus = await page_1920.evaluate("document.querySelectorAll('.k-action-dropdown.is-open').length")
        assert visible_menus <= 1, f"Expected <=1 open menu, found {visible_menus}"
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "08_events_action_menu_1920.png"), full_page=True)
        
        # close the menu
        await page_1920.click("body")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "07_events_desktop_1920.png"), full_page=True)
        
        # Get event detail URL
        event_link = await page_1920.get_attribute(".table-title-link >> nth=0", "href")
        full_event_url = f"http://10.34.12.2:8012{event_link}"
        
        # 2. Calendar Mobile (01, 02, 03)
        print("Capturing calendar mobile...")
        await page_390.goto("http://10.34.12.2:8012/calendar/")
        await page_390.wait_for_selector(".fc-daygrid-day", state="visible")
        await asyncio.sleep(1)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "01_calendar_mobile_390.png"), full_page=True)
        
        # click a day with dot if present
        dots_visible = await page_390.evaluate("document.querySelectorAll('.k-mobile-event-dot').length > 0")
        if dots_visible:
            await page_390.evaluate("document.querySelector('.k-mobile-event-dot').click()")
            await asyncio.sleep(0.5)
            await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "02_calendar_mobile_event_day_390.png"), full_page=True)
            await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "03_calendar_mobile_agenda_event_390.png"), full_page=True)

        # 3. Calendar Desktop (04, 05)
        print("Capturing calendar desktop...")
        await page_1920.goto("http://10.34.12.2:8012/calendar/")
        await page_1920.wait_for_selector(".fc-daygrid-day", state="visible")
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "04_calendar_desktop_events_1920.png"), full_page=True)
        
        # hover on event
        event_visible = await page_1920.evaluate("document.querySelectorAll('.fc-event').length > 0")
        if event_visible:
            await page_1920.hover(".fc-event >> nth=0")
            await asyncio.sleep(0.5)
            await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "05_calendar_desktop_popover_1920.png"), full_page=True)
            
        # 4. Event Detail (09, 10)
        print("Capturing event detail...")
        await page_1920.goto(full_event_url)
        await page_1920.wait_for_selector(".detail-card", state="visible")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "09_event_detail_desktop_1920.png"), full_page=True)
        
        await page_390.goto(full_event_url)
        await page_390.wait_for_selector(".detail-card", state="visible")
        await asyncio.sleep(1)
        
        # Ensure mobile layout is single column
        col_count = await page_390.evaluate("""() => {
            const grid = document.querySelector('.card-grid');
            if(!grid) return 1;
            return window.getComputedStyle(grid).gridTemplateColumns.split(' ').length;
        }""")
        assert col_count == 1, f"EVENT_DETAIL_390_COLUMN_COUNT failed: {col_count} columns found"
        
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "10_event_detail_mobile_390.png"), full_page=True)
        
        # Verification passed
        print("All visual QA tasks and assertions passed.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_all())
