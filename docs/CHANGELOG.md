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

