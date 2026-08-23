import os
import re

filepath = 'C:/IEMS/templates/reporting/leadership_dashboard.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <div class="leadership-kpi" style="--kpi-color: var(--color-brand-cobalt);">
# With <div class="kpi-card leadership-kpi">
# And the icon wrappers
content = re.sub(
    r'<div class="leadership-kpi" style="--kpi-color: var\(--color-brand-cobalt\);">\s*<div class="kpi-header">\s*<span>([^<]+)</span>\s*(<svg[^>]+>.*?</svg>)\s*</div>',
    r'<div class="kpi-card leadership-kpi">\n      <div class="kpi-header">\n        <span class="kpi-title">\1</span>\n        <div class="kpi-icon blue">\2</div>\n      </div>',
    content, flags=re.DOTALL
)

content = re.sub(
    r'<div class="leadership-kpi" style="--kpi-color: var\(--amber-500\);">\s*<div class="kpi-header">\s*<span>([^<]+)</span>\s*(<svg[^>]+>.*?</svg>)\s*</div>',
    r'<div class="kpi-card leadership-kpi">\n      <div class="kpi-header">\n        <span class="kpi-title">\1</span>\n        <div class="kpi-icon amber">\2</div>\n      </div>',
    content, flags=re.DOTALL
)

content = re.sub(
    r'<div class="leadership-kpi" style="--kpi-color: var\(--scientific-cyan\);">\s*<div class="kpi-header">\s*<span>([^<]+)</span>\s*(<svg[^>]+>.*?</svg>)\s*</div>',
    r'<div class="kpi-card leadership-kpi">\n      <div class="kpi-header">\n        <span class="kpi-title">\1</span>\n        <div class="kpi-icon blue">\2</div>\n      </div>',
    content, flags=re.DOTALL
)

content = re.sub(
    r'<div class="leadership-kpi" style="--kpi-color: var\(--emerald-500\);">\s*<div class="kpi-header">\s*<span>([^<]+)</span>\s*(<svg[^>]+>.*?</svg>)\s*</div>',
    r'<div class="kpi-card leadership-kpi">\n      <div class="kpi-header">\n        <span class="kpi-title">\1</span>\n        <div class="kpi-icon emerald">\2</div>\n      </div>',
    content, flags=re.DOTALL
)

content = re.sub(r'<strong id="([^"]+)">', r'<strong id="\1" class="kpi-value">', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated leadership_dashboard.html")
