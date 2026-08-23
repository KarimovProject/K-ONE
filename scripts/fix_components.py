import re

with open(r"C:\IEMS\static\css\components.css", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("padding: 6px 12px;\n  border-radius: var(--radius-md);", "padding: 6px 14px;\n  border-radius: var(--radius-md);")

content += """
@media (max-width: 767px) {
  .btn, .primary-button, .secondary-button,
  .text-button, .primary-link, .quiet-link,
  .btn-primary, .btn-success, .btn-edit, .btn-danger,
  .btn-info, .btn-telegram, .btn-export, .btn-neutral, .btn-ghost,
  .btn--compact, .compact {
    min-height: 44px !important;
  }
}
"""

with open(r"C:\IEMS\static\css\components.css", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed components.css")
