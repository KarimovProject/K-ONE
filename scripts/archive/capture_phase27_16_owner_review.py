import asyncio
import os
import glob
import shutil
import json
from playwright.async_api import async_playwright

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_16_owner_review"
MANIFEST_PATH = r"C:\IEMS\tests\visual_baseline\phase27_16_capture_manifest.json"

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
    url = page.url
    title = await page.title()
    content = await page.content()
    
    django_404_detected = (
        "Page not found" in title or 
        "Page not found" in content or 
        "Using the URLconf" in content or 
        "The current path" in content or
        "technical_404_response" in content or
        "404" in title
    )
    login_detected = "login" in url
    
    heading_found = False
    h1_count = await page.locator("h1").count()
    if h1_count > 0:
        h1_text = await page.locator("h1").first.inner_text()
        if len(h1_text.strip()) > 2:
            heading_found = True
        
    active_nav_found = await page.locator(".nav-item.is-active, .nav-item.active, [aria-current='page']").count() > 0
    
    # Check horizontal overflow
    horizontal_overflow = await page.evaluate("document.body.scrollWidth > window.innerWidth")

    premium_dropdown_found = False
    if open_menu and not django_404_detected and not login_detected:
        dropdown = page.locator(".dropdown-toggle").first
        if await dropdown.is_visible():
            await dropdown.click()
            await page.wait_for_timeout(300)
            
            # Assert .premium-dropdown-menu is visible
            premium_menu = page.locator(".premium-dropdown-menu").first
            if await premium_menu.is_visible():
                view_item = premium_menu.locator(".action-view").first
                edit_item = premium_menu.locator(".action-edit").first
                
                # We expect at least one of these to be visible if the menu is open
                if (await view_item.count() > 0 and await view_item.is_visible()) or \
                   (await edit_item.count() > 0 and await edit_item.is_visible()):
                    premium_dropdown_found = True

    # For screenshots that aren't open_menu, we don't care about premium_dropdown_found
    if not open_menu:
        premium_dropdown_found = True
    
    # Screenshot
    await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}.png"))
    print(f"Captured {name}.png")
    
    return {
        "filename": f"{name}.png",
        "requested_url": route,
        "final_url": url,
        "http_status": status,
        "language": "unknown",
        "viewport": viewport,
        "expected_heading": "extracted_h1: " + (h1_text if h1_count > 0 else "None"),
        "heading_found": heading_found,
        "active_nav_found": active_nav_found,
        "django_404_detected": django_404_detected,
        "login_detected": login_detected,
        "horizontal_overflow": horizontal_overflow,
        "premium_dropdown_found": premium_dropdown_found
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
            ("/master-data/venues/", "Rooms_1920", (1920, 1080), False, "uz"),
            ("/master-data/venues/", "Rooms_menu_open_1920", (1920, 1080), True, "uz"),
            ("/master-data/venues/", "Rooms_1366", (1366, 768), False, "uz"),
            ("/master-data/venues/", "Rooms_768", (768, 1024), False, "uz"),
            ("/master-data/venues/", "Rooms_390", (390, 844), False, "uz"),
            
            # Event Types
            ("/master-data/event-types/", "Event_Types_1920", (1920, 1080), False, "uz"),
            ("/master-data/event-types/", "Event_Types_menu_open_1920", (1920, 1080), True, "uz"),
            ("/master-data/event-types/", "Event_Types_768", (768, 1024), False, "uz"),
            ("/master-data/event-types/", "Event_Types_390", (390, 844), False, "uz"),
            
            # Organizations
            ("/master-data/organizations/", "Organizations_1920", (1920, 1080), False, "uz"),
            ("/master-data/organizations/", "Organizations_menu_open_1920", (1920, 1080), True, "uz"),
            ("/master-data/organizations/", "Organizations_1440", (1440, 900), False, "uz"),
            
            # Sponsors
            ("/master-data/sponsors/", "Sponsors_1920", (1920, 1080), False, "uz"),
            ("/master-data/sponsors/", "Sponsors_menu_open_1920", (1920, 1080), True, "uz"),
            ("/master-data/sponsors/", "Sponsors_390", (390, 844), False, "uz"),
            
            # Speakers
            ("/events/speakers/", "Speakers_1920", (1920, 1080), False, "uz"),
            ("/events/speakers/", "Speakers_menu_open_1920", (1920, 1080), True, "uz"),
            ("/events/speakers/", "Speakers_390", (390, 844), False, "uz"),
            
            # Events
            ("/events/", "Events_1920", (1920, 1080), False, "uz"),
            ("/events/", "Events_menu_open_1920", (1920, 1080), True, "uz"),
            
            # Publications
            ("/publications/", "Publications_1920", (1920, 1080), False, "uz"),
            
            # Approvals
            ("/events/approvals/", "Approvals_1920", (1920, 1080), False, "uz"),
            ("/events/approvals/", "Approvals_menu_open_1920", (1920, 1080), True, "uz"),
            
            # Transfers
            ("/events/displaced/", "Transfers_1920", (1920, 1080), False, "uz"),
            
            # Leadership Dashboard
            ("/leadership/", "Leadership_UZ_1920", (1920, 1080), False, "uz"),
            ("/leadership/", "Leadership_UZ_390", (390, 844), False, "uz"),
            ("/leadership/", "Leadership_RU_1920", (1920, 1080), False, "ru"),
            ("/leadership/", "Leadership_EN_1920", (1920, 1080), False, "en"),
            
            # Reports
            ("/reports/", "Reports_1920", (1920, 1080), False, "uz"),
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
            if m["http_status"] >= 400 or m["django_404_detected"] or m["login_detected"] or m["horizontal_overflow"] or not m["heading_found"] or not m["premium_dropdown_found"]:
                print(f"FAILED ASSERTIONS FOR {m['filename']}: {m}")
                has_error = True
                
        if has_error:
            print("CAPTURE FAILED. ZIPPING FORBIDDEN.")
            import sys
            sys.exit(1)
            
        print("CAPTURE SUCCESSFUL.")

if __name__ == "__main__":
    asyncio.run(run())
