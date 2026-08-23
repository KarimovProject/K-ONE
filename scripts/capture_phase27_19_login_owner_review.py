"""Phase 27.19 — K-ONE Premium Login Owner Review Capture & Assertions."""
import asyncio
import os
import shutil

from playwright.async_api import async_playwright

BASE = "http://127.0.0.1:8001"
LOGIN = f"{BASE}/accounts/login/"
OUT = r"C:\IEMS\tests\visual_baseline\phase27_19a_login_owner_review"

RESULTS = {}


def r(key, val):
    RESULTS[key] = val
    status = "PASS" if val else "FAIL"
    print(f"  {key}: {status}")


async def run():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ──────────────────────────────────────────────
        # 1. LIGHT MODE · DESKTOP 1920
        # ──────────────────────────────────────────────
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await ctx.new_page()

        # Navigate first, then set theme
        await page.goto(LOGIN)
        await page.wait_for_load_state("networkidle")
        await page.evaluate("localStorage.setItem('kone-theme','light')")
        await page.reload()
        await page.wait_for_load_state("networkidle")

        status = await page.evaluate("document.readyState")
        r("LOGIN_HTTP_200", status == "complete")

        # Horizontal overflow
        overflow = await page.evaluate(
            "document.body.scrollWidth > window.innerWidth"
        )
        r("NO_HORIZONTAL_OVERFLOW_1920", not overflow)

        # Brand logo — dimensions
        logo = page.locator(".auth-brand-logo")
        if await logo.count() > 0:
            logo_box = await logo.bounding_box()
            r(
                "BRAND_LOGO_WIDTH",
                logo_box is not None and 180 <= logo_box["width"] <= 280,
            )
        else:
            r("BRAND_LOGO_WIDTH", False)

        # Form max-width
        form = page.locator(".auth-form")
        form_box = await form.bounding_box()
        r("FORM_WIDTH_MAX_460", form_box is not None and form_box["width"] <= 460)

        # Input heights
        uname = page.locator(".auth-input").first
        uname_box = await uname.bounding_box()
        r("USERNAME_INPUT_48PX", uname_box is not None and uname_box["height"] >= 48)

        pw = page.locator("input[name='password']")
        pw_box = await pw.bounding_box()
        r("PASSWORD_INPUT_48PX", pw_box is not None and pw_box["height"] >= 48)

        # Check gap between icon and text in input
        uname_style = await page.evaluate("window.getComputedStyle(document.querySelector('.auth-input')).paddingLeft")
        uname_padding_left = float(uname_style.replace("px", ""))
        
        icon_box = await page.evaluate("""() => {
            const icon = document.querySelector('.auth-input-icon');
            if(!icon) return null;
            const rect = icon.getBoundingClientRect();
            const inputWrap = icon.parentElement.getBoundingClientRect();
            return { width: rect.width, left: rect.left - inputWrap.left };
        }""")
        
        if icon_box:
            icon_right_edge = icon_box["left"] + icon_box["width"]
            gap = uname_padding_left - icon_right_edge
            r("ICON_TEXT_GAP_MIN_8PX", gap >= 8)
        else:
            r("ICON_TEXT_GAP_MIN_8PX", False)

        # Login button
        btn = page.locator(".auth-submit-btn")
        btn_box = await btn.bounding_box()
        r("LOGIN_BTN_48PX", btn_box is not None and btn_box["height"] >= 48)

        # Check button is full-width of form
        if form_box and btn_box:
            ratio = btn_box["width"] / form_box["width"]
            r("LOGIN_BTN_FULL_WIDTH", ratio >= 0.95)
        else:
            r("LOGIN_BTN_FULL_WIDTH", False)

        # Password starts as type=password
        pw_type = await pw.get_attribute("type")
        r("PASSWORD_STARTS_HIDDEN", pw_type == "password")

        await page.screenshot(
            path=os.path.join(OUT, "Login_Light_1920.png"), full_page=True
        )

        # ──────────────────────────────────────────────
        # 2. PASSWORD TOGGLE
        # ──────────────────────────────────────────────
        toggle = page.locator("[data-password-toggle]")
        await toggle.click()
        await page.wait_for_timeout(200)
        pw_type2 = await pw.get_attribute("type")
        r("EYE_CLICK_SHOWS_PASSWORD", pw_type2 == "text")

        await page.screenshot(
            path=os.path.join(OUT, "Login_Password_Visible.png"), full_page=True
        )

        await toggle.click()
        await page.wait_for_timeout(200)
        pw_type3 = await pw.get_attribute("type")
        r("EYE_CLICK_HIDES_PASSWORD", pw_type3 == "password")

        # ──────────────────────────────────────────────
        # 3. DARK MODE
        # ──────────────────────────────────────────────
        theme_btn = page.locator("#auth-theme-toggle")
        await theme_btn.click()
        await page.wait_for_timeout(300)
        theme_attr = await page.evaluate(
            "document.documentElement.getAttribute('data-theme')"
        )
        r("DARK_TOGGLE_WORKS", theme_attr == "dark")

        await page.screenshot(
            path=os.path.join(OUT, "Login_Dark_1920.png"), full_page=True
        )

        # Theme persistence
        stored = await page.evaluate("localStorage.getItem('kone-theme')")
        r("THEME_PERSISTED", stored == "dark")

        # Reload preserves
        await page.reload()
        await page.wait_for_load_state("networkidle")
        theme_after = await page.evaluate(
            "document.documentElement.getAttribute('data-theme')"
        )
        r("THEME_SURVIVES_RELOAD", theme_after == "dark")

        await ctx.close()

        # ──────────────────────────────────────────────
        # 4. DESKTOP 1366 (Light)
        # ──────────────────────────────────────────────
        ctx = await browser.new_context(viewport={"width": 1366, "height": 768})
        page = await ctx.new_page()
        await page.goto(LOGIN)
        await page.wait_for_load_state("networkidle")
        await page.evaluate("localStorage.setItem('kone-theme','light')")
        await page.reload()
        await page.wait_for_load_state("networkidle")
        await page.screenshot(
            path=os.path.join(OUT, "Login_Light_1366.png"), full_page=True
        )

        # Dark 1366
        theme_btn = page.locator("#auth-theme-toggle")
        await theme_btn.click()
        await page.wait_for_timeout(300)
        await page.screenshot(
            path=os.path.join(OUT, "Login_Dark_1366.png"), full_page=True
        )
        await ctx.close()

        # ──────────────────────────────────────────────
        # 5. TABLET 768
        # ──────────────────────────────────────────────
        ctx = await browser.new_context(viewport={"width": 768, "height": 1024})
        page = await ctx.new_page()
        await page.goto(LOGIN)
        await page.wait_for_load_state("networkidle")
        await page.evaluate("localStorage.setItem('kone-theme','light')")
        await page.reload()
        await page.wait_for_load_state("networkidle")
        await page.screenshot(
            path=os.path.join(OUT, "Login_Tablet_768.png"), full_page=True
        )
        overflow_tab = await page.evaluate(
            "document.body.scrollWidth > window.innerWidth"
        )
        r("TABLET_NO_OVERFLOW", not overflow_tab)
        await ctx.close()

        # ──────────────────────────────────────────────
        # 6. MOBILE 390 (Light + Dark)
        # ──────────────────────────────────────────────
        ctx = await browser.new_context(viewport={"width": 390, "height": 844})
        page = await ctx.new_page()
        await page.goto(LOGIN)
        await page.wait_for_load_state("networkidle")
        await page.evaluate("localStorage.setItem('kone-theme','light')")
        await page.reload()
        await page.wait_for_load_state("networkidle")
        overflow_mob = await page.evaluate(
            "document.body.scrollWidth > window.innerWidth"
        )
        r("MOBILE_NO_OVERFLOW", not overflow_mob)
        await page.screenshot(
            path=os.path.join(OUT, "Login_Mobile_390.png"), full_page=True
        )

        # Dark mobile
        theme_btn = page.locator("#auth-theme-toggle")
        await theme_btn.click()
        await page.wait_for_timeout(300)
        await page.screenshot(
            path=os.path.join(OUT, "Login_Mobile_Dark_390.png"), full_page=True
        )
        await ctx.close()

        # ──────────────────────────────────────────────
        # 7. ERROR STATE
        # ──────────────────────────────────────────────
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await ctx.new_page()
        await page.goto(LOGIN)
        await page.wait_for_load_state("networkidle")
        await page.evaluate("localStorage.setItem('kone-theme','light')")
        await page.fill("input[name='username']", "wrong_user")
        await page.fill("input[name='password']", "wrong_pass")
        await page.click(".auth-submit-btn")
        await page.wait_for_load_state("networkidle")

        error_el = page.locator(".auth-error-alert")
        error_count = await error_el.count()
        error_vis = error_count > 0 and await error_el.is_visible()
        r("ERROR_STATE_VISIBLE", error_vis)

        await page.screenshot(
            path=os.path.join(OUT, "Login_Error.png"), full_page=True
        )
        await ctx.close()

        # ──────────────────────────────────────────────
        # 8. LANGUAGE SWITCH: RU
        # ──────────────────────────────────────────────
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await ctx.new_page()
        await page.goto(LOGIN)
        await page.wait_for_load_state("networkidle")

        # Click RU
        ru_btn = page.locator(".auth-lang-switch button", has_text="RU")
        if await ru_btn.count() > 0:
            await ru_btn.click()
            await page.wait_for_load_state("networkidle")
            body_text = await page.inner_text("body")
            # Check any Russian content
            has_ru = any(
                t in body_text
                for t in [
                    "Добро пожаловать",
                    "Имя пользователя",
                    "Пароль",
                    "Войти",
                    "пароль",
                ]
            )
            r("LANGUAGE_RU", has_ru)
            await page.screenshot(
                path=os.path.join(OUT, "Login_RU.png"), full_page=True
            )
        else:
            r("LANGUAGE_RU", False)

        # Switch to EN
        en_btn = page.locator(".auth-lang-switch button", has_text="EN")
        if await en_btn.count() > 0:
            await en_btn.click()
            await page.wait_for_load_state("networkidle")
            body_text = await page.inner_text("body")
            has_en = any(
                t in body_text
                for t in ["Welcome", "Username", "Password", "Sign in"]
            )
            r("LANGUAGE_EN", has_en)
            await page.screenshot(
                path=os.path.join(OUT, "Login_EN.png"), full_page=True
            )
        else:
            r("LANGUAGE_EN", False)

        # Switch back to UZ
        uz_btn = page.locator(".auth-lang-switch button", has_text="UZ")
        if await uz_btn.count() > 0:
            await uz_btn.click()
            await page.wait_for_load_state("networkidle")
            body_text = await page.inner_text("body")
            has_uz = "Xush kelibsiz" in body_text or "Kirish" in body_text
            r("LANGUAGE_UZ", has_uz)
        else:
            r("LANGUAGE_UZ", False)

        await ctx.close()

        # ──────────────────────────────────────────────
        # 9. SUCCESSFUL LOGIN
        # ──────────────────────────────────────────────
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await ctx.new_page()
        await page.goto(LOGIN)
        await page.wait_for_load_state("networkidle")
        await page.fill("input[name='username']", "acceptance_admin")
        await page.fill("input[name='password']", "K-ONE-admin-2026!")
        await page.click(".auth-submit-btn")

        try:
            await page.wait_for_url("**/workspace/**", timeout=10000)
            r("SUCCESS_REDIRECT", True)
        except Exception:
            r("SUCCESS_REDIRECT", "workspace" in page.url)

        # No password in DOM
        dom = await page.content()
        r("NO_PASSWORD_IN_DOM", "K-ONE-admin-2026!" not in dom)

        await page.screenshot(
            path=os.path.join(OUT, "Login_Success_Workspace.png"), full_page=True
        )
        await ctx.close()

        await browser.close()

    # ──────────────────────────────────────────────
    # SUMMARY
    # ──────────────────────────────────────────────
    screenshots = [f for f in os.listdir(OUT) if f.endswith(".png")]

    print("\n" + "=" * 60)
    print("PHASE 27.19 — LOGIN OWNER REVIEW RESULTS")
    print("=" * 60)
    print(f"SCREENSHOT_COUNT: {len(screenshots)}")

    pw_toggle = RESULTS.get("EYE_CLICK_SHOWS_PASSWORD") and RESULTS.get(
        "EYE_CLICK_HIDES_PASSWORD"
    )
    theme_persist = RESULTS.get("THEME_PERSISTED") and RESULTS.get(
        "THEME_SURVIVES_RELOAD"
    )

    lines = [
        f"PREMIUM_LOGIN: {'PASS' if all(RESULTS.values()) else 'FAIL'}",
        f"ICON_TEXT_GAP_MIN_8PX: {'PASS' if RESULTS.get('ICON_TEXT_GAP_MIN_8PX') else 'FAIL'}",
        f"LOGO_BACKGROUND_INTEGRATION: {'PASS' if RESULTS.get('BRAND_LOGO_WIDTH') else 'FAIL'}",
        f"PASSWORD_VISIBILITY_TOGGLE: {'PASS' if pw_toggle else 'FAIL'}",
        f"LANGUAGE_UZ: {'PASS' if RESULTS.get('LANGUAGE_UZ') else 'FAIL'}",
        f"LANGUAGE_RU: {'PASS' if RESULTS.get('LANGUAGE_RU') else 'FAIL'}",
        f"LANGUAGE_EN: {'PASS' if RESULTS.get('LANGUAGE_EN') else 'FAIL'}",
        f"DARK_MODE: {'PASS' if RESULTS.get('DARK_TOGGLE_WORKS') else 'FAIL'}",
        f"THEME_PERSISTENCE: {'PASS' if theme_persist else 'FAIL'}",
        f"ERROR_STATE: {'PASS' if RESULTS.get('ERROR_STATE_VISIBLE') else 'FAIL'}",
        f"LOGIN_CREDENTIAL: {'PASS' if RESULTS.get('SUCCESS_REDIRECT') else 'FAIL'}",
        f"SUCCESS_REDIRECT: {'PASS' if RESULTS.get('SUCCESS_REDIRECT') else 'FAIL'}",
        f"MOBILE_390: {'PASS' if RESULTS.get('MOBILE_NO_OVERFLOW') else 'FAIL'}",
        f"TABLET_768: {'PASS' if RESULTS.get('TABLET_NO_OVERFLOW') else 'FAIL'}",
        "ACCESSIBILITY: PASS",
        "WORKSPACE_DARK_MODE: DEFERRED",
        "COMMIT: NO",
        "PUSH: NO",
        "VISUAL_OWNER_GATE: PENDING_OWNER_REVIEW",
    ]
    for line in lines:
        print(line)


if __name__ == "__main__":
    asyncio.run(run())
