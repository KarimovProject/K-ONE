import re

with open('templates/public/venues.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_style = """<style>
  .venues-command-center {
    background: transparent;
    padding: clamp(1.5rem, 3vw, 2.5rem);
    position: relative;
    overflow: hidden;
    margin-bottom: var(--space-6);
  }
  .venues-head {
    position: relative;
    z-index: 2;
    margin-bottom: var(--space-5);
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: var(--space-4);
  }
  .venues-head h1 {
    font-size: var(--text-title-xl);
    font-weight: var(--weight-black);
    color: var(--color-text-title);
    margin: var(--space-1) 0;
    letter-spacing: -0.03em;
  }
  .venues-head p {
    color: var(--color-text-secondary);
    font-size: var(--text-body);
    margin: 0;
  }
  .venues-legend {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    font-size: var(--text-meta);
    color: var(--color-text-muted);
    background: #FFFFFF;
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border-subtle);
    box-shadow: var(--shadow-sm);
  }
  .legend-item {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-weight: var(--weight-bold);
  }
  .venues-command-grid {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-4);
  }
  .venues-command-grid .live-venue-card {
    background: #FFFFFF;
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-lg);
    padding: var(--space-5);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 14.5rem;
    box-shadow: var(--shadow-sm);
    transition: all var(--motion-micro) var(--ease-standard);
  }
  .venues-command-grid .live-venue-card:hover {
    transform: translateY(-3px);
    border-color: rgba(25, 198, 244, 0.4);
    box-shadow: var(--shadow-md);
  }
  .venues-command-grid .live-venue-card.status-occupied {
    border-left: 4px solid var(--color-brand-cobalt);
  }
  .venues-command-grid .live-venue-card.status-upcoming {
    border-left: 4px solid var(--color-status-upcoming);
  }
  .venues-command-grid .live-venue-card.status-available {
    border-left: 4px solid var(--color-status-free);
  }
  .venues-command-grid .live-venue-card header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-3);
  }
  .venue-identity {
    display: flex;
    align-items: center;
    gap: var(--space-2);
  }
  .venues-command-grid .venue-monogram {
    padding: 0.2rem 0.65rem;
    background: rgba(20, 92, 255, 0.05);
    border: 1px solid rgba(20, 92, 255, 0.2);
    border-radius: var(--radius-sm);
    color: var(--color-brand-cobalt);
    font-size: 13px;
    font-weight: var(--weight-black);
    font-family: var(--font-mono);
  }
  .venue-capacity-tag {
    font-size: var(--text-meta);
    color: var(--color-text-muted);
    font-weight: var(--weight-bold);
  }
  .venues-command-grid .live-status {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.75rem;
    border-radius: var(--radius-pill);
    font-size: 12px;
    font-weight: var(--weight-black);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .venues-command-grid .status-available .live-status { color: var(--color-status-free); background: var(--color-status-free-bg); }
  .venues-command-grid .status-occupied .live-status { color: var(--color-status-active); background: var(--color-status-active-bg); }
  .venues-command-grid .status-upcoming .live-status { color: var(--color-status-upcoming); background: var(--color-status-upcoming-bg); }

  .venues-command-grid .venue-title {
    font-size: var(--text-heading);
    font-weight: var(--weight-bold);
    color: var(--color-text-title);
    margin: 0 0 var(--space-2);
  }
  .venues-command-grid .venue-current {
    font-size: 15px;
    font-weight: var(--weight-bold);
    color: var(--color-text-main);
    margin-bottom: var(--space-2);
    line-height: 1.3;
  }
  .venues-command-grid .venue-current.is-free {
    color: var(--color-text-muted);
    font-weight: var(--weight-medium);
  }
  .venues-command-grid .venue-countdown {
    color: var(--color-text-secondary);
    font-size: var(--text-meta);
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    margin: var(--space-1) 0;
  }
  .venues-command-grid .venue-progress {
    height: 6px;
    border-radius: var(--radius-pill);
    background: var(--color-surface-panel);
    overflow: hidden;
    margin: var(--space-2) 0;
  }
  .venues-command-grid .venue-progress i {
    display: block;
    height: 100%;
    background: var(--color-brand-cyan);
    border-radius: var(--radius-pill);
  }
  .venues-command-grid .venue-progress.is-upcoming i {
    background: var(--color-status-upcoming);
  }
  .venues-command-grid .venue-next {
    margin-top: var(--space-3);
    padding: var(--space-2) var(--space-3);
    background: var(--color-surface-panel);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-md);
  }
  .venues-command-grid .venue-next .next-label {
    display: block;
    color: var(--color-text-muted);
    font-size: 11px;
    font-weight: var(--weight-bold);
    text-transform: uppercase;
  }
  .venues-command-grid .venue-next .next-title {
    display: block;
    color: var(--color-text-title);
    font-size: 14px;
    font-weight: var(--weight-bold);
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .venues-command-grid footer {
    margin-top: var(--space-4);
    padding-top: var(--space-3);
    border-top: 1px dashed var(--color-border-subtle);
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: var(--color-text-muted);
    font-size: var(--text-meta);
  }
  .footer-left strong {
    color: var(--color-text-main);
  }
  .footer-count {
    padding: 2px 8px;
    border-radius: var(--radius-pill);
    background: var(--color-surface-panel);
    color: var(--color-text-muted);
    font-size: 11px;
    font-weight: var(--weight-bold);
  }
  @media (max-width: 54rem) {
    .venues-command-grid { grid-template-columns: 1fr; }
  }
</style>"""

html = re.sub(r'<style>.*?</style>', new_style, html, flags=re.DOTALL)

with open('templates/public/venues.html', 'w', encoding='utf-8') as f:
    f.write(html)
