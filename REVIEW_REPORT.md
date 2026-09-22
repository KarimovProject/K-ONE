# Ultra Review hisoboti — IEMS (International Events Management System)
Sana: 2026-09-22 | Scope: butun repozitoriy | Stack: Django 5.2.16 + DRF 3.17.1 + PostgreSQL + Redis + Celery/Celery Beat, native Windows deploy (Docker faqat reference)

## 1. Umumiy xulosa

- **Production'ga tayyorlik bahosi: 6.5/10**
- **Release blocker'lar soni: 1 CRITICAL + 10 tasdiqlangan HIGH**
- Kod bazasi umuman olganda **puxta va yaxshi parvarish qilingan**: xavfsizlik nuqtai nazaridan fayl yuklash, token generatsiyasi, RBAC/object-level ruxsatlar va loyihaning o'z tarixidagi mashhur "AnonymousUser'da `.role` yo'q" bug klassi barcha tekshirilgan joylarda to'g'ri qopqonlangan; test to'plami ham toza ishlaydi (395/395 o'tadi).
- Asosiy muammo **kod emas, operatsion konfiguratsiya**: Windows'dagi haqiqiy production launch skriptlari (`register-tasks.ps1`, `run-web.ps1`) `DJANGO_SETTINGS_MODULE`ni hech qachon `config.settings.production`ga o'rnatmaydi — demak amaldagi production deploy sukut bo'yicha `config.settings.local` sozlamalarida ishlashi mumkin (DEBUG=True, xavfsiz bo'lmagan cookie'lar, HTTPS majburiy emas). Bu — yagona CRITICAL topilma va eng birinchi tuzatilishi kerak bo'lgan narsa.
- Ikkinchi darajali, ammo real: `apps/publications` API'sida ruxsat nazorati yo'qligi (istalgan autentifikatsiyadan o'tgan foydalanuvchi barcha tashkilotlarning nashrlarini ko'ra oladi), reservation-conflict logikasida DRAFT holatidagi tadbirlarning zal/vaqtni "ushlab turishi" bugi va ijtimoiy tarmoqqa nashr qilishda qayta urinishda ikki marta post qilinish xavfi — bularning barchasi aniq, tasdiqlangan, `file:line` darajasida ko'rsatilgan haqiqiy bug'lar.
- CI/CD pipeline umuman yo'q — bu release jarayonini avtomatik tekshiruvsiz qoldiradi, garchi loyihaning o'zi `pytest`/`ruff`/`manage.py check`ni qo'lda ishga tushirish tartibini hujjatlashtirgan bo'lsa ham.

## 2. Statistika

| Soha | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|
| 🔐 Xavfsizlik | 1 (umumiy, DevOps bilan) | 0 | 1 | 1 |
| 🐛 To'g'rilik va mantiq | 0 | 2 | 1 | 0 |
| ⚡ Ishlash va DB | 0 | 1 | 4 | 3 |
| 🔌 API dizayni va validatsiya | 0 | 2 | 2 | 2 |
| 🏗️ Arxitektura va kod sifati | 0 | 1 | 2 | 4 |
| 🧪 Testlar va ishonchlilik | 0 | 1 | 1 | 0 (1 rad etildi) |
| 🐳 DevOps va infratuzilma | 1 (umumiy, Xavfsizlik bilan) | 3 | 3 | 4 |
| 📦 Bog'liqliklar va konfiguratsiya | 0 | 1 (past ta'sirli) | 1 | 2 |
| **Jami** | **1** | **11** | **15** | **16** |

## 3. 🚨 Release blocker'lar (CRITICAL + HIGH, tasdiqlangan)

