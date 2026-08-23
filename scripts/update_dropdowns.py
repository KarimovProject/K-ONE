import re
import os
import glob

files = [
    r"C:\IEMS\templates\venues\venue_list.html",
    r"C:\IEMS\templates\reporting\reports_dashboard.html",
    r"C:\IEMS\templates\organizations\sponsor_list.html",
    r"C:\IEMS\templates\organizations\organization_list.html",
    r"C:\IEMS\templates\events\speaker_list.html"
]

for fp in files:
    if not os.path.exists(fp):
        continue
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove inline styles from premium-dropdown-menu
    content = re.sub(r'<div class="premium-dropdown-menu"\s+hidden\s+style="[^"]*">', '<div class="premium-dropdown-menu" hidden>', content)

    # Replace links with semantic classes
    # View
    content = re.sub(
        r'<a([^>]+href="[^"]*detail[^"]*"[^>]*)>',
        r'<a\1 class="action-view">',
        content
    )
    # Edit
    content = re.sub(
        r'<a([^>]+href="[^"]*edit[^"]*"[^>]*)>',
        r'<a\1 class="action-edit">',
        content
    )
    # Delete
    content = re.sub(
        r'<a([^>]+href="[^"]*delete[^"]*"[^>]*)>',
        r'<a\1 class="action-delete">',
        content
    )
    
    # Fix double classes if any
    content = content.replace('class="action-view" class="action-view"', 'class="action-view"')
    content = content.replace('class="action-edit" class="action-edit"', 'class="action-edit"')
    content = content.replace('class="action-delete" class="action-delete"', 'class="action-delete"')

    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)

print("Updated dropdowns in CRUD lists.")
