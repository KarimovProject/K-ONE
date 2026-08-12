# Docker-free Windows local setup

## Prerequisites

- Native Python 3.13 (`py -3.13 --version`).
- PostgreSQL installed as a Windows service.
- Redis installed as a local Windows-compatible service. This workstation currently uses
  Redis 3.0.504 as the native `Redis` service with
  `C:\Program Files\Redis\redis-cli.exe`. The pinned RESP2-compatible Python client is
  required for this service; do not upgrade it without repeating the Celery/cache gate.

Docker Desktop is not required.

## One-time project setup

```powershell
cd C:\IEMS
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup-local.ps1
notepad .env
```

Set `DB_PASSWORD` to the password for the configured local PostgreSQL role. The setup script
never creates, drops, or resets databases and never changes PostgreSQL authentication.

Create the development database with PostgreSQL tooling when it does not already exist:

```powershell
& "C:\Program Files\PostgreSQL\15\bin\createdb.exe" `
  -h 127.0.0.1 -p 5432 -U postgres iems
```

The command prompts for the existing PostgreSQL password.

## Verify native services

```powershell
Get-Service *postgres*
Get-Service Redis
& "C:\Program Files\PostgreSQL\15\bin\pg_isready.exe" -h 127.0.0.1 -p 5432
& "C:\Program Files\Redis\redis-cli.exe" -h 127.0.0.1 -p 6379 ping
.\scripts\check-services.ps1
```

Expected results are a running PostgreSQL service, a running Redis service,
`accepting connections`, and `PONG`.

## Daily startup order

### Terminal 1 — PostgreSQL

PostgreSQL runs as an automatic Windows service. Verify it with:

```powershell
Get-Service *postgres*
```

### Terminal 2 — Redis

Redis runs as a Windows service. Verify it with:

```powershell
Get-Service Redis
& "C:\Program Files\Redis\redis-cli.exe" ping
```

### Terminal 3 — Django

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Equivalent helper: `.\scripts\run-web.ps1`.

### Terminal 4 — Celery worker

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
celery -A config worker -l info --pool=solo
```

The solo pool is the supported local Windows profile; production configuration is unchanged.
Equivalent helper: `.\scripts\run-celery.ps1`.

### Terminal 5 — Celery Beat

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
celery -A config beat -l info
```

Equivalent helper: `.\scripts\run-beat.ps1`.
