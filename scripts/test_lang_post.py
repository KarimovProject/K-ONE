import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(viewport={'width': 1920, 'height': 1080})
        pg = await ctx.new_page()
        
        await pg.goto('http://127.0.0.1:8001/accounts/login/')
        
        reqs = []
        pg.on('request', lambda r: reqs.append((r.url, r.post_data)) if r.method == 'POST' else None)
        
        ru_btn = pg.locator('.auth-lang-switch button', has_text='RU')
        async with pg.expect_navigation():
            await ru_btn.click()
            
        print("Requests:", reqs)
        await b.close()

if __name__ == '__main__':
    asyncio.run(main())
