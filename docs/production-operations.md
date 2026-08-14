# IEMS production operations

## Recommended topology

Linux is recommended for production: Nginx in front of Gunicorn, Django application processes, PostgreSQL, Redis, Celery workers and one Celery Beat process. Docker is optional, not required. Run each component as a dedicated least-privilege service account and keep `.env` outside the release directory with restrictive permissions.

Gunicorn reference: `gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60`. Configure worker count from measured CPU/DB capacity, not by copying this example blindly. Nginx terminates TLS, redirects HTTP, serves immutable `/static/`, serves only approved public `/media/` paths, disables directory indexes and limits upload bodies to 10 MB or the stricter route-specific limit.

Run `collectstatic --noinput`, migrations and `check --deploy --settings=config.settings.production` before switching a release. Celery workers and Beat must use the same code and environment as web. Only one Beat instance should run.

`DB_CONN_MAX_AGE` controls persistent database connection lifetime. Size Gunicorn workers plus Celery concurrency below the PostgreSQL connection budget, leaving capacity for migrations, backups and administration.

## HTTPS and integrations

Production requires a stable domain, DNS, TLS certificate and `IEMS_BASE_URL=https://...`. `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` must list only deployed origins. Telegram webhooks and Instagram media require publicly reachable HTTPS. Keep both social integrations disabled until real credentials and explicit smoke tests exist.

## Backup and restore

Run `scripts/backup.ps1` under an account allowed to execute native PostgreSQL 15 tools and read media. It produces a timestamped custom-format `database.dump`, media tree, secret-free manifest and SHA-256 checksums under ignored `backups/`. The password is supplied only through the process `PGPASSWORD` environment and never written to the archive.

Validate with `scripts/verify-backup.ps1 -BackupDirectory <path>`. Restore only into an isolated database whose name starts with `iems_restore_`:

```powershell
.\scripts\restore.ps1 -BackupDirectory C:\IEMS\backups\20260813-180346 `
  -RestoreDatabase iems_restore_drill -RestoreMediaRoot C:\IEMS\restore-media\drill -Recreate
```

After restore, point `DB_NAME` and `DJANGO_MEDIA_ROOT` to the isolated targets, run Django checks, verify migrations and representative public/attendance/report records, then remove the isolated targets after resolving their exact paths.

Retention policy proposal: seven daily, four weekly and six monthly verified backups, with an encrypted off-host copy. No automatic deletion is included. Operations must approve retention, test a dry-run inventory and validate an off-host restore before enabling pruning.

## Monitoring and alerting

Monitor HTTPS uptime, `/health/ready/`, database/Redis availability, Celery queue depth and task failures, Beat heartbeat, HTTP 5xx/429 rate, disk/media growth, PostgreSQL connections, backup age/result and certificate expiry. JSON logs are suitable for a standard collector. A Sentry-compatible backend is optional, not required. Never send credentials, raw link/browser tokens, attendee lists or sensitive notes to monitoring.

## Data retention

Audit records are append-only operational evidence with action/timestamp indexes. Archive old partitions/exports according to approved legal policy; do not silently delete them. Attendance names, Telegram connections, publication history and uploaded files require owner-approved retention periods. Connection removal and file replacement flows exist, but bulk retention deletion is intentionally not automated.

## Email

Production email defaults to Django's dummy backend and therefore fails closed. Do not claim email delivery until SMTP credentials, TLS and a delivery smoke test are supplied.
