import asyncio
from playwright.async_api import async_playwright
import os
import time
import shutil

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_6_owner_review"

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
        page_1920.on("console", lambda msg: print(f"DESKTOP CONSOLE: {msg.text}"))
        page_1920.on("pageerror", lambda exc: print(f"DESKTOP ERROR: {exc}"))
        await page_1920.goto("http://10.34.12.2:8012/accounts/login/")
        await page_1920.fill("input[name='username']", "admin")
        await page_1920.fill("input[name='password']", "admin")
        await page_1920.click("button[type='submit']")
        await page_1920.wait_for_url("**/workspace/")
        
        # Transfer cookies to mobile
        cookies = await context_1920.cookies()
        await context_390.add_cookies(cookies)
        
        page_390 = await context_390.new_page()
        page_390.on("console", lambda msg: print(f"MOBILE CONSOLE: {msg.text}"))
        page_390.on("pageerror", lambda exc: print(f"MOBILE ERROR: {exc}"))
        
        # --- 01. Mobile Events List ---
        print("Capturing 01_events_mobile_390...")
        await page_390.goto("http://10.34.12.2:8012/events/")
        await page_390.wait_for_selector(".k-mobile-events", state="visible")
        
        # Assertions
        desktop_visible = await page_390.is_visible(".k-desktop-events")
        assert desktop_visible == False, "Desktop table must be hidden on mobile"
        overflow_x = await page_390.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        assert overflow_x == False, "Horizontal overflow detected on mobile events list"
        
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "01_events_mobile_390.png"), full_page=True)
        
        # --- 02. Desktop Events List ---
        print("Capturing 02_events_desktop_1920...")
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".data-table", state="visible")
        
        # Assert CTA
        cta_bg = await page_1920.evaluate("window.getComputedStyle(document.querySelector('.primary-button')).backgroundColor")
        assert cta_bg != "transparent" and cta_bg != "rgba(0, 0, 0, 0)", "Primary CTA must not be transparent"
        
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "02_events_desktop_1920.png"), full_page=True)
        
        # --- 03. Desktop Action Menu ---
        print("Capturing 03_events_action_menu_1920...")
        # Click the first toggle
        await page_1920.click(".action-menu-toggle >> nth=0")
        await page_1920.wait_for_selector(".k-action-dropdown:not([hidden])", state="visible")
        
        # Assert one dropdown only
        visible_menus = await page_1920.evaluate("document.querySelectorAll('.k-action-dropdown:not([hidden])').length")
        assert visible_menus == 1, f"Expected 1 visible menu, found {visible_menus}"
        
        # Click the second toggle
        await page_1920.click(".action-menu-toggle >> nth=1")
        await asyncio.sleep(0.5)
        visible_menus = await page_1920.evaluate("document.querySelectorAll('.k-action-dropdown:not([hidden])').length")
        assert visible_menus == 1, f"Expected 1 visible menu after second click, found {visible_menus}"
        
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "03_events_action_menu_1920.png"), full_page=True)
        
        # --- 04. Mobile Calendar ---
        print("Capturing 04_calendar_mobile_390...")
        # Go to Aug 2026 to ensure events
        await page_390.goto("http://10.34.12.2:8012/calendar/")
        await page_390.wait_for_selector(".fc-daygrid-day", state="visible")
        
        # Assertions
        cell_count = await page_390.evaluate("document.querySelectorAll('.fc-daygrid-day').length")
        assert cell_count > 28, f"Expected >28 calendar cells on mobile, found {cell_count}"
        cal_height = await page_390.evaluate("document.querySelector('.fc-view-harness').offsetHeight")
        assert cal_height > 400, f"Expected calendar height > 400px, found {cal_height}px"
        overflow_x = await page_390.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        assert overflow_x == False, "Horizontal overflow detected on mobile calendar"
        
        await asyncio.sleep(1)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "04_calendar_mobile_390.png"), full_page=True)
        
        # --- 05. Mobile Selected Day ---
        print("Capturing 05_calendar_mobile_event_day_390...")
        await page_390.wait_for_selector(".k-mobile-event-dot", state="visible", timeout=10000)
        
        # Click via JS to ensure it registers
        await page_390.evaluate('''() => {
            const dot = document.querySelector('.k-mobile-event-dot');
            const cell = dot.closest('.fc-daygrid-day');
            cell.click();
        }''')
        
        await page_390.wait_for_selector("#mobile-agenda-sheet.active", state="visible", timeout=5000)
        await asyncio.sleep(1)
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "05_calendar_mobile_event_day_390.png"), full_page=True)
        
        # --- 06. Mobile Agenda Open ---
        print("Capturing 06_calendar_mobile_agenda_event_390...")
        is_agenda_active = await page_390.evaluate("document.getElementById('mobile-agenda-sheet').classList.contains('active')")
        assert is_agenda_active == True, "Agenda sheet should be active"
        agenda_text = await page_390.inner_text(".mobile-agenda-body")
        assert "No events" not in agenda_text, "Agenda must contain events, found 'No events'"
        
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "06_calendar_mobile_agenda_event_390.png"))
        
        # --- 07. Desktop Calendar ---
        print("Capturing 07_calendar_desktop_events_1920...")
        await page_1920.goto("http://10.34.12.2:8012/calendar/")
        await page_1920.wait_for_selector(".k-event-capsule", state="visible", timeout=5000)
        
        # Assertions
        cell_count = await page_1920.evaluate("document.querySelectorAll('.fc-daygrid-day').length")
        assert cell_count > 28, f"Expected >28 calendar cells on desktop, found {cell_count}"
        capsule_count = await page_1920.evaluate("document.querySelectorAll('.k-event-capsule').length")
        assert capsule_count > 0, "No event capsules found on desktop calendar"
        
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "07_calendar_desktop_events_1920.png"), full_page=True)
        
        # --- 08. Desktop Calendar Popover ---
        print("Capturing 08_calendar_desktop_popover_1920...")
        await page_1920.hover(".k-event-capsule >> nth=0")
        await page_1920.wait_for_selector("[data-tippy-root]", state="visible")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "08_calendar_desktop_popover_1920.png"), full_page=True)
        
        # --- 09. Event Detail Mobile ---
        print("Capturing 09_event_detail_mobile_390...")
        # Get the URL from desktop context
        await page_1920.goto("http://10.34.12.2:8012/events/")
        await page_1920.wait_for_selector(".table-title-link")
        detail_url = await page_1920.get_attribute(".table-title-link", "href")
        
        await page_390.goto("http://10.34.12.2:8012" + detail_url)
        await page_390.wait_for_selector(".detail-card", state="visible")
        await page_390.screenshot(path=os.path.join(OUTPUT_DIR, "09_event_detail_mobile_390.png"), full_page=True)
        
        # --- 10. Event Detail Desktop ---
        print("Capturing 10_event_detail_desktop_1920...")
        await page_1920.goto("http://10.34.12.2:8012" + detail_url)
        await page_1920.wait_for_selector(".detail-card", state="visible")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "10_event_detail_desktop_1920.png"), full_page=True)
        
        # --- 11. Event Detail Print Menu (or another requested state) ---
        # The user requested 11 screenshots. Let's capture the hover state on desktop action button or similar.
        print("Capturing 11_event_detail_actions_1920...")
        await page_1920.hover(".btn-ghost")
        await page_1920.screenshot(path=os.path.join(OUTPUT_DIR, "11_event_detail_actions_1920.png"), full_page=True)
        
        print(f"Captured {len(os.listdir(OUTPUT_DIR))} screenshots successfully in {OUTPUT_DIR}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_all())
