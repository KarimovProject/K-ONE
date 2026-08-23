import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(viewport={'width': 1920, 'height': 1080})
        pg = await ctx.new_page()
        
        await pg.goto('http://127.0.0.1:8001/accounts/login/')
        await pg.wait_for_load_state('networkidle')
        
        ru_btn = pg.locator('.auth-lang-switch button', has_text='RU')
        async with pg.expect_navigation(wait_until="networkidle"):
            await ru_btn.click()
            
        body_text = await pg.inner_text("body")
        with open("body.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        
        await b.close()

if __name__ == '__main__':
    asyncio.run(main())
