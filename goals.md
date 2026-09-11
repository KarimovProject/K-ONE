# IEMS — Maqsadlar va Holat Reyestri

> **QOIDA:** Ushbu loyiha ustida har qanday amal (kod yozish, refactor, feature qo'shish,
> bug fix) boshlanishidan **oldin** shu fayl to'liq o'qilishi shart. Har bir muhim
> o'zgarishdan keyin ("Joriy holat" va "Keyingi qadamlar" bo'limlari) yangilab borilishi kerak.
> Bu qoida `CLAUDE.md`da ham mustahkamlangan.

Oxirgi yangilanish: 2026-09-11 (backend + frontend — butun loyiha bo'ylab to'liq audit va bug tuzatish)

---

## 1. Loyiha haqida

**IEMS (International Events Management System)** — Xalqaro bo'lim uchun tadbirlarni
boshqarish tizimi. Django 5 + PostgreSQL + Redis + Celery/Celery Beat asosida, Windows
muhitida Docker'siz native ishlaydi (Docker faqat deployment reference sifatida saqlanadi).

Foydalanuvchilar: admin xodimlar, mas'ul xodimlar, rahbariyat (approver/viewer), kontent
menejerlar, qabulxona operatorlari. Uch tilda ishlaydi: **uz, ru, en** (+ `tr` locale fayli
ham topilgan, lekin loyihada faol ishlatilishi tasdiqlanmagan).

Asosiy arxitektura: `config/` (settings/urls/middleware) + `apps/` ichida 10 ta modulli
Django app: `accounts, events, venues, organizations, approvals, attendance, notifications,
publications, reporting, audit`.

---

## 2. Amalga oshirilgan ishlar (git tarixi asosida)

Loyiha fazama-faza (phase-by-phase) qurilgan, `docs/phase*.md` va commit tarixi buni
tasdiqlaydi:

- **Phase 0** — Django foundation: custom user model, RBAC, health endpoint, dashboard shell.
- **Phase 1–6** — master data (venues, event types, organizations, sponsors), event
  lifecycle, QR/dastur, davomat (attendance), rahbariyat paneli.
- **Phase 7** — Telegram eslatmalar (`apps/notifications/telegram/`).
- **Phase 8** — ijtimoiy tarmoqqa nashr qilish workflow (`apps/publications`).
- **Phase 9** — hisobot va analitika (`apps/reporting`).
- **Phase 10** — production readiness (health checks, deployment tayyorgarligi).
- **Phase 11** — UI/admin governance: public vs workspace vs admin ajratilishi, delete
  policy, ma'lumotlarni ochiq qilish siyosati (`docs/phase11-ui-admin-governance.md`).
- **Phase 19–27 (raqamlangan sub-fazalar)** — asosan **vizual/CSS forensika va qayta
  qurish**: layout tiklash, stylesheet arxitekturasi, login/dashboard/calendar vizual
  poliш, hero-art/logo generatsiyasi va ko'plab QA/audit skriptlari (`scripts/capture_*`,
  `scripts/verify_*`, `scripts/apply_*`).
- **So'nggi commitlar (nomlanishi rasmiy phase raqamiga mos kelmaydi, lekin funksional):**
  - `feat(ui)`: K-ONE premium responsive baseline muzlatildi.
  - `feat(events)`: reservation conflict + approval workflow (`apps/events/services/workflow.py`,
    `conflicts.py`).
  - `feat(approval)`: Approval Center va Priority Override workflow — **muhim**: bu real
    kod `apps/events/` ichida (`views.py`, `services/workflow.py`,
    `templates/events/approval_center.html`), `apps/approvals` app'ida EMAS (pastga qarang).
  - `Phase 2: Boshqaruv markazi, Theme toggle va Real-time Dashboard` — workspace/admin
    boshqaruv markazi, mavzu almashtirish, real-time yangilanadigan dashboard.

---

## 3. Joriy holat (ish davomida, commit qilinmagan)

`git status` bo'yicha quyidagi fayllar o'zgartirilgan, hali commit qilinmagan:

| Fayl | O'zgarish hajmi | Mazmuni |
|---|---|---|
| `templates/public/dashboard.html` | 394 qator | Public dashboard qayta tuzilmoqda |
| `static/css/public.css` | +563 qator | Public dashboard uchun yangi stillar |
| `static/js/public-dashboard.js` | 314 qator (kengaytirilgan) | Public dashboard interaktivligi |
| `config/settings/base.py` | 1 qator | `ALLOWED_HOSTS` default ro'yxatiga `"*"` qo'shilgan |
| `.gitignore` | +7 qator | Yangi ignore qoidalari |

**Xulosa:** hozirgi ish — **public dashboard'ning vizual va funksional qayta qurilishi**
(Phase 2 commit'idan keyingi davom etayotgan ish bo'lishi mumkin).

### 3.1 Bajarildi — Dashboard/Calendar UX tuzatishlari (2026-09-10, commit qilinmagan)