### [CRITICAL] Windows Scheduled Task'lar / launch skriptlari `DJANGO_SETTINGS_MODULE`ni hech qachon o'rnatmaydi — production `local` sozlamalarida ishlashi mumkin
- Soha: Xavfsizlik + DevOps (ikkala jamoa mustaqil topgan, birlashtirilgan)
- Joylashuv: `manage.py:7`, `config/wsgi.py:14`, `config/celery.py:5`, `scripts/register-tasks.ps1`, `scripts/run-web.ps1`
- Dalil: `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")` — uchala kirish nuqtasida ham; `register-tasks.ps1`dagi 4 ta Scheduled Task XML'ida `<Environment>` bloki yo'q; `run-web.ps1` `$env:DJANGO_SETTINGS_MODULE`ni hech qachon o'rnatmaydi. Faqat `docker-compose.yml`da to'g'ri o'rnatilgan (`DJANGO_SETTINGS_MODULE: config.settings.production`).
- Muammo: Native Windows — bu loyihaning **haqiqiy production deploy yo'li** (README/goals.md tasdiqlaydi). Agar `.env` faylida boshqa mexanizm orqali bu o'zgaruvchi majburlanmasa, tizim `config.settings.local`ga tushadi: `DEBUG=True` (sukut), `ALLOWED_HOSTS` — `["localhost","127.0.0.1","*"]`, `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` — `False`. Bu — internetdan ochiq, debug traceback'lari ko'rinadigan, xavfsiz bo'lmagan cookie'li production.
- Fix: `run-web.ps1`, `run-celery.ps1`, `run-beat.ps1` va Scheduled Task XML'ga ishga tushishdan oldin `$env:DJANGO_SETTINGS_MODULE = "config.settings.production"`ni aniq o'rnatish; yoki uchala `setdefault` chaqiruvini olib tashlab, o'zgaruvchi berilmasa xato bilan to'xtashni majburlash (jim qolib `local`ga tushishning oldini olish).
- Ishonch darajasi: yuqori (fayllar to'g'ridan-to'g'ri o'qildi va tasdiqlandi)

### [HIGH] Production logging — `pythonw.exe` + faqat `StreamHandler` = #1 bug tuzatilgach loglar butunlay yo'qoladi
- Soha: DevOps
- Joylashuv: `config/settings/base.py:202-205`, `config/settings/production.py:26-27`, `scripts/register-tasks.ps1`
- Dalil: `production_console` handler — faqat `logging.StreamHandler`, RotatingFileHandler yo'q; `production.py` root va `django.request` logger'larini faqat shu handler'ga yo'naltiradi. Barcha 4 ta Scheduled Task `pythonw.exe` orqali ishga tushadi (konsol/stdout yo'q).
- Muammo: Yuqoridagi CRITICAL bug "to'g'ri" tuzatilib, `production` sozlamalari majburlansa, ammo bu masala parallel hal qilinmasa — production loglar hech qayerga yozilmay qoladi (hozir bu faqat `local`dagi `file` handler tufayli yashiringan).
- Fix: Production LOGGING konfiguratsiyasiga faylga yozuvchi handler qo'shish, yoki Scheduled Task'larni `python.exe` + fayl'ga yo'naltirish bilan almashtirish.
- Ishonch darajasi: yuqori

### [HIGH] `docker-compose.yml`da hech qanday servisda `restart:` siyosati yo'q
- Soha: DevOps
- Joylashuv: `docker-compose.yml` (barcha 5 servis: db, redis, web, worker, beat)
- Muammo: `web`/`worker`/`beat` konteyner qulasa (xotira yetishmasligi, kutilmagan xato), qo'lda qayta ishga tushirilmaguncha o'lik holatda qoladi — o'z-o'zini davolash yo'q.
- Fix: Har bir servisga `restart: unless-stopped` qo'shish.
- Ishonch darajasi: yuqori

### [HIGH] `web`/`worker`/`beat` konteynerlarida healthcheck yo'q
- Soha: DevOps
- Joylashuv: `docker-compose.yml` (faqat `db` va `redis`da `healthcheck:` bor)
- Muammo: Orkestratsiya vositasi (yoki `docker compose`) ilova darajasidagi osilib qolishni aniqlay olmaydi — `depends_on: condition: service_healthy` faqat db/redis holatini tekshiradi.
- Fix: `web`ga HTTP health endpoint asosida (`config/health.py`/`health_checks.py` allaqachon mavjud), `worker`/`beat`ga `celery inspect ping` asosida healthcheck qo'shish.
- Ishonch darajasi: yuqori

### [HIGH] `apps/publications` API'sida ruxsat nazorati yo'q — istalgan autentifikatsiyadan o'tgan foydalanuvchi barcha tashkilotlarning nashrlarini ko'radi
- Soha: API dizayni
- Joylashuv: `apps/publications/api.py:71-78`
- Dalil: `PublicationListCreateAPIView`/`PublicationDetailAPIView` `permission_classes`ni belgilamaydi, shu sababli global sukut (`config/settings/base.py:176-178` — faqat `IsAuthenticated`) ishlaydi. Boshqa barcha master-data endpoint'lari (events, venues, organizations) aniq `CanViewMasterData` talab qiladi.
- Muammo: Har qanday rolidagi login qilgan foydalanuvchi — tizimdagi barcha tashkilotlarning nashr sarlavhasi, matni, tashqi post ID/URL va xato xabarlarini ko'ra oladi, sahifalashsiz.
- Fix: `permission_classes = (CanViewMasterData,)` (yoki tor maxsus ruxsat) qo'shish va queryset'ni foydalanuvchi mas'ul bo'lgan tadbirlar bilan cheklash.
- Ishonch darajasi: yuqori

### [HIGH] Tasdiqlanmagan raqamli parametrlar 400 o'rniga 500 xatosini keltirib chiqaradi
- Soha: API dizayni
- Joylashuv: `apps/events/api.py:263` (`VenueAvailabilityAPIView.get`)
- Dalil: `int(request.query_params.get("expected_attendees", 1))` — try/except yo'q.
- Muammo: `expected_attendees=abc` kabi raqam bo'lmagan qiymat yuborilsa, qo'lga olinmagan `ValueError` xom 500 xatosini qaytaradi.
- Fix: Boshqa joylardagi kabi (bir necha qator yuqorida sana/vaqt parsing uchun qilingani kabi) try/except bilan o'rab, 400 qaytarish.
- Ishonch darajasi: yuqori

### [HIGH] `apps/events/views.py` — 1250 qatorli, 31 ta view klassini o'z ichiga olgan "god file"
- Soha: Arxitektura va kod sifati
- Joylashuv: `apps/events/views.py` (butun fayl)
- Dalil: `wc -l` → 1250 qator, 31 ta `class ...View`. Bildirishnoma matni yaratish va yuborish (`notify_assigned_doctors`, 75-106 qatorlar) kabi biznes-logika to'g'ridan-to'g'ri view qatlamida.
- Muammo: Loyihaning o'z 500-qatorlik konventsiyasini buzadi; test qilish va qayta ishlatish qiyinlashadi (HTTP request-response tsiklisiz sinab bo'lmaydi).
- Fix: `notify_assigned_doctors` va shunga o'xshash logikani `apps/events/services/`ga ko'chirish, faylni `views/program.py`, `views/approvals.py` kabi kichikroq modullarga bo'lish.
- Ishonch darajasi: yuqori (mantroniyat/maintainability muammosi, bevosita xavfsizlik xavfi emas)

### [HIGH] DRAFT holatidagi tadbirlar conflict-tekshiruvidan chetlashtirilmagan — zal/vaqtni doimiy "egallab" qo'yishi mumkin
- Soha: To'g'rilik va mantiq
- Joylashuv: `apps/events/services/conflicts.py:36-43`, `apps/events/wizard.py:179-190`
- Dalil: `find_conflicting_events`ning `.exclude(status__in=[CANCELLED, REJECTED, DISPLACED, POSTPONED])` ro'yxatida `DRAFT` yo'q; `validate_and_lock_event_reservation` faqat `status == Event.Status.PLANNED` bo'lganda ishlaydi, ya'ni draft saqlashda hech qanday tekshiruv o'tkazilmaydi.
- Muammo: Foydalanuvchi hech qanday tasdiqlashsiz, tekshiruvsiz zal/sana/vaqt bilan draft saqlaganida, bu draft keyingi barcha `find_conflicting_events` chaqiruvlarida "band" sifatida hisoblanadi — hatto muallif uni hech qachon yubormasa ham, real tadbirlarni bloklab qo'yadi.
- Fix: `DRAFT`ni ham exclude ro'yxatiga qo'shish, yoki draft'lar rezervatsiya sifatida hisoblanmasligini boshqa yo'l bilan ta'minlash.
- Ishonch darajasi: yuqori

### [HIGH] Ijtimoiy tarmoqqa nashr qilish (`publish_publication`) tashqi API chaqiruvi davomida DB lock ushlab turadi — qulashda ikki marta post qilinish xavfi
- Soha: To'g'rilik va mantiq
- Joylashuv: `apps/publications/services.py:85-125`
- Dalil: `@transaction.atomic` butun funksiyani, jumladan `adapter.publish(...)` tashqi tarmoq chaqiruvini ham (108-qator) o'z ichiga oladi; `select_for_update()` lock butun jarayon davomida ushlab turiladi.
- Muammo: Agar worker jarayoni `adapter.publish()` muvaffaqiyatli tashqi post qilgandan keyin, ammo DB commit'dan oldin qulasa (OOM, tarmoq uzilishi) — tranzaksiya orqaga qaytadi, keyingi urinish (Celery retry yoki Beat) tashqi API'ni qayta chaqiradi va **ikkinchi marta ochiq post** yaratadi. Idempotentlik kaliti yo'q.
- Fix: `status=PUBLISHING`ni tashqi chaqiruvdan OLDIN alohida qisqa tranzaksiyada commit qilish va/yoki adapter'ga mijoz tomonidan yaratilgan idempotentlik kalitini uzatish.
- Ishonch darajasi: o'rta (aniq vaqt oynasi talab qiladi, lekin oqibati — jamoat ko'radigan ikki marta post — jiddiy)

