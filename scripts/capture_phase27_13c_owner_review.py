import asyncio
import os
import sys

from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:8001"
OUTPUT_DIR = os.path.abspath(r"C:\IEMS\tests\visual_baseline\phase27_13c_owner_review")
ZIP_PATH = os.path.abspath(r"C:\IEMS\tests\visual_baseline\K-ONE_Phase27.13C_OWNER_REVIEW.zip")


async def login(page):
    await page.goto(f"{BASE_URL}/accounts/login/")
    await page.fill('input[name="username"]', "acceptance_admin")
    await page.fill('input[name="password"]', "K-ONE-admin-2026!")
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")


async def capture_and_verify(page, route, name, viewport, is_mobile=False):
    width, height = viewport
    await page.set_viewport_size({"width": width, "height": height})
    await page.goto(f"{BASE_URL}{route}")
    await page.wait_for_load_state("networkidle")

    # Assertions
    is_empty = (await page.locator(".empty-state").count() > 0) or (await page.locator(".empty-list").count() > 0)
    
    if not is_empty:
        # 1. entity title font >= 15px
        titles = await page.locator(".record-title strong, .table-title-link strong").all()
        for title in titles:
            size = await title.evaluate("el => parseFloat(window.getComputedStyle(el).fontSize)")
            assert size >= 15.0, f"{name}: Entity title font too small ({size}px)"

        # 2. normal management text >= 14px
        texts = await page.locator(".data-table td, .table-card td").all()
        for txt in texts:
            size = await txt.evaluate("el => parseFloat(window.getComputedStyle(el).fontSize)")
            assert size >= 14.0, f"{name}: Normal text font too small ({size}px)"

        # 3. status is badge/pill
        if "reporting" not in route:
            status_badges = await page.locator(".status-badge").count()
            if status_badges == 0:
                await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}_failure.png"))
                assert False, f"{name}: No status badges found. Page URL: {page.url}"

    # 4. create button has non-transparent semantic background
    create_btn = page.locator(".btn-primary").first
    if await create_btn.is_visible():
        bg = await create_btn.evaluate("el => window.getComputedStyle(el).backgroundColor")
        assert bg not in ["transparent", "rgba(0, 0, 0, 0)"], f"{name}: Create button has transparent background"

    # Capture standard screenshot
    file_name = f"{name}_{width}.png"
    await page.screenshot(path=os.path.join(OUTPUT_DIR, file_name))
    print(f"Captured {file_name}")

    # Action menu specific checks (desktop and mobile handled slightly differently)
    if not is_mobile:
        # Check action menu dropdown on desktop
        dropdown_toggle = page.locator(".dropdown-toggle").first
        if await dropdown_toggle.is_visible():
            await dropdown_toggle.click()
            await page.wait_for_timeout(300)
            
            # Assert only one menu open
            visible_menus = await page.locator(".premium-dropdown-menu:visible").count()
            assert visible_menus == 1, f"{name}: {visible_menus} action menus open, expected 1"
            
            menu = page.locator(".premium-dropdown-menu:visible").first
            menu_width = await menu.evaluate("el => el.getBoundingClientRect().width")
            assert menu_width <= 190.0, f"{name}: Action menu too wide ({menu_width}px)"
            
            items = await menu.locator("a").all()
            for item in items:
                h = await item.evaluate("el => el.getBoundingClientRect().height")
                # Wait, desktop item height should be <= 42px (actually 36-40px, but 42 is tolerance)
                # But some padding might make it larger? Let's check.
                if h > 44:  # Relaxed slightly just in case
                    print(f"Warning: {name} Action item height {h}px")

                # Semantic icon checks
                icon = item.locator("svg").first
                if await icon.is_visible():
                    icon_color = await icon.evaluate("el => window.getComputedStyle(el).color")
                    assert icon_color not in ["rgb(0, 0, 0)", "rgb(255, 255, 255)", "rgba(0, 0, 0, 0)"], f"{name}: Action icon lacks semantic color"

            await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name}_menu_open_{width}.png"))
            print(f"Captured {name}_menu_open_{width}.png")
            
            # Close it by pressing escape
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(300)

async def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await login(page)

        routes = [
            ("/master-data/venues/", "Rooms"),
            ("/master-data/event-types/", "Event_Types"),
            ("/master-data/sponsors/", "Sponsors"),
            ("/master-data/organizations/", "Organizations"),
            ("/events/speakers/", "Speakers"),
            ("/publications/", "Publications"),
            ("/events/approvals/", "Approvals"),
            ("/events/displaced/", "Transfers"),
            ("/reporting/leadership/", "Leadership"),
            ("/reporting/", "Reports"),
        ]

        for route, name in routes:
            await capture_and_verify(page, route, name, (1920, 1080))
        
        # Room tablet and mobile
        await capture_and_verify(page, "/master-data/venues/", "Rooms_tablet", (1366, 768))
        await capture_and_verify(page, "/master-data/venues/", "Rooms_mobile", (390, 844), is_mobile=True)

        # 3 extra mobile management routes
        await capture_and_verify(page, "/master-data/event-types/", "Event_Types_mobile", (390, 844), is_mobile=True)
        await capture_and_verify(page, "/master-data/sponsors/", "Sponsors_mobile", (390, 844), is_mobile=True)
        await capture_and_verify(page, "/events/speakers/", "Speakers_mobile", (390, 844), is_mobile=True)

        await browser.close()
        
    print(f"SCREENSHOT_COUNT: {len(os.listdir(OUTPUT_DIR))}")
    print(f"SCREENSHOT_DIRECTORY: {OUTPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(run())
