import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_12b_owner_review"

async def ensure_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def capture_all():
    await ensure_dir()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_390 = await browser.new_context(viewport={"width": 390, "height": 844})
        
        # Login
        page_390 = await context_390.new_page()
        await page_390.goto("http://10.34.12.2:8012/accounts/login/")
        await page_390.fill("input[name='username']", "admin")
        await page_390.fill("input[name='password']", "admin")
        await page_390.click("button[type='submit']")
        await page_390.wait_for_url("**/workspace/")
        
        # ==========================================
        # 1. CALENDAR MOBILE STATES (390)
        # ==========================================
        print("Navigating to Calendar...")
        await page_390.goto("http://10.34.12.2:8012/calendar/")
        await asyncio.sleep(2) # wait for calendar render
        await page_390.wait_for_selector(".fc-daygrid-day")
        
        # Identify a day that actually has one or more events
        print("Clicking a populated day...")
        await page_390.evaluate("""() => {
            const eventDots = document.querySelectorAll('.k-mobile-event-dot');
            if (eventDots.length > 0) {
                const dayCell = eventDots[0].closest('.fc-daygrid-day');
                if (dayCell) dayCell.click();
            } else {
                // If no event found, just click the first day (but we assert it has events later!)
                const dayCell = document.querySelector('.fc-daygrid-day[data-date]');
                if (dayCell) dayCell.click();
            }
        }""")
        
        await asyncio.sleep(1) # wait for agenda to pop up or transition
        
        print("Asserting mobile agenda state...")
        # assert populated day selected & selected-day class/state exists
        is_active = await page_390.evaluate("document.getElementById('mobile-agenda-sheet').classList.contains('active')")
        assert is_active, "Selected-day agenda sheet did not become active/visible!"
        
        # assert agenda container visible
        is_visible = await page_390.is_visible("#mobile-agenda-sheet.active")
        assert is_visible, "Agenda container is not visible on screen!"
        
        # assert at least one real event title is visible inside
        visible_text = await page_390.locator("#mobile-agenda-body").text_content()
        assert visible_text and len(visible_text.strip()) > 0, "Agenda contains no text or is empty"
        assert "No events for this day" not in visible_text, "Agenda did not load events! The clicked day had no events."
        
        # no horizontal overflow
        no_overflow = await page_390.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert no_overflow, "Horizontal overflow detected in calendar mobile state"

        # Capture complete state
        # The user said: "If the agenda is below the fold rather than a bottom sheet, scroll it into view before capture."
        await page_390.evaluate("""() => {
            const sheet = document.getElementById('mobile-agenda-sheet');
            sheet.scrollIntoView({behavior: 'instant', block: 'end'});
        }""")
        await asyncio.sleep(0.5)
        
        print("Capturing screenshots...")
        # Since the sheet is an overlay or appended element, capturing full_page will capture it
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_calendar_mobile_selected_day_390.png"), full_page=True)
        # We provide a second screenshot in case it's slightly different or required
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_calendar_mobile_agenda_390.png"), full_page=True)

        print("Phase 27.12B QA completed successfully.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_all())
