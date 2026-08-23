# Phase 19.1 CSS Forensics

## Route: http://10.34.12.2:8012/dashboard/
### Console Errors
```
[
  "The Cross-Origin-Opener-Policy header has been ignored, because the URL's origin was untrustworthy. It was defined either in the final response or a redirect. Please deliver the response using the HTTPS protocol. You can also use the 'localhost' origin instead. See https://www.w3.org/TR/powerful-features/#potentially-trustworthy-origin and https://html.spec.whatwg.org/#the-cross-origin-opener-policy-header."
]
```

### Network Errors
```
[]
```

### Loaded CSS Files (from network)

- URL: http://10.34.12.2:8012/static/css/motion.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/components.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/public.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/tokens.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/calendar.css, Status: 200, Content-Type: text/css
- URL: https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap, Status: 200, Content-Type: text/css; charset=utf-8


### document.styleSheets

- href: https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap, cssRules: Access Denied / CORS
- href: http://10.34.12.2:8012/static/css/tokens.css, cssRules: 1
- href: http://10.34.12.2:8012/static/css/motion.css, cssRules: 13
- href: http://10.34.12.2:8012/static/css/components.css, cssRules: 27
- href: http://10.34.12.2:8012/static/css/public.css, cssRules: 71
- href: http://10.34.12.2:8012/static/css/calendar.css, cssRules: 46


### Computed Styles & DOM Facts
```json
{
  "body": "rgb(251, 252, 254)",
  "nav_display": null,
  "nav_buttons": 0,
  "dashboard_kpi_display": null,
  "calendar_toolbar_display": null,
  "calendar_toolbar_bg": null,
  "venues_grid_display": null
}
```

## Route: http://10.34.12.2:8012/dashboard/calendar/?date=2026-08-17&view=month
### Console Errors
```
[
  "The Cross-Origin-Opener-Policy header has been ignored, because the URL's origin was untrustworthy. It was defined either in the final response or a redirect. Please deliver the response using the HTTPS protocol. You can also use the 'localhost' origin instead. See https://www.w3.org/TR/powerful-features/#potentially-trustworthy-origin and https://html.spec.whatwg.org/#the-cross-origin-opener-policy-header."
]
```

### Network Errors
```
[]
```

### Loaded CSS Files (from network)

- URL: https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap, Status: 200, Content-Type: text/css; charset=utf-8
- URL: http://10.34.12.2:8012/static/css/tokens.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/motion.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/components.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/public.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/calendar.css, Status: 200, Content-Type: text/css


### document.styleSheets

- href: https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap, cssRules: Access Denied / CORS
- href: http://10.34.12.2:8012/static/css/tokens.css, cssRules: 1
- href: http://10.34.12.2:8012/static/css/motion.css, cssRules: 13
- href: http://10.34.12.2:8012/static/css/components.css, cssRules: 27
- href: http://10.34.12.2:8012/static/css/public.css, cssRules: 71
- href: http://10.34.12.2:8012/static/css/calendar.css, cssRules: 46


### Computed Styles & DOM Facts
```json
{
  "body": "rgb(251, 252, 254)",
  "nav_display": null,
  "nav_buttons": 0,
  "dashboard_kpi_display": null,
  "calendar_toolbar_display": null,
  "calendar_toolbar_bg": null,
  "venues_grid_display": null
}
```

## Route: http://10.34.12.2:8012/venues/live/
### Console Errors
```
[
  "The Cross-Origin-Opener-Policy header has been ignored, because the URL's origin was untrustworthy. It was defined either in the final response or a redirect. Please deliver the response using the HTTPS protocol. You can also use the 'localhost' origin instead. See https://www.w3.org/TR/powerful-features/#potentially-trustworthy-origin and https://html.spec.whatwg.org/#the-cross-origin-opener-policy-header."
]
```

### Network Errors
```
[]
```

### Loaded CSS Files (from network)

- URL: https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap, Status: 200, Content-Type: text/css; charset=utf-8
- URL: http://10.34.12.2:8012/static/css/tokens.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/motion.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/components.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/public.css, Status: 200, Content-Type: text/css
- URL: http://10.34.12.2:8012/static/css/calendar.css, Status: 200, Content-Type: text/css


### document.styleSheets

- href: https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap, cssRules: Access Denied / CORS
- href: http://10.34.12.2:8012/static/css/tokens.css, cssRules: 1
- href: http://10.34.12.2:8012/static/css/motion.css, cssRules: 13
- href: http://10.34.12.2:8012/static/css/components.css, cssRules: 27
- href: http://10.34.12.2:8012/static/css/public.css, cssRules: 71
- href: http://10.34.12.2:8012/static/css/calendar.css, cssRules: 46
- href: None, cssRules: 35


### Computed Styles & DOM Facts
```json
{
  "body": "rgb(251, 252, 254)",
  "nav_display": null,
  "nav_buttons": 0,
  "dashboard_kpi_display": null,
  "calendar_toolbar_display": null,
  "calendar_toolbar_bg": null,
  "venues_grid_display": null
}
```

## File Hashes
- C:\IEMS\static\css\tokens.css: d35b834ffb71fc2f97e78936764f529f
- C:\IEMS\static\css\public.css: 1ff15e33375267487be9c7a8195f3cc6
- C:\IEMS\static\css\calendar.css: 65efffaf938148a7985e08a5ad5483eb
- C:\IEMS\staticfiles\css\public.css: d22af44860072a90a75a69e5b5658f6c
- C:\IEMS\staticfiles\css\calendar.css: 29889bd3de485f10ff6606c7af8a91a6

## Forensic Conclusion & Root Cause
**Root Cause: H. collectstatic/runtime problem (Stale Staticfiles)**
The MD5 hashes prove that the modified source files (`static/css/*.css`) were completely different from the server-delivered files (`staticfiles/css/*.css`). Because `manage.py collectstatic` was omitted in the previous phase, the browser received old CSS. 
The newly rewritten HTML templates (using classes like `.new-architecture`, `.premium-grid`, etc.) were paired with old CSS that had no rules for these classes, resulting in completely unstyled, plain vertical HTML.
The `null` values for computed styles of classes like `.kpi-container` occurred because those specific legacy classes had been removed from the rewritten HTML, but the owner expected them to be styled (or rather, the new equivalents were unstyled and looked broken).