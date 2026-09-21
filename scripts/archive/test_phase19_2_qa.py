import asyncio
from playwright.async_api import async_playwright
import sys

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # DESKTOP
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        print("Testing Login 1920...")
        await page.goto('http://10.34.12.2:8012/accounts/login/')
        await page.wait_for_timeout(1000)

        # LOGIN ASSERTIONS
        left_box = await page.locator('.auth-brand-panel').bounding_box()
        right_box = await page.locator('.auth-form-panel').bounding_box()
        card_box = await page.locator('.login-card').bounding_box()
        btn_box = await page.locator('button[type="submit"]').bounding_box()
        input_box = await page.locator('input[name="username"]').bounding_box()
        skip_link_visible = await page.locator('.skip-link').is_visible()

        await page.screenshot(path='phase19_2_login_1920.png', full_page=True)

        assert left_box['width'] > 700, f"Left panel width {left_box['width']} <= 700"
        assert right_box['width'] > 700, f"Right panel width {right_box['width']} <= 700"
        assert 380 <= card_box['width'] <= 520, f"Card width {card_box['width']} not in 380-520"
        assert btn_box['width'] > 300, f"Button width {btn_box['width']} <= 300"
        assert input_box['height'] >= 48, f"Input height {input_box['height']} < 48"
        skip_box = await page.locator('.skip-link').bounding_box()
        assert skip_box['y'] < 0, f"Skip link is leaking into viewport: {skip_box['y']}"
        assert await page.locator('input[name="username"]').input_value() == "", "Username is prefilled"

        print("Testing Public Dashboard 1920...")
        await page.goto('http://10.34.12.2:8012/dashboard/')
        await page.wait_for_timeout(1000)

        # DASHBOARD ASSERTIONS
        kpi_box = await page.locator('.kpi-rail').bounding_box()
        timeline_box = await page.locator('.timeline-panel').bounding_box()
        venue_box = await page.locator('.venues-panel').bounding_box()

        assert kpi_box['width'] > 800, f"KPI rail width {kpi_box['width']} <= 800"
        assert timeline_box['width'] > 700, f"Timeline width {timeline_box['width']} <= 700"
        # Venue region positioned beside timeline (X of venue should be > X + width of timeline - margin)
        assert venue_box['x'] > timeline_box['x'] + timeline_box['width'], f"Venue not beside timeline"

        # NAV ASSERTIONS
        nav_btns = page.locator('.public-main-nav .nav-btn')
        assert await nav_btns.count() == 3, "Nav buttons != 3"
        nav_box_1 = await nav_btns.nth(0).bounding_box()
        nav_box_2 = await nav_btns.nth(1).bounding_box()
        assert nav_box_1['width'] > 0, "Nav btn width is 0"
        assert nav_box_1['y'] == nav_box_2['y'], "Nav is not horizontal"

        await page.screenshot(path='phase19_2_dashboard_1920.png', full_page=True)

        print("Testing Public Calendar 1920...")
        await page.goto('http://10.34.12.2:8012/dashboard/calendar/?date=2026-08-17&view=month')
        await page.wait_for_timeout(1000)

        # CALENDAR ASSERTIONS
        toolbar_left = await page.locator('.calendar-command-bar__left').bounding_box()
        toolbar_right = await page.locator('.calendar-command-bar__right').bounding_box()
        assert abs(toolbar_left['y'] - toolbar_right['y']) < 15, f"Calendar toolbar not horizontal: left Y={toolbar_left['y']}, right Y={toolbar_right['y']}"

        grid_box = await page.locator('.calendar-month__header').bounding_box()
        # Ensure grid columns are 7 (by checking day widths)
        day_box = await page.locator('.calendar-month__weekday').first.bounding_box()
        assert day_box['width'] > 0 and (grid_box['width'] / day_box['width']) >= 6.8, "Grid does not have 7 columns"

        search_box = await page.locator('input[type="search"]').bounding_box()
        assert search_box['height'] >= 38, "Search input not styled properly"

        drawer_box = await page.locator('.inspector-panel').bounding_box()
        # Drawer should be translated off-screen, or inspector-panel should be hidden.
        # Fixed: we moved the translation to inspector-panel. Its X should be outside viewport or offscreen
        is_open = await page.locator('.calendar-inspector').evaluate('el => el.classList.contains("is-open")')
        assert not is_open, "Inspector drawer is open initially"

        await page.screenshot(path='phase19_2_calendar_1920.png', full_page=True)

        print("Testing Live 1920...")
        await page.goto('http://10.34.12.2:8012/venues/live/')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='phase19_2_live_1920.png', full_page=True)

        # Login for Workspace
        print("Logging in for Workspace...")
        await page.goto('http://10.34.12.2:8012/accounts/login/')
        await page.fill('input[name="username"]', 'admin')
        await page.fill('input[name="password"]', 'admin')
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(1000)

        print("Testing Workspace 1920...")
        await page.goto('http://10.34.12.2:8012/workspace/')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='phase19_2_workspace_1920.png', full_page=True)

        # Desktop 1366
        context_1366 = await browser.new_context(viewport={'width': 1366, 'height': 768})
        page_1366 = await context_1366.new_page()

        await page_1366.goto('http://10.34.12.2:8012/dashboard/')
        await page_1366.wait_for_timeout(1000)
        await page_1366.screenshot(path='phase19_2_dashboard_1366.png', full_page=True)

        await page_1366.goto('http://10.34.12.2:8012/dashboard/calendar/?date=2026-08-17&view=month')
        await page_1366.wait_for_timeout(1000)
        await page_1366.screenshot(path='phase19_2_calendar_1366.png', full_page=True)

        await context_1366.close()

        # Mobile 390
        context_mobile = await browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        page_mobile = await context_mobile.new_page()

        await page_mobile.goto('http://10.34.12.2:8012/accounts/login/')
        await page_mobile.wait_for_timeout(1000)
        await page_mobile.screenshot(path='phase19_2_login_390.png', full_page=True)

        await context_mobile.close()

        await context.close()
        await browser.close()

        print("All assertions passed!")

if __name__ == '__main__':
    asyncio.run(main())
