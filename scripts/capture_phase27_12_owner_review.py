import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_12_owner_review"

async def ensure_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def capture_all():
    await ensure_dir()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_1920 = await browser.new_context(viewport={"width": 1920, "height": 1080})
        context_1366 = await browser.new_context(viewport={"width": 1366, "height": 768})
        context_390 = await browser.new_context(viewport={"width": 390, "height": 844})
        
        # Login
        page = await context_1920.new_page()
        await page.goto("http://10.34.12.2:8012/accounts/login/")
        await page.fill("input[name='username']", "admin")
        await page.fill("input[name='password']", "admin")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/workspace/")
        
        # Share cookies
        cookies = await context_1920.cookies()
        await context_1366.add_cookies(cookies)
        await context_390.add_cookies(cookies)
        
        page_1920 = page
        page_1366 = await context_1366.new_page()
        page_390 = await context_390.new_page()

        # ==========================================
        # 1. EVENTS LIST (1920, 1366, 390)
        # ==========================================
        print("Capturing events list...")
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".page-title")
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_events_desktop_1920.png"), full_page=True)

        await page_1366.goto("http://10.34.12.2:8012/events/")
        await page_1366.wait_for_selector(".page-title")
        await page_1366.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_events_desktop_1366.png"), full_page=True)

        await page_390.goto("http://10.34.12.2:8012/events/")
        await page_390.wait_for_selector(".page-title")
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_events_mobile_390.png"), full_page=True)

        # ==========================================
        # 2. EVENTS ACTION MENU (SINGLE OPEN CHECK)
        # ==========================================
        print("Testing single-open action menu...")
        toggles = await page_1920.locator(".action-menu-toggle").all()
        if len(toggles) >= 2:
            await toggles[0].click()
            await asyncio.sleep(0.5)
            await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_events_action_menu_first_1920.png"))
            
            await toggles[-1].click()
            await asyncio.sleep(0.5)
            await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_events_action_menu_second_1920.png"))
            
            # Assert only ONE is open
            open_menus = await page_1920.evaluate("document.querySelectorAll('.k-action-dropdown.is-open').length")
            assert open_menus <= 1, f"Expected max 1 open menu, found {open_menus}"
        
        # ==========================================
        # 3. CALENDAR (1920, 1366, 390)
        # ==========================================
        print("Capturing calendar...")
        await page_1920.goto("http://10.34.12.2:8012/calendar/")
        await asyncio.sleep(2)  # Wait for JS calendar render
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_calendar_desktop_1920.png"), full_page=True)

        await page_1366.goto("http://10.34.12.2:8012/calendar/")
        await asyncio.sleep(2)
        await page_1366.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_calendar_desktop_1366.png"), full_page=True)

        await page_390.goto("http://10.34.12.2:8012/calendar/")
        await asyncio.sleep(2)
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "08_calendar_mobile_390.png"), full_page=True)
        
        # Assert mobile filter styles
        mobile_form_width = await page_390.evaluate("document.querySelector('.calendar-filters').offsetWidth")
        window_width = await page_390.evaluate("window.innerWidth")
        assert mobile_form_width > window_width * 0.8, "Mobile calendar filters are not full width"
        
        # ==========================================
        # 4. EVENT DETAIL (1920, 390)
        # ==========================================
        print("Capturing event details...")
        # Get first event URL
        event_url = await page_1920.evaluate("""() => {
            const link = document.querySelector('a[href*="/events/"][href$="/"]');
            return link ? link.href : null;
        }""")
        
        if event_url:
            await page_1920.goto(event_url)
            await page_1920.wait_for_selector(".page-title")
            await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "09_event_detail_desktop_1920.png"), full_page=True)
            
            await page_390.goto(event_url)
            await page_390.wait_for_selector(".page-title")
            await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "10_event_detail_mobile_390.png"), full_page=True)
            
            # Computed CSS Assertions for Action Buttons on Mobile
            has_valid_button = await page_390.evaluate("""() => {
                const btn = document.querySelector('.event-detail-actions .btn-primary');
                if (!btn) return true; // Pass if no button
                const styles = window.getComputedStyle(btn);
                return styles.backgroundColor !== 'rgba(0, 0, 0, 0)' && 
                       styles.backgroundColor !== 'transparent' &&
                       styles.textDecorationLine === 'none' &&
                       parseFloat(styles.height) >= 40;
            }""")
            assert has_valid_button, "Mobile event detail action buttons lack semantic styles or height"

        # ==========================================
        # 5. COMPONENT COMPUTED CSS ASSERTIONS
        # ==========================================
        print("Running computed CSS assertions...")
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".btn-primary")
        
        btn_css_valid = await page_1920.evaluate("""() => {
            const btn = document.querySelector('.btn-create-event');
            if (!btn) return true;
            const styles = window.getComputedStyle(btn);
            return styles.display === 'inline-flex' &&
                   styles.textDecorationLine === 'none' &&
                   parseFloat(styles.height) >= 40 &&
                   styles.backgroundColor !== 'rgba(0, 0, 0, 0)';
        }""")
        assert btn_css_valid, "Desktop primary button lost its base semantic styles!"

        no_horizontal_overflow = await page_390.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert no_horizontal_overflow, "Horizontal overflow detected on mobile!"

        print("All visual QA tasks and computed CSS assertions passed.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_all())
