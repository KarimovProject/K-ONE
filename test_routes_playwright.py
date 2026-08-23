import asyncio
from playwright.async_api import async_playwright
import sys

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context()
        page = await ctx.new_page()

        res = await page.goto("http://10.34.12.2:8012/accounts/login/")
        print(f"Login GET: {res.status}")
        
        await page.fill("input[name=username]", "acceptance_admin")
        await page.fill("input[name=password]", "K-ONE-admin-2026!")
        await page.click("button[type=submit]")
        await page.wait_for_url("**/workspace/*")
        print("Login POST: PASS")
        
        routes = [
            "/workspace/",
            "/events/",
            "/dashboard/calendar/",
            "/venues/",
            "/master-data/event-types/",
            "/master-data/organizations/",
            "/master-data/sponsors/",
            "/master-data/speakers/",
            "/publications/",
            "/leadership/",
            "/reporting/"
        ]

        for r in routes:
            res = await page.goto(f"http://10.34.12.2:8012{r}")
            print(f"GET {r}: {res.status}")
            
        await b.close()

asyncio.run(run())
