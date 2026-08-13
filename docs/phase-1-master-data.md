# Phase 1 — Master Data

Phase 1 adds the reference data required by later event workflows without implementing
event scheduling or approval behavior.

## Boundaries

- `venues` owns halls and rooms.
- `events` currently owns only reusable event-type reference data.
- `organizations` owns organizations and sponsors. Sponsors are not linked to events.
- `accounts` remains the single source of staff identities and exposes role-based selectors.
- Capability-based RBAC grants all authenticated roles read access; only super administrators
  and international administrators can create, edit, or delete master data.

## Seed data

Run `python manage.py seed_master_data`. The command is transactional and idempotently
upserts the four approved venues and ten approved event types.

## HTTP surface

Authenticated HTML CRUD is under `/master-data/`. Read-only REST endpoints are under
`/api/v1/`. List pages provide search, active-state filtering, and pagination.

Uploaded venue photos and organization/sponsor logos accept JPEG, PNG, or WebP files up to
5 MB. Validation checks extension, declared MIME type, and file signature.

## Explicitly deferred

Event CRUD, scheduling, calendars, venue conflicts, approvals, emergency workflows, QR,
attendance, public event pages, messaging integrations, and reporting logic remain out of
scope until a later phase is approved.
