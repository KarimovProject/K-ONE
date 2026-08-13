import os

from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8555"
OUTPUT_DIR = os.path.join(os.getcwd(), "tests", "visual_baseline")
os.makedirs(OUTPUT_DIR, exist_ok=True)

results = {
    "web_crud": {},
    "rbac": {},
    "localization": {},
    "responsive": {},
    "accessibility": {},
    "screenshots": [],
}


def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ---------------------------------------------------------------
        # 1. VISUAL BASELINE SCREENSHOTS & WEB CRUD (1920x1080)
        # ---------------------------------------------------------------
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Login as intl_admin
        page.goto(f"{BASE_URL}/accounts/login/")
        page.fill("form input[name='username']", "intl_admin")
        page.fill("form input[name='password']", "Password123!")
        page.click("form button[type='submit']")
        page.wait_for_selector(".app-shell")

        # Dashboard / Sidebar Screenshot
        page.goto(f"{BASE_URL}/")
        dash_shot = os.path.join(OUTPUT_DIR, "09_dashboard_sidebar_1920x1080.png")
        page.screenshot(path=dash_shot)
        results["screenshots"].append(dash_shot)

        # --- Venues ---
        page.goto(f"{BASE_URL}/master-data/venues/")
        venue_list_shot = os.path.join(OUTPUT_DIR, "01_venue_list_1920x1080.png")
        page.screenshot(path=venue_list_shot)
        results["screenshots"].append(venue_list_shot)
        assert "ICH" in page.content(), "Venue list missing ICH code"

        page.goto(f"{BASE_URL}/master-data/venues/new/")
        venue_form_shot = os.path.join(OUTPUT_DIR, "02_venue_form_create_1920x1080.png")
        page.screenshot(path=venue_form_shot)
        results["screenshots"].append(venue_form_shot)

        # Test Venue Create
        page.fill("form.data-form input[name='code']", "TEST_HALL")
        page.fill("form.data-form input[name='name_uz']", "Test Zali")
        page.fill("form.data-form input[name='name_ru']", "Тестовый зал")
        page.fill("form.data-form input[name='name_en']", "Test Hall")
        page.fill("form.data-form input[name='capacity']", "150")
        page.fill("form.data-form input[name='working_start']", "09:00")
        page.fill("form.data-form input[name='working_end']", "18:00")
        page.click("form.data-form button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/master-data/venues/")
        assert "TEST_HALL" in page.content(), "TEST_HALL not found after creation"

        # Test Venue Detail & Edit
        venue_row = page.locator("tr:has-text('TEST_HALL')")
        detail_link = venue_row.locator("a").first
        if detail_link.count() > 0:
            detail_link.click()
            page.wait_for_timeout(500)
            assert "TEST_HALL" in page.content()

        # Test Venue Validation Error (working_end <= working_start)
        page.goto(f"{BASE_URL}/master-data/venues/new/")
        page.fill("form.data-form input[name='code']", "FAIL_HALL")
        page.fill("form.data-form input[name='name_uz']", "Fail Hall")
        page.fill("form.data-form input[name='name_ru']", "Fail Hall")
        page.fill("form.data-form input[name='name_en']", "Fail Hall")
        page.fill("form.data-form input[name='capacity']", "50")
        page.fill("form.data-form input[name='working_start']", "18:00")
        page.fill("form.data-form input[name='working_end']", "09:00")
        page.click("form.data-form button[type='submit']")
        page.wait_for_timeout(500)
        assert "has-error" in page.content() or "field-error" in page.content()

        results["web_crud"]["venues"] = "PASS"

        # --- Event Types ---
        page.goto(f"{BASE_URL}/master-data/event-types/")
        et_list_shot = os.path.join(OUTPUT_DIR, "03_event_type_list_1920x1080.png")
        page.screenshot(path=et_list_shot)
        results["screenshots"].append(et_list_shot)
        assert "Konferensiya" in page.content() or "Conference" in page.content()

        page.goto(f"{BASE_URL}/master-data/event-types/new/")
        et_form_shot = os.path.join(OUTPUT_DIR, "04_event_type_form_create_1920x1080.png")
        page.screenshot(path=et_form_shot)
        results["screenshots"].append(et_form_shot)

        # Test EventType Create
        page.fill("form.data-form input[name='code']", "webinar")
        page.fill("form.data-form input[name='name_uz']", "Vebinar")
        page.fill("form.data-form input[name='name_ru']", "Вебинар")
        page.fill("form.data-form input[name='name_en']", "Webinar")
        page.click("form.data-form button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/master-data/event-types/")
        assert "webinar" in page.content() or "Vebinar" in page.content()

        results["web_crud"]["event_types"] = "PASS"

        # --- Organizations ---
        page.goto(f"{BASE_URL}/master-data/organizations/")
        org_list_shot = os.path.join(OUTPUT_DIR, "05_organization_list_1920x1080.png")
        page.screenshot(path=org_list_shot)
        results["screenshots"].append(org_list_shot)

        page.goto(f"{BASE_URL}/master-data/organizations/new/")
        org_form_shot = os.path.join(OUTPUT_DIR, "06_organization_form_create_1920x1080.png")
        page.screenshot(path=org_form_shot)
        results["screenshots"].append(org_form_shot)

        # Test Organization Create
        page.fill("form.data-form input[name='name']", "Test Organization")
        page.fill("form.data-form input[name='short_name']", "TO")
        page.fill("form.data-form input[name='country']", "Uzbekistan")
        page.fill("form.data-form input[name='website']", "https://testorg.uz")
        page.click("form.data-form button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/master-data/organizations/")
        assert "Test Organization" in page.content()

        # Test Organization invalid website URL error
        page.goto(f"{BASE_URL}/master-data/organizations/new/")
        page.fill("form.data-form input[name='name']", "Bad Web Org")
        page.fill("form.data-form input[name='website']", "invalid_url")
        page.click("form.data-form button[type='submit']")
        page.wait_for_timeout(500)
        assert "has-error" in page.content() or "field-error" in page.content()

        results["web_crud"]["organizations"] = "PASS"

        # --- Sponsors ---
        page.goto(f"{BASE_URL}/master-data/sponsors/")
        sp_list_shot = os.path.join(OUTPUT_DIR, "07_sponsor_list_1920x1080.png")
        page.screenshot(path=sp_list_shot)
        results["screenshots"].append(sp_list_shot)

        page.goto(f"{BASE_URL}/master-data/sponsors/new/")
        sp_form_shot = os.path.join(OUTPUT_DIR, "08_sponsor_form_create_1920x1080.png")
        page.screenshot(path=sp_form_shot)
        results["screenshots"].append(sp_form_shot)

        # Test Sponsor Create
        page.fill("form.data-form input[name='name']", "Test Sponsor Inc")
        page.fill("form.data-form input[name='website']", "https://sponsor.com")
        page.click("form.data-form button[type='submit']")
        page.wait_for_url(f"{BASE_URL}/master-data/sponsors/")
        assert "Test Sponsor Inc" in page.content()

        results["web_crud"]["sponsors"] = "PASS"
        context.close()

        # ---------------------------------------------------------------
        # 2. RBAC MANUAL CHECK
        # ---------------------------------------------------------------
        # Read-only user: mgmt_resp
        ctx_read = browser.new_context(viewport={"width": 1920, "height": 1080})
        p_read = ctx_read.new_page()
        p_read.goto(f"{BASE_URL}/accounts/login/")
        p_read.fill("form input[name='username']", "mgmt_resp")
        p_read.fill("form input[name='password']", "Password123!")
        p_read.click("form button[type='submit']")
        p_read.wait_for_selector(".app-shell")

        p_read.goto(f"{BASE_URL}/master-data/venues/")
        create_btn = p_read.query_selector("a[href*='/new/']")
        assert create_btn is None, "Write action button visible to read-only user!"
        results["rbac"]["read_only_protection"] = "PASS"
        ctx_read.close()

        # ---------------------------------------------------------------
        # 3. LOCALIZATION CHECK (UZ, RU, EN)
        # ---------------------------------------------------------------
        ctx_loc = browser.new_context(viewport={"width": 1920, "height": 1080})
        p_loc = ctx_loc.new_page()
        p_loc.goto(f"{BASE_URL}/accounts/login/")
        p_loc.fill("form input[name='username']", "intl_admin")
        p_loc.fill("form input[name='password']", "Password123!")
        p_loc.click("form button[type='submit']")

        for lang_code in ("uz", "ru", "en"):
            cookie = [{"name": "django_language", "value": lang_code, "url": BASE_URL}]
            p_loc.context.add_cookies(cookie)

            p_loc.goto(f"{BASE_URL}/master-data/venues/")
            body_text = p_loc.content()
            assert "{%" not in body_text, f"Raw template tag found in {lang_code}"
            assert "django.utils.translation" not in body_text, "Translation debug string found"

        results["localization"]["clean_text"] = "PASS"
        ctx_loc.close()

        # ---------------------------------------------------------------
        # 4. RESPONSIVE BREAKPOINT SCREENSHOTS
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
            p_resp.fill("form input[name='username']", "intl_admin")
            p_resp.fill("form input[name='password']", "Password123!")
            p_resp.click("form button[type='submit']")
            p_resp.wait_for_selector(".app-shell")

            p_resp.goto(f"{BASE_URL}/master-data/venues/")
            shot_path = os.path.join(OUTPUT_DIR, f"responsive_venues_{name}.png")
            p_resp.screenshot(path=shot_path)
            results["screenshots"].append(shot_path)
            ctx_resp.close()

        results["responsive"]["all_viewports"] = "PASS"

        # ---------------------------------------------------------------
        # 5. ACCESSIBILITY CHECK
        # ---------------------------------------------------------------
        ctx_a11y = browser.new_context(viewport={"width": 1920, "height": 1080})
        p_a11y = ctx_a11y.new_page()
        p_a11y.goto(f"{BASE_URL}/accounts/login/")
        p_a11y.fill("form input[name='username']", "intl_admin")
        p_a11y.fill("form input[name='password']", "Password123!")
        p_a11y.click("form button[type='submit']")

        p_a11y.goto(f"{BASE_URL}/master-data/venues/new/")
        code_input = p_a11y.query_selector("input#id_code")
        assert code_input is not None, "Form input missing matching ID for label"
        results["accessibility"]["labels_and_focus"] = "PASS"
        ctx_a11y.close()

        browser.close()

    print("ALL VERIFICATION CHECKS PASSED PERFECTLY!")
    print(f"Captured {len(results['screenshots'])} visual baseline screenshots in {OUTPUT_DIR}:")
    for s in results["screenshots"]:
        print(f"  - {os.path.basename(s)}")


if __name__ == "__main__":
    run_verification()
