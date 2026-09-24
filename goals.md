# IEMS — Maqsadlar va Holat Reyestri

> **QOIDA:** Ushbu loyiha ustida har qanday amal (kod yozish, refactor, feature qo'shish,
> bug fix) boshlanishidan **oldin** shu fayl to'liq o'qilishi shart. Har bir muhim
> o'zgarishdan keyin ("Joriy holat" va "Keyingi qadamlar" bo'limlari) yangilab borilishi kerak.

Oxirgi yangilanish: 2026-09-24 (Public QR check-in: tadbir boshlanmagan bo'lsa
sahifada ogohlantirish chiqadigan bo'ldi va "bir vaqtda bitta tadbir" qoidasi
sessiya o'rniga bazaga bog'landi — ikkala mantiq ham aslida buzilmagan edi,
sabablari boshqa bo'lib chiqdi, `docs/CHANGELOG.md` 3.56-band; bundan oldin:
yordamchi vosita fayllari (`.claude/` va h.k., 351 fayl) repozitoriydan
olib tashlandi, diskda qoldi (3.55-band); bundan oldin: Foydalanuvchilar
sahifasi KPI ko'rinishida qayta dizayn qilindi, o'chirish funksiyasi qo'shildi
va Telegram xabarlari faqat "mas'ul tayinlash + eslatma"ga cheklandi
(3.54-band), 420 ta test o'tadi; bundan oldin: Ultra Review — 8 yo'nalishli
production-readiness
auditi (`REVIEW_REPORT.md`) o'tkazildi, verifikator tomonidan tasdiqlangan barcha
CRITICAL/HIGH topilmalar tuzatildi: production'da `DJANGO_SETTINGS_MODULE`ning
majburiy o'rnatilmasligi (eng jiddiy topilma — 4-bo'lim 13-band endi HAL QILINDI),
`apps/publications` API ruxsat nazorati, DRAFT tadbirlarning zal/vaqtni band
qilib qo'yishi, ijtimoiy tarmoqqa nashr qilishda ikki marta post qilinish xavfi,
Docker restart/healthcheck, Waitress statik fayl muammosi (`whitenoise`), GitHub
Actions CI qo'shildi — tafsilot `docs/CHANGELOG.md` 3.53-bo'limda, 411 ta test
o'tadi; bundan oldin: Xuddi shu "AnonymousUser'da `.role` yo'q"
bug turi bo'yicha butun loyiha bo'ylab qidiruv — yana bitta joy
(`apps/publications` — nashr yaratish/tahrirlash) topilib tuzatildi,
qolgan barcha joylar tekshirilib xavfsiz deb tasdiqlandi; tafsilot
`docs/CHANGELOG.md` 3.52-bo'limda); bundan oldin: Loyiha bo'ylab mobil
moslashuvchanlik
auditi: public dashboard'dagi soatlik jadval mobilda matn kesilib
qolishi (CSS Grid `1fr` vs `minmax(0,1fr)` xatosi + klass nomi
to'qnashuvi) tuzatildi; audit jarayonida Telegram kanal sozlamalari
sahifasining anonim foydalanuvchi uchun 500 xato bilan qulashi ham
topilib tuzatildi (mobilga aloqasi yo'q, lekin muhim xavfsizlik/barqarorlik
bugi) — ~25 sahifa tekshirilib, boshqa muammo topilmadi; tafsilot
`docs/CHANGELOG.md` 3.51-bo'limda); bundan oldin: Telegram ulash: xom HTTP redirect
ba'zi brauzer/OS'larda "hech narsa ochilmasligi"ga sabab bo'lgani
aniqlanib, o'rniga har doim ko'rinadigan/bosiladigan tugmali oraliq
sahifa qilindi — `docs/CHANGELOG.md` 3.50-band); bundan oldin:
Telegram ulash tugmasidagi `target="_blank"` real foydalanuvchi
sinovida "qora oyna" osilib qolishiga sabab bo'lgani aniqlanib, bir
xil tabga qaytarildi (3.49-band); bundan oldin: Telegram ulash 1
bosishga tushirildi (oldin ikkinchi, ko'zga tashlanmaydigan tugmani
bosish kerak edi),
botga kirganda tushuntirish matni qo'shildi (bot description + jim
qolgan `/start`ga javob), va tadbirga mas'ul tayinlanganda/qayta
tayinlanganda Telegram orqali xabar boradigan bo'ldi — eslatmalar
tizimi esa allaqachon Phase 7'dan beri to'liq ishlagani aniqlandi,
kod tegilmadi; tafsilot `docs/CHANGELOG.md` 3.48-bo'limda); bundan
oldin: Registratsiyada minimal parol uzunligi 12'dan 8ga tushirildi
(`docs/CHANGELOG.md` 3.47-band); bundan oldin:
Hisobotlar: sana oralig'ini tanlab
bo'lmasligi bugi tuzatildi (`ReportFilterForm.date_range()` `period`
qiymatidan qat'iy nazar aniq sanalarga ustunlik beradi + JS
sinxronizatsiya); Excel eksporti foydalanuvchi so'rovi bo'yicha bitta
varaqqa qayta qurildi — Tadbirlar (sana/xona/davomat/mas'ul bitta
qatorda) → Band xodimlar → Xulosa → Nashrlar tartibida; tafsilot
`docs/CHANGELOG.md` 3.46-bo'limda); bundan oldin: Hisobotlar bo'limining
Excel eksportiga oy bo'yicha guruhlash, "Attendees" (ishtirokchilar) va
"Busy staff" (band xodimlar) varaqlari qo'shildi (3.45-band); bundan
oldin: Telegram kanal integratsiyasi uchidan-uchigacha
sinaldi — guruhga ulandi, lekin rasmli avtomatik post `IEMS_BASE_URL`ning
eskirgan LAN IP'iga (`10.34.12.2` → haqiqiysi `10.34.12.152`) bog'liqligi
sababli ishlamadi; shu jarayonda `register-tasks.ps1`dagi loyiha-yo'li bugi
tuzatildi, barcha deploy skriptlaridagi eski IP yangilandi, `telegram_poll`
uchun 4-chi Windows Scheduled Task tayyorlandi (hali faollashtirilmagan) —
tafsilot `docs/CHANGELOG.md` 3.43-bo'limda); bundan oldin: Telegram bot
integratsiyasi real token bilan yoqildi (@docker_manajer_bot) va
`client.py`dagi `getUpdates` timeout bug'i tuzatildi; bundan oldin: public
dashboard'da
dark mode uzun sahifalarda ochiq fon chizig'i tuzatildi (`.public-shell`ning
mavjud bo'lmagan CSS o'zgaruvchisi); shifokorlar uchun ishlatib bo'lmaydigan
Tadbirlar/Taqvim/Hisobotlar bo'limlari sidebar va bosh sahifadan
yashirildi (DOCTOR roli hech qanday capability'ga ega emasligi
sababli); bundan oldin: dark mode'da login/register matni ko'rinmay
qolish bug'i, loyiha bo'ylab qo'shimcha audit, filtr iconka/tarjima
bug'lari — to'liq tafsilot `docs/CHANGELOG.md`dagi 3.25–3.41-bo'limlarda)

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

