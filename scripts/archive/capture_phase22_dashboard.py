import asyncio
import os
import shutil
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"
ARTIFACT_DIR = r"C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6"
BASELINE_DIR = r"C:\IEMS\tests\visual_baseline\phase22"
os.makedirs(BASELINE_DIR, exist_ok=True)

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for width, height, name_suffix in [(1920, 1080, "1920"), (1366, 768, "1366")]:
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                locale="uz-UZ"
            )
            page = await context.new_page()

            password = os.environ.get("IEMS_ACCEPTANCE_PASSWORD", "Password123!")
            await page.goto(f"{BASE_URL}/accounts/login/", wait_until="networkidle")
            await page.fill('input[name="username"]', "acceptance_admin")
            await page.fill('input[name="password"]', password)
            async with page.expect_navigation():
                await page.click('button[type="submit"]')
            await asyncio.sleep(0.5)

            shot_name = f"phase22_dashboard_{name_suffix}.png"
            local_path = os.path.join(BASELINE_DIR, shot_name)
            artifact_path = os.path.join(ARTIFACT_DIR, shot_name)

            await page.screenshot(path=local_path, full_page=False)
            shutil.copy2(local_path, artifact_path)
            print(f"Captured: {shot_name}")

            await context.close()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
