import re

with open('templates/public/calendar.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the inline styled calendar-filters with a new coherent filter bar
old_filters = r'<div class="calendar-filters".*?</div>\s*<div style="flex:1;">.*?</div>\s*<div style="flex:1;">.*?</div>\s*<button.*?>.*?</button>\s*</div>'
new_filters = """<div class="calendar-filters premium-filters">
    <div class="filter-group">
      <div class="filter-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      </div>
      <input type="search" data-filter="search" class="input-control filter-input" placeholder="Tadbirni qidirish...">
    </div>

    <div class="filter-divider"></div>

    <div class="filter-group">
      <select data-filter="venue" class="input-control select-control filter-select">
        <option value="">Barcha Zallar</option>
        {% for v in venues %}
          <option value="{{ v.code }}">{{ v.code }} - {{ v.localized_name }}</option>
        {% endfor %}
      </select>
    </div>

    <div class="filter-divider"></div>

    <div class="filter-group">
      <select data-filter="type" class="input-control select-control filter-select">
        <option value="">Barcha Turlar</option>
        {% for event_type in event_types %}
          <option value="{{ event_type.code }}">{{ event_type.localized_name }}</option>
        {% endfor %}
      </select>
    </div>

    <button type="button" class="btn btn--ghost filter-clear" data-clear-filters>Tozalash</button>
  </div>"""

html = re.sub(old_filters, new_filters, html, flags=re.DOTALL)

with open('templates/public/calendar.html', 'w', encoding='utf-8') as f:
    f.write(html)