## 3. Joriy holat (qisqa xulosa — to'liq tarix uchun `docs/CHANGELOG.md`ga qarang)

**Loyiha holati: barqaror, ishlaydigan.** `manage.py check` va to'liq test
to'plami (`pytest tests/`, e2e/human_acceptance/visual_baseline bundan
mustasno) doim tekshiriladi — joriy holat: **420 test o'tadi**, ma'lum
muvaffaqiyatsizlik yo'q. Endi CI ham bor: har push/PR'da GitHub Actions
orqali `ruff` + `manage.py check` + `pytest` avtomatik ishga tushadi.

### So'nggi yakunlangan yirik ishlar (2026-09-24 holatiga)

- **Public QR check-in — ikkita xatti-harakat tuzatildi** (3.56-band):
  tadbir hali boshlanmagan bo'lsa sahifada "⏳ Tadbir hali boshlanmagan —
  HH:MM da boshlanadi" ogohlantirishi chiqadi (check-in 60 daqiqa oldin
  ochilishi o'zgartirilmadi); "bir vaqtda bitta tadbir" qoidasi endi
  sessiya emas, bazadagi yozuvlar + brauzer tokeni asosida ishlaydi.
  **Muhim**: ikkala mantiq ham aslida buzilmagan edi — foydalanuvchi
  ko'rgan holat 60 daqiqalik oyna va sessiyaning yo'qolishi bilan
  izohlandi.
