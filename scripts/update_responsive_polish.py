import os

# Update public.css with timeline mobile scroll
with open('static/css/public.css', 'r', encoding='utf-8') as f:
    pub_css = f.read()

pub_css = pub_css.replace("""@media (max-width: 640px) {
  .public-header {
    height: 72px;
    padding: 0 16px;
  }
  .public-header__center {
    display: none;
  }
  .kpi-rail {
    grid-template-columns: 1fr;
  }
  .dashboard-hero__row {
    flex-direction: column;
    align-items: flex-start;
  }
  .timeline-container {
    overflow-x: auto;
  }
}""", """@media (max-width: 640px) {
  .public-header {
    height: 72px;
    padding: 0 16px;
  }
  .public-header__center {
    display: none;
  }
  .kpi-rail {
    grid-template-columns: 1fr;
  }
  .dashboard-hero__row {
    flex-direction: column;
    align-items: flex-start;
  }
  .timeline-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .timeline-scale,
  .timeline-tracks {
    min-width: 640px;
  }
}""")

with open('static/css/public.css', 'w', encoding='utf-8') as f:
    f.write(pub_css)

# Update calendar.css with mobile toolbar & filter polish
with open('static/css/calendar.css', 'r', encoding='utf-8') as f:
    cal_css = f.read()

cal_css = cal_css.replace("""@media (max-width: 768px) {
  .calendar-toolbar-row {
    flex-direction: column;
    align-items: stretch;
  }
  .calendar-filters.premium-filters {
    flex-wrap: wrap;
    max-width: 100%;
  }
}""", """@media (max-width: 768px) {
  .calendar-command-bar {
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
    border-radius: var(--radius-lg);
    padding: 12px 16px;
  }
  .calendar-command-bar__left {
    order: 1;
  }
  .calendar-command-bar__center {
    order: 2;
    font-size: 1.15rem;
  }
  .calendar-command-bar__right {
    order: 3;
    width: 100%;
    justify-content: center;
  }
  .calendar-toolbar-row {
    flex-direction: column;
    align-items: stretch;
  }
  .calendar-filters.premium-filters {
    flex-direction: column;
    align-items: stretch;
    max-width: 100%;
    padding: 8px 12px;
    gap: 6px;
  }
  .filter-divider {
    display: none;
  }
  .filter-input, .filter-select {
    width: 100% !important;
    border-bottom: 1px solid var(--color-border-subtle) !important;
    border-radius: 0 !important;
    padding: 8px 8px !important;
  }
  .btn-create-event {
    width: 100%;
    justify-content: center;
  }
}""")

with open('static/css/calendar.css', 'w', encoding='utf-8') as f:
    f.write(cal_css)

print("Responsive CSS updated.")
