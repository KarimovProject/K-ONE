import os
import re

# 1. Update workspace.css
workspace_css = "C:/IEMS/static/css/workspace.css"
css_append = """
/* Phase 27.18 overrides */
@media (min-width: 768px) {
  .mobile-only {
    display: none !important;
  }
}

.premium-dropdown-menu .action-view, .premium-dropdown-menu .action-view svg,
.dropdown-wrapper .action-view, .dropdown-wrapper .action-view svg {
    color: var(--color-brand-cobalt, #2563eb) !important;
}

.premium-dropdown-menu .action-edit, .premium-dropdown-menu .action-edit svg,
.dropdown-wrapper .action-edit, .dropdown-wrapper .action-edit svg {
    color: var(--amber-600, #d97706) !important;
}

.premium-dropdown-menu .action-activate, .premium-dropdown-menu .action-activate svg,
.dropdown-wrapper .action-activate, .dropdown-wrapper .action-activate svg {
    color: var(--emerald-600, #059669) !important;
}

.premium-dropdown-menu .action-delete, .premium-dropdown-menu .action-delete svg,
.dropdown-wrapper .action-delete, .dropdown-wrapper .action-delete svg {
    color: var(--crimson-600, #dc2626) !important;
}
"""
with open(workspace_css, "a", encoding="utf-8") as f:
    f.write(css_append)

# 2. Update leadership_dashboard.html
leadership_html = "C:/IEMS/templates/reporting/leadership_dashboard.html"
with open(leadership_html, "r", encoding="utf-8") as f:
    content = f.read()

# Update spacing
content = content.replace("margin-bottom: var(--space-8);\n    padding-bottom: var(--space-6);", "margin-bottom: var(--space-6);\n    padding-bottom: var(--space-4);")
content = content.replace("gap: var(--space-5);\n    margin-bottom: var(--space-8);", "gap: var(--space-5);\n    margin-bottom: var(--space-6);")

# Update H1 size
content = content.replace("font-size: var(--font-size-page-title);\n    font-weight: var(--font-weight-extrabold);", "font-size: 32px;\n    font-weight: 700;")

# Update header text
old_header = """<p class="eyebrow" style="color: var(--scientific-cyan);">{% trans "Executive Intelligence" %}</p>
      <h1>{% trans "Leadership Dashboard" %}</h1>
      <p class="muted">{% trans "Real-time institutional oversight and executive resource visibility." %}</p>"""
new_header = """<p class="eyebrow" style="margin-bottom: var(--space-1); text-transform: uppercase; font-size: var(--font-size-xs); font-weight: var(--font-weight-bold); letter-spacing: 0.05em; color: var(--scientific-cyan);">K-ONE / RAHBARIYAT</p>
      <h1>Rahbariyat paneli</h1>
      <p class="muted">Muassasa ustidan real vaqt rejimida nazorat va resurslar holati.</p>"""
content = content.replace(old_header, new_header)

# Make KPI numbers and labels correct sizes
content = content.replace("font-size: var(--font-size-5xl);", "font-size: 30px;")
content = content.replace("font-size: var(--font-size-small);", "font-size: 14.5px;")

# Fix KPIs 3, 4, 5 to have icon containers
kpi3_old = """<div class="leadership-kpi" style="--kpi-color: var(--crimson-500);">
      <div class="kpi-header">
        <span>{% trans "Occupied Venues" %}</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
      </div>"""
kpi3_new = """<div class="kpi-card leadership-kpi" style="--kpi-color: var(--crimson-500);">
      <div class="kpi-header">
        <span class="kpi-title">{% trans "Occupied Venues" %}</span>
        <div class="kpi-icon crimson"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg></div>
      </div>"""
content = content.replace(kpi3_old, kpi3_new)

kpi4_old = """<div class="leadership-kpi" style="--kpi-color: var(--royal-blue);">
      <div class="kpi-header">
        <span>{% trans "Today's Check-ins" %}</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg>
      </div>"""
kpi4_new = """<div class="kpi-card leadership-kpi" style="--kpi-color: var(--royal-blue);">
      <div class="kpi-header">
        <span class="kpi-title">{% trans "Today's Check-ins" %}</span>
        <div class="kpi-icon blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><polyline points="17 11 19 13 23 9"/></svg></div>
      </div>"""
content = content.replace(kpi4_old, kpi4_new)

with open(leadership_html, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied Phase 27.18 overrides!")
