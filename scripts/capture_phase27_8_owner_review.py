import asyncio
from playwright.async_api import async_playwright
import os
import shutil

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_8_owner_review"

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
        
        # We need the event detail link
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".data-table", state="visible")
        event_link = await page_1920.get_attribute(".table-title-link >> nth=0", "href")
        full_event_url = f"http://10.34.12.2:8012{event_link}"
        
        # Capture 15, 16, 17 (Events)
        print("Capturing events...")
        await page_390.goto("http://10.34.12.2:8012/events/")
        await page_390.wait_for_selector(".k-mobile-events", state="visible")
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "15_events_mobile_390.png"), full_page=True)
        
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "16_events_desktop_1920.png"), full_page=True)
        
        await page_1920.click(".action-menu-toggle >> nth=0")
        await page_1920.wait_for_selector(".k-action-dropdown.is-open", state="visible")
        await page_1920.click(".action-menu-toggle >> nth=1")
        await asyncio.sleep(0.5)
        visible_menus = await page_1920.evaluate("document.querySelectorAll('.k-action-dropdown.is-open').length")
        assert visible_menus <= 1, f"Expected <=1 open menu, found {visible_menus}"
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "17_events_single_action_menu_1920.png"), full_page=True)
        
        # Capture 12, 13, 14 (Calendar)
        print("Capturing calendar...")
        await page_390.goto("http://10.34.12.2:8012/calendar/")
        await page_390.wait_for_selector(".fc-daygrid-day", state="visible")
        await asyncio.sleep(1)
        
        dots_visible = await page_390.evaluate("document.querySelectorAll('.k-mobile-event-dot').length > 0")
        assert dots_visible, "CALENDAR_MOBILE_DOTS_VISIBLE failed"
        
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "12_calendar_mobile_390.png"), full_page=True)
        
        # click a day with dot
        await page_390.evaluate("document.querySelector('.k-mobile-event-dot').click()")
        await page_390.wait_for_selector(".fc-day-today", state="visible")
        await asyncio.sleep(0.5)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "13_calendar_mobile_agenda_390.png"), full_page=True)
        
        await page_1920.goto("http://10.34.12.2:8012/calendar/")
        await page_1920.wait_for_selector(".fc-daygrid-day", state="visible")
        await asyncio.sleep(1)
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "14_calendar_desktop_1920.png"), full_page=True)
        
        # Capture Event Detail Mobile (01-04)
        print("Capturing event detail mobile...")
        await page_390.goto(full_event_url)
        await page_390.wait_for_selector(".detail-card", state="visible")
        await asyncio.sleep(1) # let fonts load
        
        # OVERFLOW QA
        overflow_x = await page_390.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        assert overflow_x == False, "DOCUMENT_HORIZONTAL_OVERFLOW detected"
        
        col_count = await page_390.evaluate("""() => {
            const grid = document.querySelector('.card-grid');
            if(!grid) return 1;
            return window.getComputedStyle(grid).gridTemplateColumns.split(' ').length;
        }""")
        assert col_count == 1, f"EVENT_DETAIL_390_COLUMN_COUNT failed: {col_count} columns found"
        
        overflowing_children = await page_390.evaluate("""() => {
            const viewportWidth = window.innerWidth;
            const cards = document.querySelectorAll('.detail-card');
            let errors = [];
            for (const card of cards) {
                const children = card.querySelectorAll('*');
                for (const child of children) {
                    const rect = child.getBoundingClientRect();
                    if (rect.width === 0 && rect.height === 0) continue;
                    if (child.tagName === 'STYLE' || child.tagName === 'SCRIPT') continue;
                    
                    if (rect.left < -1 || rect.right > viewportWidth + 1 || rect.width > viewportWidth + 1) {
                        errors.push(child.tagName + '.' + child.className + ': ' + child.textContent.substring(0,20));
                    }
                }
            }
            return errors;
        }""")
        assert len(overflowing_children) == 0, f"EVENT_DETAIL_390_CHILD_OVERFLOW failed: {overflowing_children}"
        
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "01_event_detail_mobile_top_390.png"))
        await page_390.evaluate("window.scrollBy(0, window.innerHeight)")
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "02_event_detail_mobile_middle_390.png"))
        await page_390.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "03_event_detail_mobile_bottom_390.png"))
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "04_event_detail_mobile_full_390.png"), full_page=True)
        
        # Capture Event Detail Desktop (05)
        print("Capturing event detail desktop...")
        await page_1920.goto(full_event_url)
        await page_1920.wait_for_selector(".detail-card", state="visible")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "05_event_detail_desktop_1920.png"), full_page=True)
        
        # Localization Checks (06-11)
        print("Capturing localizations...")
        languages = {'uz': ('06_event_detail_uz_390.png', '09_event_detail_uz_1920.png'),
                     'ru': ('07_event_detail_ru_390.png', '10_event_detail_ru_1920.png'),
                     'en': ('08_event_detail_en_390.png', '11_event_detail_en_1920.png')}
                     
        for lang, (mob_img, desk_img) in languages.items():
            await context_390.clear_cookies()
            await context_1920.clear_cookies()
            
            # set cookie
            await context_390.add_cookies([{"name": "django_language", "value": lang, "domain": "10.34.12.2", "path": "/"}])
            await context_1920.add_cookies([{"name": "django_language", "value": lang, "domain": "10.34.12.2", "path": "/"}])
            
            # also authenticate again since clear_cookies removes session
            await page_1920.goto("http://10.34.12.2:8012/accounts/login/")
            if await page_1920.is_visible("input[name='username']"):
                await page_1920.fill("input[name='username']", "admin")
                await page_1920.fill("input[name='password']", "admin")
                await page_1920.click("button[type='submit']")
                await page_1920.wait_for_url("**/workspace/")
            
            cookies = await context_1920.cookies()
            # re-add django_language just in case login cleared it
            cookies.append({"name": "django_language", "value": lang, "domain": "10.34.12.2", "path": "/"})
            await context_390.add_cookies(cookies)
            await context_1920.add_cookies(cookies)
            
            cache_bust_url = full_event_url + f"?t={lang}"
            await page_390.goto(cache_bust_url)
            await page_390.wait_for_selector(".detail-card", state="visible")
            await page_390.screenshot(path=os.path.join(OUTPUT_DIR, mob_img), full_page=True)
            
            await page_1920.goto(cache_bust_url)
            await page_1920.wait_for_selector(".detail-card", state="visible")
            await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, desk_img), full_page=True)
            
            text = await page_1920.evaluate("document.body.innerText")
            text = text.lower()
            if lang == 'uz':
                assert 'program mode' not in text, "UZ_STATIC_ENGLISH_LABEL_COUNT failed (Program Mode found)"
                assert 'dastur rejimi' in text, "UZ_STATIC_ENGLISH_LABEL_COUNT failed (Dastur rejimi missing)"
            elif lang == 'ru':
                assert 'dastur rejimi' not in text, "RU_HARDCODED_UZBEK_LABEL_COUNT failed (Dastur rejimi found in RU)"
            elif lang == 'en':
                assert 'dastur rejimi' not in text, "EN localization failed (UZ text found)"
        
        await browser.close()
        print(f"Captured 17 screenshots successfully in {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(capture_all())
