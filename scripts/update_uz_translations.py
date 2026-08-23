import os
import re
import subprocess

TRANSLATIONS = {
    "Analytics & Reporting": "Tahlil va hisobotlar",
    "Reports & Analytics": "Hisobotlar va tahlil",
    "Reporting & analytics": "Hisobot va tahlil",
    "Bounded operational and leadership insight from verified K-ONE records.": "Tasdiqlangan K-ONE ma'lumotlari asosidagi operatsion tahlil.",
    "Bounded operational and leadership insight from verified IEMS records.": "Tasdiqlangan K-ONE ma'lumotlari asosidagi operatsion tahlil.",
    "Event Approvals Queue": "Tasdiqlash navbati",
    "Event Calendar": "Taqvim",
    "Displaced Events": "Ko‘chirilgan tadbirlar",
    "Speakers Directory": "Ma'ruzachilar",
    "Add New Speaker": "+ Yangi ma'ruzachi",
    "All Event Types": "Barcha tadbir turlari",
    "Apply filters": "Filtrlash",
    "Apply Filters": "Filtrlash",
    "Reset": "Tozalash",
    "Event trend": "Tadbirlar dinamikasi",
    "active days": "faol kun",
    "Status distribution": "Holatlar taqsimoti",
    "Event type distribution": "Tadbir turlari taqsimoti",
    "Venue utilization": "Zallardan foydalanish",
    "Attendance": "Davomat",
    "Attendance rate": "Davomat darajasi",
    "Approval performance": "Tasdiqlash samaradorligi",
    "Publication status": "Nashrlar holati",
    "Publication distribution": "Nashrlar taqsimoti",
    "Telegram reminders": "Telegram eslatmalari",
    "Organization activity": "Tashkilotlar faolligi",
    "Assigned workload": "Xodimlar bandligi",
    "Expected attendees": "Kutilayotgan ishtirokchilar",
    "Registered capacity": "Qayd etilgan sig‘im",
    "Checked in": "Qatnashganlar",
    "Active hall ratio": "Faol zallar ulushi",
    "Reminder success": "Eslatmalar yetkazilishi",
    "Delivery performance": "Yetkazish samaradorligi",
    "Submitted": "Yuborilgan",
    "Approved": "Tasdiqlangan",
    "Rejected": "Rad etilgan",
    "Pending": "Kutilmoqda",
    "Average hours": "O‘rtacha vaqt (soat)",
    "Median hours": "Mediana vaqt (soat)",
    "Total": "Jami",
    "Retries": "Qayta urinishlar",
    "Scheduled": "Rejalashtirilgan",
    "Sent": "Yuborilgan",
    "Connected recipients": "Ulangan qabul qiluvchilar",
    "No data for selected period.": "Tanlangan davr uchun ma’lumot yo‘q.",
    "events": "tadbir",
    "Failed": "Muvaffaqiyatsiz",
    "Previous period": "Oldingi davr",
    "Total Events": "Jami tadbirlar",
    "Anonymous": "Anonim",
    "Identified": "Identifikatsiyalangan",
    "Public QR": "Ochiq QR",
    "Staff manual": "Xodim qo‘lda",
    "Planned Events": "Rejalashtirilgan tadbirlar",
    "Live Venue Status": "Jonli zallar holati",
    "Manage Program & Public Page": "Dastur va ochiq sahifa boshqaruvi",
    "Venues": "Xonalar",
    "Organizations": "Tashkilotlar",
    "Sponsors": "Homiylar",
    "Event types": "Tadbir turlari",
    "Leadership Dashboard": "Rahbariyat paneli",
    "IEMS TV Wallboard": "K-ONE TV Wallboard",
    "Role & Permissions": "Rol va ruxsatlar",
    "Operational Activity": "Operatsion faollik",
    "Role and permissions are managed centrally by system administrators.": "Rollar va ruxsatlar tizim ma'murlari tomonidan markazlashgan holda boshqariladi.",
    "Staff Status": "Xodim maqomi",
    "Superuser": "Superfoydalanuvchi",
    "Assigned events": "Biriktirilgan tadbirlar",
    "Management events": "Boshqaruv tadbirlari",
    "Connected": "Ulangan",
    "Not connected": "Ulanmagan",
    "Account control": "Hisob boshqaruvi",
    "Profile and preferences": "Profil va sozlamalar",
    "Manage your identity and interface language. Access role changes require an administrator.": "Shaxsiy ma'lumot va interfeys tilini boshqaring. Rolni faqat administrator o'zgartiradi.",
    "Save profile": "Profilni saqlash",
    "Access": "Kirish huquqi",
    "Activity": "Faollik",
    "First name": "Ism",
    "Last name": "Familiya",
    "OPERATSION MARKAZ": "OPERATSION MARKAZ",
    "XRONOLOGIK MONITORING": "XRONOLOGIK MONITORING",
    "Bugungi operatsion oqim": "Bugungi operatsion oqim",
    "Kutilayotgan": "Kutilayotgan",
    "HOZIR": "HOZIR",
    "JONLI MONITORING": "JONLI MONITORING",
    "Zallar holati": "Zallar holati",
    "OPERATSION NAZORAT": "OPERATSION NAZORAT",
    "Tizim holati": "Tizim holati",
    "Navbatdagi so'rovlar": "Navbatdagi so'rovlar",
    "Kechikayotgan tadbirlar": "Kechikayotgan tadbirlar",
    "Barcha jadvallar vaqtida": "Barcha jadvallar vaqtida",
    "Zal to'qnashuvlari": "Zal to'qnashuvlari",
    "Konfliktlar aniqlanmadi": "Konfliktlar aniqlanmadi",
    "Hozir bo'sh": "Hozir bo'sh",
    "Navbatda": "Navbatda",
    "Barcha tadbirlar": "Barcha tadbirlar",
    "Yaqinlashayotgan tadbirlar ro'yxati": "Yaqinlashayotgan tadbirlar ro'yxati",
    "Hozircha rejalashtirilgan tadbirlar mavjud emas.": "Hozircha rejalashtirilgan tadbirlar mavjud emas.",
}

po_path = "locale/uz/LC_MESSAGES/django.po"
with open(po_path, "r", encoding="utf-8") as f:
    content = f.read()

for msgid, msgstr in TRANSLATIONS.items():
    # If msgid exists, replace msgstr
    pattern = rf'(msgid "{re.escape(msgid)}"\s*\nmsgstr )""(\s*\n"[^"]*")*'
    exact_pattern = rf'(msgid "{re.escape(msgid)}"\s*\nmsgstr )[^\n]+'

    if f'msgid "{msgid}"' in content:
        # Replace existing entry
        content = re.sub(
            rf'msgid "{re.escape(msgid)}"\s*\nmsgstr\s+(""|".*?")(?:\s*\n".*?")*',
            f'msgid "{msgid}"\nmsgstr "{msgstr}"',
            content
        )
    else:
        content += f'\n\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'

with open(po_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Updated {po_path} with all Phase 21 translations.")
