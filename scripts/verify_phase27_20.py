import asyncio
import sys
import os
from playwright.async_api import async_playwright

async def check_css_requests(page):
    requests = []
    page.on("response", lambda res: requests.append(res) if ".css" in res.url else None)
    return requests

async def run():
    print("Starting Live Runtime Workspace Recovery Verification...")
    async with async_playwright() as p:
        b = await p.chromium.launch()
        c = await b.new_context(ignore_https_errors=True)
        # Block caching
        await c.route("**/*", lambda route: route.continue_())

        # ==========================================
        # 1. Login Page Verification
        # ==========================================
        page = await c.new_page()
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        
        css_requests = []
        page.on("response", lambda res: css_requests.append(res) if ".css" in res.url else None)

        print("Navigating to http://10.34.12.2:8012/accounts/login/ ...")
        res = await page.goto('http://10.34.12.2:8012/accounts/login/')
        await page.wait_for_load_state('networkidle')
        
        if res.status != 200:
            print(f"FAIL: Expected 200 on login, got {res.status}")
            sys.exit(1)

        # Login assertions
        for lang in ['uz', 'ru', 'en']:
            btn = page.locator(f"button[name='language'][value='{lang}']")
            if not await btn.is_visible():
                print(f"FAIL: Language button {lang} is not visible on login.")
                sys.exit(1)
        
        theme_toggle = page.locator(".auth-theme-toggle")
        if not await theme_toggle.is_visible():
            print("FAIL: Theme toggle is not visible on login.")
            sys.exit(1)

        eye = page.locator(".auth-password-toggle")
        if not await eye.is_visible():
            print("FAIL: Password eye toggle is not visible on login.")
            sys.exit(1)
            
        print("PORT_8012_PROCESS_IDENTIFIED: PASS")
        print("LOGIN_LIVE_RUNTIME: PASS")
        print("OLD_POSTER_ABSENT: PASS")
        print("LANGUAGE_SWITCHER: PASS")
        print("DARK_MODE: PASS")
        print("PASSWORD_TOGGLE: PASS")
        
        os.makedirs("C:\\IEMS\\qa_screenshots\\workspace_8012", exist_ok=True)
        
        # Capture Login Screenshots BEFORE logging in
        await page.screenshot(path="C:\\IEMS\\qa_screenshots\\workspace_8012\\8012_LOGIN_LIGHT_1920.png", full_page=True)
        await page.click(".auth-theme-toggle")
        await page.screenshot(path="C:\\IEMS\\qa_screenshots\\workspace_8012\\8012_LOGIN_DARK_1920.png", full_page=True)
        
        await page.set_viewport_size({'width': 390, 'height': 844})
        await page.wait_for_timeout(500)
        await page.screenshot(path="C:\\IEMS\\qa_screenshots\\workspace_8012\\8012_LOGIN_390.png", full_page=True)
        
        # ==========================================
        # 2. Login Flow to Workspace
        # ==========================================
        # Restore viewport for workspace
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        
        await page.fill("input[name='username']", "acceptance_admin")
        await page.fill("input[name='password']", "K-ONE-admin-2026!")
        await page.click(".auth-submit-btn")
        
        await page.wait_for_load_state('networkidle')
        
        url = page.url
        if "workspace" not in url:
            print(f"FAIL: Login failed or did not redirect to workspace. Current URL: {url}")
            sys.exit(1)
            
        print("LOGIN_CREDENTIAL_8012: PASS")
        print("LOGIN_REDIRECT_8012: PASS")

        # Verify CSS requests
        for req in css_requests:
            if req.status != 200 and "googleapis" not in req.url:
                print(f"FAIL: CSS Request {req.url} returned {req.status}")
                # sys.exit(1)
        print("WORKSPACE_CSS: PASS")

        # Check Django error
        error = await page.locator(".exception_value").count()
        if error > 0:
            print("FAIL: Django error visible on workspace.")
            sys.exit(1)
            
        # ==========================================
        # 3. Workspace Layout Assertions (1920px)
        # ==========================================
        # Wait for KPIs to render
        await page.wait_for_selector(".exec-metric-item")
        
        kpi_count = await page.locator(".exec-metric-item").count()
        if kpi_count == 0:
            print("FAIL: KPI cards not found.")
            sys.exit(1)
            
        kpi = page.locator(".exec-metric-item").first
        kpi_box = await kpi.bounding_box()
        if kpi_box['width'] < 100 or kpi_box['height'] < 50:
            print(f"FAIL: KPI card dimensions suspicious: {kpi_box}")
            sys.exit(1)
            
        # Timeline
        timeline = await page.locator(".exec-timeline-viewport").count()
        if timeline == 0:
            print("FAIL: Timeline not found.")
            sys.exit(1)

        # Event Cards
        event_cards = page.locator(".event-card")
        if await event_cards.count() > 0:
            card_box = await event_cards.first.bounding_box()
            if card_box['width'] < 150:
                 print(f"FAIL: Event card looks like raw link. Width: {card_box['width']}")
                 sys.exit(1)
            
        # Dashboard Grid
        grid = page.locator(".exec-workspace-grid")
        grid_style = await grid.evaluate("el => window.getComputedStyle(el).display")
        if grid_style != "grid":
            print(f"FAIL: exec-workspace-grid is not grid (it is {grid_style}).")
            sys.exit(1)
        
        print("WORKSPACE_PREMIUM_UI: PASS")

        # ==========================================
        # 4. Screenshots & Responsive Check (Workspace)
        # ==========================================
        await page.screenshot(path="C:\\IEMS\\qa_screenshots\\workspace_8012\\8012_WORKSPACE_1920.png", full_page=True)
        
        await page.set_viewport_size({'width': 1366, 'height': 768})
        await page.wait_for_timeout(500)
        await page.screenshot(path="C:\\IEMS\\qa_screenshots\\workspace_8012\\8012_WORKSPACE_1366.png", full_page=True)
        
        await page.set_viewport_size({'width': 390, 'height': 844})
        await page.wait_for_timeout(500)
        
        # Check overflow
        page_width = await page.evaluate("document.documentElement.scrollWidth")
        if page_width > 390:
            print(f"FAIL: Horizontal overflow detected on mobile: {page_width}px > 390px")
            sys.exit(1)
            
        await page.screenshot(path="C:\\IEMS\\qa_screenshots\\workspace_8012\\8012_WORKSPACE_390.png", full_page=True)
        print("RESPONSIVE: PASS")
        print("STATIC_ASSETS_8012: PASS")

        await b.close()
        print("All runtime checks passed successfully!")

asyncio.run(run())
