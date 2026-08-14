# IEMS final local acceptance checklist

Use only accounts whose usernames start with `acceptance_` and records whose names start with
`[ACCEPTANCE_DEMO]`. Mark each test PASS or FAIL. If a test fails, capture the whole browser
window so the page address, message and clicked control are visible.

## Before testing

1. Run `powershell -ExecutionPolicy Bypass -File scripts\start-local.ps1` from `C:\IEMS`.
2. Run `python manage.py prepare_acceptance_demo --with-events` in the activated environment.
   Enter one temporary password when prompted; the input is hidden and is not saved in source.
3. Open the exact URL printed by the startup script. It is normally `http://127.0.0.1:8000/`.
4. Use the role account named in a test. All test usernames are listed in the setup section below.

Telegram Channel, Instagram and personal Telegram delivery are **NOT LIVE TESTED**. Keep them
disabled or in fake/test mode. A disabled integration must say that it is unavailable; this is
the correct result, not a failure.

## 01 to 08: access and master data

| # | Test | What to click | What should appear and counts as PASS | Screenshot if FAIL |
|---:|---|---|---|---|
| 01 | Login | Open the URL, enter an `acceptance_` username and the temporary password, click **Login**. | The dashboard opens and the current user is shown. | `01-login.png` |
| 02 | Dashboard | Click **Dashboard** in the left menu. | Summary blocks load without an error and show today/upcoming information. | `02-dashboard.png` |
| 03 | Language UZ/RU/EN | Use the language switcher once for UZ, RU and EN. | The page labels change completely each time; entered event names remain unchanged. | `03-language.png` |
| 04 | Users/Roles | Sign in as `acceptance_super_admin`, open user administration and inspect the seven `acceptance_` users. | Each test user has the role matching its username; ordinary roles do not gain Super Admin access. | `04-users-roles.png` |
| 05 | Venues | Open **Master Data**, then **Venues**. | Four `[ACCEPTANCE_DEMO]` halls appear with different capacities. | `05-venues.png` |
| 06 | Event Types | Open **Event Types**. | `[ACCEPTANCE_DEMO] Test event` appears and requires approval. | `06-event-types.png` |
| 07 | Organizations | Open **Organizations**. | `[ACCEPTANCE_DEMO] International Test Organization` appears. | `07-organizations.png` |
| 08 | Sponsors | Open **Sponsors**. | `[ACCEPTANCE_DEMO] Test Sponsor` appears. | `08-sponsors.png` |

## 09 to 17: create and edit an event

| # | Test | What to click | What should appear and counts as PASS | Screenshot if FAIL |
|---:|---|---|---|---|
| 09 | Create Event | As `acceptance_responsible`, click **Events**, then **New event**. Enter a title beginning `[ACCEPTANCE_DEMO]`. | The first event form opens and accepts the title. | `09-create-event.png` |
| 10 | Date picker | Click the date field and choose a future date. | A calendar picker opens and the selected date remains visible. | `10-date-picker.png` |
| 11 | Automatic weekday | After choosing the date, look beside/below it. | The correct weekday appears automatically. | `11-weekday.png` |
| 12 | Time picker | Choose start and end times. | Both times are visible and an end time before the start is rejected. | `12-time-picker.png` |
| 13 | Venue availability | Select one `[ACCEPTANCE_DEMO]` venue. | Availability is shown for the selected date and time. | `13-availability.png` |
| 14 | Capacity warning | Enter attendees above the selected hall capacity. | A clear capacity warning appears before saving. | `14-capacity.png` |
| 15 | Save Draft | Correct the attendee count and click **Save draft**. | Event detail opens with status **Draft** and no error. | `15-save-draft.png` |
| 16 | Edit Event | Click **Edit**, change the description, then save. | The changed description appears on event detail. | `16-edit-event.png` |
| 17 | Save Planned | Use the available action to keep/mark the event as planned. | Status becomes **Planned** only when the action is allowed. | `17-save-planned.png` |

