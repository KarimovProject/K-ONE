import os

css = """
/* Phase 27.16: Premium Typography and Spacing */
.data-table th {
  font-size: 13px !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
  padding: 12px 16px !important;
}
.data-table td {
  font-size: 14.5px !important;
  padding: 14px 16px !important;
}
.data-table .record-title strong {
  font-size: 15.5px !important;
  font-weight: 600 !important;
  color: var(--color-text-title) !important;
}
.data-table .record-title small, .data-table .record-title span {
  font-size: 13.5px !important;
  color: var(--color-text-muted) !important;
}
.data-table .muted, .data-table .soft-badge, .data-table .phase-badge, .data-table .tag {
  font-size: 13.5px !important;
}
.data-table tr {
  height: auto !important;
  min-height: 64px !important;
}

/* Phase 27.16: Sidebar Premium Styling */
.sidebar-nav-item svg {
  stroke-width: 2px !important;
  opacity: 0.8;
  transition: opacity 0.2s, transform 0.2s;
}
.sidebar-nav-item:hover svg {
  opacity: 1;
  transform: scale(1.05);
}
.sidebar-nav-item.is-active, .sidebar-nav-item.active {
  background: var(--color-surface-2) !important;
  border-left: 3px solid var(--color-brand-cobalt) !important;
  font-weight: 600 !important;
  color: var(--color-text-title) !important;
}
.sidebar-nav-item.is-active svg, .sidebar-nav-item.active svg {
  opacity: 1 !important;
}

/* Phase 27.16: Primary Buttons (Zal yaratish, Filtrlash, etc) */
.data-toolbar .btn-primary, .page-header .btn-primary, .btn-primary {
  background: var(--color-brand-cobalt, #1D4ED8) !important;
  color: #ffffff !important;
  border: none !important;
  font-weight: 500 !important;
  padding: 0 16px !important;
  height: 40px !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(29, 78, 216, 0.2) !important;
  transition: all 0.2s ease !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
}
.btn-primary:hover {
  background: var(--blue-700, #1e40af) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(29, 78, 216, 0.3) !important;
}

/* Phase 27.16: Action Dropdown Popovers */
.premium-dropdown-menu {
  width: 170px !important;
  border-radius: 10px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12) !important;
  border: 1px solid var(--color-border) !important;
  padding: 6px !important;
  background: var(--color-surface-1, #fff) !important;
}
.premium-dropdown-menu a, .premium-dropdown-menu button {
  height: 40px !important;
  font-size: 14.5px !important;
  border-radius: 6px !important;
  padding: 0 12px !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  font-weight: 500 !important;
  background: transparent !important;
  border: none !important;
  width: 100% !important;
  text-align: left !important;
  cursor: pointer !important;
}
.premium-dropdown-menu a:hover, .premium-dropdown-menu button:hover {
  background: var(--color-surface-2) !important;
}
.premium-dropdown-menu a svg, .premium-dropdown-menu button svg {
  width: 18px !important; height: 18px !important;
}

/* Phase 27.16: Mobile Cards Semantic Backgrounds */
@media (max-width: 767px) {
  .mobile-actions-row > a, .mobile-actions-row > button {
    height: 44px !important;
    border-radius: 8px !important;
    font-size: 14.5px !important;
    font-weight: 600 !important;
  }
  .mobile-actions-row .action-view { background: rgba(29,78,216,0.1) !important; color: var(--color-brand-cobalt) !important; border-color: rgba(29,78,216,0.2) !important; }
  .mobile-actions-row .action-edit { background: rgba(217,119,6,0.1) !important; color: var(--amber-600) !important; border-color: rgba(217,119,6,0.2) !important; }
  .mobile-actions-row .action-activate { background: rgba(5,150,105,0.1) !important; color: var(--emerald-600) !important; border-color: rgba(5,150,105,0.2) !important; }
  .mobile-actions-row .action-delete { background: rgba(220,38,38,0.1) !important; color: var(--crimson-600) !important; border-color: rgba(220,38,38,0.2) !important; }
}

/* Phase 27.16: Leadership Dashboard Executive Polish */
body[data-route*="leadership"] .page-header {
  padding-top: 24px !important;
  padding-bottom: 24px !important;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-1);
}
body[data-route*="leadership"] .page-header h1 {
  font-size: 28px !important;
  font-weight: 700 !important;
  color: var(--color-text-title);
  margin-bottom: 4px !important;
}
.kpi-card {
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
  background: var(--color-surface-1);
  padding: 24px;
  display: flex;
  flex-direction: column;
}
.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.kpi-icon.blue { background: rgba(29,78,216,0.1); color: var(--color-brand-cobalt); }
.kpi-icon.emerald { background: rgba(5,150,105,0.1); color: var(--emerald-600); }
.kpi-icon.amber { background: rgba(217,119,6,0.1); color: var(--amber-600); }
.kpi-title { font-size: 14.5px; font-weight: 600; color: var(--color-text-secondary); }
.kpi-value { font-size: 32px; font-weight: 700; color: var(--color-text-title); line-height: 1.2; }
"""
with open("C:/IEMS/static/css/workspace.css", "a", encoding="utf-8") as f:
    f.write(css)
