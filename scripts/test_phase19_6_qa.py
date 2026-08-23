import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"

async def run_phase19_6_qa():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Capture 1920x1080
        print("Capturing 1920x1080 Login...")
        ctx_1920 = await browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page_1920 = await ctx_1920.new_page()
        await page_1920.goto(f"{BASE_URL}/accounts/login/")
        await page_1920.wait_for_selector(".login-card")
        await page_1920.wait_for_timeout(800)
        await page_1920.screenshot(path="phase19_6_login_1920.png", full_page=False)
        await ctx_1920.close()

        # 2. Capture 1366x768
        print("Capturing 1366x768 Login...")
        ctx_1366 = await browser.new_context(viewport={"width": 1366, "height": 768}, device_scale_factor=1)
        page_1366 = await ctx_1366.new_page()
        await page_1366.goto(f"{BASE_URL}/accounts/login/")
        await page_1366.wait_for_selector(".login-card")
        await page_1366.wait_for_timeout(800)
        await page_1366.screenshot(path="phase19_6_login_1366.png", full_page=False)
        await ctx_1366.close()

        # 3. Capture 390x844 (Mobile)
        print("Capturing 390x844 Mobile Login...")
        ctx_390 = await browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, device_scale_factor=2)
        page_390 = await ctx_390.new_page()
        await page_390.goto(f"{BASE_URL}/accounts/login/")
        await page_390.wait_for_selector(".login-card")
        await page_390.wait_for_timeout(800)
        await page_390.screenshot(path="phase19_6_login_390.png", full_page=False)
        await ctx_390.close()

        # 4. Capture Error State
        print("Capturing Login Error State...")
        ctx_err = await browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page_err = await ctx_err.new_page()
        await page_err.goto(f"{BASE_URL}/accounts/login/")
        await page_err.fill('input[name="username"]', 'wrong_user')
        await page_err.fill('input[name="password"]', 'wrong_pass')
        await page_err.click('button[type="submit"]')
        await page_err.wait_for_selector(".form-alert")
        await page_err.wait_for_timeout(500)
        await page_err.screenshot(path="phase19_6_login_error_1920.png", full_page=False)
        await ctx_err.close()

        await browser.close()
        print("All Phase 19.6 QA screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(run_phase19_6_qa())
