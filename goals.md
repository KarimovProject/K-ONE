# IEMS — Maqsadlar va Holat Reyestri

> **QOIDA:** Ushbu loyiha ustida har qanday amal (kod yozish, refactor, feature qo'shish,
> bug fix) boshlanishidan **oldin** shu fayl to'liq o'qilishi shart. Har bir muhim
> o'zgarishdan keyin ("Joriy holat" va "Keyingi qadamlar" bo'limlari) yangilab borilishi kerak.
> Bu qoida `CLAUDE.md`da ham mustahkamlangan.

Oxirgi yangilanish: 2026-09-21 (tasdiqlanmagan hisob bilan kirishga
urinilganda "arizangiz ko'rib chiqilmoqda" aniq xabari qo'shildi —
shu jarayonda login.html'dagi qattiq kodlangan xato-matn bug'i ham
topilib tuzatildi; bundan oldin: ro'yxatdan o'tgandan keyingi tasdiqlash
sahifasi, telefon/email validatsiyasi, topshirishdan oldingi to'liq
audit — to'liq tafsilot `docs/CHANGELOG.md`dagi 3.25–3.37-bo'limlarda)

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
mustasno) doim tekshiriladi — joriy holat: **373 test o'tadi**, 1 ta oldindan
mavjud, ushbu loyihaga aloqasi yo'q muvaffaqiyatsizlik yo'q (barcha bilingan
muvaffaqiyatsizliklar tuzatilgan).

### So'nggi yakunlangan yirik ishlar (2026-09-16 holatiga)

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
4. **`scripts/` papkasi 100+ bir martalik skriptlar bilan to'lib ketgan**
   (`capture_phase27_*`, `verify_phase*`, `apply_*`, `fix_*`) — bular tarixiy vizual-QA
   ishlari, asosiy runtime'ga aloqasi yo'q. Kelajakda arxivlash yoki `scripts/archive/`ga
   ko'chirish mumkin (foydalanuvchi tasdiqlasa).
5. **`static/css/workspace_corrupted.css`** nomli fayl commit tarixida o'chirilgan holat
   ko'rinadi (Phase 2 diffida `-451` qator) — bu fayl endi mavjud emasligini tasdiqlash kerak.
6. ~~**`locale/tr/`** — turkcha tarjima fayllari mavjud...~~ **HAL QILINDI
   (`docs/CHANGELOG.md` 3.20-band, 2026-09-12)**: foydalanuvchi turkchani ham
   to'liq qo'llab-quvvatlash kerakligini tasdiqladi. Endi `tr` to'liq tarjima
   qilingan, 224 ta buzilgan yozuv tuzatilgan.
7. ~~**`apps/events` ichida ~111 ta ... yo'q msgid**~~ **HAL QILINDI
   (`docs/CHANGELOG.md` 3.20-band, 2026-09-12)**: butun loyiha bo'ylab (faqat `apps/events` emas)
   to'liq tarjima auditi o'tkazildi, 487 ta yetishmayotgan matn barcha 4 tilga
   qo'shildi. **QOLDIQ XAVF**: bu audit faqat "yetishmayotgan" (butunlay yo'q)
   yozuvlarni topdi. `tr.po`da tasodifan yana ikkita **sifat xatosi** (noto'g'ri
   ma'noli, lekin "yo'q" yoki "buzilgan" emas tarjima — masalan "Parol" →
   "Şartlı tahliye") vizual tekshiruv orqali topilib tuzatildi. Bu degani —
   `tr.po`da (va ehtimol boshqa tillarda ham, kamroq ehtimol bilan) shunga
   o'xshash, avtomatik dasturiy tekshiruv topa olmaydigan boshqa semantik xato
   tarjimalar qolgan bo'lishi mumkin. To'liq ishonch uchun malakali tarjimon
   tomonidan qo'lda proofreading talab qilinadi — bu alohida, katta ish.
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
