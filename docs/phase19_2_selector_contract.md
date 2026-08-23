# Selector Contract Audit

| CLASS | ROUTE | DEFINED_IN | LOADED_IN_BROWSER | MATCH_COUNT | COMPUTED_STYLE_EXPECTED | COMPUTED_STYLE_ACTUAL | STATUS |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `.auth-layout` | `/accounts/login/` | `app.css` | YES | 1 | flex layout | flex | PASS |
| `.auth-brand-panel` | `/accounts/login/` | `app.css` | YES | 1 | 50-55% width, flex | 1226px flex | PASS |
| `.auth-form-panel` | `/accounts/login/` | `app.css` | YES | 1 | 45-50% width, block | 597px block | PASS |
| `input[name="username"]` | `/accounts/login/` | `app.css` (Missing) | YES | 1 | styled input | default | FAIL |
| `button[type="submit"]` | `/accounts/login/` | `app.css` (Missing) | YES | 1 | premium button | default | FAIL |
| `.public-main-nav` | `/dashboard/` | `public.css` | YES | 0 | flex navbar | null (Missing in DOM) | FAIL |
| `.kpi-rail` | `/dashboard/` | `public.css` | YES | 0 | flex row | null (Missing in DOM) | FAIL |
| `.timeline-panel` | `/dashboard/` | `public.css` | YES | 0 | flex col | null (Missing in DOM) | FAIL |
| `.calendar-toolbar` | `/calendar/` | `calendar.css` | YES | 0 | flex row | null (Missing in DOM) | FAIL |
| `.calendar-grid` | `/calendar/` | `calendar.css` | YES | 0 | CSS grid 7 cols | null (Missing in DOM) | FAIL |

**Conclusion:** 
The CSS files exist and are loaded. However, the templates (`login.html`, `dashboard.html`, `calendar.html`) do not emit the correct classes for the newer Phase 19/19.1 architecture, causing them to fall back to generic/raw HTML styling or fail entirely (missing classes).
