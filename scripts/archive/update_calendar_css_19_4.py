import os

CALENDAR_CSS = """/* ==========================================================================
   IEMS PUBLIC CALENDAR - Phase 19.4 K-ONE Operational Center
   Scoped strictly to .public-calendar and .calendar-inspector
   ========================================================================== */

.public-calendar {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 1800px;
  margin: 0 auto;
  width: 100%;
}

/* --------------------------------------------------------------------------
   1. TOP COMMAND BAR
   -------------------------------------------------------------------------- */
.calendar-command-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: #FFFFFF;
  border-radius: var(--radius-pill);
  border: 1px solid var(--color-border-subtle);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-2);
}

.calendar-command-bar__left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.btn-cal-nav {
  width: 36px;
  height: 36px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 800;
  font-size: 14px;
}
.btn-cal-today {
  height: 36px;
  padding: 0 16px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 700;
}

.calendar-command-bar__center {
  font-size: clamp(1.2rem, 2vw, 1.45rem);
  font-weight: 800;
  color: var(--color-text-title, #071A33);
  letter-spacing: -0.02em;
}

.calendar-command-bar__right {
  display: flex;
  align-items: center;
}

/* --------------------------------------------------------------------------
   2. UNIFIED FILTER TOOLBAR & CTA
   -------------------------------------------------------------------------- */
.calendar-toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  flex-wrap: wrap;
}

.calendar-filters.premium-filters {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: 4px 8px;
  box-shadow: var(--shadow-sm);
  flex: 1;
  max-width: 820px;
}

.filter-group {
  display: flex;
  align-items: center;
  position: relative;
}
.filter-group--search {
  flex: 1.2;
}

.filter-icon {
  position: absolute;
  left: 10px;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  pointer-events: none;
}

.filter-input {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 8px 12px 8px 34px !important;
  font-size: 13px;
  color: var(--color-text-main);
  width: 100%;
}
.filter-input:focus { outline: none; }

.filter-select {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 8px 24px 8px 12px !important;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-main);
  cursor: pointer;
  appearance: none;
  min-width: 160px;
}
.filter-select:focus { outline: none; }

.filter-divider {
  width: 1px;
  height: 22px;
  background: var(--color-border-subtle);
  margin: 0 4px;
}

.filter-clear {
  color: var(--color-text-muted);
  font-weight: 700;
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  margin-left: 4px;
  white-space: nowrap;
}
.filter-clear:hover {
  background: rgba(0,0,0,0.03);
  color: var(--color-text-title);
}

.btn-create-event {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #082B57;
  color: #FFFFFF;
  font-weight: 700;
  font-size: 13px;
  padding: 10px 22px;
  border-radius: var(--radius-pill);
  border: 1px solid rgba(22, 188, 235, 0.3);
  box-shadow: 0 2px 8px rgba(8, 43, 87, 0.2);
  transition: all 0.2s var(--ease-out);
  text-decoration: none;
  white-space: nowrap;
}
.btn-create-event:hover {
  background: #0A356C;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 43, 87, 0.25);
  color: #FFFFFF;
}

/* --------------------------------------------------------------------------
   3. MONTH GRID
   -------------------------------------------------------------------------- */
.calendar-month.premium-grid {
  background: #FFFFFF;
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border-subtle);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.calendar-month__header {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  border-bottom: 1px solid var(--color-border-subtle);
  background: #FAFBFD;
}
.calendar-month__weekday {
  padding: 12px 8px;
  text-align: center;
  font-size: 11px;
  font-weight: 800;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.calendar-month__grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  grid-auto-rows: minmax(135px, auto);
  gap: 1px;
  background: var(--color-border-subtle);
}

/* Day Cells */
.calendar-day {
  background: #FFFFFF;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  transition: background-color 0.15s ease;
  min-height: 135px;
}
.calendar-day:hover {
  background: #FAFBFD;
}
.calendar-day--weekend {
  background: #F8FAFC;
}
.calendar-day--outside {
  opacity: 0.35;
  background: #FAFBFD;
}
.calendar-day--today {
  background: #F2F7FF !important;
}

.calendar-day__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.calendar-day__number {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-main);
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.calendar-day--today .calendar-day__number {
  background: #082B57;
  color: #FFFFFF;
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(8, 43, 87, 0.35);
}
.calendar-day__count {
  font-size: 10px;
  font-weight: 800;
  color: var(--color-brand-cobalt);
  background: rgba(20, 92, 255, 0.08);
  padding: 1px 6px;
  border-radius: var(--radius-pill);
}

/* Event Capsules in Calendar */
.calendar-events {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.cal-capsule {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 4px 7px;
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
  border-left: 3px solid transparent;
  background: #FFFFFF;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border-top: 1px solid rgba(0,0,0,0.04);
  border-right: 1px solid rgba(0,0,0,0.04);
  border-bottom: 1px solid rgba(0,0,0,0.04);
  transition: transform 0.16s var(--ease-out), box-shadow 0.16s var(--ease-out);
}
.cal-capsule:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 8px rgba(0,0,0,0.08);
}

.cal-capsule--cobalt {
  border-left-color: var(--color-brand-cobalt);
}
.cal-capsule--cyan {
  border-left-color: var(--color-brand-cyan);
}
.cal-capsule--emerald {
  border-left-color: var(--color-status-free);
}
.cal-capsule--violet {
  border-left-color: var(--color-brand-violet);
}
.cal-capsule--amber {
  border-left-color: var(--color-status-upcoming);
}

.cal-capsule__meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--color-text-muted);
  font-weight: 700;
}
.cal-capsule__room {
  color: var(--color-brand-cobalt);
  font-weight: 800;
}
.cal-capsule__title {
  font-weight: 700;
  color: var(--color-text-title);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.cal-more {
  font-size: 10px;
  font-weight: 800;
  color: var(--color-brand-cobalt);
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(20, 92, 255, 0.06);
  width: max-content;
  cursor: pointer;
  margin-top: 2px;
}
.cal-more:hover {
  background: rgba(20, 92, 255, 0.12);
}

/* --------------------------------------------------------------------------
   4. EVENT INSPECTOR DRAWER
   -------------------------------------------------------------------------- */
.calendar-inspector.premium-inspector {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  pointer-events: none;
  display: flex;
  justify-content: flex-end;
}
.calendar-inspector.premium-inspector.is-open {
  pointer-events: auto;
}

.inspector-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(8, 43, 87, 0.2);
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.calendar-inspector.premium-inspector.is-open .inspector-backdrop {
  opacity: 1;
}

.inspector-panel {
  position: relative;
  width: 440px;
  max-width: 90vw;
  background: #FFFFFF;
  box-shadow: -10px 0 30px rgba(8, 43, 87, 0.15);
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.calendar-inspector.premium-inspector.is-open .inspector-panel {
  transform: translateX(0);
}

.inspector-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-3);
}
.inspector-title {
  font-size: 1.4rem;
  font-weight: 800;
  line-height: 1.2;
  color: var(--color-text-title);
  margin: 0;
}

.inspector-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
  padding: var(--space-4);
  background: #FAFBFD;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-subtle);
}
.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.meta-label {
  font-size: 11px;
  font-weight: 800;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.meta-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-main);
}

.inspector-body {
  flex: 1;
  overflow-y: auto;
}
.inspector-desc {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.inspector-footer {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-subtle);
}

@media (max-width: 768px) {
  .calendar-toolbar-row {
    flex-direction: column;
    align-items: stretch;
  }
  .calendar-filters.premium-filters {
    flex-wrap: wrap;
    max-width: 100%;
  }
}
"""

with open('static/css/calendar.css', 'w', encoding='utf-8') as f:
    f.write(CALENDAR_CSS)
print("Updated calendar.css")
