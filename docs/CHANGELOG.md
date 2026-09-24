# IEMS — Batafsil o'zgarishlar tarixi (Changelog)

> Bu fayl `goals.md`dan ajratilgan **to'liq, batafsil tarixiy jurnal** —
> har bir sessiyada nima qilingani, nega, qanday tekshirilgani haqida
> to'liq yozuv. `goals.md` esa endi faqat **joriy holat va keyingi
> qadamlar**ni qisqa saqlaydi, tezkor o'qish uchun.
>
> Yangi yozuv qo'shish: eng oxiriga (fayl oxiriga), xronologik tartibda,
> mavjud formatga (`### N.NN Sarlavha (sana)`) ergashib qo'shing.

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
o'tkazib yuborilishi kerakmi?), bu esa loyihaning "faqat so'ralganini qil"
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
tizim darajasidagi o'zgarish bo'lgani uchun avtomatik bajarilmadi —
buyruqni administrator huquqi bilan qo'lda ishga tushirish tavsiya etildi.

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

### 3.20 Bajarildi — Loyiha bo'ylab to'liq tarjima auditi (uz/ru/en/tr) (2026-09-12)

Foydalanuvchi: *"Projectning to'liq tarjimasini ko'rib chiq tarjima qilinmagan
joylar bor ekan"*, so'ng aniq ko'lam so'ralganda: *"Hammasini tarjima qil va
ular uz ru en tr tillarida bo'lsinda"*.

**Aniqlangan va tuzatilgan 3 xil muammo**:

1. **487 ta matn butun loyiha bo'ylab (`templates/**/*.html`, `apps/**/*.py`,
   `config/**/*.py`) kamida bitta tildan umuman yo'q edi** — `uz`da 303,
   `ru`da 301, `en`da 399, `tr`da 485 ta yetishmayotgan edi. Chiqarish uchun
   maxsus skript yozildi (Django shablon `{% trans %}`/`{% blocktrans %}` va
   Python `gettext`/`_()` chaqiruvlarini regex bilan aniqlab, escape-belgilarni
   to'g'ri "unescape" qiladigan). Barcha 487 ta matn qo'lda uz/ru/en/tr
   tillariga tarjima qilinib, `.po` fayllarga qo'shildi va `.mo`larga
   kompilyatsiya qilindi. **Natija: barcha 4 tilda 0 ta tarjima qilinmagan
   matn qoldi** (tasdiqlangan — tekshiruv skripti qayta ishga tushirilib).
2. **`uz.po`da 64 ta HTML-entity bilan buzilgan tarjima topildi** — masalan,
   `Step 1: Basic Information` → `1-qadam: Asosiy ma&#39;lumotlar` (haqiqiy
   apostrof o'rniga `&#39;`). Bu qandaydir avvalgi avtomatik import
   bosqichida matn HTML-escape qilinib saqlangani natijasi. Barchasi
   `html.unescape()` orqali tuzatildi.
3. **`tr.po`da 224 ta yozuv butunlay buzilgan edi** — msgstr'da haqiqiy
   tarjima o'rniga tasodifiy "Error 500 (Server Error)!!1500.That's an
   error..." matni saqlanib qolgan (aftidan avvalgi avtomatik tarjima
   pipeline'i xato server javobini "tarjima" sifatida saqlab qo'ygan).
   Bu Playwright orqali login sahifasini turkcha ko'rib tekshirganda vizual
   ravishda aniqlandi ("Xavfsiz kirish" o'rniga xato matni ko'rinib turgan
   edi). Barcha 224 tasi qo'lda haqiqiy turkcha tarjima bilan almashtirildi.
