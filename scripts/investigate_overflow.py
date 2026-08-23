import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"
ROUTES = ["/dashboard/", "/dashboard/calendar/"]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 390, "height": 844})
        page = await context.new_page()

        print("Authenticating...")
        await page.goto(f"{BASE_URL}/workspace/")
        if "login" in page.url:
            await page.fill("input[name='username']", "admin")
            await page.fill("input[name='password']", "admin")
            await page.click("button[type='submit']")
            await page.wait_for_url("**/workspace/**")

        for route in ROUTES:
            await page.goto(f"{BASE_URL}{route}", wait_until="networkidle")
            await asyncio.sleep(1)
            
            # Temporarily remove overflow-x: hidden from html/body to expose the overflow
            await page.evaluate("document.documentElement.style.overflowX = 'visible'")
            await page.evaluate("document.body.style.overflowX = 'visible'")
            
            scroll_width = await page.evaluate("document.documentElement.scrollWidth")
            inner_width = await page.evaluate("window.innerWidth")
            
            print(f"--- {route} ---")
            print(f"ScrollWidth: {scroll_width}, InnerWidth: {inner_width}")
            
            if scroll_width > inner_width:
                js_code = """
                () => {
                    let w = window.innerWidth;
                    let els = document.querySelectorAll('*');
                    let offenders = [];
                    for(let el of els) {
                        let rect = el.getBoundingClientRect();
                        if (rect.width > w || rect.right > w) {
                            let comp = window.getComputedStyle(el);
                            offenders.push({
                                tag: el.tagName,
                                id: el.id,
                                cls: el.className,
                                right: rect.right,
                                width: rect.width,
                                compWidth: comp.width,
                                border: comp.border,
                                boxSizing: comp.boxSizing
                            });
                        }
                    }
                    let debug = [];
                    let main = document.querySelector('.public-main');
                    if (main) {
                        let c = window.getComputedStyle(main);
                        debug.push(`MAIN: W=${main.getBoundingClientRect().width}, Pad=${c.padding}, MinW=${c.minWidth}, Flex=${c.flex}`);
                    }
                    let kpi_rail = document.querySelector('.kpi-rail');
                    if (kpi_rail) {
                        let c = window.getComputedStyle(kpi_rail);
                        let r = kpi_rail.getBoundingClientRect();
                        debug.push(`KPI_RAIL: W=${r.width}, Right=${r.right}, Pad=${c.padding}, Margin=${c.margin}, Disp=${c.display}`);
                    }
                    let shell = document.querySelector('.dashboard-shell');
                    if (shell) {
                        let c = window.getComputedStyle(shell);
                        let r = shell.getBoundingClientRect();
                        debug.push(`DASH_SHELL: W=${r.width}, Right=${r.right}, Pad=${c.padding}, Margin=${c.margin}`);
                    }
                    return { offenders, debug };
                }
                """
                res = await page.evaluate(js_code)
                for d in res['debug']:
                    print(d)
                for o in res['offenders']:
                    if o['width'] > 390 or o['right'] > 390:
                        print(f"Offender: {o['tag']} .{o['cls']}")
                        print(f"  Right: {o['right']}, Width: {o['width']}, CompWidth: {o['compWidth']}")
                        print(f"  Box-Sizing: {o['boxSizing']}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
