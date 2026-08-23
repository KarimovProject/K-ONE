import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        c = await b.new_context(viewport={'width': 1920, 'height': 1080})
        page = await c.new_page()
        await page.goto('http://127.0.0.1:8001/accounts/login/')
        await page.wait_for_load_state('networkidle')
        
        # Reloading to make sure CSS is updated
        await page.reload()
        await page.wait_for_load_state('networkidle')
        
        style = await page.evaluate("window.getComputedStyle(document.querySelector('.auth-input')).paddingLeft")
        print('paddingLeft:', style)
        
        html = await page.evaluate("document.querySelector('.auth-input').outerHTML")
        print('html:', html)
        
        css_text = await page.evaluate("window.getComputedStyle(document.querySelector('.auth-input')).cssText")
        print('css_text includes padding-left:', 'padding-left' in css_text)
        
        # Get all stylesheets
        sheets = await page.evaluate("""() => {
            return Array.from(document.styleSheets).map(s => s.href).join(', ');
        }""")
        print('Stylesheets:', sheets)
        
        await b.close()

asyncio.run(run())