### [HIGH] `EventDetailView` har bir sahifa yuklashda tadbirni ikki marta so'raydi
- Soha: Ishlash va DB
- Joylashuv: `apps/events/views.py:241-246`
- Dalil: `get_context_data` `self.object`dan foydalanish o'rniga `self.get_object()`ni qayta chaqiradi — bu 6 ta FK `select_related` va 2 ta M2M `prefetch_related`li so'rovni ikki marta bajaradi.
- Fix: `event = self.object` ishlatish.
- Ishonch darajasi: yuqori

### [HIGH] `publish_publication_task`ning retry/failure logikasi butunlay test qilinmagan
- Soha: Testlar va ishonchlilik
- Joylashuv: `apps/publications/tasks.py:21-31`, `tests/test_phase8_publications.py:239`
- Dalil: Mavjud yagona test `.delay`ni monkeypatch qiladi (`lambda pk: calls.append(pk)`) — task tanasi, jumladan `except`/`self.retry()` mantiqiy, hech qachon haqiqiy chaqirilmaydi.
- Muammo: Telegram/Instagram nashr qilish muvaffaqiyatsiz bo'lganda ishga tushadigan aynan shu kod yo'lida (retry_count, transient vs permanent xato ajratish) hech qanday test yo'q — bu yerdagi bug production'da jim qolib, nashr holatini buzishi mumkin.
- Fix: `PublicationAdapterError(transient=True/False)` chiqaradigan soxta adapter bilan `publish_publication_task`ni to'g'ridan-to'g'ri chaqiruvchi unit testlar qo'shish.
- Ishonch darajasi: yuqori