4. **Qo'shimcha, alohida topilgan 2 ta sifat xatosi (`tr.po`)**: `Xush
   kelibsiz` → noto'g'ri "Rica ederim" (bu "Marhamat/Arzimaydi" degani, salom
   emas) va `Parol` → noto'g'ri "Şartlı tahliye" (bu "shartli ozodlik"
   degani!). Ikkalasi ham to'g'ri turkcha ("Hoş geldiniz!", "Şifre") bilan
   almashtirildi. **Diqqat**: bu ikkisi tasodifan Playwright skrinshotida
   ko'zga tashlanib qoldi — `tr.po`da menga qidirilgan aniq naqshlarga
   (`Error 500`, HTML-entity) mos kelmaydigan boshqa shunga o'xshash sifat
   xatolari qolgan bo'lishi ehtimoldan xoli emas (4-bo'limga qarang).

**Yon ta'sir — 3 ta test buzilib, tuzatildi**: yangi haqiqiy tarjimalar
ishlay boshlagach, 3 ta test avvalgi "tarjima yo'qligi tufayli inglizcha
matn ko'rinib turgan" holatga tayanib yozilgan ekan (`test_wizard_step_1_get`,
`test_submit_event_flow`, `test_approve_event_flow`, `test_capacity_warning`)
— assertionlar haqiqiy (endi to'g'ri ishlayotgan) o'zbekcha matnga mos
yangilandi. Shu jarayonda **yana bir haqiqiy, oldindan mavjud bug** topildi:
`test_phase3_workflow.py`dagi ikkita test to'g'ridan-to'g'ri servis
funksiyalarini chaqiradi (request/LocaleMiddleware'siz), va ulardan oldin
ishlaydigan boshqa test (`test_final_acceptance_blockers.py`) `ru` tilini
faollashtirib, uni hech qachon deaktivatsiya qilmaydi — bu holat keyingi
testlarga "sizib o'tadi" (test tartibiga bog'liq, tasodifiy natija). Bu
avval sezilmagan, chunki tarjimalar yo'qligi tufayli natija baribir bir xil
(inglizcha) ko'rinib turgan edi. Tuzatildi: ikkala test endi
`translation.override("uz")` bilan aniq tilni belgilaydi.

**Yakuniy holat**: `pytest tests/` — 341/341, `ruff check` — toza,
`manage.py check` — toza. Server qayta ishga tushirilib, Playwright orqali
login sahifasi 4 tilda (`uz`, `ru`, `en`, `tr`) tekshirildi.

---

### 3.21 Tuzatildi — master-data/venues (Zallar) qidiruv formasi buzilib ko'rinishi (2026-09-14)

Foydalanuvchi: *"master-data/venues ya'ni zallar bo'limida qidirish oynasi
biroz buzilib qolibdi"*. Playwright orqali turli ekran o'lchamlarida
tekshirilib, **ikkita bog'liq, real sabab** topildi:

1. **Asosiy sabab — sidebar butun responsive layout'ni buzgan**:
   `templates/partials/sidebar.html`dagi `<aside>` elementida qattiq yozilgan
   inline `style="position: relative; transition: width 0.3s;"` bor edi.
   Inline style har doim CSS'dan ustun turadi — bu esa `@media
   (max-width: 1024px) { .sidebar { position: fixed; ... } }` qoidasini
   butunlay bekor qilib, planshet/kichikroq oynalarda sidebar'ni ekrandan
   tashqariga (`translateX(-100%)`) yashirilishi kerak bo'lgan joyda oddiy
   oqim elementi sifatida qoldirgan — natijada butun sahifa kontenti
   (qidiruv oynasi ham) yuzlab pikselga pastga surilib, ko'rinmay qolgan.
   `transition: width 0.3s` esa hech qanday amaldagi CSS qoidaga mos
   kelmaydigan "o'lik" kod ekan (`.sidebar-collapsed` uchun `width`
   o'zgartiruvchi CSS umuman yo'q). **Tuzatildi**: inline style butunlay
   olib tashlandi (`position: relative` allaqachon asosiy CSS'da to'g'ri
   belgilangan edi).
2. **Ikkinchi sabab — qidiruv formasi konteyneri**: `static/css/
   components.css`dagi `.command-filter-form` doim to'liq "pill" shaklida
   (`border-radius: 9999px`) edi — bu faqat BIR QATORLI holatda chiroyli
   ko'rinadi. Forma o'zining `.data-toolbar` ota-konteynerida hech qanday
   `flex-grow`ga ega emas edi, shuning uchun mavjud bo'sh joydan
   foydalanmasdan, faqat ichidagi elementlarning minimal kengligigacha
   siqilib qolar edi — bu esa hatto 1280px kengligidagi oynalarda ham
   (agar vertikal scroll-bar sabab bir necha piksel kamayib qolsa) tugma
   keyingi qatorga "sirg'alib tushishi" mumkin edi (beqaror, chegara holati
   bug'i). Tor ekranlarda esa bir necha qatorga bo'linib, to'liq pill radiusi
   butun ko'p qatorli blokka tarqalib, g'alati "shar" shaklini hosil qilardi.
   **Tuzatildi**: `border-radius` → `var(--radius-2xl)` (16px, har qanday
   qator sonida chiroyli ko'rinadi), va `flex: 1 1 auto; min-width: 0;
   max-width: 720px;` qo'shildi — endi forma mavjud bo'sh joydan to'g'ri
   foydalanadi va beqaror qatorlanish yo'qoldi.

**Tekshirildi**: Playwright orqali `master-data/venues/` sahifasi kengliklar
bo'yicha (1280×700 — avval buzuq chegara holati, 900px planshet, 400px
mobil) skrinshot qilindi — barchasida forma endi toza va to'g'ri ko'rinadi.
`pytest tests/` — 341/341, `ruff check` va `manage.py check` — toza. CSS
versiyasi (`components.css?v=31.0`) oshirildi, server qayta ishga tushirildi.

**Eslatma**: bu tuzatish faqat `master_data/filters.html` (venues, event
types, organizations, sponsors — bularning barchasi shu umumiy shablonni
ishlatadi) va butun sidebar'ga tegishli bo'lgani uchun — bu ikkita bug
loyihadagi BARCHA workspace sahifalariga (nafaqat Zallar bo'limiga) ta'sir
qilgan edi, endi hammasida tuzatildi.

---

### 3.22 Bajarildi — Shifokorga "sizni tayinlashdi" bildirishnomasi (in-app + email) va profilda ro'yxat (2026-09-14)

Foydalanuvchi: *"biror uchrashuvga biror shifokorni speaker yoki ma'sul qilib
tayinlasa qanday qilib bilib oladi shifokor"*. Tekshirilganda — bu haqiqiy,
oldindan mavjud bo'shliq ekan: shifokor `attending_doctors` (Ma'ruzachi)
sifatida tayinlanganda hech qanday bildirishnoma (na in-app, na email)
yuborilmagan (faqat workflow status-o'zgarish bildirishnomalari — submit/
approve/reject — mavjud edi). ("Ma'sul" rollarga — `responsible_employee`/
`management_responsible` — shifokorlar 3.12-bandda ataylab chiqarib
tashlangan, shuning uchun bu qism faqat "Ma'ruzachi" tayinlashiga tegishli.)

Foydalanuvchi so'ragan variantlar: (1) in-app bildirishnoma + email,
(2) profil sahifasida hisoblagich + bosilganda ochiladigan ro'yxat.

**Amalga oshirildi**:
- `apps/notifications/services.py::send_notification_email()` — yangi,
  xatoga chidamli (`fail_silently=True`, hech qachon asosiy amalni
  bloklamaydi) email yuboruvchi funksiya. `config/settings/base.py`ga
  `DEFAULT_FROM_EMAIL` (env orqali sozlanadigan, standart
  `noreply@k-one.local`) qo'shildi.
- `apps/events/views.py::notify_assigned_doctors(event, doctors)` — yangi
  tadbir yaratilganda (`wizard.py::finalize_event`) barcha tanlangan
  ma'ruzachi shifokorlarga, tadbir tahrirlanganda (`EventUpdateView.
  form_valid`) esa faqat **yangi qo'shilgan** shifokorlarga (avvalgi va
  yangi `attending_doctors` to'plamlari solishtirilib) in-app + email
  bildirishnoma yuboradi — qayta saqlashda takroriy xabar yubormaydi
  (testda tasdiqlangan).
- `apps/accounts/views.py::DoctorAssignedEventsView` — yangi,
  `/profile/assigned-events/` — faqat `DOCTOR` roli uchun, o'zining
  `attending_events`ini ro'yxat qiladi. **Diqqat**: `events:detail` sahifasi
  `VIEW_MASTER_DATA` huquqini talab qiladi, shifokor esa hech qanday
  capability'ga ega emas — shuning uchun bu alohida, cheklangan ko'rish
  sahifasi qilib qurildi (to'liq ichki boshqaruv sahifasiga kirish huquqi
  BERILMADI — ortiqcha imkoniyat berish xavfsizlik nuqtai nazaridan noto'g'ri
  bo'lardi). Bildirishnomaning `target_url`si ham shu sahifaga yo'naltiriladi
  (`events:detail`ga emas).
- `templates/accounts/profile.html` — "Faoliyat xulosasi"ga faqat
  `user.role == 'doctor'` bo'lsa ko'rinadigan "Ma'ruzachi bo'lgan tadbirlar"
  hisoblagichi (bosilsa ro'yxatga o'tadi) qo'shildi.
- 7 ta yangi matn barcha 4 tilga (uz/ru/en/tr) tarjima qilindi.

**Tekshirildi**: 6 ta yangi test qo'shildi (`tests/test_doctor_registration.py`)
— bildirishnoma+email yaratilishi, qayta tayinlashda takrorlanmasligi,
email yo'q shifokorda ham in-app xabar kelishi, profil hisoblagichi,
ro'yxat sahifasi, va shifokor bo'lmagan foydalanuvchi bu sahifaga 403 bilan
kira olmasligi. `manage.py shell` orqali haqiqiy dev-server sozlamalarida
ham qo'lda tekshirildi — konsolga email chiqdi (mahalliy `EMAIL_BACKEND=
console`), Notification yaratildi. **Yakuniy holat**: `pytest tests/` —
347/347 (avvalgi 341 + yangi 6), `ruff check` va `manage.py check` — toza.

**MUHIM — foydalanuvchi uchun eslatma**: email haqiqatan Gmail'ga borishi
uchun productionda SMTP ma'lumotlari (`EMAIL_HOST`, `EMAIL_HOST_USER`,
`EMAIL_HOST_PASSWORD` — Gmail uchun oddiy parol emas, "ilova paroli"/App
Password kerak, `EMAIL_PORT=587`, `EMAIL_USE_TLS=True`) `.env` fayliga
qo'shilishi kerak — bu kod emas, operatsion sozlash qadami, men buni
o'zim hal qila olmayman (maxfiy ma'lumotlar). Mahalliy rejimda
(`EMAIL_BACKEND=console`) email hozircha faqat server terminaliga
chiqariladi — bu ataylab shunday, dasturchi uchun qulay.

---

### 3.23 Tuzatildi — Shifokor tayinlanganda hech narsa saqlanmagan (asl sabab: "Ctrl bosib tanlash" UX tuzog'i) (2026-09-14)

Foydalanuvchi: *"tadbir yaratib satosylvni biriktirdik keyin satosylv
profiliga kirdim biriktirilgan tadbilarda ham bildirishnomada ham hech
narsa yo'qku"* — 3.22-bandda qurilgan bildirishnoma funksiyasi ishlamayotgan
bo'lib chiqdi. To'g'ridan-to'g'ri bazani tekshirib, keyin Playwright orqali
wizard oqimini qayta o'ynab chuqur tekshirildi.

**Ildiz sabab aniqlandi**: `apps/events/forms.py`dagi `EventStep3Form` va
`EventUpdateForm`dagi `attending_doctors` maydoni oddiy HTML
`<select multiple>` widget'i orqali chizilar edi — bu **bir nechta variantni
tanlash uchun Ctrl (yoki Cmd) bosib turishni talab qiladigan** brauzer
konvensiyasi. Ko'p foydalanuvchi buni bilmaydi va oddiy bosish bilan tanlashga
harakat qiladi — natijada tanlov "yopishib qolmaydi" va forma jo'natilganda
`attending_doctors` bo'sh boradi. Audit jurnali tekshirilganda, foydalanuvchi
tasvirlagan tadbir hech qachon tahrirlanmagan (faqat yaratish+tasdiqlash
harakatlari bor) — demak, muammo aynan yaratish paytida, birinchi
tanlovning o'zida yuz bergan.

**Tuzatildi**: `attending_doctors` maydoni ikkala formada ham
`forms.CheckboxSelectMultiple`ga o'zgartirildi — endi har bir shifokor
alohida checkbox sifatida ko'rinadi, oddiy bitta bosish bilan aniq
belgilanadi/bekor qilinadi, Ctrl talab qilinmaydi. `static/css/
components.css`ga `.checkbox-multiple` uslubi qo'shildi (aylanma chegarali,
scroll qiluvchi ro'yxat ko'rinishi).

**IKKINCHI, TUZATISH DAVOMIDA TOPILGAN BUG**: `EventUpdateForm`ni
tuzatgandan so'ng, tahrirlash sahifasida (`events:edit`) checkbox ro'yxati
**butunlay bo'sh** chiqib qolgani aniqlandi (Playwright orqali chuqur
tekshirilganda — `widget.choices` bo'sh `[]` ekanligi topildi, garchi
`field.queryset` to'g'ri 1 ta yozuvni qaytarsa ham). Sabab — Django'ning
kam ma'lum "tuzog'i": `ModelMultipleChoiceField.queryset`ning setter'i
`widget.choices`ni FAQAT o'sha payt biriktirilgan widget'ga yozadi; agar
keyinroq `field.widget`ga yangi widget obyekti tayinlansa (aynan men
birinchi tuzatishda qilganimdek — avval `queryset`, keyin `widget`),
yangi widget hech qachon `choices` olmaydi va bo'sh checkbox ro'yxati
chiqadi. `EventStep3Form`da bu muammo yo'q edi, chunki u yerda widget
sinf darajasida boshidanoq to'g'ri belgilangan edi (shuning uchun vizard
3-qadamida ishlayotgandek ko'ringan, lekin tahrirlash sahifasida
buzilgan edi). **Tuzatildi**: `EventUpdateForm.__init__`da widget
almashtirish `queryset` tayinlashdan OLDIN qilinadigan qilib
qayta tartiblangan.

**Tekshirildi**: Playwright orqali wizard'ni to'liq boshidan oxirigacha
qayta o'ynab (real brauzer bosishlari bilan) tasdiqlandi — checkbox
belgilanganda `Event.attending_doctors`ga to'g'ri saqlanadi, bildirishnoma
va email yuboriladi. Tahrirlash sahifasida ham checkbox endi to'g'ri
ko'rinadi va belgilangan holda chiqadi (skrinshot bilan tasdiqlangan).
Yangi regression-test qo'shildi
(`test_attending_doctors_checkbox_widget_actually_has_choices`) — bu xato
kelajakda qaytib chiqsa, test darhol ushlab qoladi. `pytest tests/` —
347/347, `ruff check` va `manage.py check` — toza. `components.css?v=32.0`,
server qayta ishga tushirildi.

---

### 3.24 Bajarildi — Bildirishnoma qo'ng'irog'ida qizil belgi + kirganda ko'rinadigan toast xabar (2026-09-14)

Foydalanuvchi: *"bildirishnomalarga kelyapdi lekin bosib ko'rmagunimcha
bilib bo'lmayapdi... birinchi kirganda ko'zga tashlanadigan qilib ber va
5 sekund davomida ko'rinib tursin keyin yangi xabar borligini ham bilinib
tursin qachonki ochib ko'rsa qizil belgicha yo'qolsin"*.

Tekshirilganda — `apps/notifications/services.py::get_unread_count()`
funksiyasi mavjud edi-yu, lekin **hech qayerda ishlatilmagan** (yana bir
"o'lik funksiya" — shu sessiyadagi `checkin_enabled` bug'i bilan bir xil
sinf). Qo'ng'iroq belgisida hech qanday indikator yo'q edi.

**Amalga oshirildi**:
- `apps/notifications/context_processors.py::unread_notifications()` —
  yangi, `unread_notification_count` va `latest_unread_notification`ni
  BARCHA workspace shablonlariga avtomatik uzatadigan context processor
  (`config/settings/base.py`ning `TEMPLATES`ga ro'yxatdan o'tkazildi).
- `templates/partials/topbar.html` — qo'ng'iroq belgisiga qizil
  `.notification-badge` (son bilan, 9 dan ko'p bo'lsa "9+") qo'shildi.
- `templates/base.html` — sahifa yuklanganda ko'rinadigan
  `.notification-toast` (eng so'nggi bildirishnoma sarlavhasi/matni yoki
  umumiy "Sizda N ta o'qilmagan bildirishnoma bor" xabari bilan).
  JavaScript: `sessionStorage` orqali **bitta brauzer sessiyasida faqat bir
  marta** ko'rsatiladi (joriy son uchun) — har sahifa o'tishda emas, faqat
  "birinchi kirganda". 5000ms dan keyin avtomatik yashiriladi.
- `apps/notifications/views.py::NotificationListView.get()` — endi
  ro'yxat sahifasini OCHISHNING O'ZI barcha o'qilmagan bildirishnomalarni
  "o'qilgan" deb belgilaydi (avval faqat har birini alohida bosish yoki
  "hammasini o'qilgan deb belgilash" tugmasi orqali mumkin edi) — bu
  qo'ng'iroqdagi qizil belgini darhol tozalaydi. Sahifa "yangi" ko'rinishini
  yo'qotmasligi uchun (ochilgan payt qaysi yozuvlar o'qilmagan bo'lgani)
  `newly_read_ids` orqali alohida saqlab, shablonda ajratib ko'rsatish
  saqlab qolindi. Endi doim ishlamay qoladigan (`{% if not notif.is_read %}`
  — sahifa ochilgach bu shart hech qachon rost bo'lmaydi) "alohida o'qilgan
  deb belgilash" tugmasi o'lik kod bo'lib qolgani uchun olib tashlandi.

**Tuzatish davomida topilgan 2 ta qo'shimcha bug (toast to'g'ri
yashirilmasdi)**:
1. JS `animationend` hodisasiga tayanardi — headless brauzerlar yoki
   `prefers-reduced-motion` yoqilgan foydalanuvchilarda animatsiya
   ishlamasligi/hodisa otilmasligi mumkin, natijada toast abadiy ekranda
   qolib ketardi. Oddiy `setTimeout` bilan mustahkamlandi.
2. `.notification-toast { display: flex; }` qoidasi brauzerning tabiiy
   `[hidden] { display: none }` xatti-harakatini bekor qilib qo'ygan edi
   (ikkalasi ham bir xil CSS specificity'ga ega, mening qoidam keyinroq
   yuklangani uchun g'olib chiqqan). `.notification-toast[hidden] {
   display: none; }` (yuqoriroq specificity) qo'shib tuzatildi.

**Tekshirildi**: Playwright orqali to'liq sinov — bildirishnoma yaratilib,
toast darhol ko'rinishi, qo'ng'iroqda to'g'ri son ko'rsatilishi, 5.6
soniyadan keyin toast to'liq yo'qolishi (avval yo'qolmasdi — ikkala bug ham
shu jarayonda topilgan), ro'yxat sahifasi ochilgach qo'ng'iroqdagi
belgining yo'qolishi — barchasi skrinshot va dasturiy tekshiruv bilan
tasdiqlandi. Yangi test fayli qo'shildi: `tests/
test_notification_toast_badge.py` (7 ta test — context processor,
badge ko'rinishi/yo'qolishi, ro'yxatni ochish "hammasini o'qilgan"
qilishi, "yangi o'qilgan" ajratib ko'rsatish saqlanishi).

**Yakuniy holat**: `pytest tests/` — 355/355 (avvalgi 348 + yangi 7),
`ruff check` va `manage.py check` — toza. `app.css?v=31.0`, server qayta
ishga tushirildi.

### 3.25 Bajarildi — Profil sahifasi qayta ishlab chiqildi: rasm yuklash, KPI ko'rinishi (2026-09-15/16)

Foydalanuvchi profil sahifasi "oddiy" ko'rinishidan shikoyat qildi. Sabab
aniqlandi: sahifa shablonida ishlatilgan asosiy klasslarning (`profile-layout-3zone`,
`security-item` va h.k.) **hech biri CSS'da umuman yozilmagan edi** — bu shu
sessiya davomida qayta-qayta uchragan tizimli muammoning birinchi ko'rinishi.

- **`User.avatar`** (`ImageField`) qo'shildi — migratsiya `0003_user_avatar`.
  Profil sahifasida rasmga bosib yuklash, JS orqali darhol oldindan ko'rish,
  "Rasmni olib tashlash" katagi. Rasm yo'q bo'lsa — ism bosh harflaridan
  (`User.initials`) rangli doira avtomatik chiqadi. Tepadagi panel (topbar)da
  ham xuddi shu rasm/initials ko'rinadi.
- "Xodim maqomi" va "Superfoydalanuvchi" qatorlari (foydasiz, oddiy
  foydalanuvchiga hech narsa bermaydigan) butunlay olib tashlandi.
- "Faoliyat xulosasi" oddiy matn ro'yxatidan bosh sahifada ishlatiladigan
  `.metric-tile` KPI-plitka komponentiga o'tkazildi (mavjud komponentni
  qayta ishlatish — yangi CSS yozish shart bo'lmadi).
- To'liq CSS yozildi: `profile-layout-3zone`, `identity-zone`,
  `profile-avatar-wrap/-edit-badge`, `security-zone`, `kpi-zone` va h.k.
- **Tekshiruv**: 5 ta yangi test (`tests/test_profile_avatar.py`), Playwright
  orqali to'liq oqim (yuklash→oldindan ko'rish→saqlash→o'chirish) tasdiqlandi.

### 3.26 Bajarildi — "Faoliyat xulosasi" KPI plitkalari haqiqiy tadbirlar ro'yxatiga ulandi (2026-09-15)

Foydalanuvchi: KPI plitkalaridagi sonlar (Biriktirilgan/Boshqaruv/Ma'ruzachi
tadbirlar) ortida haqiqiy ro'yxat bo'lishi kerak, o'tgan va yangi (kelayotgan)
tadbirlar alohida ko'rinsin.

- `apps/accounts/views.py::MyEventsListView` — umumiy bazaviy klass, 3 marta
  meros qilingan: `ResponsibleEventsListView`, `ManagementEventsListView`,
  `DoctorAssignedEventsView` (oxirgisi — eski, faqat shifokorlar uchun bo'lgan
  sahifaning yangi dizaynga o'tkazilgan versiyasi). Har biri tadbirlarni
  **"O'tgan"** (yaqin o'tgandan boshlab) va **"Tez orada"** (yaqin
  kelajakdan boshlab) bo'limlariga ajratib ko'rsatadi, `workspace-event-row`
  komponenti bilan (sana/vaqt/zal/holat belgisi).
- Yangi shablon: `templates/accounts/event_relation_list.html` (uchalasi
  uchun umumiy, eski `assigned_events.html` o'chirildi).
- Yangi URL'lar: `responsible-events`, `management-events` (`doctor-assigned-events`
  saqlanib qoldi, endi shu umumiy bazaga asoslanadi).
- **Tekshiruv**: `tests/test_profile_event_lists.py` (8 test), jami 368 test.

### 3.27 Bajarildi — Profil sahifasida "Yaqinlashayotgan biriktirilgan uchrashuvlar" (2026-09-15/16)

Foydalanuvchi aniqlashtirdi: 3.26-banddagi alohida sahifalar yaxshi, lekin
profil sahifasining o'zida — uchta box (Shaxsiy/Hisob/KPI)dan **pastda**,
bo'sh joyda — faqat foydalanuvchiga **har qanday tarzda biriktirilgan**
(mas'ul xodim, boshqaruv mas'uli YOKI ma'ruzachi shifokor) **yangi/kelayotgan**
tadbirlar ro'yxati chiqishi kerak edi.

- `ProfileView.get_context_data()`ga `upcoming_assigned_events` qo'shildi —
  `Q(responsible_employee=user) | Q(management_responsible=user) |
  Q(attending_doctors=user)` orqali uchala turdagi biriktirishni birlashtirib,
  faqat kelajakdagilarini ko'rsatadi. Boshida faqat `responsible_employee`
  tekshirilgan edi — foydalanuvchi haqiqiy holatda sinab ko'rib
  ("men admindan yaratdim, shifokorni ma'ruzachi qilib biriktirdim, nega
  shifokor profilida ko'rinmayapti?") aniqladi, keyin kengaytirildi.
- **Tekshiruv**: 4 ta yangi test, jami 370 test.

### 3.28 Tuzatildi — 5 bosqichli tadbir yaratish wizardi: dizayn + 2 ta haqiqiy bug (2026-09-16)

Eng katta tuzatish shu sessiyada. Ikkita **funksional** bug topildi (dizayndan
ham muhimroq edi):

1. **Soxta "to'ldirilishi shart" xatolari**: `apps/events/wizard.py::get()`
   har bir bosqich formasini SESSIYADAGI OLDINGI bosqichlar ma'lumoti bilan
   `data=` (bog'langan/bound) qilib qurar edi — hatto joriy bosqichning o'z
   maydonlari bo'sh bo'lsa ham forma "bog'langan" hisoblanib, DARHOL barcha
   majburiy maydonlar uchun xato ko'rsatardi, foydalanuvchi hali hech narsa
   kiritmasidan oldin. Tuzatish: `get_step_forms()` endi `initial=` orqali
   oldindan to'ldiradi (`data=` faqat haqiqiy POST validatsiyasida ishlatiladi).
2. **"Orqaga" tugmasi bosilmasdi**: u ham `type="submit"` edi, brauzerning
   HTML5 validatsiyasi joriy bosqichda bo'sh majburiy maydon bo'lsa TUGMANI
   BOSISHGA HAM to'sqinlik qilardi. Har bir "Orqaga" tugmasiga
   `formnovalidate` qo'shildi.

**Dizayn tuzatishlari** (xuddi profil sahifasidagi kabi — CSS klasslari
yozilmagan edi): bosqichlar ko'rsatkichi (`is-active`/`is-complete` ↔ CSS'da
`.active`/`.completed` nomuvofiqligi), `<form class="data-form wizard-form">`
ikkita grid-klassni bir vaqtda tashib yurgani (sarlavha/xato/tugmalarni ham
tasodifiy grid katakchalariga sochib yuborishi mumkin edi — `data-form`
olib tashlandi), `.wizard-form`, `.form-alert`, `.availability-card/-indicator`,
`.capacity-warning-box`, `.review-summary-card/.summary-grid` — hammasi
yozildi. Sana/vaqt inputlari (`<input type="date/time">`) BUTUN SAYT
bo'ylab asosiy CSS qoidasiga umuman kiritilmagan ekan (faqat rang, chegara/
balandlik/burchak yo'q) — bu global tuzatildi (`components.css`), shu bilan
boshqa joylardagi shunga o'xshash "xunuk" sana/vaqt maydonlari ham avtomatik
tuzaldi. 4-bosqichdagi (Tashkilotlar/Homiylar) noqulay ko'p-tanlov ro'yxati
checkbox ro'yxatiga almashtirildi (3-bosqichdagi shifokorlar bilan bir xil
yechim). Bonusda: "Qatnashuvchilar" so'zi o'zbekchada butunlay buzilgan
tarjima bilan chiqayotgan edi (`"& Qatnashuvchilar@ info: whatsthis"`) — tuzatildi.

**Tekshiruv**: jami 370 test (2 ta yangi regressiya testi soxta-xato bugi
uchun), Playwright orqali 5 bosqichning barchasi to'liq sinovdan o'tkazildi.

### 3.29 Bajarildi — Shifokorning band vaqtini o'chirish faqat administratorga (2026-09-16)

Foydalanuvchi: shifokor o'zi belgilagan band vaqtni o'zi o'chira olar edi —
bu tizimni chetlab o'tish imkonini berardi (band deb belgilab, tekshiruvdan
oldin o'chirib qo'yish). So'rov: o'chirish tugmasini olib tashlash, faqat
administrator o'chira/qo'sha olsin.

- Shifokorning o'z sahifasidan (`/profile/availability/`) o'chirish tugmasi
  **va orqa tomondagi ruxsat ham** olib tashlandi (faqat tugmani yashirish
  emas — `AvailabilityDeleteView` butunlay o'chirildi, to'g'ridan-to'g'ri
  so'rov yuborib ham o'chira olmaydi).
- Yangi: `AdminDoctorAvailabilityView` + `AdminAvailabilityDeleteView`
  (`Capability.MANAGE_USERS` bilan himoyalangan) — `/users/<pk>/availability/`.
  `/users/` sahifasida har bir shifokor qatoriga "Band vaqtlari" havolasi
  qo'shildi. Administrator qo'shgan yangi band vaqtga **yillik 4 talik
  cheklov qo'llanilmaydi** (o'zi ataylab qo'shayotgani uchun).
- Shifokorning o'zi band vaqt **qo'shish** huquqi saqlanib qoldi — faqat
  o'chirish administratorga o'tkazildi.
- **Tekshiruv**: eski "o'chirish orqali kvota bo'shatish" testlari yangi
  xatti-harakatga moslab qayta yozildi, jami 373 test.

### 3.30 Bajarildi — Loyiha bo'ylab qo'shimcha dizayn auditi (2026-09-16)

Foydalanuvchi so'rovi bo'yicha ("boshqa yaxshilash kerak bo'lgan joylar
bormi?") fon-agent orqali butun loyiha CSS-klass qamrovi tekshirildi.
Ko'pgina sahifalar (bosh sahifa, ochiq/public sahifalar, rahbariyat paneli,
TV devor ekrani, bildirishnomalar) aslida yaxshi holatda ekani aniqlandi —
avtomatik audit signal bergan bo'lsa ham, qo'lda skrinshot orqali tekshirilib,
ko'pi yolg'on signal ekani (JS orqali render qilinadigan qism, boshqa klass
nomi bilan allaqachon ishlagan) aniqlandi. Haqiqiy topilmalar:

- **`venues/live_status.html`** (`/master-data/venues/live-status/`) —
  haqiqatan ham CHIROYSIZ edi: hech qanday kartochka, faqat matn oqimi
  (`status-card`, `venue-code-badge`, `live-indicator` va h.k. — hech biri
  CSS'da yo'q edi). To'liq qayta qurildi — rangli chap-chegarali kartochkalar.
- **`publications/form.html`** (nashr tayyorlash) — `{{ form.as_p }}` orqali
  chizilar edi, bu APP'NING BUTUN DIZAYN TIZIMINI CHETLAB O'TARDI: natijada
  forma maydonlari **inglizcha, tarjima qilinmagan** holda chiqardi
  ("Platform:", "Include qr:" va h.k. — `Publication` modelida `verbose_name`
  berilmagani uchun Django avtomatik, tarjimasiz label yaratgan edi).
  `PublicationForm.Meta.labels` qo'shildi (uz/ru/en tarjima bilan), shablon
  standart `form-grid`/`form-field` naqshiga o'tkazildi, o'ng tomondagi
  "Platforma ko'rinishi" paneli uchun CSS yozildi.
- **`publications/list.html`** — yuqoridagi son ko'rsatkichlari (Qoralama/
  Tayyor/...) oddiy matn qatorlari edi — KPI-plitka ko'rinishiga o'tkazildi.
- **`workspace/home.html`** — "Yaqinlashayotgan tadbirlar" ro'yxatidagi holat
  belgisi (`status-pill status-{{status}}`) CSS'da yo'q edi — allaqachon
  mavjud, yaxshi ishlaydigan `status-badge` komponentiga almashtirildi.
- **Public dashboard**: "Zallar Faolligi"/"Haftalik Faollik" vidjetlarining
  yuklanish skeleti (`.widget-loading`, uch nuqta) CSS'siz — ma'lumot
  kelmaguncha butunlay ko'rinmas edi. Kichik pulsatsiya animatsiyasi qo'shildi.

**Tekshiruv**: 373 test o'zgarishsiz o'tdi (yangi test qo'shilmadi — faqat
CSS/shablon/forma o'zgarishlari), har bir sahifa Playwright orqali skrinshotda
tasdiqlandi.

### 3.31 Tuzatildi — Public dashboard "HOZIR" chizig'i va "Zallar/Haftalik" vidjetlari (2026-09-16)

Foydalanuvchi: bosh sahifadagi joriy vaqtni ko'rsatuvchi chiziq sahifa
ochilganda **noto'g'ri joyda** turadi, faqat biroz vaqtdan keyin to'g'rilanadi;
boshqa sahifaga o'tib qaytib kelsa yana xato ko'rinadi. "Zallar Faolligi" va
"Haftalik Faollik" vidjetlari ham umuman ko'rsatmay qoldi.

**Ildiz sabab 1 (haqiqiy bug)**: `static/js/public-dashboard.js`da
`updateRealtimeTimeline()` (HOZIR chizig'ini joylashtiruvchi funksiya) FAQAT
`renderTimeline()` ichida chaqirilardi — bu esa serverdan `/api/public/dashboard/`
javobi kelgandan KEYIN ishga tushardi. Sahifa yuklangan zahoti (tarmoq
javobidan oldin) chiziq CSS default holatida — chap chetda (08:00 belgisida)
turardi. Agar bugun tadbir bo'lmasa, funksiya UMUMAN chaqirilmasdi (erta
`return`). Tuzatish: `updateRealtimeTimeline()` endi skript yuklangan zahoti,
tarmoq so'rovidan mustaqil ravishda, DARHOL chaqiriladi.

**Ildiz sabab 2 (haqiqiy bug — vidjetlar ko'rinmay qolishi)**: server
loglarini tekshirganda `/api/public/dashboard/` **429 (Too Many Requests)**
qaytarayotgani aniqlandi — sabab: shu sessiya davomida qilingan ko'plab
Playwright avtomatik tekshiruvlari (`config/rate_limit.py`, IP bo'yicha,
180 so'rov/60 soniya) chegarani to'ldirib qo'ygan edi (haqiqiy son: 309).
Bundan tashqari, `refresh()` funksiyasi `!res.ok` holatida **jim** qaytib
ketardi (na konsolga yozuv, na qayta urinish) — shuning uchun vaqtinchalik
429 xatosi ham vidjetlarni ABADIY bo'sh holatda qoldirishi mumkin edi.
Bitta umumiy ofis IP orti(dagi bir nechta ekran/kiosk)dan foydalanishda ham
xuddi shu muammo real hayotda takrorlanishi mumkin edi.

- `apps/reporting/views.py`: `public-dashboard` va `public-venues`
  cheklovlari 180/60'dan **600/60**ga oshirildi (bu — autentifikatsiyasiz,
  faqat o'qish uchun ochiq endpoint, xavfsizlik nuqtai nazaridan xatarsiz).
- `public-dashboard.js::refresh()`: endi 429 kelsa `console.warn` bilan
  ogohlantiradi va 5 soniyadan keyin bitta qo'shimcha urinish qiladi
  (10 soniyalik navbatdagi davrni kutib o'tirmasdan).

**Tekshiruv**: `manage.py check`, 373 test o'tdi, Redis keshida haqiqiy
hisoblagich (`309`) to'g'ridan-to'g'ri tekshirilib sabab tasdiqlandi, yangi
limit ostida `/api/public/dashboard/` 200 qaytarishi va HOZIR chizig'i
sahifa yuklangan zahoti to'g'ri joyda turishi Playwright skrinshotida
tasdiqlandi.

**Eslatma**: shu sessiya davomida (3.25–3.31) `goals.md` **vaqtida
yangilanmagan** — foydalanuvchi to'g'ridan-to'g'ri so'ragandan keyin bir
yo'la, orqaga qarab yozildi. Keyingi safar har bir muhim o'zgarishdan so'ng
darhol yangilash kerak (6-bo'limdagi qoidaga muvofiq).

---

### 3.32 Tuzatildi — Ma'ruzachilar sidebar bug'i, taqvim CSS/iconkalar, "Band shifokorlar" bo'limi (2026-09-16/17)

Foydalanuvchi 4 ta narsani xabar qildi: (1) "Ma'ruzachilar"ni bosganda
sidebar'da "Tadbirlar" yoritilib qolyapti, (2) taqvimda CSS/iconka
muammolari bor, (3) public dashboard'ga "Band shifokorlar" (rahbariyat
uchun, qaysi shifokor qatnasha olmasligi va sababi) bo'limi kerak, (4) avval
tuzatilgan "HOZIR" chizig'i baribir sekin yangilanyapti.

- **`apps/events/views.py`**: `SpeakerListView.get_context_data()`da
  `context["nav_key"] = "events"` qattiq yozilgan edi — `"speakers"`ga
  tuzatildi; `SpeakerCreateView`/`SpeakerUpdateView`ga ham `nav_key="speakers"`
  qo'shildi. Regressiya testi: `tests/test_final_acceptance_blockers.py::
  test_speaker_pages_highlight_the_speakers_sidebar_item_not_events`.
- **Yangi `apps/reporting/views.py::PublicBusyDoctorsView`** +
  **`templates/public/busy_doctors.html`** + **`config/urls.py`**
  (`doctors/busy/` → `public-busy-doctors`): "hozir band", "bugun band",
  "bu hafta band" KPI kartalari va har bir band shifokor uchun sabab/vaqt
  oralig'i ko'rsatiladigan kartochkalar. `templates/public/base.html`ga
  navigatsiyaga 4-tugma qo'shildi. Testlar: `tests/test_public_busy_doctors.py`
  (5 ta test).
- **Taqvim CSS/lokal nomlash** (`templates/events/calendar.html`): FullCalendar
  o'zining "uz" lokali oy/hafta kun nomlarini umuman bermaydi — bu holat
  ICU fallback orqali buzuq sarlavha ("2026 M09") va inglizcha kun
  nomlarini keltirib chiqargan edi. Endi o'z `MONTH_NAMES`/`WEEKDAY_SHORT`
  massivlari va `formatCalendarTitle()`/`dayHeaderContent` orqali qo'lda
  formatlanadi. Shuningdek, `fullcalendar` meta-paketida alohida CSS fayli
  yo'qligi va `locales-all` to'plami mavjud emasligi (jsdelivr API orqali
  tasdiqlandi) sababli noto'g'ri `<link>`/`<script>` manzillari to'g'irlandi.
- **`static/css/public.css`**: 4 ta segmentli nav uchun `nav-indicator`
  matematikasi (`width: calc(25% - 6px)`, `translateX` 4 ta `nth-child`
  qoidasi) 3 tadan 4 tagacha yangilandi.

**Tekshiruv**: `manage.py check`, 378/379 test o'tdi (1 ta bu ishga
aloqasi yo'q), Playwright skrinshotlari orqali barcha 4 band tasdiqlandi.

---

### 3.33 Tuzatildi — Band shifokorlar nav pill, taqvim strelka iconkasi, filtr paneli (2026-09-17)

3.32'dan keyin foydalanuvchi yana uchta kosmetik muammoni topdi: (1) "Band
shifokorlar" tanlanganda ko'k pill icon+matnni to'liq o'rab olmayapti —
icon pill chap chetidan tashqarida "yopishib" qolayapti, (2) taqvimdagi
oldinga/orqaga tugmalar iconkasi tўртburchak (kvadrat) bo'lib ko'rinyapti,
(3) taqvimning filtr paneli (Zal/Turi/Xolat) ikki qatorga bo'linib,
"biroz xunuk" ko'rinyapti.

**Ildiz sabablari va tuzatishlar:**

1. **Nav pill "yopishib qolish"** — `.premium-segment-btn`da `white-space:
   nowrap` yo'q edi, shuning uchun eng uzun yorliq ("Band shifokorlar")
   ikki qatorga bukilib, icon pill tashqarisida qolib ketardi (nav
   `max-width:580px`ni 4 ta teng segmentga bo'lganda har biriga atigi
   ~138px tegardi). `static/css/public.css`: nav `max-width` 580px→720px,
   `.premium-segment-btn`ga `white-space: nowrap` va `padding: 0 10px`
   qo'shildi — endi barcha 4 ta tugma bir qatorda, pill icon+matnni
   to'liq qamrab oladi (Playwright orqali tasdiqlandi: barcha tugmalar
   balandligi bir xil 42px, indikator koordinatasi faol tugma bilan
   aniq mos keladi).
2. **Taqvim strelka iconkasi kvadrat bo'lib ko'rinishi — asl sabab CSS
   sintaksis xatosi edi, faqat kosmetika emas**: `static/css/calendar.css`
   ichida `@media (max-width: 768px) { ... }` bloki (573-qator atrofida)
   yopilmagan holda qolgan edi (yo'qolgan `}`), shuning uchun undan keyin
   kelgan **butun "FullCalendar Enterprise Styling" bo'limi (`.fc`,
   `.fc-toolbar`, `.fc-button-group`, `.fc-icon` va h.k., ~430 qator)**
   tasodifan faqat `max-width:768px` (mobil) ostida joylashib qolgan va
   desktop'da HECH QACHON qo'llanilmagan edi — shuning uchun brauzer
   FullCalendar'ning o'z ichki icon-font uslubini (`font-size:1.5em`,
   `content:""`) ishlatgan, u esa CSP tomonidan bloklangan `data:`
   shrift URL'ga tayanib bo'sh kvadrat sifatida ko'ringan. Fayl oxirida
   (1083–1088-qatorlar) yana bitta buzuq joy topildi: ikkita ustma-ust
   ochilgan, yopilmagan `@media` bloki (`min-width:769px` va
   `max-width:768px`) — bu esa butun faylning qolgan qismini (hattoki
   `.tippy-box` va boshqa keyingi qoidalarni) brauzer CSSOM'ida noto'g'ri
   guruhlagan (jami muvozanatsizlik: 3 ta ortiqcha ochilgan qavs, sinov
   skripti bilan tasdiqlandi). Ikkala joy ham tuzatildi: yo'qolgan `}`
   qo'shildi va ortiqcha ikkita `@media` ochuvchi qatori olib tashlandi
   (`.calendar-filters.premium-filters` — bu `templates/public/calendar.html`
   uchun ishlatiladigan, boshqa mustaqil komponent — o'zgarishsiz qoldi,
   faqat noto'g'ri joylashgan qavslari tuzatildi). Shundan keyin
   `.fc .fc-icon`dagi avvalgi tuzatish (font-size:0, chevron belgi
   `::before` orqali) nihoyat haqiqatan qo'llanila boshladi. Bonus fix:
   o'sha qoidada `width/height: 1em` `font-size:0` bilan birga 0px'ga
   aylanib, iconning o'zi va uning `::before`si (`inset:0`) yig'ilib
   ketayotgan edi — `16px`ga o'zgartirildi.
3. **Filtr paneli ikki qatorga bo'linishi** — `.command-filter-form`
   (`static/css/components.css`) barcha ro'yxat sahifalari uchun umumiy
   `max-width:720px` bilan cheklangan (odatda 1-2 ta dropdown uchun
   yetarli). Taqvim sahifasida 3 ta dropdown + 2 ta tugma bor, ularning
   umumiy kengligi 720px'dan oshib, qatorga sig'maganda ikkinchi qatorga
   tushib ketardi. `templates/events/calendar.html`ga sahifaga xos
   `.calendar-toolbar-row .command-filter-form { max-width: none; }`
   qo'shildi — endi to'liq mavjud kenglikni egallab, bitta qatorda tekis
   joylashadi.

**Tekshiruv**: brauzer CSSOM darajasida qavslar muvozanati dasturiy
tekshirildi (`{` va `}` soni endi teng — avval 201 vs 198, endi 201 vs
201), Playwright orqali barcha uchala tuzatish live serverda skrinshot va
`getBoundingClientRect`/`getComputedStyle` bilan tasdiqlandi (icon endi
16×16px, `content: "‹"`; filtr paneli balandligi 104px→58px, bitta
qatorda; nav indikatori koordinatasi faol tugma bilan aniq mos keladi),
`manage.py check` toza, to'liq test to'plami (379 test) o'tdi. Dasturiy
test qo'shilmadi — bu sof CSS/vizual tuzatish, mavjud
`test_public_busy_doctors.py` va boshqa view-darajasidagi testlar
o'zgarishsiz o'tadi.

---

### 3.34 Bajarildi — To'liq loyiha auditi va topilgan kamchiliklarni tuzatish (2026-09-17)

Foydalanuvchi loyihani topshirishdan oldin "ipidan ignasigacha" to'liq audit
so'radi — bog'liqliklar, sozlamalar, migratsiyalar, testlar, statik fayllar,
tarjimalar, xavfsizlik va repo tozaligi. Audit natijasida topilgan va
tuzatilgan narsalar:

1. **Turkcha tarjimada 8 ta yangi satr yo'q edi** (3.32'da qo'shilgan "Band
   shifokorlar" sahifasi uchun) — bu shu sessiyaning o'z regressiyasi edi.
   `locale/tr/LC_MESSAGES/django.po`ga ru/en tarjimalaridan aniq ma'no olib
   8 ta yozuv qo'shildi, barcha 4 tilning `.mo` fayllari qayta kompilyatsiya
   qilindi (`polib` orqali, gettext vositalari bu Windows muhitida yo'q).
2. **`.has-error` klassi hech qayerda stillanmagan edi** — wizard 1-5
   qadam, event tahrirlash, nashr formasi, master-data formalarida xato
   maydon `has-error` klassini olardi, lekin chegarasi vizual jihatdan
   o'zgarmasdi (faqat pastdagi qizil matn ko'rinardi).
   `static/css/components.css`ga `.form-field.has-error input/select/
   textarea` va `.form-group.has-error ...` uchun qizil chegara + soya
   qo'shildi. Test: `client.post` orqali bo'sh formani yuborib, javobda
   `has-error` klassi borligi va CSS qoidasi mos kelishi tasdiqlandi.
3. **Yangi "Band shifokorlar" sahifasida `Cache-Control: no-store` yo'q
   edi** — shifokorning shaxsiy sababi umumiy/kiosk kompyuterda keshda
   qolishi mumkin edi. `config/middleware.py::
   ProductionSecurityHeadersMiddleware`dagi maxfiy-sahifalar ro'yxatiga
   `/doctors/busy/` va `/api/public/` prefikslari qo'shildi. Playwright
   orqali ikkalasi ham endi `private, no-store, max-age=0` qaytarishi
   tasdiqlandi.
4. **`requirements/base.txt`da `psycopg[binary]` versiyasiz edi** —
   reproducibility uchun xavfli (build vaqtida boshqa versiya kelishi
   mumkin). O'rnatilgan haqiqiy versiyaga (`3.3.5`) mahkamlandi.
5. **Repo tozaligi**: `scratch_py_missing.json` (39KB, eski tarjima-audit
   debug-artefakti) butunlay o'chirildi; `qa_screenshots/` (18MB, 66 ta
   tarixiy QA skrinshot) git kuzatuvidan chiqarildi (`git rm --cached`) —
   fayllar diskda qoladi, lekin endi commit qilinmaydi. Ikkalasi ham
   `.gitignore`ga qo'shildi. Bir nechta 0-baytli tasodifiy fayl (`3.13`,
   `button` va h.k. — terminal buyruqlaridan qolgan xato) ham tozalandi.

**Audit davomida tasdiqlangan, MUAMMO TOPILMAGAN sohalar**: Python/JS
sintaksis (barcha fayl), Django `check`, migratsiyalar (yetishmayotgan/
qo'llanilmagan yo'q), to'liq test to'plami (379/379), CSS qavslar balansi
(barcha 13 fayl), shablonlardagi barcha `{% static %}` va `{% url %}`
havolalari (110 ta nom — hammasi ro'yxatdan o'tgan), xavfsizlik naqshlari
(`|safe`, `mark_safe`, xom SQL, `eval`/`exec`/`pickle`, `csrf_exempt` —
birortasi yo'q), fayl yuklash validatsiyasi (kengaytma+hajm+content-type+
magic-byte+PIL dekod), CSP sarlavhasi, `pip check`, tarjima bo'sh/fuzzy
yozuvlar. Django 5.2.16 va Pillow 12.3.0 — ikkalasi ham veb-qidiruv orqali
tasdiqlangan eng so'nggi xavfsizlik-tuzatilgan versiyalar.

**Ochiq qoldirilgan (foydalanuvchi qarori kerak, kod o'zgarishi emas)**:
`en.po`da 95 ta, `tr.po`da qolgan ~125 ta (yangi 8 tadan tashqari)
o'zbekcha/inglizcha manba-satr tarjima qilinmagan — bular eski, oldindan
mavjud fazalardan qolgan, katta hajmli va sifatli tarjimon ishi talab
qiladigan alohida vazifa (`goals.md` 4-bo'lim, band 7ga qarang);
`scripts/` papkasidagi 188 ta bir martalik skript arxivlash masalasi
hamon ochiq.

**Tekshiruv**: `manage.py check` toza, to'liq test to'plami (379 test)
o'tdi, Playwright orqali `.has-error` va `Cache-Control` tuzatishlari
jonli serverda tasdiqlandi, `pip check` ziddiyatsiz.

---

### 3.35 Bajarildi — Telefon va email maydonlariga qat'iy validatsiya (2026-09-20)

Foydalanuvchi: "Registratsiya oynasidagi kataloglarda xatolik bor... raqam
kiritish oynasida faqat raqam kiritishi kerak... huddi shunday gmail
kiritish oynasida ham va boshqalarida ham." Tekshiruv shuni ko'rsatdi:
telefon maydoni (`DoctorProfile.phone`, `Organization.phone`,
`Sponsor.phone`) oddiy matn maydoni edi — hech qanday format tekshiruvi
yo'q, foydalanuvchi harflar yozsa ham qabul qilinardi. Email maydonlari
(`EmailField`) server tomonda allaqachon to'g'ri tekshirilardi, lekin
registratsiya sahifasida xato maydon vizual ajratilmasdi.

- **`config/validators.py::validate_phone_number`** — yangi validator:
  faqat raqam, bo'shliq, `+ - ( )` belgilariga ruxsat beradi va
  raqamlar soni 9–15 oralig'ida bo'lishini tekshiradi.
  `DoctorProfile.phone`, `Organization.phone`, `Sponsor.phone` model
  maydonlariga qo'shildi (migratsiyalar yaratildi:
  `accounts/0004_alter_doctorprofile_phone`,
  `organizations/0002_alter_organization_phone_alter_sponsor_phone`) va
  `DoctorRegistrationForm.phone`ga ham qo'lda qo'shildi (bu forma maydoni
  modeldan avtomatik chiqarilmagani uchun).
- **Telefon inputlari** endi `type="tel"` va `inputmode="tel"` (mobil
  qurilmada raqamli klaviatura chiqadi) — registratsiya formasi,
  Tashkilot/Homiy formalari.
- **`static/js/app.js`**: barcha `input[type="tel"]` uchun umumiy JS —
  yozish jarayonida ruxsat etilmagan belgilar (harflar) darhol olib
  tashlanadi.
- **`templates/registration/register.html`**: maydon o'rovchisiga
  `{% if field.errors %} has-error{% endif %}` qo'shildi — avval xato
  maydon hech qanday vizual belgi olmasdi (faqat pastdagi qizil matn).
  **`static/css/login.css`**: `.auth-field.has-error .auth-input` uchun
  qizil chegara qoidasi qo'shildi (3.34-bo'limdagi `.form-field.has-error`
  qoidasiga o'xshash, lekin auth-sahifalar boshqa CSS-klasslardan
  foydalangani uchun alohida qo'shildi).
- Ikkita yangi validator xabari (`Enter a valid phone number...`,
  `Phone number must contain between 9 and 15 digits.`) barcha 4 tilga
  (uz/ru/en/tr) tarjima qilindi.
- **Testlar**: `tests/test_doctor_registration.py`ga 3 ta yangi test
  qo'shildi — harfli telefon rad etiladi, juda qisqa telefon rad etiladi,
  noto'g'ri email rad etiladi.

**Tekshiruv**: `manage.py check` toza, to'liq test to'plami (382 test,
+3 yangi) o'tdi, Playwright orqali jonli serverda: telefon maydoniga
harf yozish darhol tozalanishi, noto'g'ri email/telefon bilan yuborilgan
forma har ikkala maydonni qizil chegara bilan ajratishi va tarjima
qilingan xabar ko'rsatishi tasdiqlandi (skrinshot orqali vizual
tekshirildi).

---

### 3.36 Bajarildi — Ro'yxatdan o'tgach nima bo'lganini aniq ko'rsatuvchi sahifa (2026-09-21)

Foydalanuvchi: "kimdir registratsiya qilganda hisobingiz tasdiqlanishi
uchun adminga yuborildi degan bildirishnoma chiqsin, odamlar nima
bo'layotganini bilmay qolayapdi." Tekshiruv shuni ko'rsatdi: bu — dizayn
kamchiligi emas, **haqiqiy bug** edi. `DoctorRegisterView.form_valid()`
`messages.success(...)` orqali xabar qo'yardi va `login` sahifasiga
yo'naltirardi, lekin `templates/base.html`da `{% if messages %}` bloki
FAQAT `{% if user.is_authenticated %}` shoxobchasi ICHIDA joylashgan edi
(84-90 qatorlar) — login/register kabi autentifikatsiyasiz sahifalar esa
`{% else %}` shoxobchasidagi `unauthenticated_content` blokidan
foydalanadi, u yerda xabarlar umuman chiqarilmasdi. Natijada
ro'yxatdan o'tgan har bir kishi "ariza ketdimi, yo'qmi" bilmay
qolardi — xabar navbatda session'da qolib, hech qachon ko'rinmasdi.

Oddiy tuzatish (`{% if messages %}`ni `{% else %}` shoxobchasiga ham
qo'shish) o'rniga, foydalanuvchi taklifiga ko'ra ("o'zing ham fantaziya
qilsang bo'ladi") **alohida, chalg'itmaydigan tasdiqlash sahifasi**
yaratildi:

- **`apps/accounts/views.py::RegistrationSubmittedView`** — yangi
  `TemplateView`. `DoctorRegisterView.success_url` endi `login` emas,
  balki shu yangi `register-submitted` nomli URLga yo'naltiradi.
  `form_valid()` endi `messages.success` o'rniga
  `request.session["just_registered_username"]`ga foydalanuvchi nomini
  yozadi (bir martalik, `get_context_data`da `.pop()` bilan o'qiladi).
- **`templates/registration/register_submitted.html`** — login/register
  sahifalari bilan bir xil vizual uslubda (brand panel + form panel),
  animatsiyali yashil ✓ belgisi, foydalanuvchi nomi bilan shaxsiylashtir-
  ilgan sarlavha va 3 bosqichli aniq tushuntirish: (1) Ariza yuborildi
  ✓ — bajarilgan, (2) Administrator ko'rib chiqmoqda, (3) Tizimga
  kirasiz — hisobingiz faollashtirilgach. Pastda "Tizimga kirish
  sahifasiga qaytish" tugmasi.
- **`config/urls.py`**: `accounts/register/submitted/` →
  `register-submitted`.
- Barcha yangi matnlar 4 tilga (uz/ru/en/tr) tarjima qilindi.
- **Testlar**: `tests/test_doctor_registration.py`ga 3 ta yangi test —
  muvaffaqiyatli ro'yxatdan o'tish shu sahifaga yo'naltirishi va
  foydalanuvchi nomini ko'rsatishi, sessiyasiz ham sahifa ishlashi,
  autentifikatsiyadan o'tgan foydalanuvchi dashboardga qaytarilishi.

**Tekshiruv**: `manage.py check` toza, to'liq test to'plami (385 test,
+3 yangi) o'tdi, Playwright orqali to'liq ro'yxatdan o'tish oqimi
boshidan oxirigacha sinovdan o'tkazildi va skrinshot bilan tasdiqlandi
(foydalanuvchi nomi bilan va sessiyasiz ikkala holat ham).

---

### 3.37 Bajarildi — Tasdiqlanmagan hisob bilan kirishga urinilganda aniq xabar (2026-09-21)

Foydalanuvchi: "login oynasiga qaytib arizasi hali tasdiqlanmagan login
parol terilsa arizangiz administrator tomonidan ko'rib chiqilmoqda deb
chiqsin." Tekshiruv shuni ko'rsatdi: Django standart xatti-harakati
bo'yicha to'g'ri login/parol kiritilgan, lekin hali faollashtirilmagan
(`is_active=False`) hisob uchun ham xuddi noto'g'ri parol kiritilgandagi
kabi **umumiy** "Login yoki parol noto'g'ri" xabari chiqadi — chunki
`authenticate()` faollashtirilmagan foydalanuvchini "topilmadi" deb
hisoblaydi, farqlamaydi.

**Bonus topilma**: `templates/registration/login.html`da xato xabari
QATTIQ KODLANGAN edi (`{% if form.non_field_errors %}` shart sifatida
ishlatilgan, lekin ICHIDA statik matn chiqarilardi, forma xatosining
HAQIQIY matni emas) — bu bug bo'lmasa ham, yangi xabarlarni chiqarish
UCHUN birinchi navbatda tuzatilishi shart edi.

- **`templates/registration/login.html`**: `{{ form.non_field_errors|join:" " }}`
  ga o'zgartirildi — endi haqiqiy xato matni ko'rsatiladi (avval statik
  matn qattiq yozilgan edi).
- **`apps/accounts/models.py`**: yangi `User.approved_at` maydoni (qachon
  administrator birinchi marta faollashtirgani). Migratsiya mavjud
  faollashtirilgan foydalanuvchilar uchun buni orqaga to'ldiradi (`date_joined`
  bilan) — shunda kelajakda ular deaktivatsiya qilinsa, "ariza ko'rib
  chiqilmoqda" degan noto'g'ri xabar chiqmaydi.
- **`apps/accounts/views.py::UserToggleActiveView`**: hisobni birinchi
  marta faollashtirganda `approved_at`ni belgilaydi.
- **`apps/accounts/forms.py::PendingApprovalAwareLoginForm`** — yangi
  login formasi: agar login/parol to'g'ri bo'lsa-yu, hisob hali faol
  bo'lmasa, ikkita holatni ajratadi: (1) `approved_at is None` — hali
  hech qachon tasdiqlanmagan → "Arizangiz administrator tomonidan ko'rib
  chiqilmoqda..."; (2) avval tasdiqlangan, keyin deaktivatsiya qilingan →
  "Hisobingiz faollashtirilmagan. Administrator bilan bog'laning."
  Noto'g'ri parol bilan urinishda (hisob faol bo'lsin yoki bo'lmasin)
  hech qanday qo'shimcha ma'lumot oshkor qilinmaydi — faqat standart
  umumiy xabar (xavfsizlik: parolni "taxmin qilib tekshirish" imkoniyati
  ochilmasin).
- **`config/views.py::ThrottledLoginView`**: yangi forma ulandi
  (`authentication_form = PendingApprovalAwareLoginForm`).
- Barcha yangi xabarlar 4 tilga tarjima qilindi.
- **Testlar**: `tests/test_authentication.py`ga 3 ta yangi test —
  tasdiqlanmagan hisob uchun to'g'ri xabar, avval tasdiqlangan-keyin
  o'chirilgan hisob uchun boshqa xabar, va noto'g'ri parolda hech narsa
  oshkor qilinmasligi (xavfsizlik regressiya testi).

**Tekshiruv**: `manage.py check` toza, to'liq test to'plami (388 test,
+3 yangi) o'tdi, Playwright orqali jonli serverda tasdiqlangan xabar
matni skrinshotda ko'rsatilgandek to'g'ri chiqishi tekshirildi.

---

### 3.38 Tuzatildi — Filtr qidiruv oynasi iconka bilan yopishib qolgan, "Barcha holatlar" o'rniga "Barcha xonalar" chiqishi (2026-09-21)

Foydalanuvchi: "filtr qilish oynasi g'alati bo'lib qolgan, yozish
joyida lupachaning iconkasi bilan yopishib ketgan va ba'zi filtrlar
to'g'ri ishlamayotgandek." Bu **ikkita mustaqil, aralashib ketgan bug**
ekan:

1. **CSS specificity bug** — `static/css/components.css`da "FORMS &
   INPUTS" bo'limidagi umumiy `input[type="search"]`/`input[type="date"]`
   qoidasi (elementga bog'langan atribut selektor, specificity (0,1,1))
   pastroqdagi `.command-search-input`/`.command-date-input` klass
   selektoridan (0,1,0) KUCHLIROQ edi — shuning uchun qidiruv maydonining
   `padding-left: 36px` (iconkaga joy qoldirish uchun) `padding: 0
   var(--space-3)`ga qisqarib, matn iconka ustiga "yopishib" qolardi;
   shu bilan birga oddiy pill dizayn o'rniga qattiq chegara/orqa fon
   qaytib kelardi. Bu — `master_data/filters.html` orqali Tashkilotlar,
   Homiylar, Zallar, Tadbir turlari sahifalarida, shuningdek
   `events/event_list.html` va `events/approval_center.html`da
   qo'llaniladi — foydalanuvchining "har xil bo'limlarda" degani aynan
   shunga to'g'ri keladi. Tuzatish: `.command-search-input` va
   `.command-date-input` qoidalari ota-ona klass bilan birga
   (`.command-search-wrap .command-search-input`,
   `.command-filter-form .command-date-input`) yozildi — bu specificity'ni
   (0,2,0)ga oshirib, umumiy qoidadan g'olib chiqadi.
2. **Tarjima korruptsiyasi (haqiqiy "filtr noto'g'ri ishlayapti" hissi
   shundan kelib chiqqan)** — `locale/uz/LC_MESSAGES/django.po`da UCH TA
   yozuv, manba matni (`msgid`) allaqachon o'zbekcha bo'lishiga
   qaramay, BUTUNLAY BOSHQA (lekin baribir o'zbekcha) matnga
   tarjima qilingan edi — avtomatik/ommaviy tarjima vositasining
   noto'g'ri "fuzzy match"i natijasi (xuddi shu turdagi muammo avval
   `tr.po`da ham topilgan edi, 3.20-bandga qarang):
   - `"Barcha holatlar"` (All statuses) → **`"Barcha xonalar"`** (All
     rooms) bo'lib chiqqan — shuning uchun Tashkilotlar/Zallar/Tadbirlar
     sahifasidagi status filtri "Barcha xonalar" deb noto'g'ri ko'rsatilardi.
   - `"Barcha tadbirlar yagona tizimda"` (K-ONE shiori, 6 ta shablonda
     ishlatiladi: login, register, sidebar va h.k.) → **`"Barcha
     qurilmalar yagona tizimda"`** bo'lib chiqqan.
   - Zallar sahifasi tavsifidagi bitta jumla ham grammatik jihatdan
     buzilgan edi ("zallarining" → "uchrashuvlarining zal").
   Uchalasi ham dasturiy audit orqali topildi (uz.po'da `msgid == msgstr`
   bo'lishi kutiladigan, lekin bo'lmagan yozuvlarni skanerlash) va
   ru/ru/en/tr tarjimalari bilan tekshirilib (ular hammasi to'g'ri edi —
   faqat uz.po buzilgan edi), identity qiymatga qaytarildi. Bonus: xuddi
   shu skanerlash `"Operatsion holatda"` → `"Operation holatda"` (aralash
   til) yozuvini ham topdi, u ham tuzatildi.

