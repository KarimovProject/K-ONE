import re

with open(r"C:\IEMS\templates\events\event_list.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the HTML for the dropdown
dropdown_regex = r'<div class="k-action-dropdown" hidden[^>]*>.*?</div>'
new_dropdown = """<div class="k-action-dropdown" style="position: absolute; top: 100%; right: 0; margin-top: 4px; z-index: 100; background: white; border: 1px solid var(--color-border-strong, #e2e8f0); border-radius: 8px; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15); display: none; flex-direction: column; padding: 4px; min-width: 160px; text-align: left;">
                    <a class="btn-ghost compact" style="color: #0284C7; display: flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 6px; text-decoration: none;" onmouseover="this.style.backgroundColor='#F0F9FF'" onmouseout="this.style.backgroundColor='transparent'" href="{% url 'events:detail' pk=e.pk %}">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                      {% trans 'View' %}
                    </a>
                    {% if can_create and e.status != 'cancelled' %}
                      <a class="btn-ghost compact" style="color: #2563EB; display: flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 6px; text-decoration: none;" onmouseover="this.style.backgroundColor='#EFF6FF'" onmouseout="this.style.backgroundColor='transparent'" href="{% url 'events:edit' pk=e.pk %}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                        {% trans 'Edit' %}
                      </a>
                      <a class="btn-ghost compact" style="color: #E11D48; display: flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 6px; text-decoration: none;" onmouseover="this.style.backgroundColor='#FFF1F2'" onmouseout="this.style.backgroundColor='transparent'" href="{% url 'events:cancel' pk=e.pk %}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
                        {% trans 'Cancel' %}
                      </a>
                    {% endif %}
                  </div>"""

content = re.sub(dropdown_regex, new_dropdown, content, flags=re.DOTALL)

# Update the JS toggle function
js_regex = r'function toggleActionMenu\(button, event\) \{.*?\n\}'
new_js = """function toggleActionMenu(button, event) {
  event.preventDefault();
  event.stopPropagation();
  const dropdown = button.nextElementSibling;
  const isCurrentlyOpen = dropdown.style.display === 'flex';
  
  // Close all other dropdowns
  document.querySelectorAll('.k-action-dropdown').forEach(el => {
    el.style.display = 'none';
    el.classList.remove('is-open');
  });
  
  if (!isCurrentlyOpen) {
    dropdown.style.display = 'flex';
    dropdown.classList.add('is-open');
  }
}"""

content = re.sub(js_regex, new_js, content, flags=re.DOTALL)

# Update JS event listeners to close on click outside/escape
js_listeners_regex = r"document\.addEventListener\('click', function\(e\) \{.*?\}\);"
new_js_listeners = """document.addEventListener('click', function(e) {
  if (!e.target.closest('.table-actions')) {
    document.querySelectorAll('.k-action-dropdown').forEach(el => {
      el.style.display = 'none';
      el.classList.remove('is-open');
    });
  }
});"""

content = re.sub(js_listeners_regex, new_js_listeners, content, flags=re.DOTALL)

js_listeners_esc_regex = r"document\.addEventListener\('keydown', function\(e\) \{.*?\}\);"
new_js_listeners_esc = """document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    document.querySelectorAll('.k-action-dropdown').forEach(el => {
      el.style.display = 'none';
      el.classList.remove('is-open');
    });
  }
});
window.addEventListener('scroll', function(e) {
  document.querySelectorAll('.k-action-dropdown').forEach(el => {
      el.style.display = 'none';
      el.classList.remove('is-open');
  });
});
window.addEventListener('resize', function(e) {
  document.querySelectorAll('.k-action-dropdown').forEach(el => {
      el.style.display = 'none';
      el.classList.remove('is-open');
  });
});"""

content = re.sub(js_listeners_esc_regex, new_js_listeners_esc, content, flags=re.DOTALL)

with open(r"C:\IEMS\templates\events\event_list.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed event action menu.")
