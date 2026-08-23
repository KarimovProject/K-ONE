"""Add login translations to RU and EN locale files."""
import os

LOGIN_TRANSLATIONS_RU = """
# Login page translations (Phase 27.19)
msgid "Kirish"
msgstr "Войти"

msgid "Xush kelibsiz"
msgstr "Добро пожаловать"

msgid "K-ONE boshqaruv tizimiga kiring"
msgstr "Войдите в систему управления K-ONE"

msgid "Foydalanuvchi nomi"
msgstr "Имя пользователя"

msgid "Parol"
msgstr "Пароль"

msgid "Parolni ko'rsatish"
msgstr "Показать пароль"

msgid "Parolni yashirish"
msgstr "Скрыть пароль"

msgid "Login yoki parol noto'g'ri. Ma'lumotlarni tekshirib qayta urinib ko'ring."
msgstr "Неверное имя пользователя или пароль. Проверьте данные и попробуйте снова."

msgid "Tizimga kirish faqat ruxsat etilgan xodimlar uchun."
msgstr "Вход в систему только для уполномоченных сотрудников."

msgid "Barcha tadbirlar yagona tizimda"
msgstr "Все мероприятия в единой системе"

msgid "Tadbirlar, konferensiya zallari va boshqaruv jarayonlarini yagona professional platformada boshqaring."
msgstr "Управляйте мероприятиями, конференц-залами и процессами на единой профессиональной платформе."

msgid "Xavfsiz kirish"
msgstr "Безопасный вход"

msgid "Real vaqt monitoringi"
msgstr "Мониторинг в реальном времени"

msgid "Markazlashgan boshqaruv"
msgstr "Централизованное управление"

msgid "Mavzuni o'zgartirish"
msgstr "Сменить тему"
"""

LOGIN_TRANSLATIONS_EN = """
# Login page translations (Phase 27.19)
msgid "Kirish"
msgstr "Sign in"

msgid "Xush kelibsiz"
msgstr "Welcome back"

msgid "K-ONE boshqaruv tizimiga kiring"
msgstr "Sign in to K-ONE management system"

msgid "Foydalanuvchi nomi"
msgstr "Username"

msgid "Parol"
msgstr "Password"

msgid "Parolni ko'rsatish"
msgstr "Show password"

msgid "Parolni yashirish"
msgstr "Hide password"

msgid "Login yoki parol noto'g'ri. Ma'lumotlarni tekshirib qayta urinib ko'ring."
msgstr "Incorrect username or password. Please check your credentials and try again."

msgid "Tizimga kirish faqat ruxsat etilgan xodimlar uchun."
msgstr "System access is restricted to authorized personnel only."

msgid "Barcha tadbirlar yagona tizimda"
msgstr "All events in a unified system"

msgid "Tadbirlar, konferensiya zallari va boshqaruv jarayonlarini yagona professional platformada boshqaring."
msgstr "Manage events, conference halls and administrative processes on a single professional platform."

msgid "Xavfsiz kirish"
msgstr "Secure access"

msgid "Real vaqt monitoringi"
msgstr "Real-time monitoring"

msgid "Markazlashgan boshqaruv"
msgstr "Centralized management"

msgid "Mavzuni o'zgartirish"
msgstr "Toggle theme"
"""


def append_translations(po_path, translations):
    with open(po_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if already added
    if "Phase 27.19" in content:
        print(f"  Skipping {po_path} — already has Phase 27.19 translations")
        return

    with open(po_path, "a", encoding="utf-8") as f:
        f.write("\n" + translations.strip() + "\n")
    print(f"  Added translations to {po_path}")


append_translations(r"C:\IEMS\locale\ru\LC_MESSAGES\django.po", LOGIN_TRANSLATIONS_RU)
append_translations(r"C:\IEMS\locale\en\LC_MESSAGES\django.po", LOGIN_TRANSLATIONS_EN)

print("Done! Run compilemessages next.")
