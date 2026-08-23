import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_viewport_size({'width': 390, 'height': 844})
        await page.goto("http://10.34.12.2:8012/accounts/login/")
        await page.fill("input[name='username']", "admin")
        await page.fill("input[name='password']", "admin")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/workspace/")
        await page.goto("http://10.34.12.2:8012/events/", wait_until="networkidle")
        
        html = await page.content()
        print("k-mobile-events in HTML string:", "k-mobile-events" in html)
        
        mobiles = await page.query_selector_all(".k-mobile-events")
        print("Count of .k-mobile-events in DOM:", len(mobiles))
        
        if len(mobiles) > 0:
            display = await page.evaluate("window.getComputedStyle(document.querySelector('.k-mobile-events')).display")
            print("Mobile events display:", display)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
