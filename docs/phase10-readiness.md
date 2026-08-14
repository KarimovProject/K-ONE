# Phase 10 readiness evidence

## Performance profile

Profiled against native PostgreSQL on the Docker-free Windows baseline. Figures are local observations, not production SLAs.

| Surface | Queries | Response time | Payload |
|---|---:|---:|---:|
| Dashboard | 2 | 324.04 ms cold | 7,223 bytes |
| Calendar | 4 | 9.72 ms | 12,951 bytes |
| Leadership | 7 | 23.40 ms | 12,787 bytes |
| Leadership venue API | 4 | 3.62 ms | 2,151 bytes |
| Publication list | 4 | 7.68 ms | 6,995 bytes |
| Reports | 67 | 83.36 ms | 14,953 bytes |

The reports view performs many independent bounded aggregates, so its count is higher but not an N+1 pattern; a regression guard caps it at 80 queries. No speculative cache or index was added. Existing event date/status/venue, attendance timestamp/hash, publication status/schedule, Telegram status/schedule and audit action/time indexes match the reviewed filters. PostgreSQL may choose sequential scans on this small development dataset; new indexes require production cardinality and `EXPLAIN ANALYZE` evidence.

## Safe local load test

`scripts/load_phase10.py` used native PostgreSQL/Redis, no production credentials and `DB_CONN_MAX_AGE=0` for the threaded development server. Final results:

| Scenario | Error rate | p50 | p95 | p99 |
|---|---:|---:|---:|---:|
| 100 public event users | 0% | 767.91 ms | 1,648.49 ms | 1,656.41 ms |
| 100 concurrent unique QR check-ins | 0% | 695.81 ms | 1,597.86 ms | 2,083.30 ms |
| 50 display polling clients | 0% | 649.91 ms | 1,115.56 ms | 1,125.58 ms |
| 25 report dashboard users | 0% | 1,570.00 ms | 1,641.74 ms | 1,642.95 ms |

The check-in scenario produced exactly 100 unique rows. A separate two-request same-browser race returned two idempotent HTTP responses and created exactly one row. Background work created 50 durable reminder ledgers and enqueued 25 scheduled publications in 130.39 ms with external transports suppressed.

The first development run exposed PostgreSQL connection pressure from persistent connections in 100 `runserver` threads. Making `DB_CONN_MAX_AGE` configurable and using zero in the load harness resolved it. Production Gunicorn worker count and database connection budget must be capacity tested on deployment hardware.

## Celery reliability

Worker and Beat were started, stopped and started again against real Redis. `celery inspect ping` returned `pong`. The registry contains both Telegram reminder tasks and publication tasks after adding the standard notifications task discovery bridge. Due reminders and publications are persisted in PostgreSQL and scanned by periodic dispatchers, not held only in process memory. Delivery/publication state, transaction locks, cache dispatch locks, unique constraints and retry caps provide restart/idempotency behavior. A temporary Redis interruption delays dispatch/retry; persisted due rows remain eligible when Redis returns.

## Backup restore drill

The verified backup `20260813-180346` used PostgreSQL custom format and SHA-256 checksums. It restored into isolated `iems_restore_phase10` plus an isolated media root. Verification results:

- Django system check passed against the restored database.
- Zero migrations were unapplied.
- Representative event had a non-empty public token and was publicly eligible.
- Representative attendance count was one.
- The bounded reporting selector included the representative event.
- Media paths and checksums were preserved.
- The isolated database was removed after the drill; source `iems` was never overwritten.

Backups remain ignored and contain no configuration secrets.

## Accessibility, localization and visuals

Automated readiness smoke covers headings, associated login labels, keyboard-native controls, mobile layout and production error pages. Existing visible focus, reduced-motion support, semantic tables and non-color report labels remain intact. UZ/RU catalogs include the new error/security messages; EN uses source strings. Phase 1 through Phase 9 screenshots were rerun. Dynamic data changed generated pixels, so baselines were not blindly accepted; approved tracked images were restored. No unexpected structural visual regression was observed.
