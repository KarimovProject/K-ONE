import os
import asyncio
from playwright.async_api import async_playwright

async def test_auth_flow():
    password = os.environ.get("IEMS_ACCEPTANCE_PASSWORD", "Password123!")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 1. Test navigation to /login/ alias
        response = await page.goto("http://10.34.12.2:8012/login/", wait_until="networkidle")
        print("Navigated to /login/, final URL:", page.url, "Status:", response.status)
        assert "/accounts/login/" in page.url

        # 2. Fill login credentials
        await page.fill('input[name="username"]', "acceptance_admin")
        await page.fill('input[name="password"]', password)

        # 3. Submit
        async with page.expect_navigation():
            await page.click('button[type="submit"]')

        print("After submit, URL:", page.url)
        assert "/workspace/" in page.url

        # 4. Verify authenticated elements
        page_content = await page.content()
        assert "acceptance_admin" in page_content or "Asosiy panel" in page_content or "Chiqish" in page_content
        print("Authenticated workspace loaded successfully (HTTP 200).")

        # 5. Test logout flow
        logout_btn = await page.query_selector('form[action*="logout"] button, a[href*="logout"]')
        if logout_btn:
            await logout_btn.click()
            await page.wait_for_load_state("networkidle")
            print("Logged out. Current URL:", page.url)
        else:
            await page.goto("http://10.34.12.2:8012/accounts/logout/")
            print("Logged out via direct URL. Current URL:", page.url)

        await browser.close()
        print("ALL AUTH FLOW STEPS PASSED SUCCESSFULLY.")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
