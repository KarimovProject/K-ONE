import re

file_path = r"C:\IEMS\templates\events\event_detail.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Map section titles to accent classes
replacements = [
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Program & Public Page" %})', r'\1 card-accent-cobalt\2'),
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Schedule & Timing" %})', r'\1 card-accent-cyan\2'),
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Venue Details" %})', r'\1 card-accent-emerald\2'),
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Responsible Staff" %})', r'\1 card-accent-violet\2'),
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Online Links" %})', r'\1 card-accent-blue\2'),
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Telegram Reminders" %})', r'\1 card-accent-sky\2'),
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Publications" %})', r'\1 card-accent-amber\2'),
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Partners & Sponsors" %})', r'\1 card-accent-teal\2'),
    (r'(<section class="detail-card[^>]*?)(>[\s\S]*?\{% trans "Audit Metadata" %})', r'\1 card-accent-slate\2')
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

# Replace legacy buttons in event_detail.html
content = content.replace('class="primary-button"', 'class="btn-primary"')
content = content.replace('class="primary-button compact"', 'class="btn-primary compact"')
content = content.replace('class="secondary-button"', 'class="btn-neutral"')
content = content.replace('class="secondary-button compact"', 'class="btn-neutral compact"')

# specific semantic replacements if any exist:
# "Configure Program" -> btn-edit
content = content.replace('class="btn-neutral compact" href="{% url \'events:program\' pk=event.pk %}"', 'class="btn-edit compact" href="{% url \'events:program\' pk=event.pk %}"')
# "Print Poster" -> btn-export
content = content.replace('class="btn-neutral" href="{% url \'events:print-qr\' pk=event.pk %}"', 'class="btn-export" href="{% url \'events:print-qr\' pk=event.pk %}"')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied card accents and button classes to event_detail.html")
