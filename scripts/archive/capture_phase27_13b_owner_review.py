import asyncio
import os
import shutil
import sys
from playwright.async_api import async_playwright

SCREENSHOT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_13b_owner_review"

if os.path.exists(SCREENSHOT_DIR):
    shutil.rmtree(SCREENSHOT_DIR)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def check_response(response):
    if response.status >= 400 and response.request.resource_type == "document":
        print(f"Error: {response.url} returned {response.status}")
        sys.exit(1)

async def verify_no_login(page):
    if "/accounts/login" in page.url:
        print(f"Error: Unexpectedly redirected to login on {page.url}")
        sys.exit(1)

async def verify_overflow(page):
    overflow = await page.evaluate("() => document.documentElement.scrollWidth > window.innerWidth")
    if overflow:
        print(f"Error: Horizontal overflow detected on {page.url} at {page.viewport_size['width']}px")
        sys.exit(1)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # --- DESKTOP 1920 ---
        context_1920 = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page_1920 = await context_1920.new_page()
        page_1920.on("response", check_response)
        
        print("Logging in (Desktop)...")
        await page_1920.goto("http://127.0.0.1:8014/accounts/login/")
        await page_1920.fill("input[name='username']", "admin")
        await page_1920.fill("input[name='password']", "admin")
        await page_1920.click("button[type='submit']")
        await page_1920.wait_for_url("**/workspace/")
        cookies = await context_1920.cookies()
        
        # Event Types 1920
        await page_1920.goto("http://127.0.0.1:8014/master-data/event-types/")
        await verify_no_login(page_1920)
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_event_types_desktop_1920.png"), full_page=True)

        # Sponsors 1920
        await page_1920.goto("http://127.0.0.1:8014/master-data/sponsors/")
        await verify_no_login(page_1920)
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_sponsors_desktop_1920.png"), full_page=True)
        
        # Leadership UZ 1920
        await context_1920.add_cookies([{'name': 'django_language', 'value': 'uz', 'domain': '127.0.0.1', 'path': '/'}])
        await page_1920.goto("http://127.0.0.1:8014/leadership/")
        await verify_no_login(page_1920)
        await asyncio.sleep(1)
        
        # Assert no english strings in UZ leadership
        content = await page_1920.content()
        if "EXECUTIVE INTELLIGENCE" in content:
            print("Error: English string 'EXECUTIVE INTELLIGENCE' found in UZ mode.")
            sys.exit(1)
            
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_leadership_uz_1920.png"), full_page=True)

        # --- TABLET 768 ---
        context_768 = await browser.new_context(viewport={"width": 768, "height": 1024})
        await context_768.add_cookies(cookies)
        page_768 = await context_768.new_page()
        page_768.on("response", check_response)
        
        await page_768.goto("http://127.0.0.1:8014/master-data/event-types/")
        await verify_no_login(page_768)
        await asyncio.sleep(1)
        await verify_overflow(page_768)
        await page_768.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_event_types_tablet_768.png"), full_page=True)
        
        # --- MOBILE 390 ---
        context_390 = await browser.new_context(viewport={"width": 390, "height": 844})
        await context_390.add_cookies(cookies)
        page_390 = await context_390.new_page()
        page_390.on("response", check_response)
        
        # Event Types 390 complete card
        await page_390.goto("http://127.0.0.1:8014/master-data/event-types/")
        await verify_no_login(page_390)
        await asyncio.sleep(1)
        await verify_overflow(page_390)
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_event_types_mobile_390.png"), full_page=True)
        
        # Event Types 390 actions (ensure buttons are visible)
        actions_visible = await page_390.locator(".mobile-actions-row").first.is_visible()
        if not actions_visible:
            print("Error: .mobile-actions-row not visible on mobile!")
            sys.exit(1)
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_event_types_actions_390.png"))
        
        # Speakers 390 - Multi-Language Tests
        async def test_speakers_locale(lang_code, idx, expected_btn):
            await context_390.add_cookies([{'name': 'django_language', 'value': lang_code, 'domain': '127.0.0.1', 'path': '/'}])
            await page_390.goto("http://127.0.0.1:8014/events/speakers/")
            await verify_no_login(page_390)
            await asyncio.sleep(1)
            
            # Assert CTA plus icon
            btn_text = await page_390.locator("a[data-testid='add-speaker-btn']").inner_text()
            if btn_text.count('+') > 1:
                print(f"Error: Multiple '+' found in CTA button for {lang_code}: '{btn_text}'")
                sys.exit(1)
            if expected_btn not in btn_text:
                print(f"Error: Expected '{expected_btn}' in CTA, got '{btn_text}'")
                sys.exit(1)
                
            await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{idx}_speakers_{lang_code}_390.png"), full_page=True)

        await test_speakers_locale("uz", "07", "Ma'ruzachi qo'shish")
        await test_speakers_locale("ru", "08", "Добавить")
        await test_speakers_locale("en", "09", "New Speaker")

        # Leadership 390 - Multi-Language Tests
        async def test_leadership_locale(lang_code, idx):
            await context_390.add_cookies([{'name': 'django_language', 'value': lang_code, 'domain': '127.0.0.1', 'path': '/'}])
            await page_390.goto("http://127.0.0.1:8014/leadership/")
            await verify_no_login(page_390)
            await asyncio.sleep(1)
            await verify_overflow(page_390)
            await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{idx}_leadership_{lang_code}_390.png"), full_page=True)

        await test_leadership_locale("uz", "10")
        await test_leadership_locale("ru", "11")
        await test_leadership_locale("en", "12")
        
        print("All visual captures and assertions passed.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