### [HIGH, ammo past ta'sirli] `Django==5.2.16`da e'lon qilingan DoS zaifligi (PYSEC-2026-3717) — 5.2.17'da tuzatilgan
- Soha: Bog'liqliklar
- Joylashuv: `requirements/base.txt:1`
- Dalil: `pip-audit` orqali tasdiqlangan: GeoDjango `GEOSGeometry`dagi cheksiz rekursiya. `apps/`da `django.contrib.gis`/`GEOSGeometry`/`GeometryField` ishlatilishi topilmadi.
- Muammo: Zaiflik real, ammo bu loyihada GeoDjango ishlatilmagani sababli amaliy hujum yuzasi yo'q — shunga qaramay, versiya eskirgan.
- Fix: `Django==5.2.17`ga yangilash (arzon, xavfsiz bump).
- Ishonch darajasi: yuqori

## 4. MEDIUM

### [MEDIUM] `djangorestframework==3.17.1`da ikkita e'lon qilingan zaiflik — 3.17.2'da tuzatilgan
- Soha: Bog'liqliklar | Joylashuv: `requirements/base.txt:4`
- `PYSEC-2026-3827` (`DATA_UPLOAD_MAX_MEMORY_SIZE` chetlab o'tilishi) va `PYSEC-2026-3828` (`AdminRenderer` orqali ma'lumot sizishi). `AdminRenderer` loyihada ishlatilmaydi, ta'sir cheklangan. Fix: `djangorestframework==3.17.2`ga bump.

### [MEDIUM] Lokal `.env`dagi `SECRET_KEY` zaif/dev-uslubida
- Soha: Xavfsizlik | Joylashuv: `.env` (`manage.py check --deploy` orqali W009 ogohlantirishi)
- `.env` git'ga committed emas (tasdiqlangan) — bu faqat lokal gigiyena masalasi, sizib chiqish emas. Fix: har qanday production/staging uchun uzun tasodifiy `DJANGO_SECRET_KEY` generatsiya qilish.