**Tekshiruv**: `manage.py check` toza, to'liq test to'plami (388 test)
o'tdi, Playwright orqali Tashkilotlar va Tadbirlar sahifalarida qidiruv
maydonining `padding-left` (36px), border/orqa fon va status filtrining
to'g'ri "Barcha holatlar" matni bilan chiqishi skrinshot orqali
tasdiqlandi.

---

### 3.39 Bajarildi — Loyiha bo'ylab qo'shimcha audit: shu turdagi CSS/tarjima xatolari boshqa joylarda ham qidirildi (2026-09-21)

Foydalanuvchi 3.38'dagi ikkita bug'dan keyin: "Boshqa bo'limlarni ham
tekshirib chiq, xatolik bormi. Ham backend ham frontend tomondan."
Tizimli tarzda ikkala bug SINFI (CSS specificity, uz.po korruptsiyasi)
boshqa joylarda ham qidirildi:

**CSS specificity — yana bitta joy topildi**: `static/css/login.css`dagi
`.auth-input` (login/register/register_submitted sahifalaridagi barcha
matn/parol/email inputlari) xuddi shu sababdan (`input[type="..."]`
umumiy qoidasi kuchliroq specificity bilan) `border`, `background`,
`border-radius`ni bosib qo'ygan edi — faqat `padding`da avvaldan
`!important` borligi sababli vizual jihatdan unchalik sezilmasdi (radius
12px o'rniga 10px, oq fon o'rniga token fon, #E2E8F0 chegara o'rniga
boshqa rang — mayda farq). `.auth-input-wrap .auth-input` qilib
scope qilindi. Loyihadagi BOSHQA barcha `.command-search-input`/
`.command-date-input`/`.filter-input`/`.filter-select`/`.command-select`
ishlatilgan 5 ta sahifa (`master_data/filters.html` orqali 4 ta +
`publications/list.html`, `events/approval_center.html`) alohida-alohida
Playwright orqali tekshirilib, hammasi 3.38'dagi fix bilan allaqachon
to'g'irlanganligi tasdiqlandi.