- **Yordamchi vosita fayllari repozitoriydan olib tashlandi** (3.55-band):
  `.claude/`, `.claude-flow/`, `.swarm/`, `.mcp.json`, `CLAUDE.md` — 351
  fayl. **Diskda qoladi**, `.gitignore`da. Commit xabarlariga attribution
  qatori qo'shilmaydi. Git tarixi ataylab qayta yozilmadi.
- **Foydalanuvchilar sahifasi (`/users/`) qayta dizayn qilindi** (3.54-band):
  KPI kartalari + uchta guruhlangan bo'lim (Kutilayotgan/Faol/Bloklangan),
  karta ko'rinishidagi foydalanuvchilar, "Kutilmoqda" va "Bloklangan"
  holatlari ajratildi, o'chirish funksiyasi qo'shildi (faqat faol
  foydalanuvchilar uchun, tadbir tarixiga bog'langanlar himoyalangan).
- **Telegram xabarlari cheklandi** (3.54-band): endi faqat mas'ul etib
  tayinlanganlik xabari va rejalashtirilgan eslatmalar boradi. Tasdiqlash
  bosqichlari (submitted/approved/rejected va h.k.) uchun Telegram xabari
  yuborilmaydi — ilova ichidagi bildirishnoma ishlaydi.

### Bundan oldingi yirik ishlar (2026-09-22 holatiga)

- **Ultra Review — production-readiness auditi va tuzatishlar**: 8
  yo'nalishli (xavfsizlik, mantiq, ishlash, API, arxitektura, testlar,
  DevOps, bog'liqliklar) to'liq audit + verifikatsiya. Eng muhimi:
  production Windows Scheduled Task'lar `DJANGO_SETTINGS_MODULE`ni hech
  qachon o'rnatmasdi (production aslida `local` sozlamalarda ishlar edi) —
  hal qilindi, **faqat `register-tasks.ps1`da**, `run-web.ps1` (lokal dev)
  ataylab tegilmadi. Boshqa tuzatishlar: publications API ruxsati, DRAFT
  conflict bugi, publish idempotentligi, Docker restart/healthcheck,
  statik fayl serveri (`whitenoise`), N+1 so'rovlar, RBAC test kengaytmasi,
  GitHub Actions CI. To'liq ro'yxat: `docs/CHANGELOG.md` 3.53-bo'lim,
  hisobot: `REVIEW_REPORT.md`.

### Bundan oldingi yirik ishlar (2026-09-16 holatiga)

- **Shifokor moduli**: ro'yxatdan o'tish, profil, band vaqt boshqaruvi (endi
  o'chirish faqat administratorga — o'z-o'zini "band/erkin" qilib
  o'ynash imkoniyati yopilgan), tadbirga ma'ruzachi sifatida biriktirish,
  band bo'lsa saqlashni to'liq bloklash.
- **Foydalanuvchilarni boshqarish** (`/users/`) — Django admin'siz
  tasdiqlash/bloklash, shifokorlarning band vaqtini admin nomidan
  qo'shish/o'chirish.
- **Profil sahifasi** — rasm yuklash (yoki bosh harflardan avtomatik
  belgi), KPI ko'rinishidagi faoliyat xulosasi, "biriktirilgan/boshqaruv/
  ma'ruzachi" tadbirlar ro'yxati (o'tgan/kelayotgan bo'lib ajratilgan) va
  profil sahifasining o'zida eng yaqin uchrashuvlar ro'yxati.
- **5 bosqichli tadbir yaratish wizardi** — to'liq qayta ishlab chiqilgan
  dizayn, ikkita real funksional bug (soxta validatsiya xatolari, ishlamaydigan
  "Orqaga" tugmasi) tuzatilgan.
- **Bildirishnoma tizimi** — qo'ng'iroq belgisi, kirganda ko'rinadigan toast,
  ro'yxatni ochish "hammasini o'qilgan" qiladi.
- **Public dashboard / TV devor ekrani / rahbariyat paneli** — vizual audit
  o'tkazilgan, bir nechta CSS/JS bug tuzatilgan (jumladan "HOZIR" vaqt
  chizig'i va rate-limit muammosi).
- **Tarjima (uz/ru/en/tr)** — loyiha bo'ylab to'liq audit o'tkazilgan,
  yetishmayotgan va buzilgan yozuvlar tuzatilgan.
- **Ma'ruzachilar sahifasi** — sidebar'da noto'g'ri bo'lim yoritilishi
  (`nav_key` bug'i) tuzatildi.
- **"Band shifokorlar" bo'limi** — public dashboard'ga rahbariyat uchun
  yangi KPI-uslubidagi bo'lim qo'shildi (qaysi shifokor hozir/bugun/shu
  hafta band va sababi).
- **Taqvim** — FullCalendar "uz" lokali uchun qo'lda oy/hafta nomlari,
  nav pill (4-bo'lim uchun "yopishib qolish" bug'i), strelka iconkasi
  (asl sabab: `calendar.css`da ikkita joyda yopilmagan `@media` bloki,
  bu butun bir CSS bo'limini tasodifan faqat mobil rejimga
  cheklab qo'ygan edi) va filtr panelining ikki qatorga bo'linib
  ketishi tuzatildi.
- **To'liq loyiha auditi (topshirishdan oldin)** — tr tarjimadagi 8 ta
  yangi satr regressiyasi, `.has-error` forma-xato stilining butunlay
  yo'qligi, yangi "Band shifokorlar" sahifasida `Cache-Control: no-store`
  yo'qligi, `psycopg[binary]` versiyasiz ekanligi, repo'da 18MB tarixiy
  QA skrinshot va eski debug-artefakt (`scratch_py_missing.json`)
  saqlanib qolgani — barchasi topilib tuzatildi.
- **Telefon/email validatsiyasi** — telefon maydoni (registratsiya,
  tashkilot, homiy formalari) avval hech qanday format tekshiruvisiz edi;
  endi faqat raqam/`+ - ( )` qabul qiladi, 9-15 raqam oralig'ini talab
  qiladi, mobil klaviaturani raqamli qiladi va yozish jarayonida harflarni
  avtomatik tozalaydi. Registratsiya sahifasida xato maydon endi qizil
  chegara bilan ajratiladi (avval faqat matn ko'rinardi).
- **Ro'yxatdan o'tish tasdiqlash sahifasi** — haqiqiy bug tufayli
  (`base.html`dagi `{% if messages %}` faqat autentifikatsiyadan o'tgan
  foydalanuvchilar uchun ishlardi) "arizangiz adminga yuborildi" xabari
  hech qachon ko'rinmasdi. Endi alohida sahifa: ✓ belgisi, foydalanuvchi
  nomi va 3 bosqichli tushuntirish ("ariza yuborildi → admin ko'rib
  chiqmoqda → tizimga kirasiz").
- **Tasdiqlanmagan hisob bilan kirish** — to'g'ri login/parol, lekin
  hali faollashtirilmagan hisob uchun endi aniq "arizangiz ko'rib
  chiqilmoqda" xabari chiqadi (avval umumiy "login/parol noto'g'ri"
  xabari bilan bir xil edi). Shu jarayonda `login.html`da xato matnining
  qattiq kodlangani (forma xatosi mazmunidan qat'iy nazar doim bir xil
  matn chiqishi) ham topilib tuzatildi. Yangi `User.approved_at`
  maydoni "hech qachon tasdiqlanmagan" va "avval tasdiqlangan, keyin
  o'chirilgan" holatlarni farqlaydi.
- **Ro'yxat sahifalari filtri** — ikkita mustaqil bug: (1) qidiruv
  maydonining `padding-left`i umumiy `input[type="search"]` qoidasi
  tomonidan bosib qolinib, matn lupacha iconkasi ustiga yopishib
  qolardi (CSS specificity muammosi — endi ota-ona klass bilan
  scope qilindi); (2) `uz.po`da "Barcha holatlar" tarjimasi tasodifan
  "Barcha xonalar" bo'lib qolgan edi (avtomatik tarjima vositasining
  xato fuzzy-match natijasi) — status filtri barcha ro'yxat
  sahifalarida noto'g'ri nom bilan chiqardi. Shu skanerlash orqali
  yana ikkita shunga o'xshash uz.po korruptsiyasi (K-ONE shiori va
  "Operatsion holatda" yozuvi) ham topilib tuzatildi.
- **Public dashboard dark mode + shifokorlar uchun yashirin bo'limlar**
  — `.public-shell`ning mavjud bo'lmagan CSS o'zgaruvchisiga bog'liq
  fon rangi (uzun sahifalarda ochiq chiziq qoldirardi) tuzatildi;
  DOCTOR roli `ROLE_CAPABILITIES`da umuman yo'qligi sababli
  Tadbirlar/Taqvim/Hisobotlar/"Yangi tadbir" havolalari (403 qaytarardi)
  sidebar va bosh sahifadan shifokorlar uchun yashirildi.
- **Telegram bot integratsiyasi yoqildi** — real token bilan `.env`ga
  sozlandi (@docker_manajer_bot), `getMe` bilan tasdiqlandi.
  `apps/notifications/telegram/client.py`da haqiqiy bug topildi:
  `get_updates()` server tomonida 20s long-poll so'rasa-da, client
  soket timeout'i 8s bo'lib qolgan edi — shu sababli har safar yangi
  xabar kelmasa, so'rov darhol xato bilan yiqilardi. Tuzatildi
  (`_call()`ga ixtiyoriy `timeout` qo'shildi). Yana bir bug topildi:
  jarayon istalgan vaqtinchalik tarmoq xatosida butunlay yiqilardi —
  endi `TelegramTransientError` backoff bilan qayta uriniladi, faqat
  `TelegramPermanentError` jarayonni to'xtatadi. `telegram_poll`
  hozircha faqat lokal terminal orqali fon jarayonida ishlayapti.
- **Telegram guruh/kanal integratsiyasi va deploy skript bug'lari** —
  `TelegramChannelSettings` orqali guruhga xabar yuborish sinaldi va
  ishlayotgani tasdiqlandi; rasmli avtomatik post `IEMS_BASE_URL`ning
  eskirgan LAN IP'iga bog'liqligi sababli ishlamadi (hal qilinmagan,
  4-bo'lim). Shu jarayonda `register-tasks.ps1` va
  `compile_po_polib.py`da bir xil turdagi loyiha-yo'li bugi topilib
  tuzatildi, 170 ta tarixiy skript arxivlandi, `tr.po`da 6 ta semantik
  tarjima xatosi tuzatildi.
- **Hisobotlar — Excel eksportiga oy/ishtirokchi/band-xodim varaqlari
  qo'shildi** — mavjud eksport tugmasi (`/reports/`) endi "Attendees"
  va "Busy staff" varaqlarini ham chiqaradi, "Events" varag'iga "Month"
  ustuni qo'shildi (`docs/CHANGELOG.md` 3.45-band).
- **Hisobotlar — sana oralig'i bugi tuzatildi, Excel bitta varaqqa
  qayta qurildi** — foydalanuvchi fikri asosida: sana tanlash endi
  ishlaydi (real bug edi), Excel endi bitta "Report" varag'ida
  Tadbirlar → Band xodimlar → Xulosa → Nashrlar tartibida
  (`docs/CHANGELOG.md` 3.46-band).

Har bir ishning **to'liq tafsiloti, sababi va tekshiruv usuli** —
`docs/CHANGELOG.md` faylida, xronologik tartibda (3.1 dan boshlab).

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
4. ~~**`scripts/` papkasi 100+ bir martalik skriptlar bilan to'lib ketgan**~~
   **HAL QILINDI (2026-09-21)**: 170 ta tarixiy bir martalik skript
   `scripts/archive/`ga ko'chirildi (`git mv`, tarix saqlangan). Faqat
   hali foydali vositalar qoldi: `compile_po*.py`, `scan_py_i18n.py`,
   `load_phase10.py`, `update_user.py` va barcha `.ps1` operatsion skriptlar.
5. **`static/css/workspace_corrupted.css`** nomli fayl commit tarixida o'chirilgan holat
   ko'rinadi (Phase 2 diffida `-451` qator) — bu fayl endi mavjud emasligini tasdiqlash kerak.
6. ~~**`locale/tr/`** — turkcha tarjima fayllari mavjud...~~ **HAL QILINDI
   (`docs/CHANGELOG.md` 3.20-band, 2026-09-12)**: foydalanuvchi turkchani ham
   to'liq qo'llab-quvvatlash kerakligini tasdiqladi. Endi `tr` to'liq tarjima
   qilingan, 224 ta buzilgan yozuv tuzatilgan.
7. ~~**`apps/events` ichida ~111 ta ... yo'q msgid**~~ **HAL QILINDI
   (`docs/CHANGELOG.md` 3.20-band, 2026-09-12)**: butun loyiha bo'ylab (faqat `apps/events` emas)
   to'liq tarjima auditi o'tkazildi, 487 ta yetishmayotgan matn barcha 4 tilga
   qo'shildi. **`tr.po` semantik audit — QISMAN HAL QILINDI (2026-09-21,
   `docs/CHANGELOG.md` 3.44-band)**: barcha 1481 ta `tr.po` yozuvi qo'lda (AI
   fork orqali) o'qib chiqildi, 6 ta aniq false-cognate xato topilib tuzatildi
   ("Telgraf"→"Telegram", "hoparlör"→"konuşmacı" va h.k.). **QOLDIQ XAVF hali
   ham bor**: bu audit ham inson-malakali tarjimon darajasidagi kafolat emas,
   faqat "sezilarli darajada noto'g'ri" xatolarni topa oladi — nozik
   uslub/registr xatolari uchun hali ham professional proofreading tavsiya
   etiladi.
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
    — "o'lik maydonlar"** (`docs/CHANGELOG.md` 3.16-bandga qarang). Admin/forma/API orqali
    sozlanadi, lekin hech qanday workflow qarori (tasdiqlash, override) ularni
    o'qimaydi — har qanday tadbir turi bir xil qat'iy tasdiqlash yo'lidan
    o'tadi. Agar bu maydonlar amaliy ma'no kasb etishi kerak bo'lsa (masalan,
    ba'zi tadbir turlari tasdiqlashsiz to'g'ridan-to'g'ri PLANNED/APPROVED
    bo'lishi kerak bo'lsa), bu — alohida, foydalanuvchi bilan kelishilishi
    kerak bo'lgan biznes-qoida qarori, chunki hozirgi testlar joriy
    (barcha turlar bir xil) xatti-harakatga tayanadi.
11. **Dark mode faqat login/register va public dashboard sahifalarida
    mavjud** — autentifikatsiyadan o'tgan workspace/admin qismida
    (`templates/base.html`) tema almashtirish tugmasi umuman yo'q va
    `workspace.css`/`components.css`da `[data-theme="dark"]` qoidalari
    yo'q. Agar kelajakda butun tizim uchun dark mode kerak bo'lsa, bu —
    katta, alohida ish (barcha ichki sahifalar CSS'ini qayta ko'rib
    chiqishni talab qiladi), hozircha so'ralmagan.
12. **`telegram_poll` production'da supervised process ostida emas — QISMAN
    HAL QILINDI (2026-09-21, `docs/CHANGELOG.md` 3.43-band)**:
    `scripts/register-tasks.ps1`ga "IEMS Telegram Poll" nomli 4-chi
    Windows Scheduled Task qo'shildi (Web/Worker/Beat bilan bir xil
    naqsh). **Hali faollashtirilmagan** — foydalanuvchi
    `register-tasks.ps1`ni o'zi keyinroq ishga tushirishni so'radi.
13. ~~**`manage.py`/`config/wsgi.py`/`config/celery.py` — barchasi
    `DJANGO_SETTINGS_MODULE`ni `config.settings.local`ga `setdefault`
    qiladi**~~ **HAL QILINDI (2026-09-22, Ultra Review,
    `docs/CHANGELOG.md` 3.53-band)**: `scripts/register-tasks.ps1`dagi har
    bir Scheduled Task endi `cmd.exe` wrapper orqali
    `DJANGO_SETTINGS_MODULE=config.settings.production`ni majburiy
    o'rnatadi (Task Scheduler XML v1.3'da alohida `<Environment>` elementi
    yo'qligi sababli). **Muhim**: `manage.py`/`wsgi.py`/`celery.py`dagi
    `setdefault("...", "local")` o'zi o'zgarmadi (bu — lokal dev uchun
    to'g'ri sukut) — faqat production launch nuqtasi (Scheduled Task)
    aniq `production`ni majburlaydi. `scripts/run-web.ps1` (kundalik lokal
    dev skripti) ataylab tegilmadi. **Yangi ochilgan qatorlar**: shu
    tuzatish davomida production'da endi haqiqatan `production.py` ishga
    tushishi mumkinligi sababli, ikkita qo'shimcha muammo ham aniqlanib
    parallel tuzatildi — production logging (`pythonw.exe` konsolsiz
    ishlagani uchun loglar yo'qolib qolishi, fayl handler qaytarildi) va
    `DEBUG=False`da statik fayllar uzatilmasligi (`whitenoise` qo'shildi).
14. **Eskirgan LAN IP (`10.34.12.2`) tarixiy bir martalik QA/screenshot
    skriptlarida hali ham uchraydi** (`scripts/capture_*`,
    `scripts/verify_phase27_*` va h.k., 2026-09-21 aniqlandi) — bular
    runtime'ga aloqasi yo'q, 4-band (scripts/ tozalash)ga bog'liq,
    ataylab tuzatilmadi.
15. **`apps/events/views.py` — 1250+ qatorli "god file"** (2026-09-22,
    Ultra Review arxitektura tahlili). 30+ view klassi, ba'zi joylarda
    biznes-logika (bildirishnoma matni yaratish) to'g'ridan-to'g'ri view
    qatlamida. Takrorlangan "owner-or-admin" ruxsat tekshiruvlari
    `apps.events.selectors.can_manage_event()`ga birlashtirildi, ammo
    faylning o'zi hali bo'linmagan — bu katta, alohida refaktoring ishi
    (regressiya xavfi bor), hali so'ralmagan.
16. **Repo papkasida vaqti-vaqti bilan bo'sh (0-baytli), tasodifiy nomli
    fayllar paydo bo'lyapti** (masalan `bool`, `raise`, `restart`, `3.13`,
    `dict[str` — 2026-09-22 kuzatildi). Manba — lokal ishlab chiqish
    muhitidagi fon jarayoni/hook skriptlari (repoga kirmaydi), aniq kod
    joyi hali topilmadi. Bir marta kuzatilgan holatda shu jarayonda
    `scripts/run-web.ps1`ga so'ralmagan `DJANGO_SETTINGS_MODULE=production`
    qatori qo'shilgani va `REVIEW_REPORT.md` o'chirilgani ham qayd etildi —
    demak bu shunchaki bo'sh-fayl-yaratish emas, balki **faol jarayon repo
    fayllarini ham o'zgartirmoqda**. Hozircha fayllar qo'lda o'chirilmoqda;
    takrorlansa lokal fon jarayonlarini alohida tekshirish kerak.
17. **Public check-in anonim — "bir vaqtda bitta tadbir" qoidasini to'liq
    kafolatlab bo'lmaydi** (2026-09-24, `docs/CHANGELOG.md` 3.56-band).
    Qoida endi bazaga bog'langan, lekin yagona identifikator — brauzerdagi
    `event_checkin_token` cookie'si. Odam QR'ni butunlay boshqa
    telefon/brauzerdan ochsa, uni avvalgi ro'yxatdan o'tishi bilan bog'lab
    bo'lmaydi. 100% kafolat uchun check-in'da shaxsni aniqlash (telefon
    raqami, SMS tasdiq yoki login) joriy etilishi kerak — bu alohida
    biznes qarori, hali so'ralmagan.
18. **Git tarixida AI attribution qolgan** (2026-09-23, 3.55-band): 54
    commitdan 34 tasida `Co-Authored-By` qatori, 3 ta eski commitda esa
    `.claude` fayllari bor. Foydalanuvchi tarixni qayta yozmaslikka qaror
    qildi (barcha commit ID'lari o'zgarib ketardi). Kelgusi commitlarga
    attribution qatori **qo'shilmaydi**.

---

## 5. Keyingi qadamlar (ochiq savollar — foydalanuvchidan tasdiq kerak)

- [x] Dashboard/Calendar: o'tish animatsiyalari, uz vaqt bugi, til indikatori, rang
      palitrasi, tarjimalar (2026-09-10 — tafsilot `docs/CHANGELOG.md` 3.1-bo'limida).
- [ ] Sayt bo'ylab qolgan 52/51/37 bo'sh msgstr (uz/ru/en, dashboard/calendar'ga
      aloqasi yo'q) — alohida so'rov bilan qaraladi.
- [x] Public dashboard qayta qurilishi, HOZIR chizig'i va rate-limit bug'lari
      tuzatildi (2026-09-15/16 — `docs/CHANGELOG.md` 3.25–3.31-bo'limlar).
- [ ] `apps/approvals` app'ining kelajagi haqida qaror: to'ldirish, birlashtirish yoki
      olib tashlash.
- [ ] `ALLOWED_HOSTS`dagi `"*"` — foydalanuvchi tomonidan ataylab, bitta tarmoqdagi
      qurilmalar loyihani ko'ra olishi uchun qo'yilgan (tasdiqlangan, 2026-09-15).
      Production'ga chiqarilganda tashqi internetdan ochiq bo'lmasligi hali ham
      alohida tekshirilishi kerak.
- [ ] `scripts/` papkasini tozalash/tartibga solish bo'yicha qaror.
- [ ] `docs/CHANGELOG.md`ning 3.30-bandida topilgan CSS-klass muammosi loyihaning KO'P joyida uchragan
      (profil, wizard, venue-status, publications) — lekin bosh sahifa
      (`workspace/home.html`)dagi `exec-panel--timeline/--agenda/--rooms/--intelligence`
      kabi ba'zi klasslar hali ham CSS'da yo'q (vizual ta'siri hozircha
      sezilmagan, chunki bazaviy `.exec-panel` yetarli ko'rinadi — lekin
      kelajakda shu modifikatorlarga bog'liq stil qo'shilsa, avval CSS'da
      aniqlanishi kerak).
- [ ] Rahbariyat paneli/TV devor ekranining "band" (occupied) holati hali
      qo'lda sinovdan o'tkazilmagan (bu sessiyada faqat "hammasi bo'sh" holat
      ko'rilgan) — real band zal bilan vizual tekshiruv tavsiya etiladi.
- [ ] Har bir yangi funksional so'rov kelganda, ushbu fayl "Amalga oshirilgan ishlar" va
      "Joriy holat" bo'limlarini **darhol** (keyingi so'rovga o'tishdan oldin)
      yangilab borish — 3.25–3.31-bo'limlar bu safar orqaga qarab, foydalanuvchi
      eslatgandan keyin yozildi.
- [x] Production'da `DJANGO_SETTINGS_MODULE` majburlanmasligi — hal qilindi
      (2026-09-22, 4-bo'lim 13-band, `docs/CHANGELOG.md` 3.53-band).
- [ ] `apps/events/views.py`ni (1250+ qator) kichik modullarga bo'lish —
      4-bo'lim 15-band, katta refaktoring, hali so'ralmagan.
- [ ] Repo papkasida o'zidan-o'zi paydo bo'layotgan bo'sh axlat fayllar —
      manba aniqlanmagan (4-bo'lim 16-band), takrorlansa chuqur diagnostika
      kerak.
- [ ] Public check-in'da shaxsni aniqlash (telefon raqami / SMS / login) —
      "bir vaqtda bitta tadbir" qoidasini brauzerdan qat'i nazar ishlatish
      uchun kerak (4-bo'lim 17-band). Biznes qarori, hali so'ralmagan.
- [ ] Check-in 60 daqiqa oldin ochilishi shundayligicha qoldirildi
      (2026-09-24 da foydalanuvchi bilan kelishildi) — agar kelajakda
      "faqat boshlangandan keyin" kerak bo'lsa,
      `Event.effective_checkin_opens_at` o'zgartiriladi.

---

## 6. Ishlash tartibi (workflow qoidasi)

**Ikki fayl, ikki maqsad** (2026-09-16dan boshlab):
- **`goals.md`** (shu fayl) — QISQA saqlanadi: loyiha haqida umumiy ma'lumot,
  joriy holatning bir necha qatorlik xulosasi, texnik qarz va ochiq keyingi
  qadamlar. Har safar ishni boshlashdan oldin **to'liq** o'qiladi — shuning
  uchun qisqa bo'lishi muhim.
- **`docs/CHANGELOG.md`** — TO'LIQ, batafsil tarixiy jurnal: har bir sessiyada
  nima qilingani, nega, qanday tekshirilgani. Faqat kerak bo'lganda (masalan,
  "nega bunday qilingan edi" degan savolga javob qidirilganda) ochiladi.

**Har bir muhim o'zgarishdan keyin (KEYINGI SO'ROVGA O'TISHDAN OLDIN, orqaga
qarab emas):**
1. `docs/CHANGELOG.md`ning oxiriga yangi, batafsil yozuv qo'shing (mavjud
   `### N.NN Sarlavha (sana)` formatiga ergashib).
2. `goals.md`dagi 3-bo'lim ("So'nggi yakunlangan yirik ishlar") va 5-bo'lim
   ("Keyingi qadamlar")ni qisqa yangilang — faqat xulosa, tafsilot emas.
3. Yangi noaniqlik yoki texnik qarz topilsa — `goals.md`ning 4-bo'limiga qo'shing.
4. Katta arxitekturaviy qarorlar (masalan, app qo'shish/olib tashlash) — avval
   foydalanuvchi bilan tasdiqlanadi, keyin yoziladi.
