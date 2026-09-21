import asyncio
import os
from playwright.async_api import async_playwright

PAGES_TO_TEST = [
    ("01_workspace_dashboard", "http://10.34.12.2:8012/workspace/"),
    ("02_events_list", "http://10.34.12.2:8012/events/"),
    ("03_internal_calendar", "http://10.34.12.2:8012/calendar/"),
    ("04_approvals_queue", "http://10.34.12.2:8012/events/approvals/"),
    ("05_displaced_events", "http://10.34.12.2:8012/events/displaced/"),
    ("06_rooms_venues", "http://10.34.12.2:8012/master-data/venues/"),
    ("07_event_types", "http://10.34.12.2:8012/master-data/event-types/"),
    ("08_organizations", "http://10.34.12.2:8012/master-data/organizations/"),
    ("09_sponsors", "http://10.34.12.2:8012/master-data/sponsors/"),
    ("10_speakers", "http://10.34.12.2:8012/events/speakers/"),
    ("11_reports_dashboard", "http://10.34.12.2:8012/reports/"),
    ("12_profile_page", "http://10.34.12.2:8012/profile/"),
]

VIEWPORTS = [
    ("1920", {"width": 1920, "height": 1080}),
    ("1366", {"width": 1366, "height": 768}),
    ("390", {"width": 390, "height": 844}),
]

async def run_phase20_qa():
    os.makedirs("tests/visual_baseline/phase20", exist_ok=True)
    password = os.environ.get("IEMS_ACCEPTANCE_PASSWORD", "Password123!")

    async with async_playwright() as p:
        for vp_name, vp_dims in VIEWPORTS:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport=vp_dims)
            page = await context.new_page()

            # 1. Login once per viewport session
            await page.goto("http://10.34.12.2:8012/accounts/login/", wait_until="networkidle")
            await page.fill('input[name="username"]', "acceptance_admin")
            await page.fill('input[name="password"]', password)
            async with page.expect_navigation():
                await page.click('button[type="submit"]')

            print(f"\n--- Testing Viewport {vp_name} ({vp_dims['width']}x{vp_dims['height']}) ---")

            for name, url in PAGES_TO_TEST:
                # On mobile test top 4 representative pages
                if vp_name == "390" and name not in ["01_workspace_dashboard", "02_events_list", "03_internal_calendar", "12_profile_page"]:
                    continue

                response = await page.goto(url, wait_until="networkidle")
                await asyncio.sleep(0.3)

                shot_path = f"tests/visual_baseline/phase20/{name}_{vp_name}.png"
                await page.screenshot(path=shot_path, full_page=False)
                print(f"Captured: {shot_path} (Status: {response.status if response else 'N/A'})")

                # Basic sanity assertions
                content = await page.content()
                assert "K-ONE" in content or "Barcha tadbirlar" in content

                # Check no purple links (#551A8B)
                unwanted_purple = await page.evaluate('''() => {
                    const links = Array.from(document.querySelectorAll('a'));
                    return links.some(a => window.getComputedStyle(a).color === 'rgb(85, 26, 139)');
                }''')
                assert not unwanted_purple, f"Found purple default link in {name}"

            await browser.close()

    print("\nALL PHASE 20 PLAYWRIGHT SCREENSHOTS CAPTURED AND ASSERTIONS PASSED!")

if __name__ == "__main__":
    asyncio.run(run_phase20_qa())
