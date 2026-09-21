import asyncio
import os
import shutil
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"
ARTIFACT_DIR = r"C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6"
LOCAL_OUTPUT_DIR = "tests/visual_baseline/phase21"

PAGES = [
    ("dashboard", f"{BASE_URL}/workspace/"),
    ("events", f"{BASE_URL}/events/"),
    ("calendar", f"{BASE_URL}/calendar/"),
    ("approvals", f"{BASE_URL}/events/approvals/"),
    ("venues", f"{BASE_URL}/master-data/venues/"),
    ("reports", f"{BASE_URL}/reports/"),
    ("profile", f"{BASE_URL}/profile/"),
]

VIEWPORTS = [
    ("1920", {"width": 1920, "height": 1080}),
    ("1366", {"width": 1366, "height": 768}),
    ("390", {"width": 390, "height": 844}),
]

async def capture_all():
    os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    password = os.environ.get("IEMS_ACCEPTANCE_PASSWORD", "Password123!")

    computed_fonts = {}

    async with async_playwright() as p:
        for vp_name, vp_dims in VIEWPORTS:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport=vp_dims)
            page = await context.new_page()

            # Login
            await page.goto(f"{BASE_URL}/accounts/login/", wait_until="networkidle")
            await page.fill('input[name="username"]', "acceptance_admin")
            await page.fill('input[name="password"]', password)
            async with page.expect_navigation():
                await page.click('button[type="submit"]')

            print(f"\n==========================================")
            print(f" Capturing Viewport: {vp_name} ({vp_dims['width']}x{vp_dims['height']})")
            print(f"==========================================")

            for key, url in PAGES:
                if vp_name == "390" and key not in ["dashboard", "events", "reports"]:
                    continue

                response = await page.goto(url, wait_until="networkidle")
                await asyncio.sleep(0.5)

                filename = f"phase21_{key}_{vp_name}.png"
                local_path = os.path.join(LOCAL_OUTPUT_DIR, filename)
                artifact_path = os.path.join(ARTIFACT_DIR, filename)

                await page.screenshot(path=local_path, full_page=False)
                shutil.copyfile(local_path, artifact_path)
                print(f"Captured: {filename} -> Status: {response.status if response else 200}")

                # Extract computed fonts on 1920
                if vp_name == "1920":
                    if key == "dashboard":
                        body_font = await page.evaluate("() => window.getComputedStyle(document.body).fontFamily")
                        h1_font = await page.evaluate("() => { const el = document.querySelector('h1, .page-title'); return el ? window.getComputedStyle(el).fontFamily : 'N/A'; }")
                        kpi_font = await page.evaluate("() => { const el = document.querySelector('.metric-tile__value'); return el ? window.getComputedStyle(el).fontFamily : 'N/A'; }")
                        sidebar_font = await page.evaluate("() => { const el = document.querySelector('.sidebar-nav-item'); return el ? window.getComputedStyle(el).fontFamily : 'N/A'; }")
                        computed_fonts["body"] = body_font
                        computed_fonts["page_title"] = h1_font
                        computed_fonts["kpi"] = kpi_font
                        computed_fonts["sidebar"] = sidebar_font
                    elif key == "events":
                        table_font = await page.evaluate("() => { const el = document.querySelector('.data-table, .approval-title, td'); return el ? window.getComputedStyle(el).fontFamily : 'N/A'; }")
                        computed_fonts["table"] = table_font

            await browser.close()

    print("\n--- COMPUTED FONTS ---")
    for k, v in computed_fonts.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    asyncio.run(capture_all())
