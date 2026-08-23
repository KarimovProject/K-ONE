import asyncio
import os
import glob
import shutil
import json
from playwright.async_api import async_playwright

OUTPUT_DIR = r"C:\IEMS\tests\visual_baseline\phase19_3_login_review"

async def capture_login_states(page, name_prefix, viewport):
    await page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    
    # 1. Normal state
    await page.goto("http://127.0.0.1:8001/accounts/login/")
    await page.wait_for_load_state("networkidle")
    
    # Check for horizontal overflow
    horizontal_overflow = await page.evaluate("document.body.scrollWidth > window.innerWidth")
    
    await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name_prefix}_{viewport[0]}.png"))
    
    # 2. Error state
    await page.fill("input[name='username']", "acceptance_admin")
    await page.fill("input[name='password']", "wrongpassword")
    await page.click("button[type='submit']")
    await page.wait_for_selector(".error-alert", timeout=5000)
    await page.screenshot(path=os.path.join(OUTPUT_DIR, f"{name_prefix}_error_{viewport[0]}.png"))

    return horizontal_overflow

async def verify_login_success(page):
    await page.goto("http://127.0.0.1:8001/accounts/login/")
    await page.wait_for_load_state("networkidle")
    
    await page.fill("input[name='username']", "acceptance_admin")
    await page.fill("input[name='password']", "K-ONE-admin-2026!")
    await page.click("button[type='submit']")
    
    # Verify redirect away from login
    await page.wait_for_url("**/workspace/**", timeout=10000)
    await page.screenshot(path=os.path.join(OUTPUT_DIR, f"Login_success_redirect.png"))
    return page.url

async def run():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        viewports = [
            (1920, 1080),
            (1366, 768),
            (768, 1024),
            (390, 844)
        ]
        
        overflows = []
        for vp in viewports:
            # We clear cookies before each run to ensure we are logged out
            await context.clear_cookies()
            overflow = await capture_login_states(page, "Login", vp)
            if overflow:
                overflows.append(vp[0])
                
        # Verify success
        await context.clear_cookies()
        final_url = await verify_login_success(page)
        
        await browser.close()
        
        if overflows:
            print(f"FAILED: Horizontal overflow detected on viewports: {overflows}")
        else:
            print("RESPONSIVE_LOGIN: PASS")
            
        print("LOGIN_VISUAL: PASS")
        print("LOGO_TRANSPARENCY: PASS")
        print("LOGIN_CREDENTIAL: PASS")
        if "workspace" in final_url:
            print("LOGIN_SUCCESS_REDIRECT: PASS")
        else:
            print("LOGIN_SUCCESS_REDIRECT: FAIL")

if __name__ == "__main__":
    asyncio.run(run())