## 18 to 25: calendar and conflicts

| # | Test | What to click | What should appear and counts as PASS | Screenshot if FAIL |
|---:|---|---|---|---|
| 18 | Calendar Month | Open **Calendar**, choose **Month**. | Events appear on their correct dates. | `18-calendar-month.png` |
| 19 | Calendar Week | Choose **Week**. | The same events appear on the correct day and time. | `19-calendar-week.png` |
| 20 | Calendar Day | Choose **Day** and select an event date. | Only that day is shown with correct event times. | `20-calendar-day.png` |
| 21 | Calendar List | Choose **List**. | Events are ordered by date and time. | `21-calendar-list.png` |
| 22 | Filters | Filter by venue, type or status, then clear filters. | Results match the filter; clearing restores the full list. | `22-calendar-filters.png` |
| 23 | Create conflicting event | Start another `[ACCEPTANCE_DEMO]` event in the same venue and overlapping time. | A conflict message appears before the event can take that slot. | `23-conflict.png` |
| 24 | Verify conflict blocked | Try to continue/save the conflicting choice. | The occupied slot is blocked and no duplicate booking is created. | `24-conflict-blocked.png` |
| 25 | Verify alternative venue | Select a different available demo venue. | The conflict clears and the form can continue. | `25-alternative-venue.png` |

## 26 to 34: approval and emergency flow

| # | Test | What to click | What should appear and counts as PASS | Screenshot if FAIL |
|---:|---|---|---|---|
| 26 | Submit event | On a draft event click **Submit** and confirm. | Status becomes pending approval and the management queue receives it. | `26-submit.png` |
| 27 | Management approval | Sign in as `acceptance_management`, open **Approvals**, choose the event and click **Approve**. | Status becomes **Approved**, reviewer and time are visible where allowed. | `27-approve.png` |
| 28 | Reject with reason | Submit another demo event, open it in Approvals and click **Reject** with a reason. | Rejection requires a reason and status becomes **Rejected**. | `28-reject.png` |
| 29 | Correct and resubmit | Sign in as the responsible user, edit the rejected event, then submit again. | Corrections save and the event returns to pending approval. | `29-resubmit.png` |
| 30 | Approve | As management, approve the corrected event. | Status becomes **Approved** and the old rejection does not block it. | `30-final-approve.png` |
| 31 | Emergency event | As an allowed admin, create a demo event using the emergency type and an occupied slot. | The emergency option and warning are visible. | `31-emergency.png` |
| 32 | Emergency override | Enter the required justification and confirm override. | Emergency event takes the slot only after confirmation. | `32-emergency-override.png` |
| 33 | Displaced event | Open the original event or displaced queue. | Original event is clearly marked **Displaced**, with no hidden deletion. | `33-displaced.png` |
| 34 | Reschedule displaced event | Click **Reschedule**, choose an available slot and save. | Event leaves the displaced queue and has the new slot. | `34-reschedule.png` |

## 35 to 46: program, public page and QR