Foydalanuvchi so'rovi bo'yicha quyidagi tuzatishlar kiritildi (hammasi test qilindi:
`manage.py check`, `pytest tests/test_dashboard.py tests/test_locale.py
tests/test_events_localization.py`, uz/ru/en cookie orqali qo'lda tekshirildi):

- **Sahifalar orasidagi o'tish animatsiyasi**: `static/css/motion.css`ga native
  `@view-transition { navigation: auto; }` bloki qo'shildi — Dashboard/Calendar/Live
  orasida navigatsiya qilinganda yumshoq fade+shift animatsiyasi (Chromium/Edge'da
  ko'rinadi, boshqa brauzerlarda oddiy o'tish, hech qanday regressiya yo'q).
  `prefers-reduced-motion` hurmat qilinadi.
- **Calendar ichida kun/hafta/oy/ro'yxat almashtirish animatsiyasi**: `static/js/
  public-calendar.js`ga `setStageHtml()` helper qo'shildi (`.is-swapping` klassi bilan
  qisqa fade+shift), `static/css/calendar.css`ga tegishli transition qo'shildi.
- **O'zbek tilida vaqt noto'g'ri ko'rsatilishi**: `static/js/public-dashboard.js` va
  `public-calendar.js`da soat/xronologik chiziq hisob-kitobi `new Date().getHours()`
  (brauzer lokal vaqt zonasi) o'rniga har doim aniq Asia/Tashkent vaqt zonasidan
  hisoblanadigan `tashkentParts()`/`tzFieldFormatter` helper'lariga o'tkazildi; soat
  matni endi `Intl.DateTimeFormat('uz-UZ', ...)`ga emas, neytral raqamli formatga
  tayanadi (ba'zi kam tarqalgan ICU lokallar uchun soat formatida nomuvofiqlik
  bo'lishi mumkin edi).
- **Qaysi til aktiv ekani bilinmasligi**: `templates/public/base.html`da til
  tugmalarida ikkita `style` atributi bo'lgan (yaroqsiz HTML) — aktiv til hech qachon
  ajratib ko'rsatilmagan. `.lang-switcher__btn--active` klassiga almashtirildi, aniq
  pill-highlight qo'shildi (`static/css/public.css`).
- **Calendar'da "och ko'k / to'q ko'k" muammosi**: `majlis/meet` turi capsulalari
  `cyan` (och ko'k) dan `amber` (oltin) rangga o'zgartirildi — endi konferensiya=cobalt
  (to'q ko'k), uchrashuv=amber (oltin), trening=emerald (yashil), rasmiy=violet
  (binafsha) — 4 ta aniq farqlanadigan rang, ikkita ko'k soyasi o'rniga.
- **Tarjimalar**: `templates/public/dashboard.html` va `base.html` nav'idagi barcha
  qattiq kodlangan (asosan o'zbekcha/inglizcha) matnlar `{% trans %}`ga o'ralди;
  `public-dashboard.js` va `public-calendar.js`dagi JS orqali render qilinadigan
  qattiq kodlangan matnlar uchun til lug'ati (`text{}`) qo'shildi. Yangi 25 ta
  msgid `locale/{uz,ru,en}/LC_MESSAGES/django.po`ga qo'shildi va `.mo` fayllar
  qayta kompilyatsiya qilindi (`polib` orqali, `scripts/compile_po_polib.py`dagi
  yo'l xato edi — undan foydalanilmadi).

**Ochiq qoldi (keyingi safar davom ettiriladi, pastga — 5-bo'limga qarang):** sayt
bo'ylab 52/51/37 ta oldindan bo'sh qolgan msgstr (uz/ru/en) — bular dashboard/calendar
bilan bog'liq emas, boshqa modullarga (publications, admin va h.k.) tegishli.

### 3.2 Tuzatildi — foydalanuvchi qayta ko'rib chiqqandan keyin (2026-09-10, xuddi shu kun)

Foydalanuvchi ikkita muammoni qayd etdi: (1) tarjima hali ham to'liq emas, (2) boshqaruv
panelini (workspace) biroz buzib qo'yilgan. Tekshiruv natijasi:

- **Sabab topildi va tuzatildi — workspace buzilishi**: 3.1-bandda `static/css/motion.css`ga
  qo'shilgan `@view-transition` bloki **sайт bo'ylab** yuklanadigan fayl edi — u faqat
  public dashboard/calendar/live uchun mo'ljallangan bo'lsa-da, `templates/base.html`
  (autentifikatsiyadan o'tgan workspace/admin qobig'i) ham `motion.css`ni yuklaydi, shuning
  uchun har bir workspace ichki navigatsiyasida ham butun sahifa fade-animatsiyasi ishga
  tushib, mavjud real-time/entrance animatsiyalar bilan to'qnashib ketgan. **Yechim**: blok
  `motion.css`dan olib tashlandi va faqat `static/css/public.css`ga ko'chirildi (bu fayl
  faqat `templates/public/base.html` orqali yuklanadi, workspace unga umuman ulanmagan).
  CSS/JS versiya-parametrlari (`?v=`) ham oshirildi — brauzer keshi eski faylni
  ko'rsatmasligi uchun.
- **Tarjima tekshiruvi — `polib` bilan barcha katalog statistikasi**: `uz/ru/en/tr`
  kataloglarining barchasi o'zidagi msgid'lar bo'yicha **100% tarjima qilingan**
  (bo'sh `msgstr` yo'q — avvalgi "52/51/37 bo'sh" hisob-kitobi noto'g'ri edi: bular
  uzun matnlar uchun gettext'ning ko'p qatorli formatidagi ochilish qatori edi, real
  bo'sh tarjima emas). Haqiqiy muammo — **kataloglar orasidagi nomuvofiqlik** edi:
  `uz.po`da bor, lekin `en.po`da yo'q — 193 ta msgid (tekshirilgach — bularning barchasi
  manba matni allaqachon inglizcha bo'lgan Phase-0 model/admin yorliqlari, masalan
  "Dashboard", "Pending", "Total" — yozuv bo'lmasa ham Django msgid'ga qaytadi, demak
  inglizcha foydalanuvchi uchun ko'rinadigan xato yo'q); `uz.po`da bor, `ru.po`da yo'q —
  **29 ta msgid** (bular haqiqiy ko'rinadigan xato edi — rus tilida "Pending", "Rejected",
  "First name", Telegram sozlamalari kabi satrlar tarjimasiz, xom inglizcha holda
  chiqardi). Shu 29 tasi rus tiliga tarjima qilinib `locale/ru/LC_MESSAGES/django.po`
  va `.mo`ga qo'shildi.
- **`tr` (turkcha) katalogida 218 ta yetishmovchi msgid bor** — lekin `tr` rasmiy
  qo'llab-quvvatlanadigan til emas (4-bo'limdagi eslatmaga qarang), shuning uchun bu
  safar qo'lga olinmadi; agar `tr` rasman kerak bo'lsa, alohida so'rov sifatida
  ko'rib chiqiladi.

**Tekshiruv**: `manage.py check`, `pytest tests/test_locale.py tests/test_dashboard.py
tests/test_events_localization.py` (barchasi o'tdi), server qayta ishga tushirilib
workspace (`/workspace/` → 302 login'ga, buzilish yo'q) va public dashboard (`/dashboard/`
→ 200) qo'lda tasdiqlandi, `view-transition` endi faqat `public.css`da borligi
tekshirildi (`motion.css`da 0 ta, `public.css`da 10 ta ta'rif).

---

### 3.3 Bajarildi — Shifokor ro'yxatdan o'tishi, profili va bandlik/bildirishnoma (2026-09-10)

Yangi katta funksionallik qo'shildi (rejalashtirilgan, `AskUserQuestion` orqali ikkita
arxitekturaviy qaror tasdiqlangan): admin tasdig'i talab qilinadigan holatda, tadbirga
"ishtirok etuvchi shifokorlar" alohida maydon sifatida.

- **`apps/accounts`**: `User.Role.DOCTOR` qo'shildi; `DoctorProfile` (mutaxassislik,
  ish joyi, lavozim, telefon, tillar, litsenziya, bio, surat) va `StaffUnavailability`
  (sana, vaqt oralig'i, majburiy sababi) modellari qo'shildi. Ro'yxatdan o'tgan
  shifokor `is_active=False` bilan yaratiladi — bu Django'ning o'zining login
  bloklash mexanizmini ishlatadi, alohida "tasdiqlash" ekrani kerak emas: admin
  mavjud `/admin/` foydalanuvchilar ro'yxatida `role=Doctor` + `Active=No` filtri
  bilan topib, faqat "Active" belgisini yoqadi.
- Ro'yxatdan o'tish: `/accounts/register/` (`login.html` bilan bir xil vizual uslub,
  throttling `ThrottledLoginView` namunasi bo'yicha). `login.html`ga "Shifokormisiz?"
  havolasi qo'shildi.
- Shaxsiy kabinet: `/profile/availability/` — shifokor o'zi band vaqtlarini (sabab
  bilan) qo'sha/o'chira oladi (faqat o'ziniki). `profile.html`da shifokorlar uchun
  havola ko'rinadi.
- **`apps/accounts/services.py`** (yangi) — `check_doctor_availability()`,
  `apps/events/services/conflicts.py`dagi zal-konflikt tekshiruvi bilan bir xil
  naqshda.
- **`apps/events`**: `Event.attending_doctors` (M2M, `responsible_employee`dan
  alohida) qo'shildi; wizard 3-qadami va oddiy tahrirlash formasiga bog'landi.
  Shifokor band vaqtga to'g'ri keladigan tadbirga biriktirilsa —
  `messages.warning()` orqali darhol ko'rinadigan ogohlantirish HAMDA
  `apps/notifications/services.py::send_notification()` orqali tayinlovchiga
  bildirishnoma (sababi bilan) yuboriladi. Bloklovchi emas — tayinlash baribir
  saqlanadi (zal sig'imidan oshib ketish ogohlantirishi bilan bir xil uslub).
- **Tarjima**: barcha yangi matnlar `{% trans %}`/`gettext_lazy` bilan o'ralgan,
  uz/ru/en uchun tarjima qo'shildi va `.mo` qayta kompilyatsiya qilindi (shu jarayonda
  avvaldan mavjud bo'lgan bir nechta umumiy so'z — "start time", "end time", "reason"
  va h.k. — uz katalogida yetishmayotgani ham aniqlanib tuzatildi, bu boshqa
  joylarga ham foyda beradi).
- **Testlar**: `tests/test_doctor_registration.py` (9 ta test — ro'yxatdan o'tish,
  faollashtirilmagan holatda kira olmaslik, admin faollashtirgach kira olish, band
  vaqt qo'shish/o'chirish (faqat o'ziniki), shifokor bo'lmagan foydalanuvchi
  bandlik sahifasiga kira olmasligi, band shifokor uchun bildirishnoma yaratilishi,
  erkin shifokor uchun bildirishnoma yaratilmasligi). To'liq test to'plami
  (`pytest tests/`, e2e/visual bundan mustasno) — 323 o'tdi, 1 ta oldindan mavjud,
  ushbu ishga aloqasi yo'q muvaffaqiyatsizlik bor (`test_phase5_attendance.py::
  test_disabled_checkin_blocked` — `git stash` bilan tekshirildi, asosiy branchda
  ham xuddi shunday muvaffaqiyatsiz, mening o'zgarishlarimga aloqasi yo'q).
- **Migratsiyalar**: `apps/accounts/migrations/0002_...py`,
  `apps/events/migrations/0010_event_attending_doctors.py` — qo'llanildi,
  `makemigrations --check` toza.

**Qo'lda tekshirilmagan qism (foydalanuvchi brauzerda sinab ko'rishi kerak):** to'liq
admin tasdiqlash oqimi va wizard orqali shifokor biriktirilgan tadbir yaratish —
avtomatik testlar bu mantiqni to'liq qamrab oladi, lekin haqiqiy brauzer orqali
click-through qilinmadi.

### 3.4 Bajarildi — `/users/` sahifasi: Django admin'siz tasdiqlash (2026-09-10)

Foydalanuvchi Django `/admin/`ga kirishda chalkashlik va chap panel ko'rinmasligi
haqida xabar berdi (sabab: `templates/admin/base.html`da butun admin qobig'i faqat
`user.is_staff=True` bo'lganda ko'rinadi — bu mo'ljallangan xatti-harakat, `manager`
kabi `is_staff=False` hisoblar uchun panel yashiringan). Foydalanuvchi Django admin'ni
"takomillashtirish" o'rniga **`/profile/` bilan bir qatorda** yangi `/users/` sahifasi
so'radi — shundan tasdiqlashlarni bajarish uchun.

- **`apps/accounts/rbac.py`**: yangi `Capability.MANAGE_USERS`, `INTERNATIONAL_ADMIN`
  roliga berildi (`SUPER_ADMIN` avtomatik — `frozenset(Capability)` orqali barcha
  capability'larga ega).
- **`apps/accounts/views.py`**: `UserManagementListView` (`/users/`) — barcha
  foydalanuvchilarni (faol bo'lmaganlar birinchi) va shifokor bo'lsa uning
  `DoctorProfile` mutaxassisligini ko'rsatadi; `UserToggleActiveView`
  (`/users/<pk>/toggle-active/`) — bitta tugma bilan faollashtirish/bloklash.
  Himoya: o'zini o'zi o'chira olmaydi, superuser bo'lmagan admin boshqa superuserni
  o'zgartira olmaydi (`PermissionDenied`).
- **`templates/partials/sidebar.html`**: "Foydalanuvchilar" havolasi qo'shildi (xuddi
  "Ma'lumotnomalar" bo'limi bilan bir xil shart — `super_admin`/`international_admin`).
- Barcha yangi matnlar uz/ru/en'ga tarjima qilindi va kompilyatsiya qilindi.
- **Testlar**: 4 ta yangi test (`TestUserManagementPage` —
  `tests/test_doctor_registration.py`da) — oddiy xodim kira olmasligi (403),
  international_admin kutilayotgan shifokorni faollashtira olishi, o'zini o'zi
  o'zgartira olmasligi, superuserni o'zgartira olmasligi. Jami test to'plami:
  327 o'tdi, 1 ta avvaldan mavjud aloqasiz muvaffaqiyatsizlik (tasdiqlangan).
- Amalda: `manager` hisobi (international_admin, `is_staff=False`) endi `/users/`ga
  to'liq kira oladi va Django `/admin/`ga umuman ehtiyoj qolmaydi.
- **Qo'shimcha so'rov bo'yicha tuzatildi**: admin huquqiga ega hisoblar (`is_superuser`,
  `super_admin`, `international_admin`) endi `/users/` ro'yxatida umuman ko'rinmaydi
  va `UserToggleActiveView` orqali ham o'zgartirib bo'lmaydi (`apps/accounts/
  selectors.py::manageable_users()` / `is_admin_privileged()`). Bu sahifa faqat
  oddiy xodimlar/shifokorlarni tasdiqlash/bloklash uchun — adminlar bir-birini shu
  yerdan boshqarmaydi. Test bilan mustahkamlangan (`test_admin_privileged_accounts_
  are_hidden_from_the_list`). Jami test to'plami: 328 o'tdi.

### 3.5 Bajarildi — "Band vaqtlarim" chap katalogga ko'chirildi + sabab majburiy (2026-09-10)

Foydalanuvchi shifokor hisobi bilan kirib, "Band vaqtlarimni boshqarish" havolasi
profil sahifasi ichida "yashiringanini" aytdi — uni chap tomondagi asosiy katalog
(sidebar) ro'yxatiga chiqarishni so'radi, shuningdek sababni yozish majburiy
ekanligini yana bir bor mustahkamlashni so'radi.

- **`templates/partials/sidebar.html`**: "Shaxsiy" bo'limida, faqat `role == 'doctor'`
  uchun ko'rinadigan "Band vaqtlarim" havolasi qo'shildi (`/profile/availability/`ga
  bog'lanadi). `templates/accounts/profile.html`dan endi ortiqcha bo'lgan tugma
  olib tashlandi.
- **`apps/accounts/views.py`**: `AvailabilityListView`ning `nav_key` qiymati
  `"profile"`dan `"availability"`ga o'zgartirildi — shunda sidebar'da faqat shu
  band o'zi faollashadi, "Profil" bilan chalkashmaydi.
- **Sabab maydoni majburiyligi mustahkamlandi**: model darajasida u allaqachon
  majburiy edi (bo'sh submit serverga o'tmasdi), lekin endi
  `StaffUnavailabilityForm.clean_reason()` bo'sh joy (whitespace)dan iborat
  matnni ham rad etadi, widget'larga HTML `required` atributi qo'shildi va
  `templates/accounts/availability.html`da har bir majburiy maydon yonida "*"
  belgisi va "Majburiy — band bo'lish sababini qisqacha yozing." matni ko'rsatiladi.
- Yangi matnlar uz/ru/en'ga tarjima qilindi.
- **Testlar**: 2 ta yangi test (bo'sh sabab va faqat bo'shliqdan iborat sabab rad
  etilishi) — jami 330 test o'tdi (1 ta avvaldan mavjud, aloqasiz muvaffaqiyatsizlik
  bundan mustasno).

### 3.6 Tuzatildi — Workspace bosh sahifasida "Chiqish" tugmasi bosilmasligi (2026-09-10)

Foydalanuvchi: workspace (`/workspace/`) bosh sahifasida turganda profil-menyudan
"Chiqish"ni bossa hech narsa bo'lmayapti, lekin boshqa sahifalarda ishlayapti, deb
xabar berdi. Sof CSS statik tahlil bilan sababini topib bo'lmadi — **Playwright**
o'rnatildi (`.venv`da allaqachon `playwright` python paketi bor edi, faqat brauzer
binarysi yetishmayotgan edi — `python -m playwright install chromium` bilan
o'rnatildi) va real brauzerda `document.elementFromPoint()` orqali aniq sabab
topildi:

- **Ildiz sabab**: `templates/workspace/home.html`dagi asosiy o'rash `<div
  class="workspace-page animate-entrance">` — `animate-entrance` klassi
  (`motion.css`) `fade-in-up` animatsiyasini ishlatadi, bu esa `transform:
  translateY(0)` bilan tugaydi va **`transform` — hatto animatsiya tugab, "dam
  olib" tursa ham — CSS'da yangi stacking context yaratadi**. Bu stacking context
  DOM tartibida topbar'dan KEYIN kelgani uchun, sahifa kontenti (jumladan "Yangi
  tadbir" tugmasi) profil-menyu ochilganda uning USTIGA chiqib, klikni "yutib
  yuboradi" — vizual jihatdan hech narsa noto'g'ri ko'rinmaydi, lekin
  `elementFromPoint` haqiqatda "Chiqish" o'rniga "Yangi tadbir" tugmasini
  qaytargan. `templates/accounts/profile.html`da bu klass yo'qligi uchun u yerda
  muammo yo'q edi — foydalanuvchining "boshqa bo'limlarda ishlayapti" kuzatuvi
  aynan shuning uchun to'g'ri edi.
- **Yashirin ikkinchi sabab**: `static/css/app.css`dagi `.dropdown-content { z-index:
  var(--z-dropdown); }` va `.topbar { z-index: var(--z-sticky); }` — bu
  o'zgaruvchilar **`tokens.css`da hech qachon aniqlanmagan edi**, shuning uchun
  har doim `z-index: auto` bo'lib, dropdown hech qachon haqiqiy balandlikka ega
  bo'lmagan.
- **Yechim**: `static/css/tokens.css`ga to'liq z-index shkalasi qo'shildi
  (`--z-base:1, --z-sticky:20, --z-dropdown:40, --z-modal:60, --z-max:100`) —
  bu darhol `.dropdown-content`ga haqiqiy `z-index:40` beradi, shu bilan u endi
  har qanday sahifadagi transform-asosli stacking context'dan mustaqil ravishda
  har doim ustida chiqadi. `animate-entrance`ni olib tashlash o'rniga (bu
  vizual entrance-effektni yo'qotardi) to'g'ridan-to'g'ri ildiz sababni —
  aniqlanmagan z-index token'larini — tuzatish afzal ko'rildi, chunki bu xuddi
  shu ikkita o'zgaruvchi ishlatilgan boshqa joylardagi (agar bo'lsa) potentsial
  xatolarni ham oldini oladi.
- **Tekshiruv**: Playwright bilan `document.elementFromPoint()` orqali avval/keyin
  solishtirildi (avval: "Yangi tadbir" tugmasi qaytgan; keyin: to'g'ri "Chiqish"
  tugmasi qaytgan), so'ng haqiqiy klik bilan to'liq chiqish oqimi sinovdan
  o'tkazildi (workspace sahifasida "Chiqish"ni bosish `/accounts/login/`ga olib
  bordi). `manage.py check` va to'liq test to'plami (330 o'tdi) ham qayta
  ishga tushirildi — regressiya yo'q.
- CSS versiya-parametrlari (`tokens.css?v=`) `templates/base.html` va
  `templates/public/base.html`da oshirildi (brauzer keshini tozalash uchun).

**Eslatma keyingi safar uchun**: bu sessiyada Playwright + Chromium birinchi marta
o'rnatildi (`.venv`da endi mavjud). Kelajakda shunga o'xshash "vizual/klik"
muammolarni aniqlash uchun qayta ishlatish mumkin — `python -m playwright install
chromium` allaqachon bajarilgan, qayta o'rnatish shart emas.

### 3.7 Bajarildi — Login logotipi tungi rejimda oq bo'lib chiqadi (2026-09-10)

Logotip rasmida (`k-one-official-transparent.png`) faqat to'q ko'k/binafsha rangli
chizilgan — tungi (dark) fonda kontrasti past edi. Alohida "dark-mode" versiya
rasm sifatida yaratish o'rniga, CSS `filter: brightness(0) invert(1)` (shaffof
fonni saqlab, chizilgan qismlarni to'liq oqqa aylantiradi) qo'llanildi —
`[data-theme="dark"] .auth-brand-logo, [data-theme="dark"] .auth-form-logo` uchun
`static/css/login.css`da. Ham katta (brand panel), ham kichik (forma sarlavhasi)
logotip qamrab olindi — ikkalasi ham bir xil tungi fonga ega bo'lgani uchun.
Playwright bilan skrinshot orqali vizual tasdiqlandi (logotip to'liq oq, aniq
ko'rinadi).

### 3.8 Tuzatildi — Public nav "Boshqaruv paneli" yorlig'i ikki qatorga bo'linib ketishi (2026-09-10)

Foydalanuvchi: dashboard tab tanlanganda ko'k pastilka "xunuk" joylashadi, "Jonli"da esa
chiroyli, deb xabar berdi. Playwright skrinshoti orqali aniq sabab topildi: 3.1-bandda
"Dashboard"ni `{% trans "Boshqaruv paneli" %}`ga tarjima qilgan edim — bu yorliq
segmentning belgilangan (flex:1, teng 1/3) kengligiga sig'may, **ikki qatorga bo'linib**
ketardi, natijada ko'k pastilka torayib, uni o'rab turgan oq konteynerga yopishib
qolganday ko'rinardi. "Taqvim"/"Jonli" bir qatorga sig'gani uchun muammosiz edi.

- **Yechim**: `templates/public/base.html`dagi yorliq `{% trans "Boshqaruv" %}`ga
  qisqartirildi (bitta so'z, bir qatorga sig'adi) — bu msgid allaqachon boshqa joyda
  (`/users/` sahifasi eyebrow'i uchun) tarjima qilingan edi (`ru: Управление, en:
  Management`), shuning uchun qo'shimcha tarjima kerak bo'lmadi.
- Playwright bilan ikkala holat (Dashboard va Live tanlangan) skrinshot qilib
  solishtirildi — endi ikkalasi ham bir xil, bitta qatorli, muvozanatli ko'rinadi.
- **Yon eslatma (muhit xatosi, kod xatosi emas)**: shablon o'zgarishi darhol
  ko'rinmadi — ishlab turgan `runserver` jarayoni (avvalgi `taskkill`lardan keyin
  qolgan) eski shablon matnini qaytarishda davom etdi. To'liq `taskkill //F //IM
  python.exe //T` + serverni qaytadan ishga tushirishdan so'ng darhol tuzaldi.
  Kelajakda shablon/tarjima o'zgarishi ko'rinmasa — avval serverni **to'liq**
  o'chirib-yoqib ko'rish kerak.
- Test to'plami qayta tekshirildi: 330 o'tdi, 1 ta avvaldan mavjud aloqasiz xato.

### 3.9 Tuzatildi — Sahifa/oy almashtirishda kuchli "qaltirash" (2026-09-10)

Foydalanuvchi: Boshqaruvdan Taqvim/Jonliga o'tishda va taqvim ichida oylarni
o'tkazishda animatsiya juda kuchli "qaltirab" ko'rinadi, deb xabar berdi. Sabab —
bir xil elementga bir nechta mustaqil harakat (transform) tizimi bir vaqtda
ta'sir qilayotgan edi:

- **Oylar orasida almashtirish**: `.cal-capsule` (har bir tadbir kapsulasi) o'zining
  `fade-in-up 320ms` kirish animatsiyasiga ega edi — bu har oy/hafta/kun almashishda
  YANGI DOM elementlar sifatida qayta yaratilgani uchun HAR SAFAR qayta ishga
  tushardi, va bu men avval qo'shgan konteyner darajasidagi cross-fade
  (`.calendar-stage.is-swapping`) bilan bir vaqtda sodir bo'lardi — natijada
  konteyner butunlay pasayib-ko'tarilayotganda, ICHIDAGI har bir kapsula HAM
  alohida pastdan yuqoriga suzib chiqardi — ikki xil harakat bir-biriga
  qo'shilib "qaltirash" hosil qilardi. `.cal-capsule`dan `animation: fade-in-up`
  olib tashlandi — endi faqat bitta, konteyner darajasidagi silliq cross-fade
  qoldi.
- **Sahifalar orasida o'tish** (3.1-bandda qo'shilgan `@view-transition`): butun
  sahifani `translateY` + `scale` bilan siljitib-kattalashtirib ko'rsatardi, bu
  esa yangi sahifaning O'ZINING `.animate-entrance`/`.animate-stagger-*`
  elementlari BILAN BIR VAQTDA ishlaydi — ikkalasi ham joyiga "o'tirayotganda"
  butun sahifa ikki marta harakatlanganday tuyulardi. `static/css/public.css`da
  `translateY`/`scale` olib tashlanib, faqat toza opacity fade qoldirildi (eskisi
  chiqishi yangisidan tezroq — 60% davomiylik — shunda yangi sahifa o'zining
  kirish animatsiyasini erkin his qiladi).
- CSS versiya-parametrlari oshirildi (`calendar.css`, `public.css`), server
  to'liq qayta ishga tushirildi (3.8-banddagi eslatmaga muvofiq — oddiy qayta
  ishga tushirish ba'zan yetarli bo'lmasligi mumkin).
