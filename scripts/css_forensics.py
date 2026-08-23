import asyncio
import json
from playwright.async_api import async_playwright

async def run_forensics():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        routes = [
            {'url': 'http://10.34.12.2:8012/accounts/login/', 'name': 'login'},
            {'url': 'http://10.34.12.2:8012/dashboard/', 'name': 'dashboard'},
            {'url': 'http://10.34.12.2:8012/dashboard/calendar/?date=2026-08-17&view=month', 'name': 'calendar'}
        ]

        results = {}

        for route in routes:
            print(f"Analyzing {route['name']}...")
            await page.goto(route['url'], wait_until='networkidle')

            # Extract stylesheets
            stylesheets = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(link => {
                    let rulesAccessible = false;
                    try {
                        rulesAccessible = !!link.sheet.cssRules;
                    } catch (e) {
                        rulesAccessible = false;
                    }
                    return {
                        href: link.href,
                        media: link.media || 'all',
                        rulesAccessible: rulesAccessible
                    };
                });
            }''')

            # Extract elements for login
            elements_data = {}
            if route['name'] == 'login':
                selectors = {
                    'login_shell': '.auth-layout, body',
                    'left_panel': '.auth-brand-panel',
                    'right_panel': '.auth-form-panel',
                    'form_card': '.login-card',
                    'username_input': 'input[name="username"]',
                    'password_input': 'input[name="password"]',
                    'submit_button': 'button[type="submit"]',
                    'skip_link': '.skip-link'
                }
            elif route['name'] == 'dashboard':
                selectors = {
                    'main_nav': '.public-main-nav, nav',
                    'kpi_rail': '.kpi-rail, .kpi-container, .metrics-bar',
                    'timeline': '.timeline-panel, .timeline-container, .chronology',
                    'venue_activity': '.venues-panel, .venue-activity'
                }
            elif route['name'] == 'calendar':
                selectors = {
                    'main_nav': '.public-main-nav, nav',
                    'command_strip': '.calendar-toolbar, .command-strip',
                    'search_input': 'input[type="search"], input[name="q"]',
                    'select': 'select',
                    'calendar_grid': '.calendar-grid, .month-view'
                }

            for key, sel in selectors.items():
                # We take the first selector that matches
                found = await page.evaluate(f'''(sel) => {{
                    const parts = sel.split(',');
                    for(let part of parts) {{
                        const el = document.querySelector(part.trim());
                        if (el) return part.trim();
                    }}
                    return null;
                }}''', sel)

                if found:
                    computed = await page.evaluate(f'''(sel) => {{
                        const el = document.querySelector(sel);
                        const comp = window.getComputedStyle(el);
                        return {{
                            className: el.className,
                            display: comp.display,
                            position: comp.position,
                            width: comp.width,
                            height: comp.height,
                            gridTemplateColumns: comp.gridTemplateColumns,
                            flexDirection: comp.flexDirection,
                            background: comp.background,
                            border: comp.border,
                            borderRadius: comp.borderRadius,
                            padding: comp.padding,
                            margin: comp.margin,
                            fontFamily: comp.fontFamily,
                            visibility: comp.visibility,
                            opacity: comp.opacity
                        }};
                    }}''', found)
                    elements_data[key] = {'selector': found, 'computed': computed}
                else:
                    elements_data[key] = {'selector': sel, 'computed': None}

            results[route['name']] = {
                'stylesheets': stylesheets,
                'elements': elements_data
            }

        with open('css_forensics.json', 'w') as f:
            json.dump(results, f, indent=2)

        await context.close()
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_forensics())
