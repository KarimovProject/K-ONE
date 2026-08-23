import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ----------------------------------------------------
        # 1. DESKTOP 1920x1080
        # ----------------------------------------------------
        context_1920 = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context_1920.new_page()

        print("Testing Login 1920...")
        await page.goto('http://10.34.12.2:8012/accounts/login/')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='phase19_4_login_1920.png', full_page=True)

        # LOGIN CHECKS
        left_box = await page.locator('.auth-brand-panel').bounding_box()
        right_box = await page.locator('.auth-form-panel').bounding_box()
        assert left_box['width'] > 700, f"Login left panel width {left_box['width']} <= 700"
        assert right_box['width'] > 700, f"Login right panel width {right_box['width']} <= 700"

        print("Testing Public Dashboard 1920...")
        await page.goto('http://10.34.12.2:8012/dashboard/')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='phase19_4_dashboard_1920.png', full_page=True)

        # DASHBOARD CHECKS
        kpi_box = await page.locator('.kpi-rail').bounding_box()
        timeline_box = await page.locator('.timeline-panel').bounding_box()
        venue_box = await page.locator('.venues-panel').bounding_box()
        logo_box = await page.locator('.brand-logo-public').bounding_box()

        assert kpi_box['width'] > 800, f"KPI rail width {kpi_box['width']} <= 800"
        assert timeline_box['width'] > 700, f"Timeline width {timeline_box['width']} <= 700"
        assert venue_box['x'] > timeline_box['x'] + timeline_box['width'] - 50, f"Venue not beside timeline"
        assert 60 <= logo_box['width'] <= 130, f"Logo width {logo_box['width']} not in 60-130 range"

        # Navigation
        nav_btns = page.locator('.public-main-nav .nav-btn')
        assert await nav_btns.count() == 3, f"Nav buttons count != 3 (got {await nav_btns.count()})"

        print("Testing Public Calendar 1920...")
        await page.goto('http://10.34.12.2:8012/dashboard/calendar/?date=2026-08-17&view=month')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='phase19_4_calendar_1920.png', full_page=True)

        # CALENDAR CHECKS
        toolbar_left = await page.locator('.calendar-command-bar__left').bounding_box()
        toolbar_right = await page.locator('.calendar-command-bar__right').bounding_box()
        assert abs(toolbar_left['y'] - toolbar_right['y']) < 20, "Calendar toolbar not horizontal"

        grid_box = await page.locator('.calendar-month__header').bounding_box()
        day_box = await page.locator('.calendar-month__weekday').first.bounding_box()
        assert (grid_box['width'] / day_box['width']) >= 6.8, "Grid does not have 7 columns"

        create_btn = await page.locator('.btn-create-event').bounding_box()
        assert create_btn['width'] > 80, "Create event CTA button missing or collapsed"

        print("Testing Public Live Venues 1920...")
        await page.goto('http://10.34.12.2:8012/venues/live/')
        await page.wait_for_timeout(1000)
        await page.screenshot(path='phase19_4_live_1920.png', full_page=True)

        venue_cards = page.locator('.live-venue-card')
        assert await venue_cards.count() >= 1, "No live venue cards rendered"

        await context_1920.close()

        # ----------------------------------------------------
        # 2. LAPTOP 1366x768
        # ----------------------------------------------------
        context_1366 = await browser.new_context(viewport={'width': 1366, 'height': 768})
        page_1366 = await context_1366.new_page()

        print("Capturing 1366x768 layouts...")
        await page_1366.goto('http://10.34.12.2:8012/dashboard/')
        await page_1366.wait_for_timeout(800)
        await page_1366.screenshot(path='phase19_4_dashboard_1366.png', full_page=True)

        await page_1366.goto('http://10.34.12.2:8012/dashboard/calendar/?date=2026-08-17&view=month')
        await page_1366.wait_for_timeout(800)
        await page_1366.screenshot(path='phase19_4_calendar_1366.png', full_page=True)

        await page_1366.goto('http://10.34.12.2:8012/venues/live/')
        await page_1366.wait_for_timeout(800)
        await page_1366.screenshot(path='phase19_4_live_1366.png', full_page=True)

        await page_1366.goto('http://10.34.12.2:8012/accounts/login/')
        await page_1366.wait_for_timeout(800)
        await page_1366.screenshot(path='phase19_4_login_1366.png', full_page=True)

        await context_1366.close()

        # ----------------------------------------------------
        # 3. MOBILE 390x844
        # ----------------------------------------------------
        context_mobile = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
        )
        page_mobile = await context_mobile.new_page()

        print("Capturing 390x844 mobile layouts...")
        await page_mobile.goto('http://10.34.12.2:8012/dashboard/')
        await page_mobile.wait_for_timeout(800)
        await page_mobile.screenshot(path='phase19_4_dashboard_390.png', full_page=True)

        await page_mobile.goto('http://10.34.12.2:8012/dashboard/calendar/?date=2026-08-17&view=month')
        await page_mobile.wait_for_timeout(800)
        await page_mobile.screenshot(path='phase19_4_calendar_390.png', full_page=True)

        await page_mobile.goto('http://10.34.12.2:8012/venues/live/')
        await page_mobile.wait_for_timeout(800)
        await page_mobile.screenshot(path='phase19_4_live_390.png', full_page=True)

        await page_mobile.goto('http://10.34.12.2:8012/accounts/login/')
        await page_mobile.wait_for_timeout(800)
        await page_mobile.screenshot(path='phase19_4_login_390.png', full_page=True)

        await context_mobile.close()
        await browser.close()

        print("All Phase 19.4 QA assertions and screenshot captures PASSED!")

if __name__ == '__main__':
    asyncio.run(main())
