import polib
import os

locales = ['uz', 'ru', 'en']
base_dir = r"C:\IEMS\locale"

translations = {
    "Speakers Directory": {"uz": "Ma'ruzachilar", "ru": "Спикеры", "en": "Speakers Directory"},
    "Manage keynote speakers, presenters, and experts.": {"uz": "Asosiy ma'ruzachilar, taqdimotchilar va ekspertlarni boshqaring.", "ru": "Управляйте основными докладчиками, ведущими и экспертами.", "en": "Manage keynote speakers, presenters, and experts."},
    "New Speaker": {"uz": "+ Ma'ruzachi qo'shish", "ru": "Новый спикер", "en": "New Speaker"},
    "No speakers found in directory.": {"uz": "Hozircha ma'ruzachilar mavjud emas.", "ru": "Спикеры не найдены.", "en": "No speakers found in directory."},
    "Full Name": {"uz": "To'liq ism", "ru": "ФИО", "en": "Full Name"},
    "Title / Position": {"uz": "Lavozimi", "ru": "Должность", "en": "Title / Position"},
    "Organization": {"uz": "Tashkilot", "ru": "Организация", "en": "Organization"},
    "Country": {"uz": "Davlat", "ru": "Страна", "en": "Country"},
    "Status": {"uz": "Holat", "ru": "Статус", "en": "Status"},
    "Actions": {"uz": "Amallar", "ru": "Действия", "en": "Actions"},
    "Public": {"uz": "Ochiq", "ru": "Открытый", "en": "Public"},
    "Hidden": {"uz": "Yashirin", "ru": "Скрытый", "en": "Hidden"},
    "Adjust the filters or create the first speaker record.": {"uz": "Filtrlarni o'zgartiring yoki birinchi ma'ruzachini qo'shing.", "ru": "Измените фильтры или добавьте первого спикера.", "en": "Adjust the filters or create the first speaker record."},
    "No event types found": {"uz": "Tadbir turlari topilmadi", "ru": "Типы мероприятий не найдены", "en": "No event types found"},
    "Adjust the filters or seed the default event types.": {"uz": "Filtrlarni moslashtiring yoki standart turlarni urug'lang.", "ru": "Настройте фильтры или создайте стандартные типы.", "en": "Adjust the filters or seed the default event types."},
    "No sponsors found": {"uz": "Homiylar topilmadi", "ru": "Спонсоры не найдены", "en": "No sponsors found"},
    "Adjust the filters or create the first sponsor record.": {"uz": "Filtrlarni o'zgartiring yoki birinchi homiyni qo'shing.", "ru": "Измените фильтры или добавьте первого спонсора.", "en": "Adjust the filters or create the first sponsor record."},
}

for lang in locales:
    po_path = os.path.join(base_dir, lang, "LC_MESSAGES", "django.po")
    mo_path = os.path.join(base_dir, lang, "LC_MESSAGES", "django.mo")
    
    if os.path.exists(po_path):
        po = polib.pofile(po_path)
        
        for msgid, trans_dict in translations.items():
            if lang in trans_dict:
                entry = po.find(msgid)
                if entry:
                    entry.msgstr = trans_dict[lang]
                else:
                    new_entry = polib.POEntry(
                        msgid=msgid,
                        msgstr=trans_dict[lang]
                    )
                    po.append(new_entry)
        
        po.save(po_path)
        po.save_as_mofile(mo_path)
        print(f"Updated and compiled {lang}")
    else:
        print(f"Skipped {lang} - PO file not found")
