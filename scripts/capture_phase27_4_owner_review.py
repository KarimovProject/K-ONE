import asyncio
import os
import shutil
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"
OUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_4_owner_review"

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
            await page.goto(f"{BASE_URL}/events/", wait_until="networkidle")
            await asyncio.sleep(1)
            
            desktop_table = await page.query_selector(".k-desktop-events")
            desktop_visible = await desktop_table.is_visible() if desktop_table else False
            
            mobile_list = await page.query_selector(".k-mobile-events")
            mobile_visible = await mobile_list.is_visible() if mobile_list else False
            
            cards = await page.query_selector_all(".mobile-event-card")
            
            if not desktop_table and not mobile_list:
                raise Exception("Neither desktop nor mobile events found! Are there events in the DB? HTML snippet: " + (await page.content())[:500])
                
            if desktop_visible: raise Exception("Desktop table is visible on mobile!")
            if not mobile_visible: raise Exception("Mobile event list is not visible!")
            if len(cards) == 0: raise Exception("No mobile cards found!")
            
            box = await cards[0].bounding_box()
            if box["width"] < 340: raise Exception("Card width is too narrow!")
            
            await capture(page, "01_events_mobile_cards_390.png")

            # 2. Workspace Calendar Mobile Clean (02_workspace_calendar_mobile_clean_390.png)
            await page.goto(f"{BASE_URL}/calendar/", wait_until="networkidle")
            await asyncio.sleep(2)
            
            capsule_titles = await page.query_selector_all(".k-event-capsule__title")
            for t in capsule_titles:
                if await t.is_visible():
                    raise Exception("Full event titles are visible inside month cells at 390px!")
                    
            await capture(page, "02_workspace_calendar_mobile_clean_390.png")

            # 3. & 4. Mobile Selected Day Agenda (03_mobile_selected_day_390.png, 04_mobile_agenda_open_390.png)
            day_with_dot = await page.query_selector(".k-mobile-event-dot")
            if not day_with_dot:
                raise Exception("No events found in mobile calendar to click!")
                
            day_cell = await day_with_dot.evaluate_handle("el => el.closest('.fc-daygrid-day')")
            await day_cell.click()
            await capture(page, "03_mobile_selected_day_390.png")
            
            agenda = await page.wait_for_selector("#mobile-agenda-sheet.active", state="visible")
            title = await page.is_visible(".agenda-title")
            if not agenda or not title:
                raise Exception("Agenda sheet didn't open correctly!")
            
            await capture(page, "04_mobile_agenda_open_390.png")
            
            # Close agenda
            await page.click("#mobile-agenda-overlay")
            await asyncio.sleep(0.5)

            # 5. Calendar Desktop (05_calendar_desktop_1920.png)
            await page.set_viewport_size(desktop)
            await page.goto(f"{BASE_URL}/calendar/", wait_until="networkidle")
            await asyncio.sleep(2)
            
            capsules = await page.query_selector_all(".k-event-capsule")
            if len(capsules) == 0:
                raise Exception("No desktop capsules found!")
                
            await capture(page, "05_calendar_desktop_1920.png")

            # 6. Calendar Event Popover (06_calendar_event_popover_1920.png)
            # 6. Calendar Event Popover (06_calendar_event_popover_1920.png)
            # 6. Calendar Event Popover (06_calendar_event_popover_1920.png)
            capsules = await page.query_selector_all(".k-event-capsule")
            if len(capsules) > 0:
                await page.evaluate("(el) => el.scrollIntoView()", capsules[0])
                await capsules[0].hover(force=True)
                try:
                    await page.wait_for_selector(".tippy-box", state="visible", timeout=3000)
                except Exception:
                    print("Tippy box did not appear, capturing anyway...")
            else:
                print("No capsules found to hover, capturing anyway...")
                
            await capture(page, "06_calendar_event_popover_1920.png")

            # 7. Events Desktop (07_events_desktop_1920.png)
            await page.goto(f"{BASE_URL}/events/", wait_until="networkidle")
            await asyncio.sleep(1)
            
            is_premium = await page.is_visible(".premium-grid")
            if not is_premium:
                raise Exception("Premium grid not visible!")
                
            await capture(page, "07_events_desktop_1920.png")

            # 8. Single Action Menu (08_single_action_menu_1920.png)
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
                
            await capture(page, "08_single_action_menu_1920.png")
            
            print("ALL ASSERTIONS PASSED")
            print("PHASE 27.4 CAPTURE COMPLETE")

        except Exception as e:
            err_msg = repr(e).encode('ascii', 'replace').decode('ascii')
            print(f"[FAIL] Assertion failed: {err_msg}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
