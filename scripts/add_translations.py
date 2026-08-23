import polib

po_path = r"C:\IEMS\locale\uz\LC_MESSAGES\django.po"
po = polib.pofile(po_path)

translations = {
    "Program Mode": "Dastur rejimi",
    "Public Accessibility": "Ommaviy kirish",
    "Manual Agenda": "Qo‘lda boshqariladigan dastur",
    "Private": "Yopiq",
    "Open Public Event Page": "Ommaviy tadbir sahifasini ochish",
    "Print Poster (A4/A5)": "Posterni chop etish (A4/A5)",
    "Schedule & Timing": "Jadval va vaqt",
    "Time Interval": "Vaqt oralig‘i",
    "Duration": "Davomiyligi",
    "Expected Attendees": "Kutilayotgan ishtirokchilar",
    "Venue Name": "Zal nomi",
    "Capacity": "Sig‘im",
    "Location": "Joylashuv",
    "Organizing Organizations": "Tashkilotchi tashkilotlar",
    "Zoom / Meeting Link": "Zoom / uchrashuv havolasi",
    "Registration Link": "Ro‘yxatdan o‘tish havolasi",
    "Telegram Reminders": "Telegram eslatmalari",
    "Configure Reminders": "Eslatmalarni sozlash",
    "Publications": "Nashrlar",
    "New": "Yangi",
    "No data.": "Ma’lumot yo‘q"
}

for msgid, msgstr in translations.items():
    entry = po.find(msgid)
    if entry:
        entry.msgstr = msgstr
    else:
        entry = polib.POEntry(
            msgid=msgid,
            msgstr=msgstr
        )
        po.append(entry)

po.save()
po.save_as_mofile(po_path.replace(".po", ".mo"))
print("Translations added and compiled successfully.")
