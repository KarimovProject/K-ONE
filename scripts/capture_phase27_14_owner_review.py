import asyncio
import os
import glob
import shutil
from playwright.async_api import async_playwright

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_14_owner_review"

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
    await page.goto(f"http://127.0.0.1:8001{route}")
    await page.wait_for_load_state("networkidle")
    
    # Verify no 404
    title = await page.title()
    assert "404" not in title, f"{name}: 404 page encountered"
    
    # Verify not login
    assert "login" not in page.url, f"{name}: Redirected to login page"

    # Handle dropdown if required
    if open_menu:
        dropdown = page.locator(".dropdown-toggle").first
        if await dropdown.is_visible():
            await dropdown.click()
            await page.wait_for_timeout(300)
    
    # Assertions based on Phase 27.14
    if "reporting" not in route:
        # Check empty state OR status badge
        empty_list = await page.locator(".empty-list").count()
        empty_state = await page.locator(".empty-state").count()
        if empty_list == 0 and empty_state == 0:
            status_badges = await page.locator(".status-badge").count()
            if status_badges == 0:
                await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}_failure.png"))
                assert False, f"{name}: No status badges found in populated list. Page URL: {page.url}"
    
    # Screenshot
    await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}.png"))
    print(f"Captured {name}.png")

async def run():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Clean up old failures from any previous dirs just in case
    for f in glob.glob(r"C:\IEMS\tests\visual_baseline\**\*_failure.png", recursive=True):
        os.remove(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        await login(page)
        
        shots = [
            ("/master-data/venues/", "Rooms_1920", (1920, 1080), False),
            ("/master-data/venues/", "Rooms_menu_open_1920", (1920, 1080), True),
            ("/master-data/venues/", "Rooms_1366", (1366, 768), False),
            ("/master-data/venues/", "Rooms_768", (768, 1024), False),
            ("/master-data/venues/", "Rooms_390", (390, 844), False),
            ("/master-data/event-types/", "Event_Types_1920", (1920, 1080), False),
            ("/master-data/event-types/", "Event_Types_menu_open_1920", (1920, 1080), True),
            ("/master-data/event-types/", "Event_Types_768", (768, 1024), False),
            ("/master-data/event-types/", "Event_Types_390", (390, 844), False),
            ("/master-data/organizations/", "Organizations_1920", (1920, 1080), False),
            ("/master-data/organizations/", "Organizations_menu_open_1920", (1920, 1080), True),
            ("/master-data/sponsors/", "Sponsors_1920", (1920, 1080), False),
            ("/master-data/sponsors/", "Sponsors_390", (390, 844), False),
            ("/events/speakers/", "Speakers_1920", (1920, 1080), False),
            ("/events/speakers/", "Speakers_390", (390, 844), False),
            ("/publications/", "Publications_1920", (1920, 1080), False),
            ("/events/approvals/", "Approvals_1920", (1920, 1080), False),
            ("/events/approvals/", "Approvals_menu_open_1920", (1920, 1080), True),
            ("/events/displaced/", "Transfers_1920", (1920, 1080), False),
        ]
        
        for route, name, viewport, open_menu in shots:
            await capture_and_verify(page, route, name, viewport, open_menu)
            
        # Leadership language tests
        await set_language(page, "uz")
        await capture_and_verify(page, "/reporting/leadership/", "Leadership_UZ_1920", (1920, 1080))
        await capture_and_verify(page, "/reporting/leadership/", "Leadership_UZ_390", (390, 844))
        
        await set_language(page, "ru")
        await capture_and_verify(page, "/reporting/leadership/", "Leadership_RU_390", (390, 844))
        
        await set_language(page, "en")
        await capture_and_verify(page, "/reporting/leadership/", "Leadership_EN_390", (390, 844))
        
        # Reset back to UZ for reports
        await set_language(page, "uz")
        await capture_and_verify(page, "/reporting/", "Reports_1920", (1920, 1080))
        
        await browser.close()
        
    print(f"SCREENSHOT_COUNT: {len(os.listdir(OUTPUT_DIR))}")
    print(f"SCREENSHOT_DIRECTORY: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(run())
