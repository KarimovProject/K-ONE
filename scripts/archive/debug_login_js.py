"""Quick debug of login JS."""
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(viewport={"width": 1920, "height": 1080})
        pg = await ctx.new_page()

        await pg.goto("http://127.0.0.1:8001/accounts/login/")
        await pg.wait_for_load_state("networkidle")

        # Check theme attribute
        theme = await pg.evaluate("document.documentElement.getAttribute('data-theme')")
        print(f"Initial theme: {theme}")

        # Check password field
        pw_id = await pg.locator("input[name='password']").get_attribute("id")
        print(f"Password ID: {pw_id}")

        pw_type = await pg.locator("input[name='password']").get_attribute("type")
        print(f"PW type before: {pw_type}")

        # Try clicking password toggle
        toggle = pg.locator("[data-password-toggle]")
        print(f"Toggle count: {await toggle.count()}")
        print(f"Toggle visible: {await toggle.is_visible()}")

        await toggle.click()
        await pg.wait_for_timeout(500)
        pw_type2 = await pg.locator("input[name='password']").get_attribute("type")
        print(f"PW type after toggle click: {pw_type2}")

        # Try clicking theme button
        theme_btn = pg.locator("#auth-theme-toggle")
        print(f"Theme btn count: {await theme_btn.count()}")
        print(f"Theme btn visible: {await theme_btn.is_visible()}")

        await theme_btn.click()
        await pg.wait_for_timeout(500)
        theme2 = await pg.evaluate("document.documentElement.getAttribute('data-theme')")
        print(f"Theme after click: {theme2}")

        # Check if JS errors exist
        errors = []
        pg.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        await pg.reload()
        await pg.wait_for_load_state("networkidle")
        await pg.wait_for_timeout(500)
        print(f"Console errors: {errors}")

        # Check the rendered script source
        scripts = await pg.evaluate("""
            Array.from(document.querySelectorAll('script')).map(s => s.textContent.substring(0, 200))
        """)
        for i, s in enumerate(scripts):
            if s.strip():
                print(f"Script {i}: {s[:200]}")

        await b.close()

asyncio.run(run())