### [MEDIUM] `approve_event` workflow'dagi yagona `transaction.atomic()`/`select_for_update()` ishlatmaydigan status-o'tish
- Soha: To'g'rilik va mantiq | Joylashuv: `apps/events/services/workflow.py:49-97`
- Hozircha keng exclude ro'yxati orqali maskalangan, ammo `reschedule_event`/`override_event`/`execute_emergency_override`dan farqli, race condition'ga qarshi himoyasiz qoladi agar exclude ro'yxati kelajakda o'zgartirilsa.

### [MEDIUM] Zal-band-bo'lish tekshiruvi asosiy dashboard'da tadbir boshiga bitta so'rov (N+1)
- Soha: Ishlash va DB | Joylashuv: `apps/reporting/selectors.py:143-166`
- Har bir `active_today_events` elementi uchun alohida `find_conflicting_events` chaqiriladi — barcha login qilgan foydalanuvchilar ko'radigan asosiy workspace dashboard'da.

### [MEDIUM] Approval Center har sahifa yuklanishida qatorga 2 tagacha qo'shimcha so'rov
- Soha: Ishlash va DB | Joylashuv: `apps/events/views.py:547-565`
- `.exists()` va keyin `list()` — sahifalangan (15/sahifa) PENDING_APPROVAL ro'yxatining har bir qatori uchun.

### [MEDIUM] Jamoat/TV devor ekrani so'rovi keshsiz va yuqori chegarasiz
- Soha: Ishlash va DB | Joylashuv: `apps/venues/services/live_status.py:139-157`
- Kiosk polling uchun mo'ljallangan (600 so'rov/60s bilan cheklangan) endpoint'larda sana oralig'i cheksiz va natija keshlanmagan.

### [MEDIUM] Rahbariyat/hisobot dashboard'lari har renderda 25-40+ alohida COUNT/aggregate so'rov yuboradi
- Soha: Ishlash va DB | Joylashuv: `apps/reporting/analytics.py:387-407`
- Eksport funksiyalari so'ralgan `kind`dan qat'iy nazar to'liq hisobotni hisoblaydi.

### [MEDIUM] API'lar orasida xato javob formati izchil emas
- Soha: API dizayni | Joylashuv: `apps/events/api.py` (`{"error": ...}`) vs `apps/publications/api.py` (DRF `{"detail": ...}`) vs `apps/reporting/api.py` (`{"errors": form.errors}`)
- Umumiy `EXCEPTION_HANDLER` yo'q; `apps/events/api.py`dagi keng `except Exception` blogi ichki xato matnini mijozga qaytaradi (ma'lumot sizishi belgisi ham).