- Test to'plami: 330 o'tdi, 1 ta avvaldan mavjud aloqasiz xato.

### 3.10 Bajarildi — Band vaqt endi ko'p kunlik oraliqni qo'llab-quvvatlaydi (2026-09-10)

Foydalanuvchi: band vaqt rejalashtirish faqat bitta kun uchun ishlar edi, boshlanish
sanasi+vaqti va tugash sanasi+vaqti alohida-alohida bo'lishi kerak, dedi (masalan,
kechqurun boshlanib ikki kundan keyin ertalab tugaydigan safar/konferensiya holati).

- **`apps/accounts/models.py`**: `StaffUnavailability.date` maydoni `start_date` +
  `end_date`ga bo'lindi (`start_time`/`end_time` saqlanib qoldi, endi mos ravishda
  boshlanish/tugash sanasiga bog'liq). `start_datetime`/`end_datetime` property'lari
  qo'shildi (solishtirish uchun).
- **`apps/accounts/services.py::find_unavailability_conflicts`**: endi to'g'ridan-to'g'ri
  sana taqqoslash o'rniga, chinakam sana+vaqt oralig'ini (`datetime.combine`) solishtiradi
  — DB darajasida arzon oldindan filtrlash (`start_date__lte=planned_date,
  end_date__gte=planned_date`), so'ng aniq ustma-ustlikni Python'da tekshiradi. Tadbir
  bitta kunlik bo'lgani uchun (Event.planned_date), ko'p kunlik band oraliq ichidagi
  istalgan kun ham to'g'ri "band" deb aniqlanadi.
