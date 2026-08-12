# IEMS — International Events Management System

IEMS Phase 0 is a production-oriented Django foundation for the International Department.
Normal local development is **Docker-free** and runs directly on Windows with Python 3.13,
PostgreSQL, Redis, Django, Celery, and Celery Beat.

Phase 0 contains modular app boundaries, a custom user model, RBAC, an authenticated
multilingual dashboard shell, health endpoints, tests, and deployment-reference Docker
artifacts. It does not implement event, calendar, approval, attendance, QR, publishing, or
reporting business behavior.

## Native Windows quick start

```powershell
cd C:\IEMS
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup-local.ps1
notepad .env
.\scripts\check-services.ps1
.\scripts\run-web.ps1
```

PostgreSQL and Redis must be running as native Windows services. Open separate PowerShell
terminals for `run-web.ps1`, `run-celery.ps1`, and `run-beat.ps1`.

See [local setup](docs/local-setup.md), [architecture](docs/architecture.md),
[environment variables](docs/environment.md), and the
[Phase 0 checklist](docs/phase-0-acceptance.md).

## Quality gate

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
ruff check .
```

## Docker policy

`docker-compose.yml` and `docker/` remain only as optional deployment/reference assets.
Docker Desktop and Docker Compose are not prerequisites for normal local development.