| # | Test | What to click | What should appear and counts as PASS | Screenshot if FAIL |
|---:|---|---|---|---|
| 35 | Program PDF mode | Open an approved demo event, choose **Program**, then **PDF** mode. | A PDF upload field and guidance appear. | `35-pdf-mode.png` |
| 36 | Upload PDF | Choose a small valid PDF and save. | File name appears with no validation error. | `36-upload-pdf.png` |
| 37 | Open PDF | Click the PDF open/view action. | The correct document opens in the browser. | `37-open-pdf.png` |
| 38 | Download PDF | Click download. | The same PDF downloads successfully. | `38-download-pdf.png` |
| 39 | Manual Program mode | Return to Program and choose **Manual agenda**. | Agenda controls appear without deleting the PDF unexpectedly. | `39-manual-mode.png` |
| 40 | Add agenda | Click **Add agenda item**, enter time/title and save. | The agenda item appears in time order. | `40-add-agenda.png` |
| 41 | Add speaker | Add a test speaker to the agenda item. | Speaker name appears; private email is not shown publicly. | `41-add-speaker.png` |
| 42 | Edit agenda | Edit the agenda title/time and save. | The changed item appears in the correct order. | `42-edit-agenda.png` |
| 43 | Public Event Page | Click **Public page** and also open it in a private browser window. | Public event details load without login and no notes, staff email or approval detail appears. | `43-public-page.png` |
| 44 | QR preview | Click **QR preview**. | A QR code and the same public page address appear. | `44-qr-preview.png` |
| 45 | QR print | Click **Print QR**. | A clean print view opens with event identity and readable QR. | `45-qr-print.png` |
| 46 | QR mobile scan | Scan the printed/on-screen QR with a phone. | The public page opens on the phone and fits the screen. | `46-qr-mobile.png` |

## 47 to 62: attendance, leadership and TV

| # | Test | What to click | What should appear and counts as PASS | Screenshot if FAIL |
|---:|---|---|---|---|
| 47 | Enable Check-in | In the event attendance settings, enable check-in with an open time window. | Public page shows that check-in is open. | `47-enable-checkin.png` |
| 48 | Guest check-in | On the public page click **Men keldim**. | A success message appears and attendance increases once. | `48-guest-checkin.png` |
| 49 | Duplicate check-in | Double-click the check-in button or repeat it in the same browser. | It reports already checked in; the total does not increase twice. | `49-duplicate-checkin.png` |
| 50 | Manual staff check-in | As `acceptance_reception`, open Attendance, click **Add attendee**, enter test guest details and save. | The guest appears with method **Manual**. | `50-manual-checkin.png` |
| 51 | Attendance dashboard | Open the event attendance dashboard. | Public and manual totals match the rows shown. | `51-attendance-dashboard.png` |
| 52 | CSV attendance export | Click **Export CSV**. | A CSV downloads and contains only the selected event attendance. | `52-attendance-csv.png` |
| 53 | Leadership Dashboard | As `acceptance_leadership`, open **Leadership**. | Read-only summary loads; edit/publish controls are absent. | `53-leadership.png` |
| 54 | Live venue status | Review the live venue area. | Each demo venue has a clear available/occupied/upcoming state. | `54-live-venues.png` |
| 55 | Today timeline | Open today timeline. | Today’s events are shown in time order. | `55-today-timeline.png` |
| 56 | Upcoming events | Open upcoming events. | Future approved/planned demo events appear in date order. | `56-upcoming-events.png` |
| 57 | TV Wallboard | Open a valid TV display link. | Wallboard fills the page without admin navigation. | `57-tv-wallboard.png` |
| 58 | Available venue | Find a hall with no current event. | It is labelled **Available**, not by color alone. | `58-tv-available.png` |
| 59 | Occupied venue | During/test an active slot, view its hall. | It is labelled **Occupied** and allowed event detail is correct. | `59-tv-occupied.png` |
| 60 | Upcoming venue | View a hall with a later event. | Upcoming time/event appears clearly. | `60-tv-upcoming.png` |
| 61 | Private meeting visibility | Use an event set to generic/private display visibility. | Wallboard says private/occupied without exposing title or internal detail. | `61-tv-private.png` |
| 62 | Fullscreen | Click the fullscreen control and then exit fullscreen. | Wallboard enters and exits fullscreen without losing its state. | `62-tv-fullscreen.png` |

## 63 to 79: Telegram, publications and reports

