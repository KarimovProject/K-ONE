import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        page = await context.new_page()
        
        await page.goto("http://10.34.12.2:8012/accounts/login/")
        await page.fill("input[name='username']", "admin")
        await page.fill("input[name='password']", "admin")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/workspace/")
        
        await page.goto("http://10.34.12.2:8012/events/calendar/?date=2026-08-01")
        await asyncio.sleep(2)
        
        html = await page.evaluate("document.querySelector('.calendar-card') ? document.querySelector('.calendar-card').outerHTML : 'NO CALENDAR CARD'")
        print("CALENDAR_CARD_HTML:")
        print(html)
        
        await browser.close()

asyncio.run(main())
