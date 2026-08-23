css = """
/* Phase 27.9 Semantic Color Utilities */
.border-cobalt { border-left-color: var(--color-cobalt) !important; }
.border-cyan { border-left-color: var(--color-electric) !important; }
.border-emerald { border-left-color: var(--color-emerald) !important; }
.border-violet { border-left-color: var(--color-violet) !important; }
.border-amber { border-left-color: var(--color-amber) !important; }

.bg-cobalt { background-color: var(--color-cobalt) !important; }
.bg-cyan { background-color: var(--color-electric) !important; }
.bg-emerald { background-color: var(--color-emerald) !important; }
.bg-violet { background-color: var(--color-violet) !important; }
.bg-amber { background-color: var(--color-amber) !important; }
"""

with open(r"C:\IEMS\static\css\calendar.css", "a", encoding="utf-8") as f:
    f.write(css)

# Fix the broken .cal-more
with open(r"C:\IEMS\static\css\calendar.css", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("margin-top: 24px;\n}\n\n/* Phase 27.9 Semantic Color Utilities */", "margin-top: 2px;\n}")
content = content.replace(".bg-amber { background-color: var(--color-amber) !important; }\n.cal-more:hover {", ".cal-more:hover {")

with open(r"C:\IEMS\static\css\calendar.css", "w", encoding="utf-8") as f:
    f.write(content)

print("calendar.css fixed and appended")