### [MEDIUM] Hech bir ro'yxat endpoint'ida sahifalash sozlanmagan
- Soha: API dizayni | Joylashuv: `config/settings/base.py:172-179` (`DEFAULT_PAGINATION_CLASS` yo'q)
- `EventListAPIView`, `VenueListAPIView`, `OrganizationListAPIView` va boshqalar to'liq, cheksiz queryset qaytaradi.

### [MEDIUM] `apps/events`/`apps/notifications` bir-biriga ikki tomonlama bog'langan
- Soha: Arxitektura | Joylashuv: `apps/events/views.py:44-46`, `apps/notifications/forms.py:4` va boshqalar
- Har ikkala tomon ham bir-birining model/servis ichki qismlariga to'g'ridan-to'g'ri kiradi — birortasini mustaqil o'zgartirish qiyin.

### [MEDIUM] Bir xil "owner-or-admin" ruxsat tekshiruvi bir necha view'da nusxalangan
- Soha: Arxitektura | Joylashuv: `apps/events/views.py:466-468`, `656-658`
- Kelajakda qoidaga o'zgartirish kiritilsa, barcha nusxalarni yangilash talab qilinadi.

### [MEDIUM] RBAC test qamrovi juda tor
- Soha: Testlar | Joylashuv: `tests/test_rbac.py` (25 qator, 2 test)
- Faqat bitta rol (MANAGEMENT_RESPONSIBLE) va bir nechta capability tekshiriladi; barcha rollar uchun "sukut bo'yicha rad etish" tasdiqlanmagan.

### [MEDIUM] Docker yo'lida nginx/reverse proxy yo'q — statik fayllarni kim xizmat qilishi noaniq
- Soha: DevOps | Joylashuv: `docker-compose.yml`, `config/settings/production.py:22`
- `ManifestStaticFilesStorage` ishlatiladi, ammo compose faylida statik fayllarni HTTP orqali uzatuvchi hech narsa yo'q (WhiteNoise ham topilmadi).

### [MEDIUM] CI/CD pipeline umuman yo'q
- Soha: DevOps | Joylashuv: repo ildizi (`.github/workflows/`, `.gitlab-ci.yml` — ikkalasi ham yo'q, tasdiqlangan)
- Test/lint/`manage.py check --deploy` push/PR'da avtomatik ishga tushmaydi — hammasi qo'lda.

## 5. LOW (qisqa ro'yxat)

- API'dagi ba'zi action endpoint'lar (`EventSubmitAPIView` va h.k.) serializer'siz `request.data.get()` bilan ishlaydi — izchillik masalasi.
- API versiyalash yo'q (hozircha ichki AJAX API bo'lgani uchun past xavf).
- `apps/events/views.py`da 3 joyda ortiqcha `or request.user.is_superuser` (bu allaqachon `user_has_capability` ichida hisobga olingan) — chalkashtiruvchi, lekin zararsiz.
- `apps/notifications/views.py` o'z servis qatlamini chetlab o'tib, `TelegramClient`ni to'g'ridan-to'g'ri chaqiradi.
- `apps/reporting/analytics.py` 7 ta boshqa app'dan to'g'ridan-to'g'ri model import qiladi (selector o'rniga) — boshqa reporting modullariga nisbatan izchil emas.
- Notifications context processor har so'rovda 2 ta qo'shimcha so'rov beradi (unread badge uchun).
- `TelegramTestView` Telegram API'ni request-response tsikli ichida sinxron chaqiradi.
- Eksport view'lari so'ralgan turidan qat'iy nazar barcha hisobot bo'limlarini hisoblaydi.
- `.gitignore`dagi `*.log` naqshi aylantirilgan log fayllarni (`web.log.1`) qamramaydi — hozircha committed emas, lekin bo'shliq bor.
- Dev-only `pytest==8.4.1`da e'lon qilingan zaiflik bor, ammo production image'ga kirmaydi (Dockerfile faqat `base.txt`ni o'rnatadi).
- `setup-local.ps1` DB_PASSWORD o'rnatilmaganida faqat ogohlantiradi (keyinroq `check-services.ps1` bu bo'shliqni yopadi).
- Gunicorn `--workers 3 --timeout 60` sozlamalarida `--max-requests` yo'q (worker qayta ishga tushirish uchun).
- Dockerfile — non-root foydalanuvchi to'g'ri sozlangan (ijobiy topilma sifatida qayd etilgan).

## 6. Harakat rejasi

