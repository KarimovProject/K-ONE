import asyncio
from playwright.async_api import async_playwright

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Desktop Context
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # Login 1920
        await page.goto('http://10.34.12.2:8012/accounts/login/')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='kone_real_login_1920.png', full_page=True)

        # Login and test authenticated routes
        await page.fill('input[name="username"]', 'admin')
        await page.fill('input[name="password"]', 'admin')
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(1000)

        # Workspace 1920
        await page.goto('http://10.34.12.2:8012/workspace/')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='kone_real_workspace_1920.png', full_page=True)

        await context.close()

        # Public Context (No auth)
        public_context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        public_page = await public_context.new_page()

        # Dashboard 1920
        await public_page.goto('http://10.34.12.2:8012/dashboard/')
        await public_page.wait_for_timeout(1000)
        await public_page.screenshot(path='kone_real_dashboard_1920.png', full_page=True)

        # Calendar 1920
        await public_page.goto('http://10.34.12.2:8012/dashboard/calendar/?date=2026-08-17&view=month')
        await public_page.wait_for_timeout(1000)
        await public_page.screenshot(path='kone_real_calendar_1920.png', full_page=True)

        # Live 1920
        await public_page.goto('http://10.34.12.2:8012/venues/live/')
        await public_page.wait_for_timeout(1000)
        await public_page.screenshot(path='kone_real_live_1920.png', full_page=True)

        await public_context.close()

        # 2. Mobile Context
        mobile_context = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        mobile_page = await mobile_context.new_page()

        # Login Mobile
        await mobile_page.goto('http://10.34.12.2:8012/accounts/login/')
        await mobile_page.wait_for_timeout(1000)
        await mobile_page.screenshot(path='kone_real_login_390.png', full_page=True)

        await mobile_context.close()

        await browser.close()

if __name__ == '__main__':
    asyncio.run(capture())
