import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        c = await b.new_context(viewport={'width': 1920, 'height': 1080})
        page = await c.new_page()

        await page.goto('http://127.0.0.1:8001/accounts/login/')
        await page.wait_for_load_state('networkidle')
        await page.fill("input[name='username']", "acceptance_admin")
        await page.fill("input[name='password']", "K-ONE-admin-2026!")
        await page.click(".auth-submit-btn")
        await page.wait_for_load_state('networkidle')
        
        html = await page.content()
        with open('workspace_dump.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        await page.screenshot(path="C:\\IEMS\\qa_screenshots\\27_20_workspace_bug.png")
        await b.close()

asyncio.run(run())