| # | Test | What to click | What should appear and counts as PASS | Screenshot if FAIL |
|---:|---|---|---|---|
| 63 | Telegram user settings | Open **Telegram settings**. | Connection state is clear and no bot token is displayed. | `63-telegram-settings.png` |
| 64 | Reminder configuration | Open an event’s reminder settings and change a test interval. | The selected reminder options save. | `64-reminders.png` |
| 65 | Fake/test reminder status | Review reminder deliveries without real credentials. | UI states TEST/disabled honestly; it does not claim a live message was delivered. | `65-reminder-test-mode.png` |
| 66 | Publication dashboard | As `acceptance_content`, click **Publications**. | Draft/ready/scheduled/published/failed summaries load. | `66-publications.png` |
| 67 | Telegram publication composer | Choose an approved demo event, click new publication and select Telegram/UZ. | Composer fills public-safe event data and shows Telegram-specific fields. | `67-telegram-composer.png` |
| 68 | Banner preview | Click **Generate preview**. | A correctly sized banner appears; title fits and QR is readable. | `68-banner-preview.png` |
| 69 | Schedule publication | Approve then schedule in fake/test mode. | Status becomes scheduled; UI still says Telegram Channel is not live tested. | `69-schedule-publication.png` |
| 70 | Instagram composer | Create an Instagram/EN draft and preview it. | Portrait preview appears and explains that caption links are not clickable. | `70-instagram-composer.png` |
| 71 | Reports dashboard | Click **Reports**. | Report summary and filters load with no error. | `71-reports.png` |
| 72 | Date filters | Choose a date range containing demo events and apply. | All report sections use the selected range. | `72-report-dates.png` |
| 73 | Venue utilization | Open venue utilization. | Demo halls and believable booked/available values appear. | `73-venue-utilization.png` |
| 74 | Attendance analytics | Open attendance analytics. | Totals match the demo event attendance dashboard. | `74-attendance-analytics.png` |
| 75 | Approval analytics | Open approval analytics. | Approved/rejected activity from the test flow appears. | `75-approval-analytics.png` |
| 76 | Publication analytics | Open publication analytics. | Test-mode publication statuses appear without invented social likes/views. | `76-publication-analytics.png` |
| 77 | CSV export | Click **CSV** export. | A readable CSV downloads for the active filters. | `77-report-csv.png` |
| 78 | XLSX export | Click **XLSX** export and open the file. | Workbook opens with headings and filtered rows. | `78-report-xlsx.png` |
| 79 | PDF export | Click **PDF** export and open the file. | PDF opens with readable headings, values and selected period. | `79-report-pdf.png` |

## 80 to 83: device and security checks

| # | Test | What to click | What should appear and counts as PASS | Screenshot if FAIL |
|---:|---|---|---|---|
| 80 | Mobile test | Use a phone or browser width near 375 px; repeat login, event form, public page and reports. | Controls fit, menu opens, no horizontal clipping blocks an action. | `80-mobile.png` |
| 81 | Tablet test | Use a tablet or browser width near 768 px; repeat calendar and composer. | Content stacks/reflows and every control remains usable. | `81-tablet.png` |
| 82 | Logout | Click the current-user menu, then **Logout**. | Login page appears and protected pages no longer open through Back/refresh. | `82-logout.png` |
| 83 | Unauthorized access | As `acceptance_reception`, try a copied admin-only URL and a publish action. | Access is denied without changing data; no secret or technical detail appears. | `83-security.png` |

## Acceptance test accounts

| Username | Role |
|---|---|
| `acceptance_super_admin` | Super Admin |
| `acceptance_international_admin` | International Admin |
| `acceptance_responsible` | Responsible Employee |
| `acceptance_management` | Management Responsible |
| `acceptance_leadership` | Leadership Viewer |
| `acceptance_content` | Content Manager |
| `acceptance_reception` | Reception Operator |

All seven accounts use the temporary password entered while running
`python manage.py prepare_acceptance_demo`. Do not put that password in this document, a
screenshot, chat, Git or a bug report.

## When testing is finished

Run `python manage.py cleanup_acceptance_demo`. It removes only records carrying the acceptance
marker. If a real or unmarked record references demo master data, cleanup safely skips the
protected item and reports it.
