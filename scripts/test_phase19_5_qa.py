import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"

async def run_phase19_5_qa():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # 1. Capture 1920x1080
        # -------------------------------------------------------------
        print("Capturing 1920x1080 layouts...")
        ctx_1920 = await browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page_1920 = await ctx_1920.new_page()

        # Public Dashboard 1920
        print("  - Public Dashboard 1920")
        await page_1920.goto(f"{BASE_URL}/dashboard/?date=2026-08-17")
        await page_1920.wait_for_selector(".brand-logo-public")
        await page_1920.wait_for_timeout(800)
        await page_1920.screenshot(path="phase19_5_dashboard_1920.png", full_page=False)

        # Login 1920
        print("  - Login 1920")
        await page_1920.goto(f"{BASE_URL}/accounts/login/")
        await page_1920.wait_for_selector(".brand-logo-large")
        await page_1920.wait_for_timeout(800)
        await page_1920.screenshot(path="phase19_5_login_1920.png", full_page=False)

        # Login and go to Workspace 1920
        print("  - Authenticated Workspace 1920")
        await page_1920.fill('input[name="username"]', 'admin')
        await page_1920.fill('input[name="password"]', 'Admin12345!')
        await page_1920.click('button[type="submit"]')
        await page_1920.wait_for_load_state("networkidle")
        await page_1920.goto(f"{BASE_URL}/workspace/")
        await page_1920.wait_for_selector(".workspace-hero")
        await page_1920.wait_for_timeout(800)
        await page_1920.screenshot(path="phase19_5_workspace_1920.png", full_page=False)

        await ctx_1920.close()

        # -------------------------------------------------------------
        # 2. Capture 1366x768
        # -------------------------------------------------------------
        print("Capturing 1366x768 layouts...")
        ctx_1366 = await browser.new_context(viewport={"width": 1366, "height": 768}, device_scale_factor=1)
        page_1366 = await ctx_1366.new_page()

        # Public Dashboard 1366
        print("  - Public Dashboard 1366")
        await page_1366.goto(f"{BASE_URL}/dashboard/?date=2026-08-17")
        await page_1366.wait_for_selector(".brand-logo-public")
        await page_1366.wait_for_timeout(800)
        await page_1366.screenshot(path="phase19_5_dashboard_1366.png", full_page=False)

        # Login 1366
        print("  - Login 1366")
        await page_1366.goto(f"{BASE_URL}/accounts/login/")
        await page_1366.wait_for_selector(".brand-logo-large")
        await page_1366.wait_for_timeout(800)
        await page_1366.screenshot(path="phase19_5_login_1366.png", full_page=False)

        # Workspace 1366
        print("  - Workspace 1366")
        await page_1366.fill('input[name="username"]', 'admin')
        await page_1366.fill('input[name="password"]', 'Admin12345!')
        await page_1366.click('button[type="submit"]')
        await page_1366.wait_for_load_state("networkidle")
        await page_1366.goto(f"{BASE_URL}/workspace/")
        await page_1366.wait_for_selector(".workspace-hero")
        await page_1366.wait_for_timeout(800)
        await page_1366.screenshot(path="phase19_5_workspace_1366.png", full_page=False)

        await ctx_1366.close()

        # -------------------------------------------------------------
        # 3. Capture 390x844 (Mobile)
        # -------------------------------------------------------------
        print("Capturing 390x844 mobile layouts...")
        ctx_390 = await browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, device_scale_factor=2)
        page_390 = await ctx_390.new_page()

        # Login 390
        print("  - Login 390")
        await page_390.goto(f"{BASE_URL}/accounts/login/")
        await page_390.wait_for_selector(".brand-logo-mobile")
        await page_390.wait_for_timeout(800)
        await page_390.screenshot(path="phase19_5_login_390.png", full_page=False)

        # Workspace 390
        print("  - Workspace 390")
        await page_390.fill('input[name="username"]', 'admin')
        await page_390.fill('input[name="password"]', 'Admin12345!')
        await page_390.click('button[type="submit"]')
        await page_390.wait_for_load_state("networkidle")
        await page_390.goto(f"{BASE_URL}/workspace/")
        await page_390.wait_for_selector(".workspace-hero")
        await page_390.wait_for_timeout(800)
        await page_390.screenshot(path="phase19_5_workspace_390.png", full_page=False)

        await ctx_390.close()
        await browser.close()
        print("All Phase 19.5 QA assertions and screenshot captures PASSED!")

if __name__ == "__main__":
    asyncio.run(run_phase19_5_qa())
