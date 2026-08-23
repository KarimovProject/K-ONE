import re

# Fix workspace.css
workspace_path = r"C:\IEMS\static\css\workspace.css"
with open(workspace_path, "r", encoding="utf-8") as f:
    workspace_content = f.read()

replacement = """@media (max-width: 767px) {
  .calendar-command-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .k-calendar-title {
    order: 2;
    text-align: center;
    font-size: 1.15rem;
    margin: 4px 0;
  }
  .nav-controls {
    order: 1;
    display: flex;
    justify-content: space-between;
    width: 100%;
  }
  .view-controls {
    order: 3;
    display: flex;
    justify-content: space-between;
    width: 100%;
  }
  .calendar-cmd {
    flex: 1;
    text-align: center;
    padding: 8px 4px;
    font-size: 13px;
  }
}"""

# Using regex to replace the old media block
pattern = r'@media \(max-width: 767px\) \{\s*\.calendar-command-bar \{[\s\S]*?\}\s*\}'
workspace_content = re.sub(pattern, replacement, workspace_content)

with open(workspace_path, "w", encoding="utf-8") as f:
    f.write(workspace_content)

# Fix calendar.css
calendar_path = r"C:\IEMS\static\css\calendar.css"
with open(calendar_path, "r", encoding="utf-8") as f:
    calendar_content = f.read()

replacement2 = """@media (max-width: 768px) {
  .calendar-command-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .calendar-command-bar__left {
    order: 1;
    width: 100%;
  }
  .command-left {
    width: 100%;
    justify-content: space-between !important;
  }
  .command-left > button {
    flex: 1;
  }
  .calendar-command-bar__center {
    order: 2;
    text-align: center;
    font-size: 1.15rem;
    margin: 4px 0;
  }
  .calendar-command-bar__right {
    order: 3;
    width: 100%;
  }
  .command-right {
    width: 100%;
    justify-content: space-between !important;
  }
  .command-right > button {
    flex: 1;
  }"""

pattern2 = r'@media \(max-width: 768px\) \{\s*\.calendar-command-bar \{[\s\S]*?justify-content: center;\s*\}'
calendar_content = re.sub(pattern2, replacement2, calendar_content)

with open(calendar_path, "w", encoding="utf-8") as f:
    f.write(calendar_content)

print("Mobile toolbars fixed")
