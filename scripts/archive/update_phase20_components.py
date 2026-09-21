import os

COMPONENTS_CSS = """/* ==========================================================================
   K-ONE DESIGN SYSTEM COMPONENTS (Phase 20)
   Unified, institutional primitives across all authenticated control center pages.
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. PAGE HEADERS & STRUCTURE
   -------------------------------------------------------------------------- */
.page-header,
.page-heading,
.master-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}

.page-title,
.page-heading h1,
.master-heading h1 {
  font-size: var(--text-title-xl);
  font-weight: var(--weight-black);
  color: var(--color-text-title);
  margin: 0;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.page-description,
.page-heading p,
.master-heading p {
  font-size: var(--text-body);
  color: var(--color-text-secondary);
  margin: var(--space-1) 0 0;
  line-height: 1.5;
}

.page-actions,
.report-export-actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
}

.eyebrow {
  font-size: var(--text-micro);
  font-weight: var(--weight-black);
  color: var(--color-brand-cyan);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  display: block;
  margin-bottom: var(--space-1);
}

/* --------------------------------------------------------------------------
   2. BUTTONS & ACTIONS
   -------------------------------------------------------------------------- */
.btn,
.primary-button,
.secondary-button,
.text-button,
.primary-link,
.quiet-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-family: var(--font-sans);
  font-size: var(--text-label);
  font-weight: var(--weight-semibold);
  height: 42px;
  padding: 0 var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
  box-sizing: border-box;
  transition: all var(--duration-micro) var(--ease-out);
}

.btn:focus-visible,
.primary-button:focus-visible,
.secondary-button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-brand-cobalt-subtle);
}

/* Primary Button (Deep Navy or Cobalt) */
.btn--primary,
.primary-button,
.primary-link {
  background: var(--color-brand-navy);
  color: var(--color-text-inverse) !important;
  border-color: rgba(0, 174, 239, 0.25);
  box-shadow: 0 2px 6px rgba(7, 26, 51, 0.12);
}

.btn--primary:hover,
.primary-button:hover,
.primary-link:hover {
  background: var(--color-brand-navy-light);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(7, 26, 51, 0.18);
}

/* Secondary Button (Clean White Surface) */
.btn--secondary,
.secondary-button {
  background: var(--color-surface-elevated);
  color: var(--color-text-main) !important;
  border-color: var(--color-border-default);
  box-shadow: var(--shadow-sm);
}

.btn--secondary:hover,
.secondary-button:hover {
  background: var(--color-surface-panel);
  border-color: var(--color-brand-cobalt);
  color: var(--color-brand-cobalt) !important;
}

/* Compact Sizing */
.btn--compact,
.primary-button.compact,
.secondary-button.compact {
  height: 36px;
  padding: 0 var(--space-3);
  font-size: var(--text-meta);
}

/* Text / Ghost Button */
.btn--ghost,
.text-button,
.quiet-link {
  background: transparent;
  color: var(--color-text-secondary) !important;
  border-color: transparent;
  padding: 0 var(--space-3);
}

.btn--ghost:hover,
.text-button:hover,
.quiet-link:hover {
  background: rgba(7, 26, 51, 0.04);
  color: var(--color-text-main) !important;
}

/* Danger / Cancel Button */
.btn--danger,
.danger-button,
a.danger {
  color: var(--color-brand-coral) !important;
  background: rgba(239, 91, 103, 0.08);
  border-color: rgba(239, 91, 103, 0.2);
}

.btn--danger:hover,
a.danger:hover {
  background: rgba(239, 91, 103, 0.15);
}

/* --------------------------------------------------------------------------
   3. FORMS, INPUTS & CONTROLS (Standard 42px)
   -------------------------------------------------------------------------- */
input[type="text"],
input[type="search"],
input[type="date"],
input[type="email"],
input[type="password"],
input[type="number"],
select,
textarea,
.form-control,
.input-control,
.search-input,
.select-control {
  font-family: var(--font-sans);
  font-size: var(--text-label);
  color: var(--color-text-main);
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  padding: 0 var(--space-3);
  height: 42px;
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--duration-micro) var(--ease-out), box-shadow var(--duration-micro) var(--ease-out);
}

input[type="text"]:focus,
input[type="search"]:focus,
input[type="date"]:focus,
input[type="email"]:focus,
input[type="password"]:focus,
input[type="number"]:focus,
select:focus,
textarea:focus,
.form-control:focus,
.input-control:focus {
  border-color: var(--color-brand-cobalt);
  box-shadow: 0 0 0 3px var(--color-brand-cobalt-subtle);
}

textarea {
  min-height: 100px;
  padding: var(--space-2) var(--space-3);
  height: auto;
  line-height: 1.5;
  resize: vertical;
}

select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2347566B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 36px;
  cursor: pointer;
}

/* Filter Bar & Toolbars */
.filter-bar,
.data-toolbar,
.table-toolbar {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  margin-bottom: var(--space-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-3);
  box-shadow: var(--shadow-sm);
}

.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-2);
  width: 100%;
}

.search-input-wrap,
.search-field {
  position: relative;
  display: inline-flex;
  align-items: center;
  flex: 1;
  min-width: 220px;
}

.search-input-wrap input,
.search-field input {
  width: 100%;
  padding-left: 36px;
}

.search-input-wrap::before,
.search-field span[aria-hidden="true"] {
  position: absolute;
  left: 12px;
  color: var(--color-text-muted);
  pointer-events: none;
  font-size: 14px;
}

.search-input-wrap::before {
  content: '⌕';
  font-size: 18px;
  line-height: 1;
}

/* Form Layouts & Grids */
.data-form,
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-4);
}

.form-field,
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.form-field label,
.form-group label {
  font-size: var(--text-label);
  font-weight: var(--weight-semibold);
  color: var(--color-text-title);
}

.form-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-5);
}

.field-error {
  color: var(--color-brand-coral);
  font-size: var(--text-meta);
  font-weight: var(--weight-medium);
}

/* --------------------------------------------------------------------------
   4. DATA TABLES & RECORD LISTS
   -------------------------------------------------------------------------- */
.table-card,
.data-surface,
.workspace-event-table {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-5);
}

.table-responsive,
.table-scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  text-align: left;
}

.data-table thead th {
  background: var(--color-surface-panel);
  color: var(--color-text-secondary);
  font-size: var(--text-micro);
  font-weight: var(--weight-black);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border-subtle);
  white-space: nowrap;
}

.data-table tbody tr {
  height: 56px;
  background: var(--color-surface-elevated);
  transition: background-color var(--duration-micro) var(--ease-out);
}

.data-table tbody tr:hover {
  background: var(--color-surface-base);
}

.data-table tbody td {
  padding: 12px 16px;
  border-bottom: 1px solid #F1F5F9;
  font-size: var(--text-table);
  color: var(--color-text-main);
  vertical-align: middle;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.table-title-link,
.record-title {
  color: var(--color-text-title);
  text-decoration: none;
  font-weight: var(--weight-bold);
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  line-height: 1.3;
}

.table-title-link:hover,
.record-title:hover {
  color: var(--color-brand-cobalt);
  text-decoration: underline;
}

.record-code {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: var(--weight-bold);
  background: var(--color-surface-panel);
  color: var(--color-text-secondary);
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  border: 1px solid var(--color-border-subtle);
}

.table-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-2);
}

.table-actions a {
  font-size: var(--text-meta);
  font-weight: var(--weight-semibold);
  color: var(--color-brand-cobalt);
  text-decoration: none;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: background 0.16s ease;
}

.table-actions a:hover {
  background: var(--color-surface-tint-blue);
  text-decoration: underline;
}

/* 3-Dot Action Menu */
details.row-actions {
  position: relative;
  display: inline-block;
}

details.row-actions summary {
  list-style: none;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: 16px;
  font-weight: var(--weight-bold);
  transition: background 0.16s ease;
  user-select: none;
}

details.row-actions summary::-webkit-details-marker {
  display: none;
}

details.row-actions summary:hover {
  background: var(--color-surface-panel);
  color: var(--color-text-main);
}

details.row-actions div {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 4px;
  background: #FFFFFF;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 140px;
  z-index: var(--z-dropdown);
  display: flex;
  flex-direction: column;
  padding: 4px;
}

details.row-actions div a {
  padding: 8px 12px;
  font-size: 12px;
  font-weight: var(--weight-semibold);
  color: var(--color-text-main);
  text-decoration: none;
  border-radius: var(--radius-sm);
  display: block;
  text-align: left;
  transition: background 0.16s ease;
}

details.row-actions div a:hover {
  background: var(--color-surface-panel);
  color: var(--color-brand-cobalt);
}

details.row-actions div a.danger {
  color: var(--color-brand-coral);
}

details.row-actions div a.danger:hover {
  background: var(--color-status-critical-bg);
}

/* --------------------------------------------------------------------------
   5. STATUS BADGES & TYPE PILLS
   -------------------------------------------------------------------------- */
.status-badge,
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  font-size: var(--text-micro);
  font-weight: var(--weight-black);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  white-space: nowrap;
  line-height: 1.4;
}

.status-badge::before,
.chip::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.published,
.status-badge.confirmed,
.status-badge.active,
.chip--free {
  background: var(--color-status-free-bg);
  color: var(--color-status-free);
}
.status-badge.published::before,
.status-badge.confirmed::before,
.status-badge.active::before,
.chip--free::before {
  background: var(--color-status-free);
}

.status-badge.pending,
.status-badge.pending_approval,
.status-badge.upcoming,
.chip--upcoming {
  background: var(--color-status-upcoming-bg);
  color: var(--color-status-upcoming);
}
.status-badge.pending::before,
.status-badge.pending_approval::before,
.status-badge.upcoming::before,
.chip--upcoming::before {
  background: var(--color-status-upcoming);
}

.status-badge.draft,
.status-badge.special,
.chip--special {
  background: var(--color-status-special-bg);
  color: var(--color-status-special);
}
.status-badge.draft::before,
.status-badge.special::before,
.chip--special::before {
  background: var(--color-status-special);
}

.status-badge.cancelled,
.status-badge.rejected,
.status-badge.critical,
.status-badge.is-inactive {
  background: var(--color-status-critical-bg);
  color: var(--color-status-critical);
}
.status-badge.cancelled::before,
.status-badge.rejected::before,
.status-badge.critical::before,
.status-badge.is-inactive::before {
  background: var(--color-status-critical);
}

.type-pill {
  display: inline-flex;
  align-items: center;
  font-size: var(--text-meta);
  font-weight: var(--weight-semibold);
  color: var(--color-text-main);
  padding: 2px 8px;
  background: var(--color-surface-panel);
  border-radius: var(--radius-xs);
}

.type-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--type-color, var(--color-brand-cobalt));
  margin-right: 6px;
}

.color-code {
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--color-surface-panel);
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.color-code span {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
  background: var(--type-color);
}

/* --------------------------------------------------------------------------
   6. EMPTY STATES & PAGINATION
   -------------------------------------------------------------------------- */
.empty-state,
.empty-list {
  padding: var(--space-10) var(--space-6);
  text-align: center;
  background: #FFFFFF;
  border-radius: var(--radius-xl);
}

.empty-state h3,
.empty-list h2 {
  font-size: 1.15rem;
  font-weight: var(--weight-black);
  color: var(--color-text-title);
  margin: var(--space-2) 0 var(--space-1);
}

.empty-state p,
.empty-list p {
  font-size: var(--text-label);
  color: var(--color-text-muted);
  max-width: 420px;
  margin: 0 auto var(--space-4);
  line-height: 1.5;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface-panel);
  border-top: 1px solid var(--color-border-subtle);
  font-size: var(--text-meta);
  color: var(--color-text-secondary);
}

.pagination-links {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.pagination-links a,
.pagination-links span {
  height: 32px;
  min-width: 32px;
  padding: 0 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  text-decoration: none;
  font-weight: var(--weight-semibold);
  font-size: 12px;
}

.pagination-links a {
  color: var(--color-text-main);
  background: #FFFFFF;
  border: 1px solid var(--color-border-subtle);
}

.pagination-links a:hover {
  background: var(--color-surface-tint-blue);
  color: var(--color-brand-cobalt);
  border-color: var(--color-brand-cobalt);
}

.pagination-links span.current {
  background: var(--color-brand-navy);
  color: #FFFFFF;
}

/* --------------------------------------------------------------------------
   7. MODALS & DRAWERS
   -------------------------------------------------------------------------- */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(7, 26, 51, 0.4);
  backdrop-filter: blur(4px);
  z-index: var(--z-drawer);
  display: flex;
  justify-content: flex-end;
}

.drawer-overlay[hidden] {
  display: none !important;
}

.drawer-panel {
  width: 100%;
  max-width: 440px;
  height: 100vh;
  background: #FFFFFF;
  box-shadow: -8px 0 24px rgba(7, 26, 51, 0.12);
  display: flex;
  flex-direction: column;
  padding: var(--space-6);
  box-sizing: border-box;
  animation: slideInRight 0.24s var(--ease-out);
}

@keyframes slideInRight {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.drawer-close {
  align-self: flex-end;
  background: transparent;
  border: none;
  font-size: 24px;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px 8px;
}

.drawer-close:hover {
  color: var(--color-text-title);
}

.drawer-header {
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border-subtle);
}

.drawer-header h2 {
  font-size: 1.25rem;
  font-weight: var(--weight-bold);
  color: var(--color-text-title);
  margin: var(--space-2) 0 0;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: var(--text-micro);
  font-weight: var(--weight-bold);
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.info-value {
  font-size: var(--text-table);
  font-weight: var(--weight-semibold);
  color: var(--color-text-title);
}

.drawer-footer {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-subtle);
}

/* Skip Link */
.skip-link {
  position: absolute;
  top: -100px;
  left: 0;
  background: var(--color-brand-navy);
  color: #FFFFFF;
  padding: 12px 16px;
  z-index: 9999;
  border-radius: 0 0 8px 0;
  font-weight: 700;
  text-decoration: none;
}
.skip-link:focus {
  top: 0;
}
"""

with open('static/css/components.css', 'w', encoding='utf-8') as f:
    f.write(COMPONENTS_CSS)

print("Updated components.css with comprehensive K-ONE components.")
