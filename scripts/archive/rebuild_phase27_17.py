import os
import re

# 1. Update CSS in workspace.css
css = """
/* Phase 27.17: Mobile Actions constraints */
.mobile-actions-row {
  display: flex !important;
  gap: 8px !important;
  width: 100% !important;
  flex-wrap: wrap !important;
}
.mobile-actions-row > a, .mobile-actions-row > button, .mobile-actions-row > form {
  flex: 1 1 calc(50% - 4px) !important;
  min-width: 0 !important;
}
.mobile-actions-row .action-view, .mobile-actions-row .action-edit, .mobile-actions-row .action-activate, .mobile-actions-row .action-delete {
  min-height: 44px !important;
  height: auto !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 8px 12px !important;
  border-radius: 8px !important;
  font-size: 14.5px !important;
  font-weight: 600 !important;
  white-space: nowrap !important;
  text-decoration: none !important;
  gap: 8px !important;
  width: 100% !important;
  box-sizing: border-box !important;
}
.mobile-actions-row svg {
  flex: 0 0 auto !important;
  width: 18px !important;
  height: 18px !important;
  max-width: 20px !important;
  max-height: 20px !important;
}

/* Phase 27.17: Desktop Dropdown Colors */
.premium-dropdown-menu {
  width: 180px !important;
  padding: 6px !important;
}
.premium-dropdown-menu .action-view, .premium-dropdown-menu .action-view svg { color: var(--color-brand-cobalt) !important; }
.premium-dropdown-menu .action-edit, .premium-dropdown-menu .action-edit svg { color: var(--amber-600) !important; }
.premium-dropdown-menu .action-activate, .premium-dropdown-menu .action-activate svg { color: var(--emerald-600) !important; }
.premium-dropdown-menu .action-delete, .premium-dropdown-menu .action-delete svg { color: var(--crimson-600) !important; }

.premium-dropdown-menu a, .premium-dropdown-menu button {
  white-space: nowrap !important;
  text-decoration: none !important;
}

/* Phase 27.17: Primary CTA */
.btn-primary, .primary-button, .btn-create-event {
  background: var(--color-brand-cobalt, #1D4ED8) !important;
  color: #ffffff !important;
  text-decoration: none !important;
  min-height: 44px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 0 20px !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 8px rgba(29, 78, 216, 0.2) !important;
  border: none !important;
  gap: 8px !important;
}
.btn-primary:hover, .primary-button:hover, .btn-create-event:hover {
  background: var(--blue-700, #1e40af) !important;
  color: #ffffff !important;
  text-decoration: none !important;
}
/* Ensure svg doesn't resize in cta */
.btn-primary svg, .primary-button svg, .btn-create-event svg {
  width: 18px !important;
  height: 18px !important;
  flex: 0 0 auto !important;
}

/* Phase 27.17: Leadership Dashboard Refinement */
body[data-route*="leadership"] .page-header {
  padding-bottom: 12px !important;
}
.leadership-head {
  margin-bottom: var(--space-4) !important;
  padding-bottom: var(--space-4) !important;
}
.leadership-kpis {
  gap: var(--space-4) !important;
}
.kpi-card {
  padding: 16px 20px !important;
}
.leadership-venue-card {
  min-height: 10rem !important;
}
.kpi-value {
  font-size: 28px !important;
}
.kpi-icon {
  width: 40px !important;
  height: 40px !important;
}
"""
with open("C:/IEMS/static/css/workspace.css", "a", encoding="utf-8") as f:
    f.write(css)

# 2. Fix events/event_list.html
event_list_path = 'C:/IEMS/templates/events/event_list.html'
with open(event_list_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Edit permission check
content = content.replace("{% if can_create and e.status != 'cancelled' %}", "{% if can_create %}")
# Remove btn-create-event and use btn-primary
content = content.replace('class="btn-create-event"', 'class="btn-primary"')
content = content.replace('class="primary-button compact"', 'class="btn-primary compact"')

with open(event_list_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 3. Ensure other lists have btn-primary
# Not strictly necessary to change the classes if my CSS hits them all, 
# but let's make sure `calendar.html` has btn-primary
calendar_path = 'C:/IEMS/templates/events/calendar.html'
with open(calendar_path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('class="primary-button"', 'class="btn-primary"')
with open(calendar_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 4. In page_header.html, verify a tag has no underline natively just in case
page_header = 'C:/IEMS/templates/master_data/page_header.html'
with open(page_header, 'r', encoding='utf-8') as f:
    content = f.read()
# It uses class="btn btn-primary", which is caught by .btn-primary CSS rule.

print("Applied Phase 27.17 fixes!")
