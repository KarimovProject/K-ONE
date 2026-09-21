import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_13a_owner_review"

async def ensure_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def check_response(response):
    if response.status >= 400:
        if "/i18n/setlang/" not in response.url:
            raise Exception(f"HTTP Error {response.status} on {response.url}")

async def verify_no_login(page):
    is_login = await page.evaluate("document.querySelector('input[name=\"username\"]') !== null")
    if is_login:
        raise Exception(f"Unexpected login page on {page.url}")

async def verify_overflow(page):
    overflow = await page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
    if overflow:
        raise Exception(f"Horizontal overflow detected on {page.url}")

async def verify_dropdowns(page):
    open_menus = await page.evaluate("document.querySelectorAll('.premium-dropdown-menu.is-open, .k-action-dropdown.is-open').length")
    if open_menus > 1:
        raise Exception(f"Multiple dropdowns open simultaneously on {page.url}")

async def capture_all():
    await ensure_dir()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Desktop Context
        context_1920 = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page_1920 = await context_1920.new_page()
        page_1920.on("response", check_response)
        
        print("Logging in (Desktop)...")
        await page_1920.goto("http://127.0.0.1:8013/accounts/login/")
        await page_1920.fill("input[name='username']", "admin")
        await page_1920.fill("input[name='password']", "admin")
        await page_1920.click("button[type='submit']")
        await page_1920.wait_for_url("**/workspace/")
        cookies = await context_1920.cookies()
        
        # Event Types Desktop
        await page_1920.goto("http://127.0.0.1:8013/master-data/event-types/")
        await verify_no_login(page_1920)
        await asyncio.sleep(2)
        
        has_active = await page_1920.evaluate("document.querySelectorAll('.status-badge.active').length > 0")
        has_inactive = await page_1920.evaluate("document.querySelectorAll('.status-badge.is-inactive').length > 0")
        if not (has_active or has_inactive):
            print("Warning: Missing active/inactive status badges, verify if seed data has them.")
            
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_event_types_desktop_statuses_1920.png"), full_page=True)
        
        # Open dropdown
        await page_1920.evaluate("""() => {
            const toggles = document.querySelectorAll('.dropdown-toggle');
            if (toggles.length > 0) toggles[0].click();
        }""")
        await asyncio.sleep(1)
        await verify_dropdowns(page_1920)
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_event_types_desktop_dropdown_1920.png"), full_page=True)

        # Sponsors Desktop
        await page_1920.goto("http://127.0.0.1:8013/master-data/sponsors/")
        await verify_no_login(page_1920)
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_sponsors_desktop_1920.png"), full_page=True)
        
        # Rahbariyat Desktop
        await page_1920.goto("http://127.0.0.1:8013/leadership/")
        await verify_no_login(page_1920)
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_leadership_desktop_1920.png"), full_page=True)

        # 2. Tablet Context
        context_768 = await browser.new_context(viewport={"width": 768, "height": 1024})
        await context_768.add_cookies(cookies)
        page_768 = await context_768.new_page()
        page_768.on("response", check_response)
        
        await page_768.goto("http://127.0.0.1:8013/master-data/event-types/")
        await verify_no_login(page_768)
        await asyncio.sleep(1)
        await page_768.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_event_types_tablet_768.png"), full_page=True)

        # 3. Mobile Context
        context_390 = await browser.new_context(viewport={"width": 390, "height": 844})
        await context_390.add_cookies(cookies)
        page_390 = await context_390.new_page()
        page_390.on("response", check_response)
        
        # Event Types Mobile
        await page_390.goto("http://127.0.0.1:8013/master-data/event-types/")
        await verify_no_login(page_390)
        await asyncio.sleep(1)
        await verify_overflow(page_390)
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_event_types_mobile_390.png"), full_page=True)
        
        await page_390.evaluate("""() => {
            const toggles = document.querySelectorAll('.dropdown-toggle');
            if (toggles.length > 0) toggles[0].click();
        }""")
        await asyncio.sleep(1)
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_event_types_mobile_dropdown_390.png"), full_page=True)
        
        # Speakers Mobile Localization Tests
        async def test_speakers_locale(lang_code):
            print(f"Setting language to {lang_code}")
            # Ensure cookie is set
            await context_390.add_cookies([{
                'name': 'django_language',
                'value': lang_code,
                'domain': '127.0.0.1',
                'path': '/'
            }])
            
            await page_390.goto("http://127.0.0.1:8013/events/speakers/")
            await verify_no_login(page_390)
            await asyncio.sleep(1)
            
            # Assert translated strings
            text_content = await page_390.content()
            if lang_code == "uz":
                if "Manage keynote speakers" in text_content:
                    raise Exception("Found untranslated English string 'Manage keynote speakers' in UZ locale")
                if "New Speaker" in text_content:
                    raise Exception("Found untranslated English string 'New Speaker' in UZ locale")
                    
            await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, f"08_speakers_{lang_code}_mobile_390.png"), full_page=True)

        await test_speakers_locale("uz")
        await test_speakers_locale("ru")
        await test_speakers_locale("en")

        # Rahbariyat Mobile
        await page_390.goto("http://127.0.0.1:8013/leadership/")
        await verify_no_login(page_390)
        await asyncio.sleep(1)
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "09_leadership_mobile_390.png"), full_page=True)

        await browser.close()
        print("All visual captures and assertions passed.")

if __name__ == "__main__":
    asyncio.run(capture_all())
