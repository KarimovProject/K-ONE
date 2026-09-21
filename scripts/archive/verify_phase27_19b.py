import asyncio
import sys
from playwright.async_api import async_playwright

async def run():
    print("Starting Live Runtime Verification...")
    async with async_playwright() as p:
        b = await p.chromium.launch()
        # Cache disabled implicitly by fresh context, but let's be explicit
        c = await b.new_context(viewport={'width': 1920, 'height': 1080}, ignore_https_errors=True)
        page = await c.new_page()

        # Route to block caching
        await page.route("**/*", lambda route: route.continue_())

        print("Navigating to http://127.0.0.1:8001/accounts/login/ ...")
        res = await page.goto('http://127.0.0.1:8001/accounts/login/')
        await page.wait_for_load_state('networkidle')
        
        if res.status != 200:
            print(f"FAIL: Expected 200, got {res.status}")
            sys.exit(1)

        # 1. Assert old poster is absent
        old_poster = await page.locator(".login-story").count()
        if old_poster > 0:
            print("FAIL: Old giant poster (.login-story) is STILL PRESENT!")
            sys.exit(1)
        else:
            print("PASS: Old giant poster is absent.")

        # 2. Assert UZ, RU, EN are visible
        for lang in ['uz', 'ru', 'en']:
            btn = page.locator(f"button[name='language'][value='{lang}']")
            if not await btn.is_visible():
                print(f"FAIL: Language button {lang} is not visible.")
                sys.exit(1)
        print("PASS: UZ, RU, EN buttons are visible.")

        # 3. Assert theme toggle is visible
        theme_toggle = page.locator(".auth-theme-toggle")
        if not await theme_toggle.is_visible():
            print("FAIL: Theme toggle is not visible.")
            sys.exit(1)
        print("PASS: Theme toggle is visible.")

        # 4. Assert password-eye toggle is visible
        eye = page.locator(".auth-password-toggle")
        if not await eye.is_visible():
            print("FAIL: Password eye toggle is not visible.")
            sys.exit(1)
        print("PASS: Password eye toggle is visible.")

        # 5. Assert full-width login button
        btn = page.locator(".auth-submit-btn")
        if not await btn.is_visible():
            print("FAIL: Login button is not visible.")
            sys.exit(1)
        btn_box = await btn.bounding_box()
        form_box = await page.locator(".auth-form").bounding_box()
        if abs(btn_box['width'] - form_box['width']) > 2:
            print(f"FAIL: Login button is not full width. Button: {btn_box['width']}, Form: {form_box['width']}")
            sys.exit(1)
        print("PASS: Login button is full width.")

        # 6. Capture screenshot
        await page.screenshot(path="C:\\IEMS\\qa_screenshots\\27_19b_live_runtime_login.png")
        print("Captured screenshot of the live runtime.")

        # 7. Verify login redirect
        await page.fill("input[name='username']", "acceptance_admin")
        await page.fill("input[name='password']", "K-ONE-admin-2026!")
        await page.click(".auth-submit-btn")
        
        await page.wait_for_load_state('networkidle')
        
        url = page.url
        if "login" in url:
            print(f"FAIL: Login failed or did not redirect. Current URL: {url}")
            sys.exit(1)
        else:
            print(f"PASS: Login successful. Redirected to {url}")
            await page.screenshot(path="C:\\IEMS\\qa_screenshots\\27_19b_live_runtime_workspace.png")

        await b.close()
        print("All runtime checks passed successfully!")

asyncio.run(run())
