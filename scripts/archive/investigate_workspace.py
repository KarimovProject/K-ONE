import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        await page.goto("http://10.34.12.2:8012/workspace/")
        if "login" in page.url:
            await page.fill("input[name='username']", "admin")
            await page.fill("input[name='password']", "admin")
            await page.click("button[type='submit']")
            await page.wait_for_url("**/workspace/**")

        js_code = """
        () => {
            let shell = document.querySelector('.app-shell');
            if(!shell) return 'No .app-shell found';
            let comp = window.getComputedStyle(shell);
            let sidebar = document.querySelector('.sidebar');
            let s_rect = sidebar ? sidebar.getBoundingClientRect() : null;
            let main = document.querySelector('.shell-main');
            let m_rect = main ? main.getBoundingClientRect() : null;
            return {
                gridColumns: comp.gridTemplateColumns,
                sidebar_rect: s_rect,
                main_rect: m_rect
            };
        }
        """
        res = await page.evaluate(js_code)
        print("At 1920x1080:")
        print(res)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
