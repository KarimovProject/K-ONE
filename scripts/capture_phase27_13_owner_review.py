import asyncio
import os
import subprocess
from playwright.async_api import async_playwright

SCREENSHOT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_13_owner_review"

async def ensure_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def capture_all():
    await ensure_dir()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # ----------------------------------------------------
        # 1. Desktop Tests (1920x1080)
        # ----------------------------------------------------
        context_1920 = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page_1920 = await context_1920.new_page()
        
        print("Logging in...")
        await page_1920.goto("http://10.34.12.2:8012/accounts/login/")
        await page_1920.fill("input[name='username']", "admin")
        await page_1920.fill("input[name='password']", "admin")
        await page_1920.click("button[type='submit']")
        await page_1920.wait_for_url("**/workspace/")
        
        print("Visiting Event Types...")
        await page_1920.goto("http://10.34.12.2:8012/master-data/event-types/")
        await asyncio.sleep(2)
        
        # Open action menu
        await page_1920.evaluate("""() => {
            const toggles = document.querySelectorAll('.dropdown-toggle');
            if (toggles.length > 0) {
                toggles[0].click();
            }
        }""")
        await asyncio.sleep(1)
        
        # Assertions
        open_menus = await page_1920.evaluate("document.querySelectorAll('.premium-dropdown-menu.is-open').length")
        assert open_menus <= 1, f"Expected at most 1 open menu, found {open_menus}"
        
        no_overflow = await page_1920.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert no_overflow, "Horizontal overflow detected!"
        
        # Capture Event Types List
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_event_types_desktop_1920.png"), full_page=True)

        print("Visiting Organizations (Sponsors)...")
        await page_1920.goto("http://10.34.12.2:8012/organizations/sponsors/")
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_sponsors_desktop_1920.png"), full_page=True)

        # ----------------------------------------------------
        # 2. Tablet Tests (768x1024)
        # ----------------------------------------------------
        context_768 = await browser.new_context(viewport={"width": 768, "height": 1024})
        page_768 = await context_768.new_page()
        await page_768.goto("http://10.34.12.2:8012/master-data/event-types/")
        await asyncio.sleep(1)
        await page_768.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_event_types_tablet_768.png"), full_page=True)

        # ----------------------------------------------------
        # 3. Mobile Tests (390x844)
        # ----------------------------------------------------
        context_390 = await browser.new_context(viewport={"width": 390, "height": 844})
        page_390 = await context_390.new_page()
        
        # Pass login state by re-using cookies? Or just login again
        cookies = await context_1920.cookies()
        await context_390.add_cookies(cookies)
        
        await page_390.goto("http://10.34.12.2:8012/master-data/event-types/")
        await asyncio.sleep(2)
        
        no_overflow_mobile = await page_390.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert no_overflow_mobile, "Horizontal overflow detected on mobile!"

        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_event_types_mobile_390.png"), full_page=True)
        
        print("Visiting Speakers...")
        await page_390.goto("http://10.34.12.2:8012/events/speakers/")
        await asyncio.sleep(1)
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_speakers_mobile_390.png"), full_page=True)

        await browser.close()
        print("All visual captures and assertions passed.")

if __name__ == "__main__":
    asyncio.run(capture_all())
