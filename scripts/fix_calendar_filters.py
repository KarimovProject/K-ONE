import re

with open(r"C:\IEMS\templates\events\calendar.html", "r", encoding="utf-8") as f:
    html = f.read()

# Make the form compact and flex-row
old_form = r'<form class="calendar-filters premium-filters".*?>'
new_form = '<form class="calendar-filters premium-filters" id="calendar-filter-form" style="display: flex; flex-direction: row; flex-wrap: wrap; align-items: center; justify-content: flex-end; gap: 12px; background: white; padding: 8px 16px; border-radius: 24px; border: 1px solid var(--color-border-subtle, #e2e8f0); max-width: fit-content; margin-left: auto;">'

html = re.sub(old_form, new_form, html, count=1)

# Remove the old dividers
html = re.sub(r'<div class="filter-divider"></div>', '', html)

# Give selects explicit width as requested
zal_regex = r'(<select class="filter-select" id="filter-venue"[^>]*>)'
turi_regex = r'(<select class="filter-select" id="filter-type"[^>]*>)'
holat_regex = r'(<select class="filter-select" id="filter-status"[^>]*>)'

html = re.sub(zal_regex, r'<select class="filter-select" id="filter-venue" style="width: 240px; border: none; background: transparent; cursor: pointer; font-size: 14px; font-weight: 500; color: #334155; padding: 4px; outline: none;" aria-label="{% trans \'Zal bo‘yicha\' %}">', html)
html = re.sub(turi_regex, r'<select class="filter-select" id="filter-type" style="width: 200px; border: none; background: transparent; cursor: pointer; font-size: 14px; font-weight: 500; color: #334155; padding: 4px; outline: none; border-left: 1px solid #e2e8f0; padding-left: 12px;" aria-label="{% trans \'Tadbir turi bo‘yicha\' %}">', html)
html = re.sub(holat_regex, r'<select class="filter-select" id="filter-status" style="width: 200px; border: none; background: transparent; cursor: pointer; font-size: 14px; font-weight: 500; color: #334155; padding: 4px; outline: none; border-left: 1px solid #e2e8f0; padding-left: 12px;" aria-label="{% trans \'Holat bo‘yicha\' %}">', html)

# Update buttons margin
btn_apply_regex = r'(<button class="btn-primary compact" style="margin-left: var\(--space-3\);"[^>]*>)'
html = re.sub(btn_apply_regex, r'<button class="btn-primary compact" style="margin-left: 4px;" type="button" id="btn-apply-filters">', html)

with open(r"C:\IEMS\templates\events\calendar.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Calendar filters fixed.")
