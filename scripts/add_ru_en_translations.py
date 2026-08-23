import polib
import os

langs = ['ru', 'en']

keys = [
    "Program Mode",
    "Public Accessibility",
    "Manual Agenda",
    "Private",
    "Open Public Event Page",
    "Print Poster (A4/A5)",
    "Schedule & Timing",
    "Time Interval",
    "Duration",
    "Expected Attendees",
    "Venue Name",
    "Capacity",
    "Location",
    "Organizing Organizations",
    "Zoom / Meeting Link",
    "Registration Link",
    "Telegram Reminders",
    "Configure Reminders",
    "Publications",
    "New",
    "No data.",
    "Program & Public Page",
    "Venue Details",
    "Partners & Sponsors",
    "Responsible Staff",
    "Responsible Employee",
    "Management Responsible",
    "Online Links",
    "Join Meeting",
    "Register Here",
    "Audit Metadata",
    "Working Hours",
    "Back to Events",
    "Sponsors",
    "Date & Weekday"
]

for lang in langs:
    po_path = rf"C:\IEMS\locale\{lang}\LC_MESSAGES\django.po"
    if not os.path.exists(po_path):
        os.makedirs(os.path.dirname(po_path), exist_ok=True)
        po = polib.POFile()
    else:
        po = polib.pofile(po_path)
    
    for msgid in keys:
        entry = po.find(msgid)
        if entry:
            if not entry.msgstr:
                entry.msgstr = msgid
        else:
            entry = polib.POEntry(
                msgid=msgid,
                msgstr=msgid  # Using English as the fallback for RU/EN instead of UZ
            )
            po.append(entry)
            
    po.save(po_path)
    po.save_as_mofile(po_path.replace(".po", ".mo"))

print("RU and EN translations updated.")