- **`apps/accounts/forms.py::StaffUnavailabilityForm`**: `start_date`/`end_date` maydonlari
  qo'shildi, `clean()` endi to'liq sana+vaqtni solishtiradi (`tugash < boshlanish` bo'lsa
  xato).
- **`templates/accounts/availability.html`**: forma 4 ta maydonga ega bo'ldi (boshlanish
  sanasi, boshlanish vaqti, tugash sanasi, tugash vaqti) + sababi; ro'yxatda ham ikkala
  sana/vaqt ko'rsatiladi.
- **Migratsiya**: `StaffUnavailability` bu sessiyada yaratilgan (hali hech qayerga
  "chiqarilmagan") bo'lgani uchun, yangi 0003 migratsiya qo'shish o'rniga mavjud
  `0002_...py`ning o'zi to'g'ridan-to'g'ri tahrirlandi (orqaga qaytarilib, qayta
  qo'llanildi) — sof migratsiya tarixini saqlab qolish uchun. Jadvalda faqat 1 ta test
  qatori bor edi, xavfsiz o'chirildi.
- **Testlar**: 5 ta yangi test (ko'p kunlik slot qo'shish, tugash boshlanishdan oldin
  bo'lsa rad etilishi, ko'p kunlik oraliq ichidagi kun uchun tadbirga band shifokor
  aniqlanishi). Playwright orqali to'liq brauzer oqimi ham sinovdan o'tkazildi
  (kechqurundan ikki kun keyingi ertalabgacha bo'lgan band vaqt to'g'ri saqlandi va
  ko'rsatildi). Jami test to'plami: 333 o'tdi, 1 ta avvaldan mavjud aloqasiz xato.

### 3.11 Bajarildi — Shifokor uchun yillik band vaqt limiti (2026-09-10)

Foydalanuvchi: bitta shifokor 1 yilda ko'pi bilan 4 marta o'zini band deb
belgilay olishi kerak, dedi.

- **`apps/accounts/forms.py`**: `MAX_UNAVAILABILITY_SLOTS_PER_YEAR = 4` konstantasi
  qo'shildi. `StaffUnavailabilityForm` endi `user` argumentini qabul qiladi
  (`__init__(..., user=None)`) va `clean()`da — agar shu foydalanuvchining
  `start_date.year`ga mos joriy yozuvlari soni limitga yetgan/oshgan bo'lsa —
  aniq xato xabari bilan rad etadi (chegara — kalendar yili, `start_date`ga
  qarab; o'chirilgan yozuvlar kvotani darhol bo'shatadi, chunki hisob doim
  joriy bazadagi qatorlar bo'yicha olinadi).
- **`apps/accounts/views.py::AvailabilityListView`**: formaga `user=request.user`
  uzatiladi (GET va POST'da ham); kontekstga `slots_used_this_year`,
  `slots_limit_per_year`, `current_year` qo'shildi — sahifada "2026-yil uchun
  ishlatilgan: 4 / 4" ko'rinishida kvota ko'rsatiladi.
- **Yon-tuzatish (shu joyda topilgan eski xato)**: `get_context_data()` xato
  bo'lgan formani (`post()`dan `form=form` bilan uzatilgan) e'tiborsiz qoldirib,
  har doim YANGI bo'sh forma yaratardi — demak xato xabarlari hech qachon
  ko'rsatilmasdi. `context.setdefault("form", ...)`ga o'zgartirildi — endi
  xato bo'lganda foydalanuvchi kiritgan ma'lumotlar va xato xabari saqlanib,
  ko'rsatiladi.
- **`templates/accounts/availability.html`**: kvota matni va
  `form.non_field_errors` bloki qo'shildi (avval umuman ko'rsatilmasdi).
- **Testlar**: 4 ta yangi test (4 tadan keyin 5-chisi rad etilishi, limit
  yil bo'yicha alohida hisoblanishi — 2027-yilga yangi slot qo'shish mumkinligi,
  o'chirish kvotani bo'shatishi). Playwright bilan to'liq brauzer oqimi ham
  vizual tasdiqlandi (4/4 holatda 5-chi urinish aniq xato bilan rad etilgani
  va forma ma'lumotlari yo'qolmagani skrinshotda ko'rindi). Jami test to'plami:
  336 o'tdi, 1 ta avvaldan mavjud aloqasiz xato.

### 3.12 Tuzatildi — Shifokorni noto'g'ri maydonga tanlash mumkin edi (2026-09-10)

Foydalanuvchi: `satosylv`ni tadbirga qo'shganda hech qanday xatolik/ogohlantirish
chiqmadi, dedi (band vaqt qo'yilgan bo'lsa ham). Playwright bilan real hisob orqali
qayta tekshirganimda **haqiqiy sabab topildi**: foydalanuvchi `satosylv`ni
**"Ishtirok etuvchi shifokorlar"** maydoniga emas, balki **"Rahbariyat mas'uli"
(management_responsible)** maydoniga tanlagan ekan — bu maydonda hech qanday
bandlik tekshiruvi yo'q (u faqat `attending_doctors` uchun ishlaydi).

- **Ildiz sabab**: `apps/events/forms.py`da `responsible_employee`/
  `management_responsible` maydonlari, agar tizimda mos rolli (masalan,
  `management_responsible`) foydalanuvchi umuman bo'lmasa, **barcha faol
  foydalanuvchilarga** (shifokorlar ham kiradi!) qaytib tushardi (fallback).
  Bazada haqiqiy `management_responsible`-rolli foydalanuvchi yo'q ekan,
  shuning uchun bu fallback doim ishga tushib, shifokorlar ham shu ro'yxatda
  ko'rinar edi — foydalanuvchi tasodifan noto'g'ri joyga bosgan.
- **Yechim**: `apps/accounts/selectors.py::selectable_staff()`ga
  `exclude_doctors: bool` parametri qo'shildi. `apps/events/forms.py`dagi
  `EventStep3Form` (wizard) va `EventUpdateForm` (tahrirlash) — ikkalasida ham
  `responsible_employee`/`management_responsible` uchun endi shifokorlar
  butunlay chiqarib tashlanadi (`selectable_staff(exclude_doctors=True)`).
  Shifokorlar endi FAQAT "Ishtirok etuvchi shifokorlar" maydonida tanlanishi
  mumkin — shu orqali bandlik tekshiruvi hech qachon chetlab o'tilmaydi.
- **Yon-tuzatish**: `EventUpdateForm`da bu ikki maydon avval **umuman
  filtrlanmagan edi** (Django ModelForm defaulti — `User.objects.all()`,
  hatto faol bo'lmagan/superuser hisoblarni ham o'z ichiga olardi). Endi
  wizard bilan bir xil, faqat faol xodimlarga cheklangan.
- **E'tibor**: dastlab `EventUpdateForm`da wizard'dagi kabi qat'iy "faqat mos
  rolli foydalanuvchi, aks holda fallback" mantig'ini qo'llagan edim, lekin bu
  `tests/test_reservation_workflow.py::test_editing_event_does_not_conflict_
  with_itself`ni buzdi (u international_admin'ni ataylab management_responsible
  qilib qo'yishga tayanadi). Shuning uchun `EventUpdateForm` uchun yumshoqroq
  qoidaga qaytarildi: faqat shifokorlarni chiqarib tashlash, boshqa hech qanday
  rol cheklovi qo'shilmadi (bu — "so'ralganidan ortiq qilma" tamoyiliga mos).
- **Testlar**: 2 ta yangi test (`TestDoctorsExcludedFromResponsiblePickers`) —
  shifokor na wizard'ning 3-qadamida, na tahrirlash formasida
  `responsible_employee`/`management_responsible` ro'yxatida ko'rinmasligini
  tasdiqlaydi. Jami test to'plami: 338 o'tdi, 1 ta avvaldan mavjud aloqasiz xato.
- **Diqqat**: foydalanuvchining haqiqiy sinov tadbiri ("Shoshilinch yig'ilish",
  2026-09-10 16:33–17:33) hozircha `management_responsible=satosylv` holatida
  qolgan — men buni o'zgartirmadim (foydalanuvchining o'z ma'lumoti). Endi
  tahrirlash formasini qayta ochsa, `satosylv` bu maydonda ko'rinmaydi — kerak
  bo'lsa, uni to'g'ri xodimga almashtirib, "Ishtirok etuvchi shifokorlar"ga
  qo'shib qo'yish kerak.

### 3.13 Bajarildi — Band shifokorni biriktirish endi bloklanadi (2026-09-10)

Foydalanuvchi: yuqorida ogohlantirish chiqsa ham, "Yaratish"/"Saqlash" tugmasi
baribir bosilaveradi va tadbir saqlanaveradi, dedi — "shifokor qanday [ikki
joyda birdan] qatnashadi?" degan haqli savol bilan. Talab: band shifokor
tanlansa, saqlash **umuman ruxsat berilmasligi** kerak (soft warning emas,
hard block).

- **`apps/accounts/services.py`**: yangi `find_busy_doctors(doctors, planned_date,
  start_time, end_time)` — bir nechta shifokorni bir yo'la tekshirib,
  (shifokor, sababi) juftliklarini qaytaradi.
  `apps/events/views.py::notify_busy_attending_doctors` (avval faqat
  `messages.warning()` + `Notification` yaratardi, saqlashni to'xtatmasdi) olib
  tashlanib, o'rniga `busy_attending_doctor_errors(...)` qo'shildi — bu shunchaki
  xato matnlari ro'yxatini qaytaradi, **hech narsani saqlamaydi**.
- **`EventUpdateView.form_valid`** (`apps/events/views.py`): endi
  `event.save()`dan OLDIN `form.cleaned_data["attending_doctors"]`ni tekshiradi;
  band shifokor topilsa `form.add_error(None, ...)` bilan **`form_invalid`ni
  qaytaradi** — hech narsa saqlanmaydi, foydalanuvchi xuddi shu forma sahifasida
  xato bilan qoladi (kiritilgan ma'lumotlar yo'qolmaydi).
- **Wizard (`apps/events/wizard.py::finalize_event`)**: `Event.objects.create()`
  chaqirilishidan OLDIN tekshiradi; band shifokor topilsa **tadbir umuman
  yaratilmaydi**, foydalanuvchi xato xabari bilan 3-qadamga (Xalq/People)
  qaytariladi — xuddi zal to'qnashuvi tekshiruvi 2-qadamga qaytargani kabi bir
  xil naqsh.
- **Tekshiruv**: Playwright bilan to'liq wizard oqimi ishga tushirilib, band
  shifokor bilan saqlashga urinildi — natija: **0 ta tadbir yaratildi**, aniq
  xato ko'rsatildi ("Abdullatif Karimov is busy at this time and cannot be
  assigned — reason: ...") va foydalanuvchi 3-qadamga, oldingi tanlovlari
  saqlangan holda qaytarildi (skrinshotda tasdiqlandi).
- **Testlar**: `TestDoctorAvailabilityConflictNotification` klassi
  `TestDoctorAvailabilityConflictBlocking`ga qayta yozildi — endi haqiqiy
  `EventUpdateView` orqali (client.post) band shifokor bilan tahrirlash **200
  (qayta render, xato bilan)** qaytarishini, erkin shifokor bilan esa **302
  (muvaffaqiyatli)** qaytarishini tasdiqlaydi. Jami test to'plami: 340 o'tdi,
  1 ta avvaldan mavjud aloqasiz xato.
- Yangi xato matni uz/ru/en'ga tarjima qilindi.

### 3.14 Aniqlandi va soddalashtirildi — "Ishtirok etuvchi shifokorlar" → "Ma'ruzachi shifokorlar" (2026-09-10)

Foydalanuvchi qo'shimcha rollar (Moderator, Konsultant) kerak-emasligini,
"Ishtirokchi"ni esa qo'lda kiritish shart emasligini aytdi — sabab: loyihada
allaqachon alohida **QR check-in tizimi** bor (`apps/attendance/models.py::
EventAttendance`) — oddiy ishtirokchilar tadbir kunida QR kod orqali o'zlari
ro'yxatdan o'tadi (ism/tashkilot/lavozimni o'zi kiritadi), oldindan ro'yxat
kerak emas. Loyihani tekshirib, bu haqiqatan ham shunday ishlashini
tasdiqladim (`apps/attendance/`, `PublicCheckinView`).

Demak, sessiya davomida qurilgan `attending_doctors` maydoni aslida faqat
**bitta** maqsadga xizmat qiladi — tadbirda ma'ruza qiladigan shifokorlarni
belgilash. Shu sababli:

- Model/forma/shablon darajasida atama **"Attending Doctors" / "Ishtirok
  etuvchi shifokorlar"dan "Speaker Doctors" / "Ma'ruzachi shifokorlar"ga**
  o'zgartirildi (`apps/events/models.py`, `apps/events/forms.py::EventStep3Form`,
  `templates/events/event_detail.html`, `templates/accounts/availability.html`
  intro matni) — bu allaqachon mavjud bo'lgan `Speaker` (Ma'ruzachi) modeli
  bilan atama jihatidan mos keladi (ikkalasi ham "ma'ruzachi" tushunchasini
  bildiradi, lekin `Speaker` — login qilmaydigan, qo'lda kiritiladigan profil;
  `attending_doctors` — tizimga kirgan shifokor `User` hisoblari; ikkisi hali
  ham texnik jihatdan alohida modellar, faqat atama mosligi berildi. Ularni
  birlashtirish — alohida, kattaroq refaktoring, hozircha so'ralmagan).
  Rol tizimi (through-model) **qo'shilmadi** — oddiy M2M saqlanib qoldi,
  chunki yagona maqsad (ma'ruzachi) uchun ortiqcha murakkablik shart emas edi.
- Migratsiya: `apps/events/migrations/0010_event_attending_doctors.py` bu
  sessiyada yaratilgan (hali "chiqarilmagan") bo'lgani uchun, yana o'sha
  fayl to'g'ridan-to'g'ri tahrirlandi (orqaga qaytarilib, qayta qo'llanildi).
- Yangi matnlar uz/ru/en'ga tarjima qilindi. `manage.py check` va to'liq test
  to'plami (340 o'tdi, 1 ta avvaldan mavjud aloqasiz xato) qayta tekshirildi.

### 3.15 To'liq audit — shoshmasdan tahlil, bog'liqliklar va bug qidiruvi (2026-09-11)

Foydalanuvchi: "loyihani to'liq shoshmasdan tahlil qil, bog'liqliklarni tekshir,
hech qanday bug qolmasin" — so'ragan. Bajarilgan tekshiruvlar va topilmalar:

- **`ruff check`** — shu sessiyada yozilgan/o'zgartirilgan barcha fayllar (`apps/
  accounts/forms.py`, `apps/accounts/services.py`, `apps/accounts/views.py`,
  `apps/events/forms.py`, `apps/events/views.py`, `apps/events/wizard.py`,
  `config/urls.py`, `tests/test_doctor_registration.py`) bo'yicha barcha
  E501 (qator uzunligi), I001 (import tartibi) va F841 (ishlatilmagan
  o'zgaruvchi) ogohlantirishlari tuzatildi — endi bu fayllar **toza**.
  Oldindan mavjud (mening ishimga aloqasi yo'q) fayllardagi ogohlantirishlarga
  tegilmadi (`config/master_data.py`, `apps/events/services/workflow.py`,
  `apps/events/views.py`ning eski qismlari).
- **HAQIQIY, ILGARI ANIQLANMAGAN BUG TOPILDI VA TUZATILDI**: `Event.checkin_status()`
  (`apps/events/models.py`) `checkin_enabled` maydonini **umuman tekshirmasdi** —
  bu maydon modelda bor edi, lekin ishlatilmagan (dead field). Natijada, admin
  tadbir uchun check-in'ni o'chirib qo'ysa ham, ommaviy QR check-in baribir
  ishlab turaverar edi. Buni `tests/test_phase5_attendance.py::
  test_disabled_checkin_blocked` doim muvaffaqiyatsiz bo'lishi orqali sezib,
  ildizigacha kuzatib bordim (`PublicCheckinView` → `process_public_checkin` →
  `Event.checkin_status()`). Tuzatildi: `checkin_status()`ga
  `if not self.checkin_enabled: return {"eligible": False, "code": "not_enabled", ...}`
  tekshiruvi qo'shildi. **Natija: endi to'liq test to'plami 341/341 o'tadi
  (avval 340/341, 1 tasi doim muvaffaqiyatsiz edi)** — bu sessiyadan oldin ham
  mavjud bo'lgan, lekin hech qachon tuzatilmagan real xato edi.
- **Bog'liqliklar**: `manage.py check` va `makemigrations --check --dry-run` —
  ikkalasi ham toza. Barcha yangi migratsiyalar (`accounts.0002`,
  `events.0010`) to'g'ri qo'llanadi va orqaga qaytariladi (sinovdan o'tkazildi).
- **Playwright orqali to'liq brauzer o'tishi**: workspace, profil, foydalanuvchilar,
  tadbirlar, taqvim, hisobotlar, master-data sahifalari — barchasi 200 qaytardi,
  JS konsolida ilovaga tegishli xato yo'q. Topbar dropdown/"Chiqish" hali ham
  ishlayapti (3.6-banddagi tuzatish saqlanib qolgan).
  - `/dashboard/calendar/`da CSP orqali bloklangan noma'lum ikonka-shrift
    (base64 TTF, "fcicons"/IcoMoon) haqida konsol xabari topildi — butun
    kod bazasi (`static/`, `templates/`) bo'yicha qidirilganda bu shrift
    HECH QAYERDA e'lon qilinmagan/ishlatilmagan — demak bu loyiha kodiga
    aloqasi yo'q (brauzer/muhitga xos artefakt bo'lishi mumkin). Harakat
    talab qilinmadi.
  - "404" deb ko'ringan `/notifications/telegram-settings/` — mening audit
    skriptimdagi noto'g'ri yo'l edi (haqiqiy yo'l `/notifications/telegram/`);
    to'g'ri yo'l bilan tekshirilganda muammosiz ishladi. Yolg'on signal edi.
- **Ma'lumotlar bazasi tozaligi**: barcha vaqtinchalik sinov hisoblari
  (`debug.*`, `audit.check` va h.k.) va sinov tadbirlari o'chirildi. Faqat
  foydalanuvchining haqiqiy ma'lumotlari qoldi.
- **Repozitoriy tozaligi**: sessiya davomida qurilgan (qobiq/kiritish
  xatolaridan kelib chiqqan) 6 ta bo'sh, chalkash nomli qoldiq fayl
  (`'`, `({text`, `({value`, `Bu`, `dict[str`, `o.text)`) topilib o'chirildi.
- **Yakuniy holat**: `pytest tests/` (e2e/human_acceptance/visual_baseline
  bundan mustasno — ularda haqiqiy test fayli yo'q, faqat README/skrinshotlar)
  — **341/341 o'tdi**. Server qayta ishga tushirilib, barcha sahifalar
  tekshirildi.

---

### 3.16 Haqiqiy loyiha bo'ylab (barcha 10 app) audit — foydalanuvchi tuzatishidan keyin (2026-09-11)

Foydalanuvchi 3.15-bandni "faqat men o'zgartirgan fayllar" deb aniq tuzatdi:
*"Ha men projectni to'liq tahlil qil degandim ya'ni ma'lum bir fayllar emas
projectni to'liq"*. Shu sababli butun `apps/` (10 ta modul) bo'yicha, faqat lint
emas, **mantiqiy/logika darajasida** qayta ko'rib chiqildi — ikkita parallel
fon-agent (`venues/organizations/publications` va `reporting/notifications`)
orqali, qolgan qismlarini (`apps/attendance`, `apps/accounts` management
buyruqlari, `apps/events` chuqurroq) o'zim to'g'ridan-to'g'ri o'qib chiqdim.

**HAQIQIY BUG TOPILDI VA TUZATILDI**: `apps/attendance/views.py`,
`EventAttendanceView.post()`, `manual_checkin` action (~286-304 qatorlar).
`messages.error(request, "Please provide a valid attendee name...")` chaqiruvi
`if form.is_valid():` blokining ICHIDA, `else:`siz turgan edi. Natijada har safar
xodim qo'lda ishtirokchini muvaffaqiyatli qo'shganda ham foydalanuvchiga
**muvaffaqiyat XABARI bilan birga xato xabari ham** ko'rsatilar edi, forma
noto'g'ri to'ldirilganda esa hech qanday xabar chiqmasdi (jim redirect).
Tuzatildi: `messages.error(...)` endi `else:` blokiga ko'chirildi.

**Aniqlandi, lekin ATAYLAB TUZATILMADI (texnik qarz sifatida hujjatlashtirildi,
4-bo'limga qarang, band 10)**: `EventType.requires_management_approval` va
`EventType.allows_emergency_override` (`apps/events/models.py:68-75`) — admin
panelida, formada, API'da sozlanadigan, lekin hech qanday workflow logikasi
(`submit_event_for_approval`, `approve_event`, `override_event`,
`EventWizardView.finalize_event`) tomonidan hech qachon o'qilmaydigan "o'lik
maydonlar". Bu `checkin_enabled` bug'iga o'xshab ko'rinsa-da, farqi: bu yerda
"tuzatish" yangi biznes-qoida ixtiro qilishni talab qiladi (masalan,
`requires_management_approval=False` bo'lsa, tasdiqlash bosqichi butunlay
o'tkazib yuborilishi kerakmi?), bu esa CLAUDE.md'ning "faqat so'ralganini qil"
qoidasiga zid va mavjud testlarni buzish xavfini tug'diradi. Shuning uchun kod
o'zgartirilmadi, faqat hujjatlashtirildi.

**Boshqa tekshirilgan, bug topilmagan sohalar**: `apps/venues`, `apps/organizations`,
CRUD/tanlov querylari; `apps/publications` (Celery beat orqali nashr rejalashtirish,
`CELERY_BEAT_SCHEDULE`ga to'g'ri ulangan); `apps/reporting` (analitika/eksport/public
API — maxfiylik qoidalariga rioya qiladi, `checkin_enabled` bu yerda TO'G'RI
tekshiriladi); `apps/notifications` + `telegram/` (eslatma dispetcheri
idempotent, `select_for_update` race-condition'lardan himoyalaydi); `apps/attendance`
modellari/admin; `apps/accounts` management buyruqlari
(`prepare_acceptance_demo.py`, `cleanup_acceptance_demo.py`).

**Yakuniy holat**: server qayta ishga tushirildi (`taskkill` + toza `runserver`,
200 OK), `ruff check apps config` — toza, `pytest tests/` (e2e/human_acceptance/
visual_baseline bundan mustasno) — **341/341 o'tdi**.

---

### 3.17 Frontend audit — foydalanuvchi ikkinchi marta tuzatdi: "backend ko'rdim, frontendni ko'rmadim" (2026-09-11)

Foydalanuvchi to'g'ri ta'kidladi: 3.16-band faqat Python/backend kodini qamragan
edi, `templates/` (88 fayl), `static/css/` (13 fayl), `static/js/` (5 fayl) hali
tekshirilmagan qolgan edi. Uchta parallel fon-agent (public+shared assets,
events/wizard/master-data/venues/organizations, accounts/admin/reporting/
publications/notifications) orqali, so'ng o'zim qo'shimcha qamrov bilan
(`event_attendance.html`, `master_data/*`, `venues/*`) to'liq frontend audit
o'tkazildi.

**HAQIQIY BUG TOPILDI VA TUZATILDI (4 ta)**:

1. **`templates/public/calendar.html` va `dashboard.html`** — "Tadbir yaratish"
   tugmasi haqiqiy tadbir yaratish sahifasi (`events:wizard`) o'rniga oddiy
   workspace bosh sahifasiga (`dashboard`) yo'naltirar edi. Tuzatildi.
2. **`templates/public/live_venues.html`** — 0 baytli, hech qayerda
   ishlatilmaydigan bo'sh fayl. O'chirildi.
3. **`static/css/tokens.css`** — `components.css`, `calendar.css`,
   `workspace.css`, `app.css`, `admin-pages.css`da ishlatilgan, lekin
   `tokens.css`da HECH QACHON aniqlanmagan **~35 ta CSS custom property**
   (`--color-text`, `--content-max`, `--color-surface`, `--radius-2xl`,
   `--shadow-lg/xl`, `--motion-fast/normal`, `--leading-*`, `--tracking-wide/
   widest/tighter` va h.k.) — xuddi shu sessiyada avval topilgan
   `--z-dropdown` bug'i bilan bir xil sinf (brauzer butun CSS
   deklaratsiyasini jim bekor qiladi). Eng jiddiy ta'sirlari: workspace
   kontent wrapper'ida `max-width` ishlamasligi, topbar dropdown menyusida
   soya yo'qligi, filter maydonlarida fokus outline ko'rinmasligi
   (accessibility). Barchasi mavjud tokenlarga mos alias sifatida qo'shildi
   (faqat qo'shimcha, hech narsa o'chirilmadi, dark-mode avtomatik moslashadi).
4. **`templates/events/wizard/step_5.html`** (yakuniy ko'rib chiqish
   bosqichi) — summary kartochkasi `summary_data.attending_doctors`ni
   umuman ko'rsatmasdi, garchi `apps/events/wizard.py::build_summary()` uni
   context'ga to'liq uzatsa ham. Foydalanuvchi "Saqlash"ga bosishdan oldin
   qaysi shifokorlarni Ma'ruzachi sifatida tanlaganini tekshira olmasdi —
   bu aynan shu sessiyada tuzatilgan shifokor-chalkashish bug'i bilan bir
   xil xavf sinfi. Tuzatildi: summary'ga "Ma'ruzachi shifokorlar" qatori
   qo'shildi.

**Qat'iy tekshiruv — `{% url %}` butun loyiha bo'ylab**: barcha 88 shablondan
107 ta noyob `{% url %}` nomi chiqarib olindi va Django resolver orqali
avtomatik tekshirildi (`reverse()` + `NoReverseMatch` xabari tahlili — "1
pattern(s) tried" bo'lganlar ro'yxatdan o'tgan, faqat argument kerak; "is not
a registered namespace"/"not found, 0 patterns" bo'lganlar haqiqiy xato
bo'lardi). **Natija: birorta ham buzilgan/mavjud bo'lmagan URL nomi yo'q.**

**Qo'shimcha tekshirilgan, bug topilmagan**: `|safe` filtri va
`autoescape off` — loyiha bo'ylab BIRORTA HAM ishlatilmagan (XSS xavfi yo'q).
`event_attendance.html` (JS fetch manzili `/api/v1/events/<pk>/attendance/
stats/` `config/api_urls.py`da to'g'ri ro'yxatdan o'tgan, Django `messages`
`base.html`da global render qilinadi — 3.16-bandda tuzatilgan manual_checkin
xabar bug'i endi to'g'ri ko'rsatiladi). `master_data/form.html`,
`confirm_delete.html` — 3 xil resurs turi (venues/event-types/organizations)
uchun umumiy shablon to'g'ri ishlaydi, resursga xos noto'g'ri taxmin yo'q.
`venues/live_status.html` — toza. `accounts/availability.html`,
`user_management.html`, `templates/admin/*` (audit log) — CSRF, kvota
ko'rsatish, admin-huquqli hisoblarni yashirish to'g'ri ishlaydi. Publikatsiya
"Publish" tugmasida frontend disable-on-submit yo'q, lekin backend
(`cache.add` lock + `select_for_update` + status-guard) ikki marta bosishni
allaqachon to'liq blokladi — frontend zaiflik emas.

**Diqqat**: birinchi fon-agent (public/CSS/JS) tekshirish davomida (menga
"faqat tekshir" deyilgan bo'lsa ham) tuzatishlarni bevosita o'zi kiritgan edi —
bu men tomonidan `git diff` orqali qayta ko'rib chiqildi va tasdiqlandi
(faqat qo'shimcha, xavfsiz o'zgarishlar ekan). Ikkita bo'sh, qobiq xatosidan
qolgan fayl (`Bu`, `span`) ham topilib o'chirildi.

**Yakuniy holat**: server qayta ishga tushirildi, `manage.py check` toza,
`ruff check apps config` toza, **`pytest tests/` — 341/341 o'tdi**.

---

### 3.18 Tuzatildi — Public event sahifasidagi QR kod telefonlarga o'qib bo'lmas edi (2026-09-11)

Foydalanuvchi: *"publi-events linkidagi qr code ni telefonlar o'qishga juda
qiynalyapdi"*. Ildizigacha kuzatib borildi:

- `Event.public_token` — `secrets.token_urlsafe(16)` orqali ~22 belgili token,
  to'liq URL (`https://.../event/<token>/?scan=true`) ~65 belgi. Bu
  `apps/events/services/qr.py`da QR versiyasini avtomatik 5-versiyaga
  (37×37 modul) ko'targan — o'zi bilan hisoblashda muammo emas.
- **Asosiy sabab topildi**: `templates/events/public_kiosk.html` va
  `templates/events/public_event_detail.html`da bu 37×37 modulli zich QR kod
  atigi **70×70 pikselda** ko'rsatilar edi (`<img style="width: 70px;
  height: 70px;">`). Har bir modul ~1.9px'ga to'g'ri kelgan — bu ikkala
  sahifa ham ekran/kiosk'da masofadan (boshqa odamning telefoni bilan)
  skanerlanishi uchun mo'ljallangan (`.desktop-qr { @media max-width:600px {
  display:none } }` — mobil qurilmada butunlay yashirin, faqat "katta ekran +
  begona telefon" ssenariysi uchun), shuning uchun kichik o'lcham real
  skanerlashni deyarli imkonsiz qilgan.
- Qo'shimcha kamchilik: `qrcode.QRCode(border=3)` — QR spetsifikatsiyasi
  tavsiya qilgan minimal "quiet zone" (4 modul)dan kam edi.

**Tuzatildi**:
1. `apps/events/services/qr.py` — `border=3` → `border=4` (PNG va SVG
   ikkalasida ham), fill rangi `#07172f` (to'q lekin qora emas) → `#000000`
   (maksimal kontrast).
2. `templates/events/public_kiosk.html` va `public_event_detail.html` — QR
   badge o'lchami `70×70px` → `150×150px` (yondosh matn uchun
   `padding-right: 90px` → `170px` ham moslashtirildi, ustma-ust tushmasligi
   uchun).
3. `templates/events/event_print_qr.html` (240px) va `event_program_edit.html`
   (180px) — bular allaqachon yetarlicha katta edi, o'zgartirilmadi.

**Tekshirildi**: `manage.py runserver` orqali haqiqiy QR PNG yuklab olindi
(410×410 native piksel, to'g'ri o'lcham), Playwright orqali public event
sahifasi skrinshot qilindi — QR badge endi matn bilan to'qnashmaydi, aniq oq
hoshiyaga ega. `pytest tests/` — 341/341, `ruff check` — toza.

---

### 3.19 Bajarildi — Server bir tarmoqdagi qurilmalarga ochildi + check-in endi avtomatik yoqiladi (2026-09-11)

**LAN kirish**: foydalanuvchi so'radi — "bitta tarmoqdagilar ham ishlatish
ko'rish uchun link". `ALLOWED_HOSTS` allaqachon `"*"` bilan sozlangan edi
(o'zgartirish shart bo'lmadi). Server `0.0.0.0:8000`ga bog'lab qayta ishga
tushirildi (avval faqat `127.0.0.1`), lokal IP (`10.34.12.152`) aniqlandi.
Havola: `http://10.34.12.152:8000/`. Windows Firewall'da 8000-port uchun
inbound qoida yo'qligi aniqlandi, lekin uni qo'shish (`New-NetFirewallRule`)
Claude Code'ning auto-mode klassifikatori tomonidan tizim darajasidagi
o'zgarish sifatida bloklandi — foydalanuvchiga buyruqni o'zi `!` prefiksi
bilan ishga tushirishi taklif qilindi (avtomatik bajarilmadi).

**`checkin_enabled` endi avtomatik yoqiladi**: foydalanuvchi — "public
eventsdagi QR kod orqali 'qatnashish' tugmasi 'ro'yxatdan o'tish
yoqilmagan' deb chiqyapti, buni qayerdan tuzataman" degan savoliga javoban
tushuntirdim: bu 3.16-bandda tuzatilgan `checkin_status()` bug'ining
to'g'ri ishlashi (avval bu tekshiruv umuman ishlamas edi) va maydonning
standart qiymati `default=False` ekanligi sabab edi. Foydalanuvchi
"avtomatik yoqiladigan qilib ber" deb aniq so'ragach:
- `apps/events/models.py::Event.checkin_enabled` — `default=False` →
  `default=True`.
- Yangi migratsiya `apps/events/migrations/0011_alter_event_checkin_enabled.py`
  — schema o'zgarishi (`AlterField`) + `RunPython` data-migratsiya orqali
  **mavjud barcha tadbirlarni ham** `checkin_enabled=True`ga o'tkazdi (faqat
  yangi tadbirlarga emas, chunki foydalanuvchi hozirgi sinov tadbiri uchun
  ham darhol ishlashini kutgan edi). Bu migratsiya oldingi (allaqachon
  qo'llangan) fazadagi maydonga tegishli bo'lgani uchun — sessiya qoidasiga
  ko'ra — joyida tahrirlanmadi, balki yangi migratsiya sifatida qo'shildi.
- Tekshirildi: `pytest tests/` — 341/341 (mavjud `test_disabled_checkin_blocked`
  testi o'zi ichida `checkin_enabled=False`ni aniq belgilagani uchun buzilmadi),
  `ruff check` — toza, barcha mavjud tadbirlar bazada `checkin_enabled=True`
  ekanligi tasdiqlandi (`Event.objects.filter(checkin_enabled=False).count()
  == 0`). Server qayta ishga tushirildi (`0.0.0.0:8000` saqlanib qolindi).

**Eslatma (texnik qarz emas, lekin kelajakda hisobga olinsin)**: xodim endi
biror tadbir uchun check-in'ni ataylab O'CHIRISHNI xohlasa, buni hali ham
Attendance Management sahifasidagi katakchani o'chirib qo'yish orqali qila
oladi — faqat standart holat endi "yoqilgan" bo'ldi.

---

## 4. E'tibor talab qiladigan narsalar / texnik qarz

1. **`apps/approvals` app deyarli bo'sh** — `models.py` faylida faqat bitta izoh bor:
   *"Approval workflow models are intentionally deferred to Phase 3."* Aslida tasdiqlash
   (approval) logikasi `apps/events` ichida joylashgan. Agar kelajakda `approvals` app'ini
   to'ldirish yoki umuman olib tashlash rejalashtirilsa — bu qaror alohida qabul qilinishi
   kerak, chunki nom bilan real joylashuv mos kelmaydi.
2. **`ALLOWED_HOSTS` default qiymatiga `"*"` qo'shilgan** (`config/settings/base.py`).
   Bu faqat `.env`da `DJANGO_ALLOWED_HOSTS` berilmagan holatlar uchun fallback, lekin
   **production uchun xavfli** — production `.env`da bu qiymat aniq host nomlari bilan
   override qilinganiga ishonch hosil qilish kerak.
3. **Root papkada vaqtinchalik/runtime fayllar bor:** `celerybeat-lan.pid`,
   `waitress.log`, `scratch_py_missing.json`, `scratch/`. Bularning `.gitignore`da
   to'g'ri qoplanganini tekshirish kerak (`.gitignore` ham hozir o'zgartirilmoqda).
4. **`scripts/` papkasi 100+ bir martalik skriptlar bilan to'lib ketgan**
   (`capture_phase27_*`, `verify_phase*`, `apply_*`, `fix_*`) — bular tarixiy vizual-QA
   ishlari, asosiy runtime'ga aloqasi yo'q. Kelajakda arxivlash yoki `scripts/archive/`ga
   ko'chirish mumkin (foydalanuvchi tasdiqlasa).
5. **`static/css/workspace_corrupted.css`** nomli fayl commit tarixida o'chirilgan holat
   ko'rinadi (Phase 2 diffida `-451` qator) — bu fayl endi mavjud emasligini tasdiqlash kerak.
6. **`locale/tr/`** — turkcha tarjima fayllari mavjud, lekin loyiha hujjatlarida (`README.md`,
   `PRODUCT.md`) faqat uz/ru/en tilga oid talab bor. Turkcha qo'llab-quvvatlash rejada
   bormi — noaniq.
7. **`apps/events` ichida ~111 ta oldindan mavjud, kodda ishlatiladigan, lekin
   `locale/uz/LC_MESSAGES/django.po`da umuman yo'q msgid** (masalan "Zoom / Meeting URL",
   "Postponement Reason", "PDF File" va h.k. — bular shifokor funksiyasiga aloqasi yo'q,
   men bu safar faqat o'zim qo'shgan satrlarni to'liq tarjima qildim). Bu — sayt bo'ylab
   to'liq tarjima auditi kerak bo'lgan alohida, kattaroq ish; foydalanuvchi alohida
   so'rasa qo'lga olinadi.
8. **Shifokor "band" bo'lishi hozircha faqat `StaffUnavailability` orqali tekshiriladi**
   — agar shifokor allaqachon boshqa tadbirga ham `attending_doctors` sifatida
   biriktirilgan bo'lsa-yu, lekin band vaqt sifatida belgilamagan bo'lsa, bu
   ziddiyat hozircha aniqlanmaydi. Kerak bo'lsa, `check_doctor_availability()`ga
   `Event.attending_doctors`ni ham tekshiruvchi qo'shimcha so'rov qo'shish mumkin.
9. **`apps/events.Speaker` (Ma'ruzachi) va `Event.attending_doctors` (Ma'ruzachi
   shifokorlar) — ikkita alohida, bog'lanmagan model**. `Speaker` — qo'lda
   kiritiladigan, login qilmaydigan profil (dastur/agenda uchun); shifokor
   `User` hisoblari esa `attending_doctors` orqali. Agar bir xil shifokor ham
   `Speaker` sifatida dastur sahifasida, ham `attending_doctors` sifatida
   bandlik tekshiruvida ko'rinishi kerak bo'lsa — bu ikkisini bog'lash yoki
   birlashtirish alohida so'rov/refaktoring talab qiladi (hozircha so'ralmagan).
10. **`EventType.requires_management_approval` / `allows_emergency_override`
    — "o'lik maydonlar"** (3.16-bandga qarang). Admin/forma/API orqali
    sozlanadi, lekin hech qanday workflow qarori (tasdiqlash, override) ularni
    o'qimaydi — har qanday tadbir turi bir xil qat'iy tasdiqlash yo'lidan
    o'tadi. Agar bu maydonlar amaliy ma'no kasb etishi kerak bo'lsa (masalan,
    ba'zi tadbir turlari tasdiqlashsiz to'g'ridan-to'g'ri PLANNED/APPROVED
    bo'lishi kerak bo'lsa), bu — alohida, foydalanuvchi bilan kelishilishi
    kerak bo'lgan biznes-qoida qarori, chunki hozirgi testlar joriy
    (barcha turlar bir xil) xatti-harakatga tayanadi.

---

## 5. Keyingi qadamlar (ochiq savollar — foydalanuvchidan tasdiq kerak)

- [x] Dashboard/Calendar: o'tish animatsiyalari, uz vaqt bugi, til indikatori, rang
      palitrasi, tarjimalar (2026-09-10 — tafsilot 3.1-bo'limda).
- [ ] Brauzerda vizual ko'rib chiqish kutilmoqda — foydalanuvchi serverni ochib
      natijani tasdiqlaydi, kerak bo'lsa qo'shimcha iteratsiya bo'ladi.
- [ ] Sayt bo'ylab qolgan 52/51/37 bo'sh msgstr (uz/ru/en, dashboard/calendar'ga
      aloqasi yo'q) — alohida so'rov bilan qaraladi.
- [ ] Public dashboard qayta qurilishini yakunlash va test qilish (joriy commit qilinmagan
      o'zgarishlar).
- [ ] `apps/approvals` app'ining kelajagi haqida qaror: to'ldirish, birlashtirish yoki
      olib tashlash.
- [ ] `ALLOWED_HOSTS` xavfsizlik nazarda tutilganini production konfiguratsiyasida
      tasdiqlash.
- [ ] `scripts/` papkasini tozalash/tartibga solish bo'yicha qaror.
- [ ] Har bir yangi funksional so'rov kelganda, ushbu fayl "Amalga oshirilgan ishlar" va
      "Joriy holat" bo'limlarini yangilab borish.

---

## 6. Ishlash tartibi (workflow qoidasi)

1. Har qanday topshiriqni boshlashdan oldin ushbu faylni o'qing.
2. O'zgarish kiritilgach, tegishli bo'limni (3 yoki 5) yangilang — eski holatni o'chirmang,
   balki "bajarildi" deb belgilang yoki ko'chiring.
3. Yangi noaniqlik yoki texnik qarz topilsa — 4-bo'limga qo'shing.
4. Katta arxitekturaviy qarorlar (masalan, app qo'shish/olib tashlash) — avval foydalanuvchi
   bilan tasdiqlanadi, keyin shu faylga yoziladi.
