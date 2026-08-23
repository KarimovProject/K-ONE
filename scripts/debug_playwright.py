import asyncio
from playwright.async_api import async_playwright

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        page.on("console", lambda msg: print(f"Browser Console: {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser Error: {err}"))
        
        await page.goto("http://10.34.12.2:8012/accounts/login/")
        await page.fill("input[name='username']", "admin")
        await page.fill("input[name='password']", "admin")
        await page.click("button[type='submit']")
        await page.wait_for_url("**/workspace/")
        
        await page.goto("http://10.34.12.2:8012/events/")
        await page.wait_for_selector(".action-menu-toggle", state="visible")
        
        print("Clicking toggle...")
        await page.click(".action-menu-toggle >> nth=0")
        await asyncio.sleep(2)
        
        is_open = await page.evaluate("document.querySelectorAll('.k-action-dropdown.is-open').length")
        print(f"Open dropdowns: {is_open}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug())
