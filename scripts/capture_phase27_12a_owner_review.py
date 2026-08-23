import asyncio
import os
import re
from playwright.async_api import async_playwright

SCREENSHOT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_12a_owner_review"

async def ensure_dir():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def capture_all():
    await ensure_dir()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_1920 = await browser.new_context(viewport={"width": 1920, "height": 1080})
        context_390 = await browser.new_context(viewport={"width": 390, "height": 844})
        
        # Login
        page_1920 = await context_1920.new_page()
        await page_1920.goto("http://10.34.12.2:8012/accounts/login/")
        await page_1920.fill("input[name='username']", "admin")
        await page_1920.fill("input[name='password']", "admin")
        await page_1920.click("button[type='submit']")
        await page_1920.wait_for_url("**/workspace/")
        
        # Share cookies
        cookies = await context_1920.cookies()
        await context_390.add_cookies(cookies)
        
        page_390 = await context_390.new_page()

        # ==========================================
        # 1. EVENT DETAIL (1920, 390)
        # ==========================================
        print("Navigating to Event Detail...")
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".table-title-link")
        
        event_url = await page_1920.evaluate("""() => {
            const link = document.querySelector('.table-title-link');
            return link ? link.href : null;
        }""")
        
        assert event_url and "/events/" in event_url and not event_url.endswith("/events/"), "Could not find a valid event detail URL"
        
        await page_1920.goto(event_url)
        await page_1920.wait_for_selector(".page-title")
        
        # Assertions for Event Detail 1920
        assert re.search(r'/events/[a-f0-9-]+/', page_1920.url), f"URL {page_1920.url} is not an event detail route"
        title = await page_1920.locator(".page-title").text_content()
        assert title, "Event title is missing"
        
        content_1920 = await page_1920.content()
        assert "Dastur va Ommaviy Sahifa" in content_1920, "Dastur va Ommaviy Sahifa is missing"
        assert "Jadval va vaqt" in content_1920, "Jadval va vaqt is missing"
        
        # Wait for action buttons
        await page_1920.wait_for_selector(".event-detail-actions")
        await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_event_detail_desktop_1920.png"), full_page=True)

        # Event Detail 390
        await page_390.goto(event_url)
        await page_390.wait_for_selector(".page-title")
        
        assert re.search(r'/events/[a-f0-9-]+/', page_390.url), "Mobile URL is not an event detail route"
        content_390 = await page_390.content()
        assert "Dastur va Ommaviy Sahifa" in content_390, "Dastur va Ommaviy Sahifa is missing on mobile"
        assert "Jadval va vaqt" in content_390, "Jadval va vaqt is missing on mobile"
        await page_390.wait_for_selector(".event-detail-actions")
        
        # Mobile specific assertions
        mobile_assertions_passed = await page_390.evaluate("""() => {
            const container = document.querySelector('.event-detail-actions');
            if (!container) return false;
            
            let passed = true;
            const buttons = container.querySelectorAll('a, button');
            for (let btn of buttons) {
                const styles = window.getComputedStyle(btn);
                if (parseFloat(styles.height) < 44) passed = false;
                if (styles.textDecorationLine !== 'none') passed = false;
                if (btn.offsetWidth > container.offsetWidth) passed = false;
            }
            return passed;
        }""")
        assert mobile_assertions_passed, "Mobile Event Detail action buttons failed CSS constraints (height, decoration, or width)"
        
        no_overflow = await page_390.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert no_overflow, "Horizontal overflow detected on mobile event detail"
        
        await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_event_detail_mobile_390.png"), full_page=True)


        # ==========================================
        # 2. CALENDAR MOBILE STATES (390)
        # ==========================================
        print("Capturing Calendar Mobile States...")
        await page_390.goto("http://10.34.12.2:8012/calendar/")
        await asyncio.sleep(2) # wait for calendar render
        
        # Click a day with an event
        # Assuming days with events have the .has-event class or we can just click today
        await page_390.evaluate("""() => {
            const eventDays = document.querySelectorAll('.calendar-day.has-event');
            if (eventDays.length > 0) {
                eventDays[0].click();
            } else {
                const anyDay = document.querySelector('.calendar-day');
                if (anyDay) anyDay.click();
            }
        }""")
        await asyncio.sleep(1) # wait for agenda to pop up or select state
        
        is_agenda_visible = await page_390.evaluate("document.querySelector('.mobile-agenda-drawer') !== null")
        if is_agenda_visible:
            # We have a separate agenda drawer!
            await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_calendar_mobile_selected_day_390.png"), full_page=True)
            await page_390.evaluate("document.querySelector('.mobile-agenda-drawer').classList.add('open')")
            await asyncio.sleep(0.5)
            await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_calendar_mobile_agenda_390.png"), full_page=True)
        else:
            # No separate drawer, just selected state with agenda in the flow
            await page_390.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_calendar_mobile_selected_day_390.png"), full_page=True)

        
        # ==========================================
        # 3. EVENTS ACTION MENU (SINGLE OPEN CHECK)
        # ==========================================
        print("Capturing Events Action Menu...")
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".table-title-link")
        
        toggles = await page_1920.locator(".action-menu-toggle").all()
        if len(toggles) >= 2:
            await toggles[0].click()
            await asyncio.sleep(0.5)
            await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_events_action_menu_first_1920.png"), full_page=True)
            
            # Click the last toggle to avoid overlapping dropdown intercepting the click
            await toggles[-1].click()
            await asyncio.sleep(0.5)
            await page_1920.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_events_action_menu_second_1920.png"), full_page=True)
            
            # Assert only ONE is open
            open_menus = await page_1920.evaluate("document.querySelectorAll('.k-action-dropdown.is-open').length")
            assert open_menus <= 1, f"Expected max 1 open menu, found {open_menus}"


        print("Phase 27.12A QA completed successfully.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_all())
