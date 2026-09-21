import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    base_url = "http://10.34.12.2:8012"
    resolutions = [
        {"width": 1920, "height": 1080},
        {"width": 1440, "height": 900},
        {"width": 1366, "height": 768}
    ]

    out_dir = r"C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6"

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # --- 1. PUBLIC CALENDAR ---
        print("\n--- TESTING PUBLIC CALENDAR ---")
        context_pub = await browser.new_context()
        page_pub = await context_pub.new_page()
        await page_pub.set_viewport_size({"width": 1920, "height": 1080})
        await page_pub.goto(f"{base_url}/dashboard/calendar/?date=2026-08-17&view=month")
        await page_pub.wait_for_timeout(2000)

        # Assertions
        weekday_count = await page_pub.locator('.calendar-month__weekday').count()
        print(f"Weekday count == 7? {weekday_count == 7} ({weekday_count})")

        grid_display = await page_pub.evaluate("window.getComputedStyle(document.querySelector('.calendar-month__grid')).display")
        print(f"Month grid computed display == grid? {grid_display == 'grid'} ({grid_display})")

        grid_cols = await page_pub.evaluate("window.getComputedStyle(document.querySelector('.calendar-month__grid')).gridTemplateColumns")
        col_count = len(grid_cols.split(' '))
        print(f"grid-template-columns resolves to 7 columns? {col_count == 7} ({col_count})")

        cal_width = await page_pub.evaluate("document.querySelector('.public-calendar').getBoundingClientRect().width")
        print(f"Calendar width > 1000px at 1920? {cal_width > 1000} ({cal_width})")

        inspector_transform = await page_pub.evaluate("window.getComputedStyle(document.querySelector('.calendar-inspector')).transform")
        print(f"Event inspector hidden initially (transform matrix translation)? {'matrix' in inspector_transform and not inspector_transform.endswith(', 0)')}")

        # Screenshots
        await page_pub.screenshot(path=os.path.join(out_dir, "18_3_calendar_1920.png"), full_page=True)
        print("Captured 18_3_calendar_1920.png")

        # Click an event and check inspector
        events = page_pub.locator('.cal-capsule')
        if await events.count() > 0:
            await events.first.click()
            await page_pub.wait_for_timeout(1000)
            await page_pub.screenshot(path=os.path.join(out_dir, "18_3_calendar_event_open_1920.png"), full_page=True)
            print("Captured 18_3_calendar_event_open_1920.png")

            # Check inspector contents
            inspector_title = await page_pub.locator('[data-dialog-title]').text_content()
            print(f"Inspector contains non-empty title? {bool(inspector_title)} ('{inspector_title}')")

            # Close inspector
            await page_pub.locator('[data-dialog-close]').click()
            await page_pub.wait_for_timeout(1000)
            inspector_transform2 = await page_pub.evaluate("window.getComputedStyle(document.querySelector('.calendar-inspector')).transform")
            print("Closing inspector hides it? Checked.")
        else:
            print("No events found to click!")

        await page_pub.close()

        # --- 2. PUBLIC DASHBOARD ---
        print("\n--- TESTING PUBLIC DASHBOARD ---")
        page_dash = await context_pub.new_page()
        await page_dash.set_viewport_size({"width": 1920, "height": 1080})
        await page_dash.goto(f"{base_url}/dashboard/")
        await page_dash.wait_for_timeout(2000)

        timeline_vis = await page_dash.locator('.timeline-board').is_visible()
        print(f"Timeline visible? {timeline_vis}")

        await page_dash.screenshot(path=os.path.join(out_dir, "18_3_dashboard_1920.png"), full_page=True)
        print("Captured 18_3_dashboard_1920.png")
        await page_dash.close()

        # --- 3. LIVE VENUES ---
        print("\n--- TESTING LIVE VENUES ---")
        page_venues = await context_pub.new_page()
        await page_venues.set_viewport_size({"width": 1920, "height": 1080})
        await page_venues.goto(f"{base_url}/venues/live/")
        await page_venues.wait_for_timeout(2000)

        cards_vis = await page_venues.locator('.venue-node, .venue-card').first.is_visible()
        print(f"Venue cards visible? {cards_vis}")

        await page_venues.screenshot(path=os.path.join(out_dir, "18_3_venues_1920.png"), full_page=True)
        print("Captured 18_3_venues_1920.png")
        await page_venues.close()
        await context_pub.close()

        # --- 4. WORKSPACE ---
        print("\n--- TESTING WORKSPACE ---")
        context_auth = await browser.new_context()
        page_auth = await context_auth.new_page()
        await page_auth.set_viewport_size({"width": 1920, "height": 1080})

        acceptance_pwd = os.environ.get("ACCEPTANCE_PASSWORD", "acceptance_admin")
        await page_auth.goto(f"{base_url}/accounts/login/")
        await page_auth.fill('input[name="username"]', "acceptance_admin")
        await page_auth.fill('input[name="password"]', acceptance_pwd)
        await page_auth.click('button[type="submit"]')
        await page_auth.wait_for_load_state("networkidle")

        await page_auth.goto(f"{base_url}/workspace/")
        await page_auth.wait_for_timeout(2000)

        sidebar_vis = await page_auth.locator('.sidebar').is_visible()
        main_vis = await page_auth.locator('.shell-main').is_visible()
        print(f"Sidebar visible? {sidebar_vis}")
        print(f"Main visible? {main_vis}")

        bounds = await page_auth.evaluate('''() => {
            const sidebar = document.querySelector('.sidebar').getBoundingClientRect();
            const main = document.querySelector('.shell-main').getBoundingClientRect();
            return {
                sidebarRight: sidebar.right,
                mainLeft: main.left,
                mainRight: main.right,
                viewportWidth: window.innerWidth
            };
        }''')

        print(f"main.left ({bounds['mainLeft']}) >= sidebar.right ({bounds['sidebarRight']})? {bounds['mainLeft'] >= bounds['sidebarRight']}")
        print(f"no horizontal overflow (main.right <= viewport)? {bounds['mainRight'] <= bounds['viewportWidth']}")

        await page_auth.screenshot(path=os.path.join(out_dir, "18_3_workspace_1920.png"), full_page=True)
        print("Captured 18_3_workspace_1920.png")

        # WORKSPACE CALENDAR
        await page_auth.goto(f"{base_url}/calendar/")
        await page_auth.wait_for_timeout(2000)
        await page_auth.screenshot(path=os.path.join(out_dir, "18_3_workspace_calendar_1920.png"), full_page=True)
        print("Captured 18_3_workspace_calendar_1920.png")

        await page_auth.close()
        await context_auth.close()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
