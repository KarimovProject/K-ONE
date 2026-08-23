import re

with open(r"C:\IEMS\apps\events\api.py", "r", encoding="utf-8") as f:
    content = f.read()

old_colors_regex = r'status_colors = \{\s+"draft".*?\}\s+color = status_colors\.get\(e\.status, "#2563EB"\)'
new_colors = """status_colors = {
                "draft": "#64748B",
                "pending_approval": "#F59E0B",
                "submitted": "#F59E0B",
                "under_review": "#F59E0B",
                "approved": "#0EA5E9",
                "rejected": "#E11D48",
                "planned": "#2563EB",
                "scheduled": "#2563EB",
                "ongoing": "#10B981",
                "completed": "#475569",
                "postponed": "#F59E0B",
                "displaced": "#E11D48",
                "cancelled": "#E11D48",
                "emergency": "#E11D48",
            }
            color = status_colors.get(e.status, "#2563EB")"""

content = re.sub(old_colors_regex, new_colors, content, flags=re.DOTALL)

with open(r"C:\IEMS\apps\events\api.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Colors mapped in API.")
