import os

css = """
/* Phase 27.15: Desktop Tables */
.data-table {
  height: max-content; /* prevent rows stretching if only 1-3 records */
}
.data-table tr {
  height: auto; /* not excessively tall */
  min-height: 60px;
  transition: background-color 0.2s ease, transform 0.2s ease;
}
.data-table tr:hover {
  background-color: var(--color-surface-2, #F8FAFC) !important;
}
.data-table td {
  padding: 12px 16px;
  vertical-align: middle;
}
.data-table .record-title strong {
  font-size: 15.5px;
  font-weight: 600;
  color: var(--color-text-title);
  display: block;
}
.data-table .record-title span {
  font-size: 13.5px;
  color: var(--color-text-muted);
}
.data-table .muted {
  font-size: 13.5px;
  color: var(--color-text-muted);
}

/* Phase 27.15: Empty States */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  max-width: 480px;
  margin: 64px auto;
  padding: 40px;
  background: var(--color-surface-1, #fff);
  border: 1px dashed var(--color-border);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}
.empty-state-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-surface-2);
  color: var(--color-brand-cobalt);
  margin-bottom: 24px;
}
.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-title);
  margin: 0 0 8px 0;
}
.empty-state p {
  font-size: 14.5px;
  color: var(--color-text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.5;
}
.empty-state .btn-primary {
  margin-top: 16px;
}

/* Semantic Icons matching requested colors */
.nav-item[href*="/venues/"] svg { color: var(--color-brand-teal, #0D9488) !important; }
.nav-item[href*="/event-types/"] svg { color: var(--color-brand-cobalt, #1D4ED8) !important; }
.nav-item[href*="/organizations/"] svg { color: var(--indigo-500, #6366F1) !important; }
.nav-item[href*="/sponsors/"] svg { color: var(--violet-500, #8B5CF6) !important; }
.nav-item[href*="/speakers/"] svg { color: var(--color-brand-teal, #0D9488) !important; }
.nav-item[href*="/publications/"] svg { color: var(--color-brand-blue, #2563EB) !important; }
.nav-item[href*="/approvals/"] svg { color: var(--amber-500, #F59E0B) !important; }
.nav-item[href*="/displaced/"] svg { color: var(--indigo-500, #6366F1) !important; }
.nav-item[href*="/leadership/"] svg { color: var(--color-brand-cobalt, #1D4ED8) !important; }
.nav-item[href*="/reports/"] svg { color: var(--color-brand-cyan, #06B6D4) !important; }

/* Action Dropdown Phase 27.15 */
.premium-dropdown-menu {
  width: 160px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
  border: 1px solid var(--color-border) !important;
  padding: 4px !important;
}
.premium-dropdown-menu a, .premium-dropdown-menu button {
  height: 38px !important;
  font-size: 14px !important;
  border-radius: 6px !important;
  padding: 0 10px !important;
}
.premium-dropdown-menu a svg, .premium-dropdown-menu button svg {
  width: 16px !important; height: 16px !important;
}

/* Action Dropdown Semantic Colors */
.premium-dropdown-menu .action-view { color: var(--color-brand-cobalt) !important; }
.premium-dropdown-menu .action-view svg { color: var(--color-brand-cobalt) !important; }
.premium-dropdown-menu .action-edit { color: var(--amber-600) !important; }
.premium-dropdown-menu .action-edit svg { color: var(--amber-600) !important; }
.premium-dropdown-menu .action-activate { color: var(--emerald-600) !important; }
.premium-dropdown-menu .action-activate svg { color: var(--emerald-600) !important; }
.premium-dropdown-menu .action-delete { color: var(--crimson-600) !important; }
.premium-dropdown-menu .action-delete svg { color: var(--crimson-600) !important; }

/* Phase 27.15: Mobile Cards Action Footer */
@media (max-width: 767px) {
  .mobile-actions-row {
    position: static !important;
    display: flex !important;
    gap: 8px !important;
    margin-top: 16px !important;
    width: 100% !important;
    flex-wrap: nowrap !important;
    overflow: hidden !important;
  }
  .mobile-actions-row > a, .mobile-actions-row > button {
    flex: 1 1 0 !important;
    height: 44px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 8px !important;
    background: var(--color-surface-1, #fff) !important;
    border: 1px solid var(--color-border) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    gap: 6px !important;
    text-decoration: none !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
  }
  .mobile-actions-row .action-view { color: var(--color-brand-cobalt) !important; border-color: rgba(29,78,216,0.2) !important; }
  .mobile-actions-row .action-view svg { color: var(--color-brand-cobalt) !important; }
  .mobile-actions-row .action-edit { color: var(--amber-600) !important; border-color: rgba(217,119,6,0.2) !important; }
  .mobile-actions-row .action-edit svg { color: var(--amber-600) !important; }
  .mobile-actions-row .action-activate { color: var(--emerald-600) !important; border-color: rgba(5,150,105,0.2) !important; }
  .mobile-actions-row .action-activate svg { color: var(--emerald-600) !important; }
  .mobile-actions-row .action-delete { color: var(--crimson-600) !important; border-color: rgba(220,38,38,0.2) !important; }
  .mobile-actions-row .action-delete svg { color: var(--crimson-600) !important; }
}

/* Horizontal Overflow Fix */
html, body { max-width: 100vw; overflow-x: hidden; }
"""
with open("C:/IEMS/static/css/workspace.css", "a", encoding="utf-8") as f:
    f.write(css)
