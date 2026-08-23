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
            scroll_width = await page.evaluate("document.documentElement.scrollWidth")
            inner_width = await page.evaluate("window.innerWidth")
            if scroll_width > inner_width:
                print(f"[FAIL] {route} - OVERFLOW: {scroll_width} > {inner_width}")
                
                # Find offending elements
                js_code = """
                () => {
                    let w = window.innerWidth;
                    let els = document.querySelectorAll('*');
                    let offenders = [];
                    for(let el of els) {
                        let rect = el.getBoundingClientRect();
                        if (rect.right > w) {
                            offenders.push(el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + el.className.split(' ').join('.') : ''));
                        }
                    }
                    return offenders;
                }
                """
                offenders = await page.evaluate(js_code)
                print("Offending elements:", offenders)
            else:
                print(f"[PASS] {route} - No overflow ({scroll_width} <= {inner_width})")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