**Hozir (release'dan oldin):**
1. Windows Scheduled Task/launch skriptlarida `DJANGO_SETTINGS_MODULE=config.settings.production`ni majburiy o'rnatish (CRITICAL).
2. `apps/publications` API'siga `permission_classes` qo'shish (HIGH — ma'lumot sizishi).
3. `Event.Status.DRAFT`ni conflict-detection exclude ro'yxatiga qo'shish yoki muqobil yechim (HIGH — biznes-mantiq bugi).
4. `apps/publications/services.py`da idempotentlik mexanizmi qo'shish (HIGH — ikki marta post qilinish xavfi).
5. `docker-compose.yml`ga `restart:` siyosati va healthcheck'lar qo'shish (agar Docker yo'li ishlatilsa).
6. Production logging'ni #1 bilan birga tekshirish va faylga yozuvni ta'minlash.

**1-hafta ichida:**
- `VenueAvailabilityAPIView`dagi `int()` parsing'ni try/except bilan o'rash.
- `EventDetailView`dagi ikki marta so'rovni tuzatish (`self.object` ishlatish).
- `publish_publication_task`ning retry/failure yo'liga test qo'shish.
- `Django`ni 5.2.17ga, `djangorestframework`ni 3.17.2ga yangilash.
- Asosiy dashboard va Approval Center'dagi N+1 so'rovlarni tuzatish.
- CI pipeline qo'shish (kamida `pytest` + `ruff` + `manage.py check --deploy`).

**Keyinroq:**
- `apps/events/views.py`ni kichikroq modullarga bo'lish.
- `apps/events`/`apps/notifications` orasidagi ikki tomonlama bog'liqlikni yumshatish.
- API xato javob formatini standartlashtirish, sahifalash qo'shish.
- RBAC test qamrovini barcha rollar bo'yicha kengaytirish.
- Jamoat/TV endpoint'lariga kesh va sana chegarasi qo'shish.

## 7. Yaxshi qilingan narsalar

- **Fayl yuklash validatsiyasi** (`config/validators.py`) — kengaytma ro'yxati + hajm chegarasi + MIME tekshiruvi + magic-byte imzo tekshiruvi + `PIL.Image.verify()` — barcha yuklash nuqtalarida (avatar, shifokor rasmi, joy rasmi, tashkilot/homiy logotipi, banner, dastur PDF) izchil qo'llangan.
- **Token generatsiyasi** — `DisplayToken`, Telegram bog'lash tokenlari, ro'yxatga olish havolalari `secrets.token_urlsafe()` orqali, bashorat qilib bo'lmaydigan.
- **Login brute-force himoyasi** — `ThrottledLoginView` (`config/views.py`) + `config/rate_limit.py` orqali 10 urinish/300s cheklovi, muvaffaqiyatli kirishda hisoblagich tozalanadi.
- **AnonymousUser `.role` bug klassi** — barcha topilgan `request.user.role` chaqiruvlari (`apps/accounts`, `apps/events`, `apps/reporting`, `apps/audit`) `is_authenticated`/`LoginRequiredMixin`/`IsAuthenticated` bilan to'g'ri qopqonlangan; jamoat sahifalari (`PublicDashboardView`, `TvWallboardView`) `.role`ga umuman tegmaydi.
- **Test to'plami** — 395 test, 5.53 soniyada, 0 xato; over-mocking yo'q, real DB yozuvlari orqali sinaladi; rezervatsiya lock'lash (`select_for_update` + `transaction.atomic`) va eslatma idempotentligi (`get_or_create`) to'g'ri amalga oshirilgan va test qilingan.
- **Settings arxitekturasi** — `base/local/production/test` toza bo'linган, `django-environ` orqali barcha maxfiy ma'lumotlar `.env`dan o'qiladi, hech qanday hardcoded API kalit/token topilmadi.
- **Docker xavfsizligi** — Dockerfile'da non-root foydalanuvchi (`USER iems`) to'g'ri sozlangan, dev bog'liqliklar production image'ga kirmaydi.
- **Bog'liqliklar gigienasi** — barcha runtime bog'liqliklar `requirements/base.txt`da deklaratsiya qilingan, ishlatilmagan bog'liqlik topilmadi, litsenziyalar (MIT/BSD) muammosiz.
- **Backup skriptlari** — native Windows yo'lida `backup.ps1`/`restore.ps1`/`verify-backup.ps1` orqali `pg_dump` + media nusxalash + SHA256 tekshiruv bilan puxta zaxiralash tizimi mavjud.

## 8. Rad etilgan topilmalar (verifier)

- **"Login uchun rate-limiting/brute-force himoyasi yo'q"** (Testlar reviewer'i) — **RAD ETILDI**. Sabab: bu tekshiruv faqat `apps/accounts/*.py`ni grep qildi, ammo haqiqiy throttling kodi `config/urls.py:97` (`ThrottledLoginView`) va `config/views.py`da joylashgan, `config/rate_limit.py`dan foydalanadi (10 urinish/300s, muvaffaqiyatda tozalanadi). Xavfsizlik reviewer'ining mustaqil tekshiruvi to'g'ri chiqdi.
- **`apps/events/api.py`dagi `get_object_or_404` chaqiruvlari** (API reviewer tomonidan "500 xatosi" bugining bir qismi sifatida keltirilgan) — **QISMAN RAD ETILDI**: DRF'ning o'z exception handler'i `Http404`ni to'g'ri 404'ga aylantiradi, bu qism xato emas. Faqat asl topilmaning `int(request.query_params.get(...))` qismi haqiqiy bug bo'lib qoldi (yuqorida HIGH sifatida saqlangan).
- **`djangorestframework` zaifliklari uchun HIGH darajasi** (Bog'liqliklar reviewer'i) — **PASAYTIRILDI (MEDIUM'ga)**: verifikator zaiflik ta'siri (`AdminRenderer` ishlatilmaydi) hisobga olingan holda darajani pasaytirishga rozi bo'ldi.
