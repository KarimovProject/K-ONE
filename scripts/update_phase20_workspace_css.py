import os

WORKSPACE_CSS = """/* ==========================================================================
   K-ONE WORKSPACE & OPERATIONAL CONTROL CENTER (Phase 20)
   Compact, High-Density Enterprise Layouts
   ========================================================================== */

.workspace-page,
.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}

.animate-entrance {
  animation: pageEntrance 0.28s var(--ease-out);
}

@keyframes pageEntrance {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --------------------------------------------------------------------------
   1. WORKSPACE HERO SECTION
   -------------------------------------------------------------------------- */
.workspace-hero {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-4) var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-sm);
}

.workspace-hero__copy {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.workspace-hero__badge-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.role-badge {
  background: rgba(23, 105, 255, 0.08);
  color: var(--color-brand-cobalt);
  font-size: var(--text-micro);
  font-weight: var(--weight-black);
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.workspace-date-pill {
  font-size: var(--text-micro);
  font-weight: var(--weight-bold);
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.workspace-hero h1 {
  font-size: var(--text-title);
  font-weight: var(--weight-black);
  color: var(--color-text-title);
  margin: 0;
  letter-spacing: -0.02em;
}

.workspace-hero p {
  font-size: var(--text-label);
  color: var(--color-text-secondary);
  margin: 0;
}

.compact-hero-btn {
  height: 42px;
  padding: 0 var(--space-5);
  border-radius: var(--radius-pill);
  font-size: var(--text-label);
  font-weight: var(--weight-bold);
  background: var(--color-brand-navy);
  color: #FFFFFF !important;
  border: 1px solid rgba(0, 174, 239, 0.3);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  box-shadow: 0 2px 6px rgba(7, 26, 51, 0.15);
  transition: all var(--duration-micro) var(--ease-out);
}

.compact-hero-btn:hover {
  background: var(--color-brand-navy-light);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(7, 26, 51, 0.22);
}

/* --------------------------------------------------------------------------
   2. KPI COMMAND TILES
   -------------------------------------------------------------------------- */
.workspace-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.metric-tile,
.metric-card {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  box-shadow: var(--shadow-sm);
  transition: transform var(--duration-fast) var(--ease-out), box-shadow var(--duration-fast) var(--ease-out), border-color var(--duration-fast) var(--ease-out);
}

.metric-tile:hover,
.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: rgba(0, 174, 239, 0.4);
}

.metric-tile__icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.metric-tile--cobalt .metric-tile__icon {
  background: rgba(23, 105, 255, 0.08);
  color: var(--color-brand-cobalt);
}

.metric-tile--coral .metric-tile__icon {
  background: rgba(239, 91, 103, 0.1);
  color: var(--color-brand-coral);
}

.metric-tile--amber .metric-tile__icon {
  background: rgba(245, 166, 35, 0.1);
  color: var(--color-status-upcoming);
}

.metric-tile--cyan .metric-tile__icon {
  background: rgba(0, 174, 239, 0.1);
  color: var(--color-brand-cyan);
}

.metric-tile__content {
  display: flex;
  flex-direction: column;
}

.metric-tile__label {
  font-size: var(--text-micro);
  font-weight: var(--weight-black);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-tile__value {
  font-size: var(--text-operational);
  font-weight: var(--weight-black);
  color: var(--color-text-title);
  line-height: 1.1;
  margin-top: 2px;
}

/* --------------------------------------------------------------------------
   3. TWO-COLUMN WORKSPACE GRID
   -------------------------------------------------------------------------- */
.workspace-grid {
  display: grid;
  grid-template-columns: 64% 1fr;
  gap: var(--space-4);
  align-items: start;
}

.workspace-panel,
.panel {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border-subtle);
}

.panel-eyebrow {
  font-size: var(--text-micro);
  font-weight: var(--weight-black);
  color: var(--color-brand-cyan);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  display: block;
}

.panel-title {
  font-size: 1.15rem;
  font-weight: var(--weight-black);
  color: var(--color-text-title);
  margin: 2px 0 0;
}

.panel-action-link {
  font-size: var(--text-meta);
  font-weight: var(--weight-bold);
  color: var(--color-brand-cobalt);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 4px;
}

.panel-action-link:hover {
  text-decoration: underline;
}

/* Agenda list */
.workspace-event-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.workspace-event-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 10px 14px;
  background: #FAFBFD;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-subtle);
  text-decoration: none;
  transition: all var(--duration-micro) var(--ease-out);
}

.workspace-event-row:hover {
  background: #FFFFFF;
  transform: translateX(2px);
  border-color: rgba(0, 174, 239, 0.4);
  box-shadow: var(--shadow-sm);
}

.event-row-time {
  display: flex;
  flex-direction: column;
  min-width: 64px;
  font-family: var(--font-mono);
}

.event-row-time .date {
  font-size: var(--text-micro);
  font-weight: var(--weight-black);
  color: var(--color-text-title);
}

.event-row-time .time {
  font-size: 10px;
  font-weight: var(--weight-semibold);
  color: var(--color-text-muted);
}

.event-row-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.event-row-info .title {
  font-size: var(--text-label);
  font-weight: var(--weight-bold);
  color: var(--color-text-title);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-row-info .meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-micro);
  color: var(--color-text-muted);
}

.event-row-arrow {
  color: var(--color-text-muted);
  font-size: 14px;
  transition: transform var(--duration-micro) ease;
}

.workspace-event-row:hover .event-row-arrow {
  transform: translateX(2px);
  color: var(--color-brand-cobalt);
}

/* Quick actions */
.workspace-quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.quick-action-item {
  height: 48px;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0 14px;
  background: #FAFBFD;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-subtle);
  text-decoration: none;
  transition: all var(--duration-micro) var(--ease-out);
}

.quick-action-item:hover {
  background: #FFFFFF;
  transform: translateX(2px);
  border-color: rgba(0, 174, 239, 0.4);
  box-shadow: var(--shadow-sm);
}

.quick-action-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-action-icon.cobalt { background: rgba(23, 105, 255, 0.08); color: var(--color-brand-cobalt); }
.quick-action-icon.cyan { background: rgba(0, 174, 239, 0.1); color: var(--color-brand-cyan); }
.quick-action-icon.emerald { background: rgba(22, 199, 132, 0.1); color: var(--color-status-free); }
.quick-action-icon.violet { background: rgba(118, 89, 255, 0.1); color: var(--color-brand-violet); }

.quick-action-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.quick-action-text strong {
  font-size: var(--text-meta);
  font-weight: var(--weight-bold);
  color: var(--color-text-title);
}

.quick-action-text small {
  font-size: 10px;
  color: var(--color-text-muted);
}

.quick-action-item .arrow {
  color: var(--color-text-muted);
  font-size: 13px;
  transition: transform var(--duration-micro) ease;
}

.quick-action-item:hover .arrow {
  transform: translateX(2px);
  color: var(--color-brand-cobalt);
}

/* --------------------------------------------------------------------------
   4. REPORTS & ANALYTICS PANELS
   -------------------------------------------------------------------------- */
.report-filter-panel {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-4);
}

.report-filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--space-3);
}

.report-period {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-mono);
  font-size: var(--text-meta);
  font-weight: var(--weight-bold);
  background: var(--color-surface-panel);
  color: var(--color-text-title);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-subtle);
}

.report-kpis {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-5);
}

.report-kpis > div {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  box-shadow: var(--shadow-sm);
}

.report-kpis > div span {
  font-size: var(--text-micro);
  font-weight: var(--weight-black);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.report-kpis > div strong {
  font-size: 1.5rem;
  font-weight: var(--weight-black);
  color: var(--color-text-title);
}

.report-kpis > div small {
  font-size: 11px;
  color: var(--color-text-muted);
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

.report-panel {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.report-panel.report-wide {
  grid-column: span 2;
}

/* --------------------------------------------------------------------------
   5. PROFILE PAGE (3 Structured Panels)
   -------------------------------------------------------------------------- */
.profile-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: var(--space-4);
  align-items: start;
}

.profile-form-panel {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.profile-identity {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border-subtle);
}

.profile-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: #FFFFFF;
  font-size: 22px;
  font-weight: var(--weight-black);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(7, 26, 51, 0.15);
}

.profile-summary {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.profile-card {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.profile-card h2 {
  font-size: 1rem;
  font-weight: var(--weight-black);
  color: var(--color-text-title);
  margin: 0 0 var(--space-2);
}

.activity-dl {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin: 0;
}

.activity-dl div {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-surface-panel);
}

.activity-dl dt {
  font-size: var(--text-label);
  color: var(--color-text-secondary);
}

.activity-dl dd {
  font-size: var(--text-label);
  font-weight: var(--weight-bold);
  color: var(--color-text-title);
  margin: 0;
}

/* --------------------------------------------------------------------------
   6. WIZARD STEP INDICATOR
   -------------------------------------------------------------------------- */
.wizard-progress {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-5);
  margin-bottom: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.wizard-step {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-muted);
  font-size: var(--text-meta);
  font-weight: var(--weight-semibold);
}

.wizard-step.active {
  color: var(--color-brand-cobalt);
  font-weight: var(--weight-bold);
}

.wizard-step.completed {
  color: var(--color-status-free);
}

.wizard-step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-surface-panel);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: var(--weight-bold);
}

.wizard-step.active .wizard-step-num {
  background: var(--color-brand-cobalt);
  color: #FFFFFF;
}

.wizard-step.completed .wizard-step-num {
  background: var(--color-status-free);
  color: #FFFFFF;
}

/* --------------------------------------------------------------------------
   7. RESPONSIVE BREAKPOINTS
   -------------------------------------------------------------------------- */
@media (max-width: 1200px) {
  .report-kpis {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .workspace-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
  .workspace-grid,
  .profile-layout,
  .report-grid {
    grid-template-columns: 1fr;
  }
  .report-panel.report-wide {
    grid-column: span 1;
  }
}

@media (max-width: 640px) {
  .workspace-hero {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }
  .compact-hero-btn {
    width: 100%;
    justify-content: center;
  }
  .workspace-metrics,
  .report-kpis {
    grid-template-columns: 1fr;
  }
}
"""

with open('static/css/workspace.css', 'w', encoding='utf-8') as f:
    f.write(WORKSPACE_CSS)

print("Updated workspace.css with high-density enterprise layouts.")
