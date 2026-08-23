import asyncio
from playwright.async_api import async_playwright
import os
import shutil

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_7_owner_review"

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
        
        # 01
        print("Capturing 01_events_mobile_390...")
        await page_390.goto("http://10.34.12.2:8012/events/")
        await page_390.wait_for_selector(".k-mobile-events", state="visible")
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "01_events_mobile_390.png"), full_page=True)
        
        # 02
        print("Capturing 02_events_desktop_1920...")
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".data-table", state="visible")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "02_events_desktop_1920.png"), full_page=True)
        
        # 03
        print("Capturing 03_events_single_action_menu_1920...")
        await page_1920.click(".action-menu-toggle >> nth=0")
        await page_1920.wait_for_selector(".k-action-dropdown.is-open", state="visible")
        await page_1920.click(".action-menu-toggle >> nth=1")
        await asyncio.sleep(0.5)
        visible_menus = await page_1920.evaluate("document.querySelectorAll('.k-action-dropdown.is-open').length")
        assert visible_menus == 1, f"Expected 1 open menu, found {visible_menus}"
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "03_events_single_action_menu_1920.png"), full_page=True)
        
        event_link = await page_1920.get_attribute(".table-title-link >> nth=0", "href")
        
        # 04
        print("Capturing 04_calendar_mobile_390...")
        await page_390.goto("http://10.34.12.2:8012/calendar/")
        await page_390.wait_for_selector(".fc-daygrid-day", state="visible")
        await asyncio.sleep(1)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "04_calendar_mobile_390.png"), full_page=True)
        
        # 05 & 06
        print("Capturing 05/06 calendar mobile...")
        await page_390.evaluate("document.querySelector('.k-mobile-event-dot').click()")
        await page_390.wait_for_selector(".fc-day-today", state="visible")
        await asyncio.sleep(0.5)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "05_calendar_mobile_event_day_390.png"))
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "06_calendar_mobile_agenda_390.png"), full_page=True)
        
        # 07
        print("Capturing 07_calendar_desktop_1920...")
        await page_1920.goto("http://10.34.12.2:8012/calendar/")
        await page_1920.wait_for_selector(".fc-daygrid-day", state="visible")
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "07_calendar_desktop_1920.png"), full_page=True)
        
        # 08
        print("Capturing 08_calendar_desktop_overflow_1920...")
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "08_calendar_desktop_overflow_1920.png"), full_page=True)
        
        # 09 & 10
        print("Capturing event detail mobile...")
        full_event_url = f"http://10.34.12.2:8012{event_link}"
        await page_390.goto(full_event_url)
        await page_390.wait_for_selector(".detail-card", state="visible")
        
        overflow_x = await page_390.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        assert overflow_x == False, "Horizontal overflow detected on mobile event detail"
        
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "09_event_detail_mobile_top_390.png"))
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "10_event_detail_mobile_full_390.png"), full_page=True)
        
        # 11 & 12
        print("Capturing event detail desktop...")
        await page_1920.goto(full_event_url)
        await page_1920.wait_for_selector(".detail-card", state="visible")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "11_event_detail_desktop_1920.png"), full_page=True)
        
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "12_event_detail_actions_1920.png"), full_page=True)
        
        await browser.close()
        print(f"Captured 12 screenshots successfully in {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(capture_all())
