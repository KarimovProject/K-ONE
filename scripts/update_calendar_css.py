import re

with open('static/css/calendar.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace the premium-filters section with our new styling
old_filters_css = r'/\* --------------------------------------------------------------------------\s*2\. FILTER BAR \(Compact\)\s*-------------------------------------------------------------------------- \*/.*?/\* --------------------------------------------------------------------------\s*3\. MONTH GRID'

new_filters_css = """/* --------------------------------------------------------------------------
   2. FILTER BAR (Premium Cohesive Surface)
   -------------------------------------------------------------------------- */
.calendar-filters.premium-filters {
  display: flex;
  align-items: center;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: 4px 8px;
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-5);
  width: max-content;
  max-width: 100%;
}

.filter-group {
  display: flex;
  align-items: center;
  position: relative;
}

.filter-icon {
  position: absolute;
  left: 12px;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  pointer-events: none;
}

.filter-input {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 8px 16px 8px 36px !important;
  min-width: 260px;
  font-size: 14px;
  color: var(--color-text-main);
}
.filter-input:focus { outline: none; }

.filter-select {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 8px 32px 8px 16px !important;
  min-width: 200px;
  font-size: 14px;
  color: var(--color-text-main);
  cursor: pointer;
  appearance: none;
}
.filter-select:focus { outline: none; }

.filter-divider {
  width: 1px;
  height: 24px;
  background: var(--color-border-subtle);
  margin: 0 8px;
}

.filter-clear {
  color: var(--color-text-muted);
  font-weight: 600;
  font-size: 13px;
  padding: 6px 12px;
  margin-left: 8px;
}
.filter-clear:hover {
  background: rgba(0,0,0,0.03);
  color: var(--color-text-title);
}

/* --------------------------------------------------------------------------
   3. MONTH GRID"""

css = re.sub(old_filters_css, new_filters_css, css, flags=re.DOTALL)

# Add clear boundaries for calendar-day and selected state
css = css.replace('.calendar-day {', '.calendar-day {\n  border: 1px solid var(--color-border-subtle); margin: -1px 0 0 -1px; background: var(--color-surface-elevated);')
css = css.replace('.calendar-day--weekend {\n  background: rgba(0,0,0,0.015);\n}', '.calendar-day--weekend {\n  background: #F8FAFC;\n}')

with open('static/css/calendar.css', 'w', encoding='utf-8') as f:
    f.write(css)
