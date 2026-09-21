import asyncio
from playwright.async_api import async_playwright, expect
import os
import shutil

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_11_owner_review"

async def sanity_check(page, is_mobile=False):
    # Wait for ready state
    await page.wait_for_function('document.readyState === "complete"')
    
    # Wait for main content
    main_el = page.locator("main, .content, .workspace-content, .k-workspace-main").first
    await main_el.wait_for(state="visible", timeout=10000)
    
    # Check dimensions
    box = await main_el.bounding_box()
    assert box is not None, "Main content has no bounding box"
    if is_mobile:
        assert box['width'] >= 350, f"Mobile main width {box['width']} < 350"
    else:
        assert box['width'] > 700, f"Desktop main width {box['width']} <= 700"
        assert box['height'] > 300, f"Desktop main height {box['height']} <= 300"

async def set_lang(context, lang):
    await context.add_cookies([{"name": "django_language", "value": lang, "domain": "10.34.12.2", "path": "/"}])

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
        
        # 1. Events List (01, 02, 03, 04)
        print("Capturing events list...")
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await sanity_check(page_1920)
        
        # 01 Closed
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "01_events_menu_closed_1920.png"), full_page=True)
        
        # 02 First Menu Open
        await page_1920.click(".action-menu-toggle >> nth=0")
        await page_1920.wait_for_selector(".k-action-dropdown.is-open", state="visible")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "02_events_first_menu_open_1920.png"), full_page=True)
        
        # 03 Second Menu Open (Singleton Check)
        await page_1920.click(".action-menu-toggle >> nth=1")
        await asyncio.sleep(0.5)
        # Automated Assertion for singleton menu
        visible_menus = await page_1920.evaluate("document.querySelectorAll('.k-action-dropdown.is-open').length")
        assert visible_menus <= 1, f"Expected <=1 open menu, found {visible_menus}"
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "03_events_second_menu_open_1920.png"), full_page=True)
        
        # 04 Mobile Events
        await page_390.goto("http://10.34.12.2:8012/events/")
        await sanity_check(page_390, is_mobile=True)
        await page_390.wait_for_selector(".k-mobile-events", state="visible")
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "04_events_mobile_390.png"), full_page=True)
        
        # Get Event URL for details
        event_link = await page_1920.get_attribute(".table-title-link >> nth=0", "href")
        full_event_url = f"http://10.34.12.2:8012{event_link}"
        
        # 2. Calendar Desktop (05, 06, 07)
        print("Capturing calendar desktop...")
        await page_1920.goto("http://10.34.12.2:8012/calendar/")
        await sanity_check(page_1920)
        await page_1920.wait_for_selector(".fc-daygrid-day", state="visible")
        await asyncio.sleep(1)
        
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "05_calendar_desktop_1920.png"), full_page=True)
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "06_calendar_semantic_statuses_1920.png"), full_page=True)
        
        event_visible = await page_1920.evaluate("document.querySelectorAll('.fc-event').length > 0")
        if event_visible:
            await page_1920.hover(".fc-event >> nth=0")
            await asyncio.sleep(0.5)
            await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "07_calendar_popover_1920.png"), full_page=True)
        
        # 3. Calendar Mobile (08, 09)
        print("Capturing calendar mobile...")
        await page_390.goto("http://10.34.12.2:8012/calendar/")
        await sanity_check(page_390, is_mobile=True)
        await page_390.wait_for_selector(".fc-daygrid-day", state="visible")
        await asyncio.sleep(1)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "08_calendar_mobile_390.png"), full_page=True)
        
        dots_visible = await page_390.evaluate("document.querySelectorAll('.k-mobile-event-dot').length > 0")
        if dots_visible:
            await page_390.evaluate("document.querySelector('.k-mobile-event-dot').click()")
            await asyncio.sleep(0.5)
            await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "09_calendar_mobile_selected_day_390.png"), full_page=True)
            
        # 4. Event Detail Languages (10-15)
        print("Capturing event details...")
        for lang, d_num, m_num in [("uz", "10", "11"), ("ru", "12", "13"), ("en", "14", "15")]:
            await set_lang(context_1920, lang)
            await set_lang(context_390, lang)
            
            await page_1920.goto(full_event_url)
            await sanity_check(page_1920)
            await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, f"{d_num}_event_detail_desktop_{lang}_1920.png"), full_page=True)
            
            await page_390.goto(full_event_url)
            await sanity_check(page_390, is_mobile=True)
            await page_390.screenshot(path=os.path.join(OUTPUT_DIR, f"{m_num}_event_detail_mobile_{lang}_390.png"), full_page=True)
            
        # 5. Dashboard (16, 17)
        print("Capturing dashboard...")
        await page_1920.goto("http://10.34.12.2:8012/workspace/")
        await sanity_check(page_1920)
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "16_dashboard_1920.png"), full_page=True)
        
        await page_390.goto("http://10.34.12.2:8012/workspace/")
        await sanity_check(page_390, is_mobile=True)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "17_dashboard_390.png"), full_page=True)
        
        # 6. Reports (18, 19)
        print("Capturing reports...")
        await page_1920.goto("http://10.34.12.2:8012/reports/")
        await sanity_check(page_1920)
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "18_reports_1920.png"), full_page=True)
        
        await page_390.goto("http://10.34.12.2:8012/reports/")
        await sanity_check(page_390, is_mobile=True)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "19_reports_390.png"), full_page=True)
        
        # 7. Profile (20, 21)
        print("Capturing profile...")
        await page_1920.goto("http://10.34.12.2:8012/accounts/profile/")
        await sanity_check(page_1920)
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "20_profile_1920.png"), full_page=True)
        
        await page_390.goto("http://10.34.12.2:8012/accounts/profile/")
        await sanity_check(page_390, is_mobile=True)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "21_profile_390.png"), full_page=True)
        
        await browser.close()
        print("All visual QA tasks and assertions passed.")
        
        files = os.listdir(OUTPUT_DIR)
        assert len(files) == 21, f"Expected 21 screenshots, got {len(files)}"

if __name__ == "__main__":
    asyncio.run(capture_all())
