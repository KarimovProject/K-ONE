import asyncio

from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://10.34.12.2:8012/accounts/login/")
        await page.fill("input[name=username]", "qa_admin")
        await page.fill("input[name=password]", "password")
        await page.click("button[type=submit]")
        await page.wait_for_load_state("networkidle")
        print("URL AFTER LOGIN:", page.url)


asyncio.run(run())
