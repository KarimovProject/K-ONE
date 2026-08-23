import asyncio
import os
import shutil
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"
OUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_5_owner_review"

desktop = {"width": 1920, "height": 1080}
mobile = {"width": 390, "height": 844}

async def capture(page, name):
    await asyncio.sleep(1)
    await page.screenshot(path=os.path.join(OUT_DIR, name), full_page=True)
    print(f"[OK] {name}")

async def main():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"BROWSER ERROR: {exc}"))

        # Login
        await page.goto(f"{BASE_URL}/accounts/login/")
        await page.fill("input[name='username']", "admin")
        await page.fill("input[name='password']", "admin")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/workspace/")
        print("Authenticating... OK")

        try:
            # 1. Mobile Events Cards (01_events_mobile_cards_390.png)
            await page.set_viewport_size(mobile)
            response = await page.goto(f"{BASE_URL}/events/", wait_until="networkidle")
            await asyncio.sleep(2)
            await page.screenshot(path=os.path.join(OUT_DIR, "debug_events_loaded.png"))
            
            print(f"Events page status: {response.status if response else 'None'}")
            print(f"Events page HTML: {(await page.content())[:200]}")
            
            desktop_table = await page.query_selector(".k-desktop-events")
            desktop_visible = await desktop_table.is_visible() if desktop_table else False
            
            mobile_list = await page.query_selector(".k-mobile-events")
            mobile_visible = await mobile_list.is_visible() if mobile_list else False
            
            cards = await page.query_selector_all(".mobile-event-card")
            
            if not desktop_table and not mobile_list:
                await page.screenshot(path=os.path.join(OUT_DIR, "debug_events_error.png"))
                raise Exception(f"Neither desktop nor mobile events found! URL: {page.url} HTML snippet: " + (await page.content())[:500])
                
            if desktop_visible: raise Exception("Desktop table is visible on mobile!")
            if not mobile_visible: raise Exception("Mobile event list is not visible!")
            if len(cards) == 0: raise Exception("No mobile cards found!")
            
            box = await cards[0].bounding_box()
            if box["width"] < 340: raise Exception("Card width is too narrow!")
            
            await capture(page, "01_events_mobile_cards_390.png")

            # 2. Workspace Calendar Mobile Clean (02_workspace_calendar_mobile_clean_390.png)
            await page.goto(f"{BASE_URL}/calendar/", wait_until="networkidle")
            
            capsule_titles = await page.query_selector_all(".k-event-capsule__title")
            for t in capsule_titles:
                if await t.is_visible():
                    raise Exception("Full event titles are visible inside month cells at 390px!")
            
            # 1. Events Mobile (06_events_mobile_390.png)
            await page.set_viewport_size({"width": 390, "height": 844})
            await page.goto(f"{BASE_URL}/events/", wait_until="networkidle")
            await capture(page, "06_events_mobile_390.png")

            # 2. Workspace Calendar Mobile Clean (01_calendar_mobile_390.png)
            await page.goto(f"{BASE_URL}/calendar/", wait_until="networkidle")
            
            # Wait for FullCalendar to initialize
            await page.wait_for_selector('.fc-daygrid-day', timeout=10000)
            await asyncio.sleep(2)
            await capture(page, "01_calendar_mobile_390.png")

            # 3. & 4. Mobile Selected Day Agenda (02_calendar_mobile_event_day_390.png, 03_calendar_mobile_agenda_event_390.png)
            day_with_dot = None
            for _ in range(12):
                day_with_dot = await page.query_selector(".k-mobile-event-dot")
                if day_with_dot:
                    break
                next_btn = await page.query_selector(".cmd-next")
                if next_btn:
                    await next_btn.click(force=True)
                await asyncio.sleep(1)
                
            if not day_with_dot:
                cal_html = await page.evaluate("() => document.getElementById('calendar-container').innerHTML")
                print(f"Calendar HTML snippet: {cal_html[:2000]}")
                await page.screenshot(path=os.path.join(OUT_DIR, "debug_cal_fail.png"))
                raise Exception("No events found in mobile calendar to click!")
                
            # Instead of clicking the cell which might not trigger, click the event dot directly!
            # Use evaluate to bypass any viewport scrolling issues on mobile
            await day_with_dot.evaluate("el => el.click()")
            await asyncio.sleep(1)
            await capture(page, "02_calendar_mobile_event_day_390.png")
            
            agenda = await page.wait_for_selector("#mobile-agenda-sheet.active", state="visible")
            if not agenda:
                raise Exception("Agenda sheet didn't open correctly!")
            
            await capture(page, "03_calendar_mobile_agenda_event_390.png")
            
            # Close agenda
            await page.click("#btn-close-agenda")
            await asyncio.sleep(0.5)

            # 5. Calendar Desktop (04_calendar_desktop_events_1920.png)
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await asyncio.sleep(1) # wait for resize
            
            capsules = []
            for _ in range(12):
                capsules = await page.query_selector_all(".k-event-capsule")
                if len(capsules) > 0:
                    break
                next_btn = await page.query_selector(".cmd-next")
                if next_btn:
                    await next_btn.click(force=True)
                await asyncio.sleep(1)
                
            if len(capsules) == 0:
                raise Exception("No desktop capsules found!")
                
            await capture(page, "04_calendar_desktop_events_1920.png")

            # 6. Calendar Event Popover (05_calendar_desktop_popover_1920.png)
            # Find the first .fc-event that contains a .k-event-capsule
            first_event = await page.evaluate_handle('''() => {
                const capsule = document.querySelector('.k-event-capsule');
                return capsule ? capsule.closest('.fc-event') : null;
            }''')
            if first_event:
                is_null = await first_event.evaluate("el => el === null")
                if not is_null:
                    # Use evaluate to dispatch mouseenter, bypassing Playwright visibility checks
                    await first_event.evaluate("el => el.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}))")
                    tippy = await page.wait_for_selector(".tippy-box", state="visible", timeout=3000)
                    if not tippy:
                        raise Exception("Tippy popover did not appear!")
                else:
                    raise Exception("No fc-events found to hover!")
            else:
                raise Exception("No fc-events found to hover!")

            await asyncio.sleep(1)
            await capture(page, "05_calendar_desktop_popover_1920.png")

            # 7. Events Desktop (07_events_desktop_1920.png)
            await page.goto(f"{BASE_URL}/events/", wait_until="networkidle")
            await asyncio.sleep(1)
            
            is_premium = await page.is_visible(".premium-grid")
            if not is_premium:
                raise Exception("Premium grid not visible!")
                
            await capture(page, "07_events_desktop_1920.png")

            # 8. Single Action Menu (08_events_action_menu_1920.png)
            toggles = await page.query_selector_all(".action-menu-toggle")
            if len(toggles) < 2:
                raise Exception("Need at least 2 events to test action menus!")
                
            await toggles[0].click(force=True)
            await asyncio.sleep(0.5)
            await toggles[1].click(force=True)
            await asyncio.sleep(0.5)
            
            open_menus = await page.query_selector_all(".k-action-dropdown:not([hidden])")
            if len(open_menus) > 1:
                raise Exception(f"Failed! Found {len(open_menus)} action menus open simultaneously!")
                
            await capture(page, "08_events_action_menu_1920.png")
            
            print("ALL ASSERTIONS PASSED")
            print("PHASE 27.5 CAPTURE COMPLETE")

        except Exception as e:
            err_msg = repr(e).encode('ascii', 'replace').decode('ascii')
            print(f"[FAIL] Assertion failed: {err_msg}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
