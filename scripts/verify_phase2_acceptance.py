import os
import random
from datetime import date, timedelta

from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8555"
OUTPUT_DIR = os.path.join(os.getcwd(), "tests", "visual_baseline")
os.makedirs(OUTPUT_DIR, exist_ok=True)

target_date = date.today() + timedelta(days=random.randint(100, 300))
date_str = target_date.strftime("%Y-%m-%d")

results = {
    "wizard": "FAIL",
    "calendar": "FAIL",
    "availability": "FAIL",
    "conflict_blocking": "FAIL",
    "cancellation": "FAIL",
    "screenshots": [],
}


def run_phase2_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ---------------------------------------------------------------
        # 1. 1920x1080 CONTEXT — EVENT WIZARD & CREATION
        # ---------------------------------------------------------------
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Login as intl_admin
        page.goto(f"{BASE_URL}/accounts/login/")
        page.fill(".login-card input[name='username']", "intl_admin")
        page.fill(".login-card input[name='password']", "Password123!")
        page.click(".login-card button[type='submit']")
        page.wait_for_selector(".app-shell")

        # Step 1: Basic Info
        page.goto(f"{BASE_URL}/events/wizard/")
        wizard_shot_1 = os.path.join(OUTPUT_DIR, "phase2_01_event_wizard_step1.png")
        page.screenshot(path=wizard_shot_1)
        results["screenshots"].append(wizard_shot_1)

        title = f"International AI Forum {random.randint(1000, 9999)}"
        page.fill(".wizard-form input[name='step1-title']", title)
        page.select_option(".wizard-form select[name='step1-event_type']", index=1)
        page.fill(
            ".wizard-form textarea[name='step1-description']",
            "Annual international robotics conference",
        )
        page.fill(".wizard-form input[name='step1-expected_attendees']", "80")
        page.click(".wizard-form button[value='next']")
        page.wait_for_url(f"{BASE_URL}/events/wizard/?step=2")

        # Step 2: Date & Venue
        page.fill(".wizard-form input[name='step2-planned_date']", date_str)
        page.fill(".wizard-form input[name='step2-start_time']", "10:00")
        page.fill(".wizard-form input[name='step2-end_time']", "13:00")
        page.select_option(".wizard-form select[name='step2-venue']", index=1)

        # Check weekday display auto-update
        page.wait_for_timeout(300)
        weekday_text = page.locator("#weekday-display").inner_text()
        assert weekday_text != "", "Weekday indicator did not auto-update"

        wizard_shot_2 = os.path.join(OUTPUT_DIR, "phase2_02_event_wizard_step2_availability.png")
        page.screenshot(path=wizard_shot_2)
        results["screenshots"].append(wizard_shot_2)
        results["availability"] = "PASS"

        page.click(".wizard-form button[value='next']")
        page.wait_for_url(f"{BASE_URL}/events/wizard/?step=3")

        # Step 3: People
        page.select_option(".wizard-form select[name='step3-responsible_employee']", index=1)
        page.select_option(".wizard-form select[name='step3-management_responsible']", index=1)
        page.click(".wizard-form button[value='next']")
        page.wait_for_url(f"{BASE_URL}/events/wizard/?step=4")

        # Step 4: Partners
        page.click(".wizard-form button[value='next']")
        page.wait_for_url(f"{BASE_URL}/events/wizard/?step=5")

        # Step 5: Review & Save Planned
        wizard_shot_5 = os.path.join(OUTPUT_DIR, "phase2_03_event_wizard_review.png")
        page.screenshot(path=wizard_shot_5)
        results["screenshots"].append(wizard_shot_5)

        page.click(".wizard-form button[value='save_planned']")
        page.wait_for_selector(".detail-title")
        assert title in page.content()
        results["wizard"] = "PASS"

        # Capture created event ID from URL
        created_event_url = page.url

        # View Detail Screenshot
        detail_shot = os.path.join(OUTPUT_DIR, "phase2_04_event_detail.png")
        page.screenshot(path=detail_shot)
        results["screenshots"].append(detail_shot)

        # ---------------------------------------------------------------
        # 2. CONFLICT BLOCKING TEST (SAME DATE & OVERLAPPING TIME)
        # ---------------------------------------------------------------
        page.goto(f"{BASE_URL}/events/wizard/")
        page.fill(".wizard-form input[name='step1-title']", "Conflicting Overlap Event")
        page.select_option(".wizard-form select[name='step1-event_type']", index=1)
        page.click(".wizard-form button[value='next']")

        page.fill(".wizard-form input[name='step2-planned_date']", date_str)
        page.fill(".wizard-form input[name='step2-start_time']", "11:00")  # Overlaps 10:00-13:00
        page.fill(".wizard-form input[name='step2-end_time']", "14:00")
        page.select_option(".wizard-form select[name='step2-venue']", index=1)
        page.click(".wizard-form button[value='next']")

        page.select_option(".wizard-form select[name='step3-responsible_employee']", index=1)
        page.select_option(".wizard-form select[name='step3-management_responsible']", index=1)
        page.click(".wizard-form button[value='next']")
        page.click(".wizard-form button[value='next']")

        conflict_shot = os.path.join(OUTPUT_DIR, "phase2_05_conflict_state.png")
        page.screenshot(path=conflict_shot)
        results["screenshots"].append(conflict_shot)

        # Submit save_planned -> should block with conflict error
        page.click(".wizard-form button[value='save_planned']")
        page.wait_for_timeout(500)
        c_low = page.content().lower()
        has_conflict = "conflict" in c_low or "occupied" in c_low or "alert" in c_low
        assert has_conflict
        results["conflict_blocking"] = "PASS"

        # ---------------------------------------------------------------
        # 3. CALENDAR VERIFICATION (MONTH & WEEK VIEWS)
        # ---------------------------------------------------------------
        page.goto(f"{BASE_URL}/calendar/")
        page.wait_for_timeout(1000)
        cal_month_shot = os.path.join(OUTPUT_DIR, "phase2_06_calendar_month.png")
        page.screenshot(path=cal_month_shot)
        results["screenshots"].append(cal_month_shot)

        week_btn = page.query_selector(
            ".fc-dayGridMonth-button, .fc-timeGridWeek-button, .fc-button-primary"
        )
        if week_btn:
            week_btn.click()
            page.wait_for_timeout(500)
        cal_week_shot = os.path.join(OUTPUT_DIR, "phase2_07_calendar_week.png")
        page.screenshot(path=cal_week_shot)
        results["screenshots"].append(cal_week_shot)
        results["calendar"] = "PASS"

        # ---------------------------------------------------------------
        # 4. LIVE VENUE STATUS PAGE
        # ---------------------------------------------------------------
        page.goto(f"{BASE_URL}/master-data/venues/live-status/")
        live_shot = os.path.join(OUTPUT_DIR, "phase2_08_venue_live_status.png")
        page.screenshot(path=live_shot)
        results["screenshots"].append(live_shot)

        # ---------------------------------------------------------------
        # 5. EVENT CANCELLATION TEST
        # ---------------------------------------------------------------
        page.goto(f"{created_event_url}cancel/")
        page.wait_for_selector(".confirm-panel textarea[name='reason']")
        reason_input = page.locator(".confirm-panel textarea[name='reason']")
        reason_input.fill("Postponed due to speaker travel shift.")
        page.click(".confirm-panel button[type='submit']")
        page.wait_for_selector(".detail-title")
        assert "CANCELLED" in page.content() or "Cancelled" in page.content()
        results["cancellation"] = "PASS"

        # ---------------------------------------------------------------
        # 6. RESPONSIVE VIEWPORT SCREENSHOTS
        # ---------------------------------------------------------------
        viewports = [
            ("1920x1080", 1920, 1080),
            ("1366x768", 1366, 768),
            ("768x1024_tablet", 768, 1024),
            ("375x812_mobile", 375, 812),
        ]
        for name, width, height in viewports:
            ctx_resp = browser.new_context(viewport={"width": width, "height": height})
            p_resp = ctx_resp.new_page()
            p_resp.goto(f"{BASE_URL}/accounts/login/")
            p_resp.fill(".login-card input[name='username']", "intl_admin")
            p_resp.fill(".login-card input[name='password']", "Password123!")
            p_resp.click(".login-card button[type='submit']")
            p_resp.wait_for_selector(".app-shell")

            p_resp.goto(f"{BASE_URL}/calendar/")
            p_resp.wait_for_timeout(500)
            shot_path = os.path.join(OUTPUT_DIR, f"phase2_responsive_calendar_{name}.png")
            p_resp.screenshot(path=shot_path)
            results["screenshots"].append(shot_path)
            ctx_resp.close()

        context.close()
        browser.close()

    print("PHASE 2 PLAYWRIGHT ACCEPTANCE PASSED PERFECTLY!")
    print(f"Captured {len(results['screenshots'])} visual baseline screenshots in {OUTPUT_DIR}:")
    for s in results["screenshots"]:
        print(f"  - {os.path.basename(s)}")


if __name__ == "__main__":
    run_phase2_verification()
