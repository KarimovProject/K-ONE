# Phase 11 UI and admin governance

## Information architecture

- `/dashboard/`, `/dashboard/calendar/`, and `/venues/live/` are anonymous, read-only surfaces.
- `/workspace/` and `/profile/` are authenticated, role-aware staff surfaces.
- `/admin/` is the full control centre for authorised staff and remains recognisably Django Admin.
- `/` redirects to `/dashboard/`; existing secure TV and operational routes remain unchanged.

## Public privacy policy

Only approved, planned, scheduled, ongoing, completed, and emergency event states enter the public
read model. Full visibility exposes the event title, type, schedule, venue, status, priority, and an
enabled public page link. Generic visibility replaces the title with “Private meeting”. Hidden
visibility exposes only the blocked venue and time. Internal UUIDs, tokens, staff, contacts, notes,
approval/rejection data, emergency justification, attendance identities, and audit data are never
serialized.

## Delete policy

| Record | Policy | Reason |
| --- | --- | --- |
| Unreferenced venue, event type, organization, sponsor, speaker | Object delete allowed; bulk delete disabled | Safe configuration cleanup with explicit confirmation |
| Referenced master data | Protected | Preserves event history and referential integrity |
| Draft, rejected, cancelled event | Object delete allowed | Non-operational cleanup |
| Other event states | Protected in Admin | Preserves workflow and operational history |
| Draft, ready, failed, cancelled publication | Object delete allowed | Safe content cleanup |
| Approved, scheduled, publishing, published publication | Protected | Preserves external publication history |
| Attendance | Read-only, no add/change/delete | Retention and reporting integrity |
| Audit log | Read-only, no add/change/delete | Evidence must not be altered through normal Admin |
| Telegram delivery | Read-only, no add/change/delete | Delivery/idempotency history |
| Display token | Rotation/enable/disable only; no delete | Avoids accidental display outage |

Django's standard deletion confirmation page shows dependent objects and consequences. Critical
models do not expose bulk delete.

## Runtime behaviour

The public clock updates every second. Dashboard and venue JSON refresh every 20 seconds with a
bounded query plan and no full-page reload. Calendar requests are limited to 93 days. Motion respects
`prefers-reduced-motion`; loading, empty, and retry states remain visible and accessible.
