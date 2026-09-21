import re

with open('static/css/public.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the old phase 19.2 minified block
content = re.sub(r'/\* DASHBOARD PHASE 19.2 \*/.*', '', content, flags=re.DOTALL)

NEW_CSS = """
/* DASHBOARD PHASE 19.3 */
.dashboard-shell { padding: var(--space-6); display: flex; flex-direction: column; gap: var(--space-6); }
.dashboard-canvas { display: grid; grid-template-columns: 2fr 1fr; gap: var(--space-6); }
.premium-panel { background: var(--color-surface-glass); border-radius: var(--radius-xl); padding: var(--space-5); border: 1px solid var(--color-border-subtle); box-shadow: var(--shadow-sm); backdrop-filter: blur(12px); }
.panel-header h2 { font-size: var(--text-heading); font-weight: bold; margin-bottom: 2px; color: var(--color-nav-base); }
.panel-header .subtitle { font-size: var(--text-meta); color: var(--color-text-muted); font-weight: 600; }

/* KPI Rail */
.kpi-rail { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-4); }
.kpi-card { background: #FFFFFF; padding: var(--space-4); border-radius: 16px; border: 1px solid var(--color-border-subtle); display: flex; align-items: center; gap: var(--space-4); box-shadow: var(--shadow-sm); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.kpi-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: rgba(22, 188, 235, 0.4); }
.kpi-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; background: var(--color-surface-base); color: var(--color-text-muted); }
.kpi-icon.icon-active { background: rgba(20, 92, 255, 0.1); color: var(--color-brand-cobalt); }
.kpi-icon.icon-free { background: rgba(22, 199, 132, 0.1); color: var(--color-status-free); }
.kpi-icon.icon-upcoming { background: rgba(255, 176, 32, 0.1); color: var(--color-status-upcoming); }
.kpi-content { display: flex; flex-direction: column; gap: 2px; }
.kpi-label { font-size: 13px; font-weight: 800; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-value { font-size: clamp(1.5rem, 2vw, 2.25rem); font-weight: 900; color: var(--color-text-main); line-height: 1; display: flex; align-items: baseline; gap: 6px; }
.kpi-unit { font-size: 14px; font-weight: 600; color: var(--color-text-muted); }
.kpi-value-group { display: flex; align-items: center; gap: 8px; }

/* Timeline */
.timeline-container { position: relative; margin-top: var(--space-5); height: 200px; }
.timeline-scale { display: flex; justify-content: space-between; position: absolute; left: 0; right: 0; top: 0; bottom: 0; }
.timeline-hour { display: flex; flex-direction: column; align-items: center; position: relative; flex: 1; color: var(--color-text-muted); font-size: 13px; font-weight: 600; }
.timeline-hour span { margin-bottom: 8px; }
.grid-line { width: 1px; background: rgba(0,0,0,0.05); flex: 1; }
.current-time-marker { position: absolute; top: 0; bottom: 0; width: 2px; z-index: 5; display: flex; flex-direction: column; align-items: center; }
.marker-line { width: 2px; background: var(--color-brand-cyan); flex: 1; }
.marker-badge { background: var(--color-brand-cyan); color: #fff; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; position: absolute; top: 30px; }
.timeline-tracks { position: absolute; top: 50px; left: 0; right: 0; bottom: 0; z-index: 10; }
.event-capsule { position: absolute; height: 48px; border-radius: 8px; box-shadow: var(--shadow-sm); display: flex; align-items: center; padding: 0 12px; border-left: 4px solid transparent; overflow: hidden; white-space: nowrap; transition: transform 0.2s ease; cursor: pointer; }
.event-capsule:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); z-index: 11; }
.event-capsule.status-active { background: rgba(20, 92, 255, 0.05); border-left-color: var(--color-brand-cobalt); border-top: 1px solid rgba(20, 92, 255, 0.1); border-right: 1px solid rgba(20, 92, 255, 0.1); border-bottom: 1px solid rgba(20, 92, 255, 0.1); }
.event-capsule.status-upcoming { background: rgba(255, 176, 32, 0.05); border-left-color: var(--color-status-upcoming); border-top: 1px solid rgba(255, 176, 32, 0.1); border-right: 1px solid rgba(255, 176, 32, 0.1); border-bottom: 1px solid rgba(255, 176, 32, 0.1); }
.event-capsule-content { display: flex; flex-direction: column; justify-content: center; overflow: hidden; }
.event-capsule .event-title { font-size: 14px; font-weight: 800; color: var(--color-text-main); text-overflow: ellipsis; overflow: hidden; }
.event-capsule .event-meta { font-size: 12px; font-weight: 600; color: var(--color-text-muted); }

/* Venue Panel */
.venue-activity-list { display: flex; flex-direction: column; gap: var(--space-3); margin-top: var(--space-4); }
.venue-activity-item { display: flex; align-items: flex-start; gap: var(--space-3); padding: var(--space-3); background: #FFFFFF; border-radius: 12px; border: 1px solid var(--color-border-subtle); box-shadow: var(--shadow-sm); transition: transform 0.2s ease; }
.venue-activity-item:hover { transform: translateX(2px); box-shadow: var(--shadow-md); }
.venue-status-dot { width: 12px; height: 12px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.bg-active { background: var(--color-brand-cobalt); }
.bg-free { background: var(--color-status-free); }
.bg-upcoming { background: var(--color-status-upcoming); }
.venue-info { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
.venue-code-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.venue-code { font-family: var(--font-mono); font-size: 14px; font-weight: 800; color: var(--color-nav-base); }
.badge { font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 12px; }
.badge-active { background: rgba(20, 92, 255, 0.1); color: var(--color-brand-cobalt); }
.badge-free { background: rgba(22, 199, 132, 0.1); color: var(--color-status-free); }
.badge-upcoming { background: rgba(255, 176, 32, 0.1); color: var(--color-status-upcoming); }
.venue-name { font-size: 14px; font-weight: 600; color: var(--color-text-muted); text-overflow: ellipsis; white-space: nowrap; overflow: hidden; }
.venue-next-event { font-size: 12px; font-weight: 600; color: var(--color-brand-cobalt); margin-top: 6px; padding-top: 6px; border-top: 1px dashed var(--color-border-subtle); }
"""

with open('static/css/public.css', 'w', encoding='utf-8') as f:
    f.write(content + "\n" + NEW_CSS)
