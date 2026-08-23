import os
import polib

BASE_DIR = r"C:\IEMS\locale"

translations = {
    "uz": {
        "EXECUTIVE INTELLIGENCE": "RAHBARIYAT NAZORATI",
        "Real-time institutional oversight and executive resource visibility.": "Muassasa ustidan real vaqt rejimida nazorat va resurslar holati.",
        "Refreshes automatically every 20 seconds": "Har 20 soniyada avtomatik yangilanadi",
        "Master Data": "MA'LUMOTNOMALAR",
        "Today's Events": "Bugungi tadbirlar",
        "In Progress": "Jarayonda",
        "Available Venues": "Bo'sh zallar",
        "Occupied Venues": "Band zallar",
        "Today's Check-ins": "Bugungi ro'yxatdan o'tganlar",
        "Live Venue Status": "Zallarning jonli holati",
        "Today's Timeline": "Bugungi reja",
        "Attendance Summary": "Davomat xulosasi",
        "Expected": "Kutilayotgan",
        "Checked in": "Ro'yxatdan o'tdi",
        "Emergency / High Priority": "Favqulodda / Yuqori ustuvorlik",
        "Upcoming Events": "Kelgusi tadbirlar",
        "Date": "Sana",
        "Time": "Vaqt",
        "Event": "Tadbir",
        "Type": "Turi",
        "Venue": "Zal",
        "Organizer": "Tashkilotchi",
        "Status": "Holati",
        "No events today": "Bugun tadbirlar yo'q",
        "No high-priority events": "Yuqori ustuvorlikdagi tadbirlar yo'q",
        "No upcoming events": "Kelgusi tadbirlar yo'q",
        "No event in progress": "Jarayondagi tadbir yo'q"
    },
    "ru": {
        "EXECUTIVE INTELLIGENCE": "РУКОВОДЯЩИЙ КОНТРОЛЬ",
        "Real-time institutional oversight and executive resource visibility.": "Мониторинг учреждения и обзор ресурсов в реальном времени.",
        "Refreshes automatically every 20 seconds": "Автоматически обновляется каждые 20 секунд",
        "Master Data": "СПРАВОЧНИКИ",
        "Today's Events": "События сегодня",
        "In Progress": "В процессе",
        "Available Venues": "Свободные залы",
        "Occupied Venues": "Занятые залы",
        "Today's Check-ins": "Регистрации сегодня",
        "Live Venue Status": "Статус залов (Live)",
        "Today's Timeline": "Расписание на сегодня",
        "Attendance Summary": "Сводка посещаемости",
        "Expected": "Ожидается",
        "Checked in": "Зарегистрировано",
        "Emergency / High Priority": "Срочные / Высокий приоритет",
        "Upcoming Events": "Предстоящие события",
        "Date": "Дата",
        "Time": "Время",
        "Event": "Событие",
        "Type": "Тип",
        "Venue": "Зал",
        "Organizer": "Организатор",
        "Status": "Статус",
        "No events today": "Сегодня событий нет",
        "No high-priority events": "Нет срочных событий",
        "No upcoming events": "Нет предстоящих событий",
        "No event in progress": "В данный момент событий нет"
    }
}

for lang, messages in translations.items():
    po_path = os.path.join(BASE_DIR, lang, "LC_MESSAGES", "django.po")
    mo_path = os.path.join(BASE_DIR, lang, "LC_MESSAGES", "django.mo")
    
    if os.path.exists(po_path):
        po = polib.pofile(po_path)
        
        # Update or add entries
        for msgid, msgstr in messages.items():
            entry = po.find(msgid)
            if entry:
                entry.msgstr = msgstr
            else:
                entry = polib.POEntry(
                    msgid=msgid,
                    msgstr=msgstr
                )
                po.append(entry)
                
        po.save(po_path)
        po.save_as_mofile(mo_path)
        print(f"Updated {lang} translations successfully.")
    else:
        print(f"PO file not found for {lang}: {po_path}")

print("Done.")