**uz.po korruptsiyasi — yana ikkita joy topildi** (bir xil, msgid allaqachon
o'zbekcha bo'lsa ham msgstr boshqa matnga aylanib qolgan naqsh):
- `"Hozirda erkin — rejalashtirish mumkin"` (Zal bo'sh — band qilish
  mumkin, ochiq zal kartalarida ko'rinadi) → `"Hozirda erkin — mumkin"`
  bo'lib, "rejalashtirish" so'zi tushib qolgan edi — jumla ma'nosiz
  bo'lib qolardi.
- Qolgan ~40 ta "msgid o'zbekcha, msgstr boshqa" holatlar tekshirilib,
  hammasi haqiqiy va to'g'ri INGLIZCHA→o'zbekcha tarjimalar ekanligi
  tasdiqlandi (bug emas).

**Backend tomondan tekshirilgan, MUAMMO TOPILMAGAN sohalar**:
`EventListView`, `EventApprovalListView`, `PublicationListView`,
`OrganizationListView`/`SponsorListView`/`VenueListView` (barchasi
`MasterDataListMixin` orqali) — barcha filtr GET-parametrlari (q, status,
venue, type, priority, platform, language, start_date, end_date) backend
va shablon orasida to'g'ri mos kelishi tasdiqlandi (xuddi shunga o'xshash
nom-mos kelmaslik xatosi 3.32'da `nav_key` bilan, 3.38'da tarjima bilan
topilgan edi — bu safar topilmadi).

**Tekshiruv**: `manage.py check` toza, to'liq test to'plami (388 test)
o'tdi, Playwright orqali 7 ta ro'yxat/filtr sahifasi (tashkilotlar,
tadbirlar, zallar, homiylar, tadbir turlari, nashrlar, tasdiqlash markazi)
va login/register sahifalarining input stillari alohida-alohida
tekshirilib tasdiqlandi.

---

### 3.40 Tuzatildi — Dark mode'da login/register'da yozilgan matn ko'rinmay qolishi (2026-09-21, o'z-o'zining regressiyasi)

3.39-bandda `.auth-input`ni `.auth-input-wrap .auth-input` qilib
scope qilish orqali CSS specificity muammosini tuzatgan edim — bu esa
kutilmagan yangi bug keltirib chiqardi: dark-mode qoidasi
(`[data-theme="dark"] .auth-input`) o'sha paytda scope qilinmagan holda
qolgan edi. Natijada ikkala qoidaning specificity'si TENGLASHIB qoldi
(ikkalasi ham endi 2 ta klass), va tie-breaker sifatida fayldagi
KEYINGI qoida (yorug' rejim, chunki fayl tartibida keyinroq joylashgan)
g'olib chiqa boshladi — hatto dark-mode yoqilgan bo'lsa ham. Natija:
matn rangi (`#0F172A`, to'q qorong'i) fonga (`rgba(11,20,38,0.5)`, ham
qorong'i) mos kelib, foydalanuvchi yozgan matni butunlay ko'rinmay
qolardi.

Foydalanuvchi: "dark mode da login oynasida username yoki parol
almashib ko'rinmay qolyapdi yozgan bo'lsam ham."

- `static/css/login.css`dagi barcha `[data-theme="dark"] .auth-input`
  qoidalari `[data-theme="dark"] .auth-input-wrap .auth-input` qilib
  qayta scope qilindi (specificity 3 klass — yorug' rejimning 2
  klassidan aniq yuqori) va qo'shimcha xavfsizlik uchun `!important`
  ham qo'shildi (rang, fon, chegara — matn ko'rinishi uchun eng muhim
  xususiyatlar).
- Ikkala sahifa (login va register) real foydalanuvchi harakatini
  taqlid qilib (tema tugmasini bosish, keyin maydonlarga yozish)
  Playwright orqali qayta tekshirildi — endi ikkalasida ham yozilgan
  matn to'liq ko'rinadi (och rangli matn, qorong'i fon).

**Eslatma**: bu — texnik jihatdan mening o'zimning 3.39-banddagi
tuzatishimning ikkilamchi ta'siri edi, alohida, mustaqil bug emas.
Kelajakda `.auth-input` kabi ikki (yoki undan ko'p) rejimli
komponentlarni scope qilishda BARCHA rejim qoidalarini bir vaqtda
yangilash kerakligini eslatib qo'yish uchun bu yerga yozib qo'yildi.

**Tekshiruv**: `manage.py check` toza, to'liq test to'plami (388 test)
o'tdi, Playwright orqali dark-mode tugmasi bosilib, haqiqiy matn
kiritilib, skrinshot orqali ikkala maydonda ham matn aniq ko'rinishi
tasdiqlandi (login va register sahifalarida alohida-alohida).

---

### 3.41 Tuzatildi — Public dashboard dark mode'da uzun sahifalarda ochiq fon chizig'i; shifokorlar uchun ishlatolmaydigan bo'limlar yashirildi (2026-09-21)

Foydalanuvchi: "Boshqa sahifalarda ham dark mode'ni tekshirib chiq, va
shu bilan birga oddiy foydalanuvchilar uchun tadbirlar, taqvim va
hisobotlar bo'limi ham ko'rinib o'tirmasin baribir ishlatolmaydiku
ularni." Ikkita alohida narsa tekshirildi va tuzatildi:

**1. Public dashboard dark mode bug'i** — `static/css/public.css`dagi
`.public-shell` (barcha public sahifalarning tashqi qobig'i) fon rangi
mavjud BO'LMAGAN `--color-surface-base` o'zgaruvchisiga bog'langan edi,
shuning uchun har doim uning literal fallback qiymatiga
(`#F7F9FC`, yorug' rang) tushib qolardi — **dark mode yoqilgan bo'lsa
ham**. Buning ustidagi dekorativ fon qatlami (`.public-atmosphere`,
`position: fixed`) esa faqat BITTA EKRAN balandligini qoplaydi
(`inset: 0` — viewport o'lchamida, sahifaning to'liq balandligida emas).
Natijada: agar sahifa bitta ekrandan uzunroq bo'lsa (masalan, "Jonli
zallar holati"da 5 ta karta 3 qatorga tushganda), pastki qism yorug'
fon bilan ko'rinib qolardi — xuddi shifokor topgan "matn ko'rinmay
qolish" bilan bir xil turdagi, aylanma CSS o'zgaruvchi xatosi.
Tuzatish: `.public-shell` fon rangi to'g'ri, ikkala rejim uchun ham
aniqlangan `--color-canvas` o'zgaruvchisiga o'zgartirildi. Boshqa
barcha public sahifalar (Boshqaruv, Taqvim, Jonli, Band shifokorlar)
Playwright orqali dark mode'da qayta tekshirilib, matn/fon kontrasti
hamma joyda to'g'ri ekanligi tasdiqlandi.

**Eslatma**: ichki (autentifikatsiyadan o'tgan) workspace/admin
qismida (`templates/base.html`) dark mode tugmasi UMUMAN MAVJUD EMAS —
bu funksiya faqat login/register va public dashboard sahifalarida
ishlaydi. Bu — "ishlamayapti" emas, balki hali qo'shilmagan funksiya;
agar kelajakda kerak bo'lsa, alohida katta ish sifatida rejalashtirish
kerak (butun `workspace.css`/`components.css`ga dark-mode qo'shish).

**2. Shifokorlar uchun ishlatolmaydigan bo'limlar yashirildi** —
tekshiruv shuni ko'rsatdi: `apps/accounts/rbac.py::ROLE_CAPABILITIES`
lug'atida **DOCTOR roli umuman yo'q** — shuning uchun shifokor
hech qanday capability'ga ega emas (`VIEW_MASTER_DATA` yo'q, demak
Tadbirlar/Taqvim/Tadbir tafsilotlari), va `apps/reporting/selectors.py::
allowed_report_sections`da ham DOCTOR alohida ko'rsatilmagan (bo'sh
to'plam qaytadi, demak Hisobotlar ham). Bu degani: shifokor bu
havolalarni bossa, **403 Permission Denied** oladi — lekin ular
sidebar'da va bosh sahifada hech qanday tekshiruvsiz hammaga bab-baravar
ko'rsatilardi.
- `templates/partials/sidebar.html`: "Tadbirlar", "Taqvim" (Ish maydoni
  bo'limida) va butun "Tahlil" bo'limi (Rahbariyat paneli, Hisobotlar,
  Audit Log sarlavhasi bilan birga) endi `{% if user.role != 'doctor' %}`
  bilan o'ralgan.
- `templates/workspace/home.html`: bosh sahifadagi "Barcha tadbirlar"
  havolasi (`events:list`ga, `VIEW_MASTER_DATA` talab qiladi) va
  "+ Yangi tadbir" CTA tugmasi (`events:wizard`ga, `CREATE_OWN_EVENTS`
  talab qiladi — DOCTOR bunga ham ega emas) xuddi shunday yashirildi.
  "Zallar holati" panelidagi "Barchasi →" havolasi (`venues:list`)
  allaqachon to'g'ri o'ralgan ekan (tekshirilib tasdiqlandi).
- **Test**: `tests/test_final_acceptance_blockers.py::
  test_doctor_sidebar_and_dashboard_hide_links_they_cannot_use` — shifokor
  hisobi bilan bosh sahifaga kirib, bu 4 ta havola (`events:list`,
  `calendar`, `reporting:dashboard`, `events:wizard`) HTML'da yo'qligini
  va to'g'ridan-to'g'ri ochilsa 403 qaytarishini tasdiqlaydi.

**Tekshiruv**: `manage.py check` toza, to'liq test to'plami (389 test,
+1 yangi) o'tdi. Playwright orqali haqiqiy shifokor hisobi bilan kirib,
sidebar'da faqat "Bosh sahifa", "Band vaqtlarim", "Telegram", "Profil"
qolgani va bosh sahifada "Yangi tadbir"/"Barcha tadbirlar" havolalari
yo'qligi skrinshot bilan tasdiqlandi. **Eslatma**: bu tekshiruv jarayonida
shablon o'zgarishi jonli serverda darhol ko'rinmadi (Django test-client
orqali to'g'ri ekanligi tasdiqlangan bo'lsa-da) — server qayta ishga
tushirilgach to'g'ri ko'rindi; sababi bu sessiyada avval ham uchragan,
hali to'liq aniqlanmagan holat (shablon "yopishib qolishi").

---

### 3.42 Bajarildi va tuzatildi — Telegram bot integratsiyasi yoqildi, `getUpdates` timeout bug'i tuzatildi (2026-09-21)

Foydalanuvchi: "telegram integratsiya" so'rovi bilan boshlandi. Avval mavjud
kod (`apps/notifications/telegram/*`) review qilindi — xavfsiz va to'g'ri
qurilgan topildi (token hash'lash, TTL, idempotent delivery, cache lock).
Keyin foydalanuvchi real bot token berdi va yoqishni so'radi.

**1. Bot yoqildi** — `.env`ga (gitignored, commit qilinmagan)
`TELEGRAM_BOT_ENABLED=true`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`
qo'shildi. Token `getMe` orqali tasdiqlandi: bot @docker_manajer_bot
("Control Services"). Kanal broadcast (`TELEGRAM_CHANNEL_ENABLED`) hali
`false` — chat ID berilmagan, kerak bo'lsa alohida so'raladi.

**2. `client.py`dagi haqiqiy bug topilib tuzatildi** — `get_updates()`
Telegram'dan server tomonida 20 soniyagacha uzoq so'rov (long poll)
so'raydi, lekin HTTP client'ning soket timeout'i konstruktordan qattiq
kodlangan 8 soniya edi (`_call()` doim `self.timeout`ni ishlatardi, `get_updates`
o'zining `timeout` parametrini transport'ga uzatmasdi). Natijada har safar
yangi xabar kelmasa (odatiy holat), so'rov 8-soniyada client tomonidan
uzilib, `TelegramTransientError("Telegram network request failed")` bilan
`manage.py telegram_poll` darhol yiqilardi — bu ehtimol "integratsiya
ishlamay qoldi" degan asl shikoyatning sababi. Tuzatish: `_call()` endi
ixtiyoriy `timeout` parametrini qabul qiladi, `get_updates()` esa
`timeout + 5` soniyalik client-side timeout uzatadi (server-side long-poll
muddatidan katta bo'lishi kerak).

**3. `manage.py telegram_poll`** fon jarayoni sifatida ishga tushirildi
(hozircha lokal Windows dev muhitida, terminal orqali — bu komandaning
o'z docstring'ida ham aytilganidek "local account-linking development"
uchun mo'ljallangan, production uchun supervised/auto-restart jarayon
kerak, hali sozlanmagan).

**Tekshiruv**: `manage.py check` toza. Token `getMe` bilan live tasdiqlandi.
Tuzatishdan keyin `telegram_poll` xatosiz, uzoq muddat ishlab turdi (avval
8 soniyada har safar yiqilardi).

**Texnik qarz** (`goals.md` 4-bo'limiga ham qo'shildi): production'da
`telegram_poll`ni doimiy ishlab turadigan supervised process (systemd/Windows
service/Docker) ostida ishga tushirish kerak — hozircha buni ta'minlaydigan
konfiguratsiya yo'q.

**4. Yana bir bug — jarayon transient xatoda butunlay yiqilardi.** #2-band
tuzatilgandan keyin ham `telegram_poll` bir marta tarmoq xatosi bilan
yiqildi: `handle()`dagi `try/except` har qanday `TelegramError`ni (shu
jumladan vaqtinchalik `TelegramTransientError`ni) tutib, butun jarayonni
`CommandError` bilan to'xtatardi — uzoq ishlaydigan pollingda esa
vaqti-vaqti bilan tarmoq xatosi bo'lishi kutilgan holat. Tuzatildi:
`get_updates()`/`send_message()` endi faqat `TelegramTransientError`ni
tutib, eksponensial backoff bilan (1s → 30s max) qayta urinadi; faqat
`TelegramPermanentError` (masalan, noto'g'ri token) jarayonni to'xtatadi.

---

### 3.43 Tuzatildi — `register-tasks.ps1`dagi loyiha yo'li bugi, eskirgan LAN IP barcha deploy skriptlarida, `telegram_poll` uchun 4-chi Scheduled Task qo'shildi (2026-09-21)

**Kontekst**: Telegram integratsiyasini uchidan-uchigacha sinash chog'ida
kanal postiga rasm yuborish "Bad Request: wrong type of the web page
content" xatosi bilan qulaganini aniqlashda, sabab sifatida
`IEMS_BASE_URL=http://10.34.12.2:8012` — bu mashinaning **eskirgan** LAN
IP manzili ekani topildi (haqiqiy joriy IP DHCP orqali `10.34.12.152`ga
o'zgargan; `.2` boshqa bir qurilmaga tegishli bo'lib qolgan).

**1. `scripts/register-tasks.ps1`da ikkita mustaqil bug topildi:**
- `$projectRoot = "D:\Projects\K ONE"` — lekin haqiqiy loyiha
  (`manage.py`, `.venv`) `D:\Projects\K ONE\K ONE` (ichki, bir xil nomli
  papka)da joylashgan. Bu tuzatilmasa, barcha 4 ta scheduled task
  `pythonw.exe`ni topa olmasdi (noto'g'ri yo'l).
- "IEMS Web" vazifasi `--listen=10.34.12.2:8012` ga qattiq bog'langan edi
  — DHCP IP o'zgarsa yana ishlamay qoladi. `--listen=0.0.0.0:8012`ga
  (barcha interfeys) o'zgartirildi — DHCP o'zgarishlariga chidamli.
- Worker/Beat logfile yo'llari ham `D:\Projects\K ONE\logs\...` (noto'g'ri,
  yuqoridagi bug bilan bir xil sabab) edi — `D:\Projects\K ONE\K ONE\logs\...`
  ga tuzatildi.

**2. Yangi 4-chi vazifa qo'shildi**: "IEMS Telegram Poll"
(`manage.py telegram_poll`) — `goals.md` 4-bo'lim 12-banddagi texnik
qarzni ("telegram_poll production'da supervised process ostida emas")
yopadi. Worker/Beat bilan bir xil naqsh: Logon trigger, 3 marta
RestartOnFailure, ExecutionTimeLimit cheklovsiz.

**3. Bir xil eskirgan IP (`10.34.12.2`) yana uch joyda topildi va
tuzatildi**: `scripts/start-local.ps1`, `scripts/status-local.ps1`
($lanIP o'zgaruvchisi `10.34.12.152`ga), `scripts/run-web.ps1` (default
bind `0.0.0.0:8012`ga). `start-local.ps1`/`stop-local.ps1`/
`status-local.ps1`dagi `$taskNames`/`$tasks` ro'yxatlariga yangi
"IEMS Telegram Poll" qo'shildi. `.env`dagi `IEMS_BASE_URL` ham
`http://10.34.12.152:8012`ga yangilandi.

**Eslatma**: tarixiy bir martalik QA/screenshot skriptlarida
(`scripts/capture_*`, `scripts/verify_phase27_*` va h.k.) ham eski IP
uchraydi — ular ataylab tuzatilmadi, chunki runtime'ga aloqasi yo'q va
`goals.md` 4-bo'lim 4-bandidagi arxivlash qaroriga bog'liq.

**`ALLOWED_HOSTS` tekshiruvi (goals.md 4-bo'lim 2-band) — xavf yo'q
deb tasdiqlandi**: `config/settings/production.py`da
`ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")` — default qiymatsiz,
ya'ni `.env`da berilmasa Django ishga tushmay xato beradi (fail-loud).
`"*"` fallback faqat `base.py`da, faqat `production.py` uni override
qilmagan holatlar uchun. Joriy `.env`da ham aniq hostlar ro'yxati bor.
Kod o'zgarishi talab qilinmadi.

**Diqqat — yangi topilgan, hali hal qilinmagan savol**: `manage.py`,
`config/wsgi.py`, `config/celery.py` — uchalasi ham
`os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")`
ishlatadi. `setdefault` faqat OS darajasida oldindan boshqa qiymat
o'rnatilmagan bo'lsa ishlaydi — yangi scheduled tasklar hech qanday
`DJANGO_SETTINGS_MODULE` environment o'zgaruvchisini belgilamaydi, demak
ular ham **`local` sozlamalar** ostida ishlaydi (`production.py` emas),
faqat `.env`dagi qiymatlarga (`DJANGO_DEBUG=true` va h.k.) tayanadi.
Bu — chalkash va potentsial xavfli holat (masalan, "production" deb
nomlangan vazifa aslida `DEBUG=True` bilan ishlashi mumkin). `goals.md`
4-bo'limiga yangi band sifatida qo'shildi — foydalanuvchi bilan
kelishilishi kerak.

**Holat**: skriptlar faqat tuzatildi/tayyorlandi, **hali ro'yxatdan
o'tkazilmadi va ishga tushirilmadi** — foydalanuvchi buni keyinroq o'zi
bajarishni so'radi (`register-tasks.ps1`ni real ishga tushirish
tizim darajasidagi doimiy o'zgarish bo'lgani uchun ataylab kutildi).

---

### 3.44 Tuzatildi — `tr.po`da 6 ta semantik tarjima xatosi (avtomatik tarjima false-cognate'lari), `compile_po_polib.py`da yana bir loyiha-yo'li bugi (2026-09-21)

**Kontekst**: `goals.md` 4-bo'lim 7-bandda qayd etilgan qoldiq xavf
("tr.po'da avtomatik dasturiy tekshiruv topa olmaydigan semantik xato
tarjimalar qolgan bo'lishi mumkin") bo'yicha to'liq qo'lda proofreading
o'tkazildi — fork subagent orqali barcha 1481 ta `tr.po` yozuvi
`en.po`dagi manba matn bilan solishtirib o'qildi.

**Topilgan va tuzatilgan 6 ta xato** (barchasi — "false cognate"/noto'g'ri
avtomatik tarjima, oldin topilgan "Parol"→"Şartlı tahliye" bilan bir xil
turdagi xato):

1. `"Telegram settings"` → edi `"Telgraf ayarları"` ("telgraf" — eski
   simli aloqa vositasi, ilova nomi "Telegram" bilan false-cognate) →
   `"Telegram ayarları"`.
2. Sidebar "Venues" (`msgid "Zallar"`) → edi `"tamamen"` ("butunlay"
   degani, mutlaqo bog'liqsiz so'z) → `"Salonlar"`.
3. `"No speakers found in directory."` (faylda 3 marta takrorlangan) →
   edi `"Dizinde hoparlör bulunamadı."` ("hoparlör" = karnay/dinamik
   audio uskunasi, "ma'ruzachi" emas) → `"Dizinde konuşmacı bulunamadı."`
4. Sidebar "Ma'ruzachilar" → edi `"Hoparlörler"` (xuddi shu
   karnay/ma'ruzachi chalkashligi) → `"Konuşmacılar"`.
5. `"You cannot change your own active status here."` → edi
   `"Kendi etkinlik durumunuzu..."` (`etkinlik` bu faylda 100+ marta
   "tadbir/event" ma'nosida ishlatilgan, "faol/active" emas — jumla
   "o'z TADBIR holatingizni" deb o'qilardi) →
   `"Kendi aktiflik durumunuzu burada değiştiremezsiniz."`
6. `"Staff Manual"` (`apps/attendance/models.py`dagi `checkin_method`
   tanlovi — "xodim tomonidan qo'lda kiritish", qo'llanma/hujjat emas) →
   edi `"Personel El İle"` (grammatik jihatdan to'liqsiz, "elle" so'zi
   qo'shilmagan bo'lak) → `"Personel (Elle)"` (qo'shni tanlovlar —
   "Genel QR", "Davet", "Kiosk" — bilan bir xil qisqa yorliq uslubida).

**Qolgan ~1475 yozuv** — audit natijasida boshqa aniq semantik xato
topilmadi (faqat stilistik farqlar, masalan "panel" vs "pano", bular
xato emas deb hisoblanib o'tkazib yuborildi).

**Yana bir bug topildi va tuzatildi**: `scripts/compile_po_polib.py`da
`register-tasks.ps1`dagi bilan **bir xil** loyiha-yo'li xatosi bor edi
(`D:\Projects\K ONE\locale\...` — ikkinchi ichki `K ONE` papkasi
yetishmagan, haqiqiysi `D:\Projects\K ONE\K ONE\locale\...`). Bu
tuzatilmasa, `.po`dan `.mo`ga qayta kompilyatsiya qilib bo'lmasdi.

**Tekshiruv**: `manage.py check` toza. `.mo` fayllar (barcha 4 til)
qayta kompilyatsiya qilindi — faqat `tr` haqiqatan o'zgardi (boshqalar
baytma-bayt bir xil qoldi, chunki manba `.po`lari o'zgarmagan).

**Texnik qarz** (`goals.md` 4-bo'lim 7-bandiga eslatma sifatida
qo'shildi): bu hali ham **to'liq qo'lda, malakali tarjimon tomonidan
proofreading** o'rnini bosmaydi — AI-audit "sezilarli semantik xato"
darajasidagi muammolarni topa oladi, lekin nozik uslub/registr
xatolarini kafolatlab topa olmaydi.

---

### 3.45 Qo'shildi — Hisobotlar bo'limidagi Excel eksportiga oy bo'yicha guruhlash, ishtirokchilar va band xodimlar varaqlari (2026-09-21)

**Kontekst**: foydalanuvchi "hisobot bo'limiga Excel'ga eksport qiladigan
tugma qo'shish" so'rovi bilan keldi. Tekshirilganda `/reports/` sahifasida
Excel/CSV/PDF eksport tugmasi **allaqachon mavjud** ekani aniqlandi
(`apps/reporting/exports.py`, `reporting:xlsx` URL) — lekin u faqat
umumlashtirilgan statistika (Summary/Events/Venues/Attendance/Approvals/
Publications) chiqarardi, oy bo'yicha guruhlash, haqiqiy ishtirokchi
ismlari yoki band xodimlar ro'yxati yo'q edi. Shu bo'shliqni to'ldirish
maqsad qilindi (mavjud tugma/infratuzilma qayta ishlatildi, yangi
tugma/endpoint qo'shilmadi).

**O'zgarishlar (`apps/reporting/exports.py`):**
1. **"Events" (Tadbirlar) varag'iga "Month" (Oy) ustuni qo'shildi**
   (`event.planned_date.strftime("%Y-%m")`, birinchi ustun) — CSV
   "events" eksportiga ham. Endi tanlangan davr (oy/chorak/yil/maxsus)
   ichidagi har bir tadbir qaysi oyga tegishli ekani ko'rinadi.
2. **Yangi "Attendees" (Qatnashuvchilar) varag'i** — `EventAttendance`
   modelidan har bir tadbirning haqiqiy ishtirokchilari (F.I.Sh,
   tashkilot, lavozim, ro'yxatga olish usuli, kelgan vaqti), oy va
   tadbir bo'yicha guruhlangan qatorlar.
3. **Yangi "Busy staff" (Band xodimlar) varag'i** — `StaffUnavailability`
   modelidan tanlangan davr bilan kesishgan barcha band bo'lish
   yozuvlari (xodim, boshlanish/tugash sana-vaqti, sababi).

**Testlar**: `tests/test_phase9_reporting.py::test_xlsx_has_professional_sheets`
yangi varaq ro'yxatini (`Summary, Events, Attendees, Busy staff, Venues,
Attendance, Approvals, Publications`) tekshiradigan qilib yangilandi.
To'liq test to'plami (389 test, e2e/human_acceptance/visual_baseline
bundan mustasno) o'tadi.

**Tarjima**: 4 ta yangi matn (`"Attendee"`, `"Check-in method"`,
`"Checked in at"`, `"Busy staff"`) barcha 4 tilga (uz/ru/en/tr)
`polib` orqali qo'shildi (GNU gettext `msguniq` bu muhitda o'rnatilmagan
bo'lgani uchun `manage.py makemessages` ishlatilmadi), `.mo` fayllar
qayta kompilyatsiya qilindi.

---

### 3.46 Tuzatildi va qayta qurildi — Sana oralig'ini tanlash ishlamasligi (haqiqiy bug), Excel eksporti bitta varaqqa, foydalanuvchi ko'rsatgan tartibda qayta tuzildi (2026-09-22)

**Bug #1 — sana oralig'ini tanlab bo'lmasligi.** Foydalanuvchi filtr
formasida "Boshlanish sana"/"Tugash sana" maydonlariga sana kiritganda
hech narsa o'zgarmasligini xabar qildi. Sabab topildi:
`ReportFilterForm.date_range()` faqat `period == "custom"` bo'lganda
qo'lda kiritilgan sanalarni ishlatardi; boshqa har qanday `period`
qiymatida (masalan standart "Bu oy") sanalar butunlay e'tiborga
olinmasdi — va UI'da "Period" dropdown'ni sanalar bilan sinxronlaydigan
HECH QANDAY JavaScript yo'q edi (`grep`bilan tasdiqlandi). Ya'ni
foydalanuvchi sana tanlashi uchun sanalarni kiritish YETARLI EMAS edi,
alohida "Period"ni ham qo'lda "Maxsus sana oralig'i"ga o'zgartirish
kerak edi — hech qanday interfeys ipuchi buni ko'rsatmasdi.

**Tuzatish (ikki qatlamli):**
1. `apps/reporting/forms.py::ReportFilterForm.date_range()` — endi
   `start_date` va `end_date` ikkalasi ham berilgan bo'lsa, `period`
   qiymatidan qat'iy nazar ular ustunlik qiladi (`clean()` ham mos
   ravishda yangilandi — ikkala sana berilganda ular tekshiriladi,
   faqat `period="custom"`da emas). Eskirgan, endi hech qachon
   bajarilmaydigan `if period == CUSTOM: return ...` shoxobchasi
   o'chirildi (o'lik kod).
2. `templates/reporting/reports_dashboard.html` — kichik JS qo'shildi:
   `start_date`/`end_date` maydoni o'zgarganda "Period" dropdown
   avtomatik "Maxsus sana oralig'i"ga o'tkaziladi (vizual izchillik
   uchun; #1dagi backend tuzatish JS'siz ham to'g'ri ishlaydi).

**Feature — Excel eksporti butunlay qayta tuzildi.** Foydalanuvchi
oldingi ko'p-varaqli tuzilmadan norozi bo'lib, bitta varaqqa, aniq
tartibda so'radi: birinchi navbatda tanlangan davrdagi tadbirlar (sana,
tadbir, xona, davomat, mas'ul), pastida xulosa va nashrlar.
`apps/reporting/exports.py::xlsx_response()` to'liq qayta yozildi:

- Eski `_sheet()` (har chaqiruvda alohida varaq yaratuvchi) o'rniga
  yangi `_append_block()` — bitta varaq ichida sarlavha+jadval
  bloklarini ketma-ket yozadi (blok sarlavhasi qalin matn, keyin
  sarlavha qatori, keyin ma'lumot, keyin bo'sh ajratuvchi qator).
- Yagona "Report"/"Hisobot" varag'i, tartib: **davr yorlig'i** →
  **"Tadbirlar" bloki** (filtrlanadigan/qotirilgan, asosiy blok) →
  **"Band xodimlar"** → **"Xulosa"** → **"Nashrlar"**.
- `_event_rows()` qayta yozildi: endi ustunlar **Oy, Sana, Tadbir,
  Xona, Mas'ul (responsible_employee), Kutilayotgan, Ro'yxatdan
  o'tgan, Qatnashuvchilar (ism-familiyalar vergul bilan qo'shilgan
  matn, alohida "Attendees" varag'i o'rniga), Holati** — foydalanuvchi
  so'ragan "sana/uchrashuv/xona/davomat/mas'ul" hammasi bitta qatorda.
  Alohida `_attendee_rows()` (normalizatsiya qilingan, bir
  ishtirokchi — bir qator) endi ishlatilmaydi, o'chirildi — CSV va
  Excel bir xil `_event_rows()`dan foydalanadi (izchillik).
- Alohida "Venues" (zal band-foydalanish statistikasi) va
  "Attendance"/"Approvals" (yig'ma ko'rsatkichlar) bloklari Excel'dan
  **olib tashlandi** (foydalanuvchi faqat "xulosa, nashrlar"ni pastda
  qoldirishni so'radi; zal nomi va davomat endi asosiy jadvalda
  qatorma-qator ko'rinadi, alohida blok keraksiz takror bo'lardi).
  Bu ma'lumotlar hali ham on-page dashboard'da va PDF eksportida bor —
  faqat Excel tuzilishi soddalashtirildi.
- **Real bug**: modul darajasida `_()` (gettext, LAZY EMAS) bilan
  qurilgan sarlavha ro'yxati yozilayotganda payqaldi va oldini olindi
  — bunday konstant import vaqtida bir marta baholanadi, so'rov
  vaqtidagi `?language=` parametriga bog'liq bo'lmay qoladi. Shu
  sababli sarlavhalar alohida `_event_headers()` FUNKSIYASI ichida
  qurilgan (har chaqiruvda joriy tilni to'g'ri oladi).

**Tekshiruv**: haqiqiy xlsx generatsiya qilib, `openpyxl` bilan
o'qib tekshirildi (bitta "Report" varag'i, 4 blok, to'g'ri
tartib/kontent). UTF-8 belgilar (en dash, o'ng qo'shtirnoq) PowerShell
orqali bayt darajasida tasdiqlandi (Bash konsolining ko'rsatish
muammosi haqiqiy fayl buzilishi bilan adashtirilmadi).
`tests/test_phase9_reporting.py::test_xlsx_has_professional_sheets`
yangi bitta-varaq tuzilishini tekshiradigan qilib yangilandi. To'liq
test to'plami (389 ta, o'zgarishsiz) o'tadi.

---

### 3.47 O'zgartirildi — Registratsiyada minimal parol uzunligi 12'dan 8ga tushirildi (2026-09-22)

Foydalanuvchi so'roviga ko'ra `config/settings/base.py`dagi
`AUTH_PASSWORD_VALIDATORS`ning `MinimumLengthValidator` qiymati
(`min_length`) 12'dan 8ga o'zgartirildi. Bu Django'ning o'rnatilgan
validatori bo'lgani uchun boshqa hech qanday joyda (frontend/JS,
tarjima matnlari) qattiq kodlangan "12" topilmadi — yagona manba shu
sozlama edi. `manage.py check` toza, `test_doctor_registration.py`
(42 test) o'tadi.

---

### 3.48 Qo'shildi va tuzatildi — Telegram ulash 1 bosishga tushirildi, botga kirganda tushuntirish matni, "mas'ul tayinlandi" xabarnomasi (2026-09-22)

**#1 — "Ulash" tugmasi 2 marta bosishni talab qilardi.** Foydalanuvchi
xabar qildi: tugmani bosgach, hech narsa ko'zga ko'rinmasdan sahifa
o'zgarardi, va faqat SHUNDAN KEYIN paydo bo'ladigan IKKINCHI
("Telegram botni ochish") tugmani bosish kerak edi — bu qadam ko'zga
tashlanmasdi. Tuzatish: `TelegramLinkView.post()` endi to'g'ridan-to'g'ri
Telegram deep-link'ga (302) redirect qiladi, ikkinchi oraliq sahifa/tugma
yo'q. Shablon (`telegram_settings.html`)dagi forma `target="_blank"`
oldi — bitta bosish, yangi tabda Telegram to'g'ridan-to'g'ri ochiladi,
IEMS sahifasi o'z joyida qoladi. Endi kerak bo'lmagan
`telegram_link_url` session-o'zgaruvchisi olib tashlandi.

**#2 — botga kirganda "ulash uchun bosing" ko'rsatmasi yo'q edi.**
Ikki qism:
- Telegram Bot API (`setMyDescription`/`setMyShortDescription`)
  orqali botning profil tavsifi sozlandi — endi foydalanuvchi botni
  birinchi marta ochganda, "START" tugmasidan OLDIN, Telegram
  o'zi ko'rsatadigan matnda ulash yo'riqnomasi bor (bu kod emas,
  bir martalik API sozlash — BotFather orqali qo'lda ham
  o'zgartirish mumkin).
- `apps/notifications/management/commands/telegram_poll.py`: avval
  token'siz oddiy `/start` xabari **butunlay jim** o'tkazib yuborilardi
  (hech qanday javob yo'q edi) — bu haqiqiy bug edi, chalkashlikning
  asosiy sababi bo'lgan bo'lishi mumkin. Endi bunday holatda foydali
  yo'riqnoma xabari qaytariladi ("IEMS saytida Sozlamalar → Telegram'ga
  o'ting..."). Shu yo'l bilan ikkita qattiq kodlangan inglizcha javob
  matni ("✅ IEMS account connected." va h.k.) ham o'zbekchaga
  o'girildi (loyihaning asosiy tili bilan izchillik uchun).

**#3 — yangi feature: "Siz mas'ul etib tayinlandingiz" Telegram
xabarnomasi.** Foydalanuvchi so'radi: kimdir biror tadbirga mas'ul
qilib tayinlanganda, o'sha shaxsga botdan xabar kelsin.
`apps/notifications/telegram/services.py`ga `schedule_responsible_assignment(event)`
qo'shildi — mavjud `schedule_event_notification()`dan farqli o'laroq,
FAQAT `event.responsible_employee`ga yuboradi (`management_responsible`ga
emas — u "tayinlangan" emas). Ikki joyga ulandi:
1. `apps/events/wizard.py` — tadbir yaratilganda (5-bosqichli wizard
   yakunida).
2. `apps/events/views.py::EventUpdateView` — tadbir tahrirlanganda
   `responsible_employee` o'zgargan (qayta tayinlangan) bo'lsagina.
   Eski qiymatni aniqlash uchun `get_object()`ga izoh bilan qayd
   qilingan qiyinchilik hal qilindi: `form.save(commit=False)`
   `self.object`ni JOYIDA o'zgartiradi, shuning uchun eski qiymat
   `form_valid()` ichida emas, `get_object()`da (forma hali tegmagan
   paytda) saqlanishi kerak edi.
`apps/notifications/telegram/formatters.py`ga yangi
`"assigned_responsible"` EVENT_ACTIONS yozuvi (uz/ru/en) qo'shildi.

**Eslatmalar haqida — kod o'zgarishi TALAB QILINMADI**: foydalanuvchi
yaqinlashayotgan tadbirlar uchun eslatma ham so'radi, lekin bu tizim
(`schedule_due_reminders`, `Event.reminder_7d/3d/1d/3h/30m`,
barchasi default `True`) **Phase 7'dan beri allaqachon to'liq
ishlaydi** va celery beat orqali har daqiqa tekshiriladi — foydalanuvchi
buni hali sinamagan bo'lishi mumkin, chunki bot bugun ulandi. Faqat
tushuntirib berildi, kod tegilmadi.

**Testlar**: `tests/test_phase7_telegram.py`ga 2 ta yangi test
qo'shildi (`test_assigned_responsible_notifies_only_that_employee`,
`test_reassigning_responsible_employee_notifies_new_assignee`). To'liq
test to'plami: 391 ta (2 tasi yangi), barchasi o'tadi.

---
### 3.49 Tuzatildi — target="_blank" Telegram ulanishida "qora oyna" osilib qolishi (2026-09-22)

3.48-bandda qo'shilgan `target="_blank"` (yangi tabda ochish) amalda
foydalanuvchida muammo tug'dirdi: "Ulash" tugmasi bosilgach yangi,
bo'sh/qora oyna ochilib qoldi, Telegram'ga hech qachon o'tmadi.
Server-tomonidagi redirect to'g'ri ekani tasdiqlandi
(`TelegramLinkView` to'g'ri `https://t.me/docker_manajer_bot?start=...`
manziliga 302 qaytaradi) — muammo faqat brauzerning yangidan ochilgan
bo'sh tabda tashqi `t.me` protokoliga o'tishni ishonchli boshqara
olmasligida edi (odatiy holat, ba'zi brauzerlarda uchraydi).

Audit log orqali tasdiqlandi: foydalanuvchining "Uzish" (disconnect)
amali muvaffaqiyatli ishlagan edi (`telegram.connection_removed`,
"Test" foydalanuvchisi uchun, 2026-09-22 06:36) — muammo faqat QAYTA
ulanishda, yangi tab ochilishida bo'lgan.

**Tuzatish**: `templates/notifications/telegram_settings.html`dan
`target="_blank"` olib tashlandi — endi forma bir xil tabda
to'g'ridan-to'g'ri Telegram'ga o'tadi (oddiy, ishonchli redirect,
hech qanday yangi/bo'sh oyna yo'q). Foydalanuvchi Telegram'da
ulanishni yakunlagach, orqaga qaytish tugmasi bilan IEMS'ga qaytadi.

---
### 3.50 Tuzatildi — Telegram ulanishida "hech qanday oyna ochilmayapti" (avtomatik redirect ishonchsiz ekan) (2026-09-22)

3.49-bandda `target="_blank"` olib tashlanib, bir xil tabda
to'g'ridan-to'g'ri `https://t.me/...`ga HTTP redirect qilinadigan
qilingandi. Foydalanuvchi buni sinab ko'rib, "umuman yangi oyna
ochilmayapti" deb xabar qildi. Server-tomon tekshirildi — redirect
to'g'ri chiqib turibdi (`POST /notifications/telegram/link/` → `302`
→ to'g'ri `t.me` manzili), lekin brauzer/OS darajasida bu avtomatik
"handoff" ba'zi holatlarda (Telegram Desktop ilovasi ro'yxatdan
o'tmagan yoki protokol ulanishi yo'q) sezilarli hech narsa
qilmasdan "yutilib" ketishi mumkin ekan — foydalanuvchiga hech qanday
signal, hech qanday bosiladigan narsa qolmaydi.

**Tuzatish — ishonchli, har doim ko'rinadigan yechim**: xom HTTP
redirect o'rniga endi `TelegramLinkView.post()` maxsus oraliq sahifa
render qiladi (`templates/notifications/telegram_open.html`):
- `<meta http-equiv="refresh">` orqali avtomatik o'tishga harakat
  qiladi (ishlaydigan brauzerlarda darhol o'tadi, foydalanuvchi
  sahifani deyarli ko'rmaydi ham),
- **lekin har doim** katta, aniq ko'rinadigan `<a href="...">` tugmasi
  ham bor ("Telegram'ni ochish") — bu oddiy HTML havola, brauzer/OS
  qanday bo'lishidan qat'iy nazar 100% bosiladi va ishlaydi,
  chunki foydalanuvchining o'zi ongli ravishda bosgan havola
  (avtomatik JS/redirect emas) — bu OS darajasidagi protokol
  ruxsatlarini ko'pincha ishonchliroq ishga tushiradi,
- "Sozlamalarga qaytish" havolasi bilan.

Bu yechim ikkala muammoni ham (3.48'dagi "ko'rinmaydi", 3.49'dagi
"qora oyna", va bugungi "hech narsa ochilmaydi") bir vaqtda hal
qiladi: har doim bosiladigan, har doim ko'rinadigan bitta aniq tugma.

**Tekshiruv**: `manage.py check` toza, real so'rov orqali sahifa
to'g'ri render bo'lishi (meta-refresh + to'g'ri deep-link) tasdiqlandi,
`test_phase7_telegram.py` (24 test) o'tadi.

---
### 3.51 Tuzatildi — Loyiha bo'ylab mobil moslashuvchanlik auditi: public dashboard'dagi jadval (timeline) mobilga sig'masligi, Telegram kanal sozlamalarida anonim foydalanuvchi uchun 500 xatosi (2026-09-22)

**Kontekst**: foydalanuvchi telefonidan kirganda public dashboard oynalari
mobilga moslanmagani haqida xabar berdi, "butun loyihani tekshir" deb
so'radi. Playwright orqali (Django sessiyasi to'g'ridan-to'g'ri DB'da
yaratilib, haqiqiy parolga tegilmasdan) 390×844 (mobil) o'lchamda ~25
sahifa avtomatik tekshirildi: har bir sahifada haqiqiy sahifa-darajasidagi
gorizontal scroll bor-yo'qligi va har qanday elementning ko'rinadigan
oynadan tashqariga chiqib ketishi tekshirildi, so'ng har bir topilma
skrinshot bilan qo'lda tasdiqlandi (soxta signallarni — masalan ataylab
gorizontal scroll qilinadigan yorliqlar qatori yoki yopiq holatdagi
off-canvas drawer'lar — haqiqiy bug'lardan ajratish uchun).

**Bug #1 (asosiy, foydalanuvchi xabar qilgan) — public dashboard'dagi
"Xronologik Oqim" (soatlik jadval) mobilda matn kesilib, o'qib
bo'lmaydigan holga kelardi.** Ikki qatlamli sabab topildi:

1. `static/css/public.css`da `@media (max-width: 1024px)` ichida
   `.executive-layout { grid-template-columns: 1fr; }` — bitta ustunga
   tushirilardi, lekin bitta `1fr` grid ustuni CSS spetsifikatsiyasi
   bo'yicha standart holda `minmax(auto, 1fr)`ga teng — ya'ni minimal
   o'lchami HALI HAM kontentning o'ziga bog'liq, ekran eniga emas. Desktop
   qoidasi (`minmax(0, 7fr) minmax(0, 3fr)`) buni to'g'ri hal qilgan edi,
   lekin mobil override'da bu unutilgan (klassik CSS Grid "kichraymaydi"
   xatosi). Tuzatildi: `minmax(0, 1fr)`.
2. Bundan tashqari, eski (`templates/workspace/home.html`da ishlatiladigan)
   `.timeline-scale`/`.timeline-tracks` uchun mobil qoida
   (`min-width: 640px`) klass nomi bir xil bo'lgani sababli **tasodifan**
   yangi "Phase 3" public dashboard komponentiga ham (`.timeline-exec-container`
   ichidagi `.timeline-scale`) ta'sir qilardi — lekin bu yangi komponentda
   mos `overflow-x: auto` yo'q edi (bazaviy qoidada `overflow: hidden`),
   shuning uchun ortiqcha kenglik gorizontal scroll o'rniga oddiygina
   **ko'rinmay qolardi**. Tuzatildi: eski qoida `.timeline-container`
   ota-onasi bilan scope qilindi (endi faqat workspace'ga tegishli), va
   Phase 3 komponenti uchun alohida, to'g'ri qoida qo'shildi
   (`.timeline-exec-container { overflow-x: auto }` + mos `min-width`lar) —
   endi soatlik jadval mobilda gorizontal surish (swipe) orqali to'liq
   ko'rinadi, matn kesilmaydi.

**Bug #2 (mobilga aloqasi yo'q, audit jarayonida topildi) — Telegram
kanal/guruh sozlamalari sahifasi (`/notifications/telegram/channel/`)
anonim (kirmagan) foydalanuvchi uchun 500 xato bilan qulardi**, login
sahifasiga yo'naltirish o'rniga. Sabab:
`TelegramChannelSettingsView.dispatch()` `_is_telegram_admin(request.user)`ni
`super().dispatch()` (bu yerda `LoginRequiredMixin`ning autentifikatsiya
tekshiruvi bajariladi) chaqirilishidan OLDIN chaqirar edi;
`_is_telegram_admin()` esa `user.role`ga to'g'ridan-to'g'ri murojaat
qilardi — `AnonymousUser`da bunday atribut yo'q
(`AttributeError: 'AnonymousUser' object has no attribute 'role'`).
Tuzatildi: `_is_telegram_admin()` endi (`user_has_capability()` bilan bir
xil naqshda) avval `user.is_authenticated`ni tekshiradi; `dispatch()`
esa autentifikatsiya qilinmagan foydalanuvchini avval
`super().dispatch()`ga o'tkazadi (u LoginRequiredMixin orqali login
sahifasiga yo'naltiradi), faqat autentifikatsiya qilingan-lekin-admin-emas
holatda `PermissionDenied` (403) qaytaradi.

**Tekshirilgan va MUAMMO TOPILMAGAN sahifalar** (~25 ta): workspace
dashboard, hisobotlar, tadbirlar ro'yxati/wizard/detail/tasdiqlash,
zallar, tadbir turlari, tashkilotlar, homiylar, Telegram sozlamalari,
profil, foydalanuvchilar, ochiq zallar/band shifokorlar, audit jurnal,
nashrlar, login/registratsiya, shifokor bandligi, taqvim oy/hafta/kun
ko'rinishlari.

**Soxta signal sifatida rad etilgan (bug emas)**: yuqori navigatsiya
yorliqlari qatori (`.premium-segment-btn`) — ataylab gorizontal surish
uchun mo'ljallangan (`overflow-x:auto`, CSS'da tasdiqlangan); taqvimdagi
tadbir tafsiloti paneli (`.inspector-panel`) — yopiq holatda ekrandan
tashqarida turadi, bosilganda to'g'ri joyga suriladi (skrinshot bilan
tasdiqlandi).

**Testlar**: `tests/test_phase7_telegram.py`ga 2 ta yangi regressiya
testi qo'shildi (`test_channel_settings_redirects_anonymous_instead_of_crashing`,
`test_channel_settings_forbidden_for_non_admin`). To'liq test to'plami:
393 ta (2 tasi yangi), barchasi o'tadi.

---
### 3.52 Tuzatildi — Xuddi shu turdagi bug yana bir joyda: `apps/publications`da anonim foydalanuvchi uchun 500 xato (2026-09-22)

3.51-bandda topilgan naqsh (`AnonymousUser`da `.role` yo'qligi sababli
qulash) bo'yicha butun loyiha bo'ylab tizimli qidiruv o'tkazildi (har bir
`dispatch()` override, ruxsat helper funksiyalari, context processor,
middleware, shablon filtri, DRF permission klasslari — barcha 10 ta
app bo'ylab).

**Topilgan va tuzatilgan**: `apps/publications/policies.py`dagi
`can_prepare()`, `can_approve()`, `can_publish()` — uchalasi ham
`user.is_superuser or user.role in (...)` shaklida edi.
`AnonymousUser.is_superuser` — `False`, shuning uchun `or` ifodasi
`.role`ga o'tib, `AttributeError` bilan qulardi. Bu
`PublicationCreateView.dispatch()` va `PublicationUpdateView.dispatch()`
orqali chaqirilardi (`super().dispatch()`dan OLDIN, xuddi 3.51-bandagi
`TelegramChannelSettingsView` bilan bir xil naqsh) — ya'ni
`/publications/events/<id>/new/` yoki `/publications/<id>/edit/`ga
kirgan har qanday anonim tashrifchi login sahifasiga yo'naltirish
o'rniga 500 xato ko'rardi.

**Tuzatish**: uchala policy funksiyasiga ham
`if not user.is_authenticated: return False` qo'shildi
(`user_has_capability()`dagi mavjud xavfsiz naqshga mos), va ikkala
view'ning `dispatch()`i anonim so'rovni avval `super().dispatch()`ga
(LoginRequiredMixin orqali login'ga yo'naltirish) o'tkazadigan qilib
qayta tartiblandi.

**Boshqa barcha joylar tekshirildi va xavfsiz deb tasdiqlandi**
(o'zgartirish talab qilinmadi): accounts/events/notifications/reporting
ilovalaridagi barcha `dispatch()`lar; `is_admin_privileged`,
`allowed_report_sections`, davomat/rahbariyat ruxsat funksiyalari —
barchasi allaqachon `is_authenticated`/`is_active`ni avval tekshiradi;
`unread_notifications` context processor; `AdminAuditLogMiddleware`;
`localized_role` shablon filtri (ko'rinishidan xavfli, lekin
`base.html`da butun autentifikatsiyalangan qism
`{% if user.is_authenticated %}` bilan o'ralgan, shuning uchun anonim
holatda hech qachon bajarilmaydi); barcha DRF `APIView`lar (global
`DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` yoki aniq
`permission_classes` bilan himoyalangan).

**Testlar**: `tests/test_phase8_publications.py`ga 2 ta yangi
regressiya testi qo'shildi. To'liq test to'plami: 395 ta (2 tasi
yangi), barchasi o'tadi.

---
### 3.53 Ultra Review — production-readiness auditi va topilgan bug'larning tuzatilishi (2026-09-22)

8 ta mustaqil yo'nalish (xavfsizlik, to'g'rilik/mantiq, ishlash/DB, API
dizayni, arxitektura, testlar, DevOps, bog'liqliklar) bo'yicha to'liq
loyiha auditi o'tkazildi, so'ngra CRITICAL/HIGH topilmalar alohida
verifikator tomonidan tasdiqlandi (to'liq hisobot: `REVIEW_REPORT.md`,
repo ildizida). Tasdiqlangan topilmalarning aksariyati shu sessiyada
tuzatildi:

**CRITICAL — tuzatildi**: Windows Scheduled Task'lar (`scripts/register-tasks.ps1`)
`DJANGO_SETTINGS_MODULE`ni hech qachon o'rnatmasdi, shuning uchun
production haqiqatda `config.settings.local`da ishlar edi (`DEBUG=True`
sukut, xavfsiz bo'lmagan cookie'lar). Endi har bir task `cmd.exe`
wrapper orqali `DJANGO_SETTINGS_MODULE=config.settings.production`ni
majburiy o'rnatadi (Task Scheduler XML sxemasida alohida `<Environment>`
elementi yo'qligi sababli). **Muhim**: `scripts/run-web.ps1` (kundalik
LOKAL development skripti) ataylab TEGILMADI — bu faqat production
Scheduled Task'lariga tegishli.

**HIGH — tuzatildi**:
- `apps/publications` API'sida ruxsat nazorati yo'q edi — endi
  `MANAGE_CONTENT` capability talab qilinadi (GET uchun; POST o'zining
  mavjud `can_prepare()` tekshiruvida qoldi).
- `Event.Status.DRAFT` conflict-detection'dan chetlashtirilmagan edi —
  qoralama tadbir zal/vaqtni doimiy "band" qilib qo'yishi mumkin edi.
- `apps/publications/services.py`dagi `publish_publication` — tashqi
  ijtimoiy tarmoq API chaqiruvi endi DB lock/tranzaksiyadan tashqarida;
  `PUBLISHING` holati oldindan commit qilinadi, shu bilan qulashda ikki
  marta post qilinish xavfi kamaydi; kutilmagan xatolar (masalan banner
  yo'qligi) endi `FAILED`ga aylanadi (avval cheksiz retry qilinardi).
- `EventDetailView` har bir sahifa yuklashda tadbirni ikki marta
  so'rardi — tuzatildi.
- `apps/events/api.py`dagi `expected_attendees` raqamli parametri
  endi try/except ichida — noto'g'ri qiymatda 500 o'rniga 400.
- Production logging faqat konsolga (`StreamHandler`) yozardi — Windows
  Scheduled Task'lar `pythonw.exe` orqali konsolsiz ishlagani uchun
  loglar yo'qolib qolardi; endi fayl handler ham parallel ishlaydi.
- `docker-compose.yml`da hech bir servisda `restart:` siyosati va
  `web`/`worker`da healthcheck yo'q edi — qo'shildi.
- Native Windows/Docker'da `DEBUG=False` bo'lganda statik fayllar
  (CSS/JS) uzatilmasdi (Waitress/gunicorn buni o'zi qilmaydi) —
  `whitenoise` kutubxonasi qo'shildi va sozlandi.
- `Django` 5.2.16→5.2.17, `djangorestframework` 3.17.1→3.17.2 (e'lon
  qilingan zaifliklar uchun).

**MEDIUM/kod sifati — tuzatildi**: `apps/events/services/workflow.py`dagi
`approve_event`ga `transaction.atomic()`+`select_for_update()` qo'shildi
(boshqa workflow funksiyalari bilan bir xil qulflash naqshi);
`apps/events/views.py`dagi 5 ta joyda takrorlangan "owner-or-admin"
ruxsat tekshiruvi yagona `apps.events.selectors.can_manage_event()`ga
birlashtirildi; 6 ta ortiqcha `or user.is_superuser` tekshiruvi olib
tashlandi (`user_has_capability` allaqachon superuserni qamraydi);
`apps/reporting/selectors.py`dagi `get_workspace_data()` — kunlik
zal-ziddiyat hisoblashi endi tadbir boshiga alohida DB so'rov
yubormaydi, Python ichida hisoblanadi (so'rovlar soni tadbirlar
sonidan mustaqil, testda tasdiqlangan); Approval Center'dagi ortiqcha
`.exists()` chaqiruvi olib tashlandi.

**Yangi**: GitHub Actions CI (`.github/workflows/ci.yml`) — `ruff`,
`manage.py check`, `makemigrations --check --dry-run`, `pytest` har
push/PR'da avtomatik ishga tushadi (avval CI umuman yo'q edi).

**Ataylab tegilmagan** (biznes qaror yoki katta refaktoring talab
qiladi, `goals.md` 4-bo'limiga qo'shildi): `apps/events/views.py`ni
(1250 qator) kichik modullarga bo'lish; shifokor "band" bo'lish
tekshiruvida `StaffUnavailability` vs `Event.attending_doctors`
ziddiyati (allaqachon 4.8-bandda qayd etilgan, o'zgarmadi).

**Testlar**: `apps/publications/tasks.py`dagi `publish_publication_task`
retry/failure logikasiga 4 ta yangi test qo'shildi (avval faqat
`.delay()` monkeypatch qilinardi, task tanasi hech qachon sinalmagandi);
`tests/test_rbac.py` 2 tadan 13 taga kengaytirildi (barcha 7 rol +
superuser/doctor/inactive/anonymous/noto'g'ri-capability edge case'lari);
workspace dashboard N+1 tuzatishi uchun regressiya testi qo'shildi.
To'liq test to'plami: **411 ta, barchasi o'tadi** (16 tasi yangi).

---
### 3.54 Foydalanuvchilar sahifasi qayta dizayn qilindi, o'chirish qo'shildi; Telegram xabarlari cheklandi (2026-09-23)

**Foydalanuvchilar sahifasi (`/users/`) — KPI ko'rinishidagi dizayn.** Avval
tekis ro'yxat edi. Endi yuqorida 5 ta KPI kartasi (Jami / Faol / Kutilmoqda /
Bloklangan / Shifokorlar, mavjud `metric-tile` uslubida) va uchta guruhlangan
bo'lim: **Kutilayotgan tasdiqlar** (amber), **Faol foydalanuvchilar** (moviy),
**Bloklangan** (qizil). Har bir foydalanuvchi karta ko'rinishida: avatar (rasm
yoki bosh harflar), holat belgisi, rol, shifokorlar uchun mutaxassislik/ish
joyi. Bo'lim sarlavhalari ham ikonkali banner shaklida. Yangi partial:
`templates/accounts/_user_card.html`.

Shu jarayonda **"Kutilmoqda" va "Bloklangan" holatlari ajratildi**: avval
`is_active=False` bo'lgan hammasi "Kutilmoqda" deb ko'rsatilardi. Endi mavjud
`User.approved_at` maydoni orqali "hech qachon tasdiqlanmagan" (kutilmoqda) va
"avval tasdiqlangan, keyin bloklangan" farqlanadi.

**Foydalanuvchini o'chirish** (`UserDeleteView`, `users/<pk>/delete/`). Tugma
faqat "Faol foydalanuvchilar" bo'limida ko'rinadi (foydalanuvchi shunday
so'radi). Himoyalar: o'zini o'chira olmaydi; admin darajasidagi hisoblar
himoyalangan (403); `Event.responsible_employee`/`management_responsible`
maydonlari `on_delete=PROTECT` bo'lgani uchun tadbirlar tarixiga bog'langan
foydalanuvchini Django o'chirishga yo'l qo'ymaydi — `ProtectedError` tutilib,
xato sahifasi o'rniga tushunarli xabar ko'rsatiladi ("bloklang").

**Telegram xabarlari faqat ikkitasiga cheklandi.** Foydalanuvchi: "faqat mas'ul
etib tayinlanganini va eslatmani yuborsa bo'ldi". Shu sababli
`schedule_event_notification()` chaqiruvlari `workflow.py` (submitted,
approved ×2, rejected, resubmitted, postponed, rescheduled) va
`emergency.py` (displaced, emergency) fayllaridan olib tashlandi. Endi Telegram
orqali faqat: (1) mas'ul etib tayinlanganlik xabari, (2) rejalashtirilgan
eslatmalar (7d/3d/1d/3h/30m) boradi. **Ilova ichidagi bildirishnoma
(`send_notification`, qo'ng'iroqcha) barcha holatlar uchun avvalgidek ishlaydi**
— faqat Telegram xabarlari to'xtatildi. Ishlatilmay qolgan kod ham tozalandi:
`schedule_event_notification()` funksiyasi, `event_recipients()`dagi
`include_admins` parametri va `EVENT_ACTIONS`dagi 7 ta keraksiz yozuv.

**Testlar**: `publish_publication_task`ning retry/failure yo'liga 4 ta test
(avval faqat `.delay` monkeypatch qilinardi); `tests/test_rbac.py` 2 tadan 13
taga kengaytirildi; foydalanuvchi o'chirish uchun 5 ta test; Telegram
xabarlari bo'yicha 3 ta test yangi xatti-harakatga moslandi. Jami: **416 ta
test, barchasi o'tadi**.

---
### 3.55 AI/yordamchi vositalar fayllari repozitoriydan olib tashlandi (2026-09-23)

Foydalanuvchi GitHub'ni ko'rganlar loyihani "faqat sun'iy intellekt qilgan"
deb baholayotganini aytdi. Loyihaga umuman ta'sir qilmaydigan yordamchi vosita
fayllari repozitoriydan chiqarildi (`git rm --cached` — **diskda to'liq
qoladi**): `.claude/` (338 fayl), `.claude-flow/` (8), `.swarm/` (2),
`.mcp.json`, `CLAUDE.md` — jami **351 fayl**. Barchasi `.gitignore`ga
qo'shildi. `goals.md` va `docs/CHANGELOG.md`dagi bir nechta shunday havola ham
olib tashlandi (bu ikki fayl — haqiqiy loyiha hujjatlari, saqlab qolindi).

**Qaror qabul qilinmadi**: git tarixi qayta yozilmadi. Shu sababli eski 34 ta
commit xabarida `Co-Authored-By` qatori va 3 ta eski commitda `.claude`
fayllari tarixda ko'rinib turibdi. Foydalanuvchi buni ataylab shunday
qoldirdi (tarixni qayta yozish barcha commit ID'larini o'zgartiradi).
Bundan keyingi commitlarga attribution qatori qo'shilmaydi.

---
### 3.56 Tuzatildi — Public QR check-in: "hali boshlanmagan" ogohlantirishi va sessiyaga bog'liq bo'lmagan "bir vaqtda bitta tadbir" qoidasi (2026-09-24)

Foydalanuvchi ikkita xatti-harakat "avval ishlardi, hozir ishlamayapti" deb
xabar berdi. **Tekshiruv shuni ko'rsatdiki, ikkala mantiq ham koddan
yo'qolmagan** — `git log -S` bo'yicha ular yozilganidan beri umuman
o'zgarmagan (`effective_checkin_opens_at` — `92fcfea`, `active_event_end`
konflikt tekshiruvi — `7f6b915`). Sabablari boshqa bo'lib chiqdi:

**1. "Hali boshlanmagan" xabari ko'rinmasligi.** Check-in tadbir
boshlanishidan **60 daqiqa oldin** ochiladi (`start_datetime - 60min`).
Ya'ni 1 soatdan kam qolganda skaner qilinsa, tizim to'g'ri ishlab odamni
ro'yxatga olardi va hech narsa demasdi; "Check-in hali ochilmagan" faqat 1
soatdan ko'p qolganda chiqardi (sinovda tasdiqlandi). Foydalanuvchi bilan
kelishilgan yechim: **oyna o'zgartirilmadi** (erta kelganlar ro'yxatdan o'ta
olishi kerak), lekin endi tadbir boshlanmagan bo'lsa sahifada sariq
ogohlantirish chiqadi: "⏳ Tadbir hali boshlanmagan — HH:MM da boshlanadi".
Yangi kontekst o'zgaruvchisi: `event_not_started`.

**2. Ikkinchi tadbirga yozilish bloki ishlamasligi.** Bu qoida faqat
`request.session`da saqlanardi. Sessiya yo'qolsa (masalan, birinchi QR
Telegram ichidagi brauzerda, ikkinchisi Camera→Chrome orqali ochilsa) qoida
butunlay ishlamay qolardi. Endi u **bazadan** hisoblanadi
(`find_ongoing_other_checkin()`): brauzer check-in tokeni bo'yicha, hozir
davom etayotgan tadbirlar orasida shu brauzer allaqachon ro'yxatdan o'tgani
bor-yo'qligi tekshiriladi. Sessiya ikkilamchi signal sifatida qoldirildi
(cookie yo'qolgan, lekin sessiya saqlangan holat uchun).

**Qoldiq cheklov**: public check-in **anonim**, brauzer tokeni yagona
identifikator. Butunlay boshqa telefon/brauzerdan skaner qilingan odamni
bog'lab bo'lmaydi — buning uchun check-in'da shaxsni aniqlash (telefon raqami
yoki login) kerak bo'ladi.

**Testlar**: `tests/test_phase5_attendance.py`ga 4 ta regressiya testi
qo'shildi (ogohlantirish ko'rinishi/ko'rinmasligi, sessiyasiz konflikt bloki,
birinchi tadbir tugagach ruxsat berilishi). Jami: **420 ta test, barchasi
o'tadi**.

---
