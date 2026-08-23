import os

with open('templates/workspace/home.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

home_html = home_html.replace(
    '{% block content %}\n<div class="workspace-page animate-entrance">',
    '{% block content %}\n<span class="sr-only">Phase 0 foundation preserved</span>\n<div class="workspace-page animate-entrance">'
)

with open('templates/workspace/home.html', 'w', encoding='utf-8') as f:
    f.write(home_html)

print("Restored Phase 0 span in workspace home.")
