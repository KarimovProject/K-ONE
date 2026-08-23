import re

with open(r"C:\IEMS\apps\events\api.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the color logic inside CalendarEventsAPIView
# The method usually maps e.event_type.color or something.
# Let's find it.
old_logic = r'''
        for e in events:
            # Color fallback logic \(if status maps to semantic colors\)
            color = e.event_type.color if e.event_type and e.event_type.color else "#165DFF"
            
            # Semantic status override
            if e.status in \['pending_approval', 'submitted', 'under_review'\]:
                color = "#F59E0B"
            elif e.status == 'approved':
                color = "#10B981"
            elif e.status == 'cancelled':
                color = "#EF4444"
'''
# Actually let me find the exact old logic by reading it first.
