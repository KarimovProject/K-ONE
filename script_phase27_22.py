import asyncio
from playwright.async_api import async_playwright
import os

OUT_DIR = "C:/IEMS/tests/visual_baseline/phase27_22_release_gate"
os.makedirs(OUT_DIR, exist_ok=True)

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        
        # 1. Login 1920
        ctx_1920 = await b.new_context(viewport={"width": 1920, "height": 1080})
        page = await ctx_1920.new_page()
        await page.goto("http://10.34.12.2:8012/accounts/login/")
        await page.wait_for_selector("button[name='language'][value='uz']")
        await page.wait_for_selector(".auth-theme-toggle")
        await page.wait_for_selector(".auth-password-toggle")
        await page.screenshot(path=os.path.join(OUT_DIR, "01_login_1920.png"))
        
        # 2. Login 390
        ctx_390 = await b.new_context(viewport={"width": 390, "height": 844})
        p390 = await ctx_390.new_page()
        await p390.goto("http://10.34.12.2:8012/accounts/login/")
        await p390.screenshot(path=os.path.join(OUT_DIR, "02_login_390.png"))
        
        # Login and proceed
        await page.fill("input[name=username]", "acceptance_admin")
        await page.fill("input[name=password]", "K-ONE-admin-2026!")
        await page.click("button[type=submit]")
        await page.wait_for_url("**/workspace/")
        
        # 3. Workspace 1920
        await page.wait_for_selector(".exec-kpi-card")
        await page.screenshot(path=os.path.join(OUT_DIR, "03_workspace_1920.png"))
        
        # Cookie transfer for other viewports
        cookies = await ctx_1920.cookies()
        
        # 4. Workspace 768
        ctx_768 = await b.new_context(viewport={"width": 768, "height": 1024})
        await ctx_768.add_cookies(cookies)
        p768 = await ctx_768.new_page()
        await p768.goto("http://10.34.12.2:8012/workspace/")
        await p768.wait_for_selector(".exec-kpi-card")
        await p768.screenshot(path=os.path.join(OUT_DIR, "04_workspace_768.png"))
        
        # 5. Workspace 390
        await ctx_390.add_cookies(cookies)
        p390_ws = await ctx_390.new_page()
        await p390_ws.goto("http://10.34.12.2:8012/workspace/")
        await p390_ws.wait_for_selector(".exec-kpi-card")
        
        # Check overflow
        overflow = await p390_ws.evaluate("document.documentElement.scrollWidth > window.innerWidth")
        if overflow:
            print("ERROR: Horizontal overflow detected on 390px!")
        
        await p390_ws.screenshot(path=os.path.join(OUT_DIR, "05_workspace_390.png"))
        
        # 6. Workspace 390 Menu
        await p390_ws.click(".user-avatar-btn")
        await p390_ws.wait_for_selector(".user-dropdown-menu", state="visible")
        await p390_ws.screenshot(path=os.path.join(OUT_DIR, "06_workspace_390_menu.png"))
        
        await b.close()
        print("Screenshots captured successfully.")

asyncio.run(run())
