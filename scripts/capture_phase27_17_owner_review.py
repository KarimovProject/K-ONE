import asyncio
import os
import glob
import shutil
import json
from playwright.async_api import async_playwright

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_17_owner_review"
MANIFEST_PATH = r"C:\IEMS\tests\visual_baseline\phase27_17_capture_manifest.json"

async def login(page):
    await page.goto("http://127.0.0.1:8001/accounts/login/")
    await page.fill("input[name='username']", "acceptance_admin")
    await page.fill("input[name='password']", "K-ONE-admin-2026!")
    await page.click("button[type='submit']")
    await page.wait_for_url("**/workspace/**")

async def set_language(page, lang_code):
    await page.goto(f"http://127.0.0.1:8001/i18n/setlang/?language={lang_code}")
    await page.goto("http://127.0.0.1:8001/workspace/")

async def capture_and_verify(page, route, name, viewport, open_menu=False):
    await page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    response = await page.goto(f"http://127.0.0.1:8001{route}")
    await page.wait_for_load_state("networkidle")
    
    status = response.status
    
    # Global checks
    horizontal_overflow = await page.evaluate("document.body.scrollWidth > window.innerWidth")
    
    mobile_action_errors = []
    cta_errors = []
    dropdown_errors = []

    # 1. Mobile Action Checks (if 390px viewport and mobile actions exist)
    if viewport[0] == 390:
        actions = page.locator(".mobile-actions-row > a, .mobile-actions-row > button")
        count = await actions.count()
        for i in range(count):
            action = actions.nth(i)
            # Evaluate client rects
            rects = await action.evaluate('''el => {
                const svg = el.querySelector('svg');
                let svgRect = {width: 0, height: 0};
                if (svg) svgRect = svg.getBoundingClientRect();
                return {
                    height: el.getBoundingClientRect().height,
                    svgWidth: svgRect.width,
                    svgHeight: svgRect.height,
                    wrap: window.getComputedStyle(el).whiteSpace !== 'nowrap'
                }
            }''')
            if rects['height'] < 43.5:
                mobile_action_errors.append(f"Button height {rects['height']} < 44px")
            if rects['svgWidth'] > 21 or rects['svgHeight'] > 21:
                mobile_action_errors.append(f"SVG size {rects['svgWidth']}x{rects['svgHeight']} > 20px")
            if rects['wrap']:
                mobile_action_errors.append(f"Button label can wrap")
                
    # 2. Events desktop CTA Checks (if Events list and desktop)
    if route == "/events/" and viewport[0] > 768:
        cta = page.locator(".btn-primary").first
        if await cta.is_visible():
            cta_styles = await cta.evaluate('''el => {
                const style = window.getComputedStyle(el);
                return {
                    textDecoration: style.textDecorationLine,
                    bg: style.backgroundColor,
                    height: el.getBoundingClientRect().height
                }
            }''')
            if cta_styles['textDecoration'] != 'none' and 'underline' in cta_styles['textDecoration']:
                cta_errors.append(f"CTA has underline: {cta_styles['textDecoration']}")
            if cta_styles['bg'] == 'rgba(0, 0, 0, 0)' or cta_styles['bg'] == 'transparent':
                cta_errors.append(f"CTA has transparent bg")
            if cta_styles['height'] < 43.5:
                cta_errors.append(f"CTA height {cta_styles['height']} < 44px")
                
    # 3. Dropdown Assertions
    if open_menu:
        dropdown = page.locator(".dropdown-toggle").first
        if await dropdown.is_visible():
            await dropdown.click()
            await page.wait_for_timeout(300)
            
            premium_menu = page.locator(".premium-dropdown-menu").first
            if not await premium_menu.is_visible():
                dropdown_errors.append("Premium dropdown not visible after click")
            else:
                view_item = premium_menu.locator(".action-view").first
                edit_item = premium_menu.locator(".action-edit").first
                
                if not await view_item.is_visible() and route != '/events/speakers/':
                    dropdown_errors.append("View item not visible")
                
                if not await edit_item.is_visible():
                    dropdown_errors.append("Edit item not visible (Expected Edit permission)")
                else:
                    colors = await page.evaluate('''() => {
                        const v = document.querySelector('.premium-dropdown-menu .action-view');
                        const e = document.querySelector('.premium-dropdown-menu .action-edit');
                        return {
                            view: v ? window.getComputedStyle(v).color : '',
                            edit: e ? window.getComputedStyle(e).color : ''
                        }
                    }''')
                    if colors['view'] == colors['edit']:
                        dropdown_errors.append(f"View and Edit have same color: {colors['view']}")
                        
    # Screenshot
    await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}.png"))
    print(f"Captured {name}.png")
    
    return {
        "filename": f"{name}.png",
        "requested_url": route,
        "http_status": status,
        "language": "unknown",
        "viewport": viewport,
        "horizontal_overflow": horizontal_overflow,
        "mobile_action_errors": mobile_action_errors,
        "cta_errors": cta_errors,
        "dropdown_errors": dropdown_errors,
        "passed": not horizontal_overflow and not mobile_action_errors and not cta_errors and not dropdown_errors
    }

async def run():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if os.path.exists(MANIFEST_PATH):
        os.remove(MANIFEST_PATH)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await login(page)
        
        manifest = []
        
        shots = [
            # Rooms
            ("/master-data/venues/", "Rooms_menu_open_1920", (1920, 1080), True, "uz"),
            ("/master-data/venues/", "Rooms_390", (390, 844), False, "uz"),
            
            # Event Types
            ("/master-data/event-types/", "Event_Types_menu_open_1920", (1920, 1080), True, "uz"),
            ("/master-data/event-types/", "Event_Types_390", (390, 844), False, "uz"),
            
            # Organizations
            ("/master-data/organizations/", "Organizations_menu_open_1920", (1920, 1080), True, "uz"),
            ("/master-data/organizations/", "Organizations_390", (390, 844), False, "uz"),
            
            # Sponsors
            ("/master-data/sponsors/", "Sponsors_menu_open_1920", (1920, 1080), True, "uz"),
            ("/master-data/sponsors/", "Sponsors_390", (390, 844), False, "uz"),
            
            # Speakers
            ("/events/speakers/", "Speakers_menu_open_1920", (1920, 1080), True, "uz"),
            ("/events/speakers/", "Speakers_390", (390, 844), False, "uz"),
            
            # Events
            ("/events/", "Events_menu_open_1920", (1920, 1080), True, "uz"),
            ("/events/", "Events_1920", (1920, 1080), False, "uz"),
            ("/events/", "Events_390", (390, 844), False, "uz"),
            
            # Leadership Dashboard
            ("/leadership/", "Leadership_UZ_1920", (1920, 1080), False, "uz"),
            ("/leadership/", "Leadership_UZ_390", (390, 844), False, "uz"),
        ]
        
        current_lang = "uz"
        for route, name, viewport, open_menu, lang in shots:
            if current_lang != lang:
                await set_language(page, lang)
                current_lang = lang
                
            res = await capture_and_verify(page, route, name, viewport, open_menu)
            res["language"] = lang
            manifest.append(res)
            
        await browser.close()
        
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
            
        has_error = False
        for m in manifest:
            if not m["passed"]:
                print(f"FAILED ASSERTIONS FOR {m['filename']}: {m}")
                has_error = True
                
        if has_error:
            print("CAPTURE FAILED. ZIPPING FORBIDDEN.")
            import sys
            sys.exit(1)
            
        print("CAPTURE SUCCESSFUL.")

if __name__ == "__main__":
    asyncio.run(run())
