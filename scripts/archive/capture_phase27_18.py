import asyncio
import os
import glob
import shutil
from playwright.async_api import async_playwright, expect

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase27_18_owner_review"

async def login(page):
    await page.goto("http://127.0.0.1:8001/accounts/login/")
    await page.fill("input[name='username']", "acceptance_admin")
    await page.fill("input[name='password']", "K-ONE-admin-2026!")
    await page.click("button[type='submit']")
    await page.wait_for_url("**/workspace/**")

async def capture_management_page(page, url, name, is_mobile=False):
    await page.goto(f"http://127.0.0.1:8001{url}")
    await page.wait_for_load_state("networkidle")
    
    # Check assertions based on viewport
    if not is_mobile:
        # Check desktop
        rows = await page.locator("tbody tr").all()
        for row in rows:
            dropdown_toggles = await row.locator(".dropdown-toggle").count()
            if dropdown_toggles != 1:
                html = await row.inner_html()
                print(f"DEBUG {name} ROW HTML: {html}")
                assert False, f"Expected 1 dropdown-toggle per row in {name}, found {dropdown_toggles}"
            
            # Ensure no action-view or action-edit outside dropdown is visible
            outside_actions = await row.locator("> td:last-child > *:not(.dropdown-wrapper) .action-view, > td:last-child > *:not(.dropdown-wrapper) .action-edit, > td:last-child > .action-view, > td:last-child > .action-edit").all()
            for action in outside_actions:
                assert not await action.is_visible(), f"Action visible outside dropdown in {name} desktop"
                
        # Click the first dropdown toggle
        first_toggle = page.locator("tbody tr .dropdown-toggle").first
        if await first_toggle.count() > 0:
            await first_toggle.click()
            await page.wait_for_selector(".premium-dropdown-menu:not([hidden])", state="visible", timeout=5000)
            
            # Check there is exactly one visible dropdown
            visible_dropdowns = await page.locator(".premium-dropdown-menu:not([hidden])").count()
            assert visible_dropdowns == 1, f"Expected exactly 1 visible dropdown in {name}, found {visible_dropdowns}"
            
            # Take screenshot with open menu
            await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}_menu_open_1920.png"))
            
            # Close it for normal screenshot
            await page.locator("body").click(position={"x": 10, "y": 10})
            
        await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}_1920.png"))
    else:
        # Mobile
        # check buttons
        overflow = await page.evaluate("document.body.scrollWidth > window.innerWidth")
        assert not overflow, f"Horizontal overflow in {name} mobile"
        
        # Take screenshot
        await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}_390.png"))


async def run():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Desktop context
        ctx_desk = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page_desk = await ctx_desk.new_page()
        await login(page_desk)
        
        pages_to_check = [
            ("/events/", "Events"),
            ("/master-data/venues/", "Rooms"),
            ("/master-data/event-types/", "Event_Types"),
            ("/master-data/organizations/", "Organizations"),
            ("/master-data/sponsors/", "Sponsors"),
            ("/events/speakers/", "Speakers"),
        ]
        
        for url, name in pages_to_check:
            print(f"Checking {name} desktop...")
            await capture_management_page(page_desk, url, name, False)
            
        # Leadership desktop
        print("Checking Leadership desktop...")
        await page_desk.goto("http://127.0.0.1:8001/leadership/")
        await page_desk.wait_for_load_state("networkidle")
        await page_desk.screenshot(path=os.path.join(OUTPUT_DIR, "Leadership_UZ_1920.png"))
        
        # Mobile context
        ctx_mob = await browser.new_context(viewport={"width": 390, "height": 844})
        page_mob = await ctx_mob.new_page()
        await login(page_mob)
        
        for url, name in [("/events/", "Events"), ("/master-data/venues/", "Rooms")]:
            print(f"Checking {name} mobile...")
            await capture_management_page(page_mob, url, name, True)
            
        # Leadership mobile
        print("Checking Leadership mobile...")
        await page_mob.goto("http://127.0.0.1:8001/leadership/")
        await page_mob.wait_for_load_state("networkidle")
        await page_mob.screenshot(path=os.path.join(OUTPUT_DIR, "Leadership_UZ_390.png"))
        
        await browser.close()
        print("CAPTURE_DONE")

if __name__ == "__main__":
    asyncio.run(run())
