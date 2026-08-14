# Start IEMS for final local human acceptance

## Easiest startup

1. Open PowerShell.
2. Run:

   ```powershell
   cd C:\IEMS
   powershell -ExecutionPolicy Bypass -File scripts\start-local.ps1
   ```

3. The script checks native PostgreSQL and Redis, starts Django, Celery and Celery Beat in the
   background, then prints the exact browser URL. Open that URL. It normally uses
   `http://127.0.0.1:8000/`; if 8000 is occupied it clearly reports a port from 8001 to 8010.
4. Runtime output is written to ignored files under `C:\IEMS\logs`.

This startup does not use Docker and does not delete or reset data.

## Create acceptance accounts and optional sample events

In a second PowerShell window:

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
python manage.py prepare_acceptance_demo --with-events
```

Enter a temporary password twice when prompted. It is hidden while typed and is not saved in
source. The command is safe to run again: it updates the same seven users, four venues, one event
type, one organization, one sponsor and three optional events instead of making duplicates.

Omit `--with-events` if you want to create every event manually.

## Separate-terminal startup

Use this only when you prefer to watch each process directly.

Terminal 1: confirm the native PostgreSQL Windows service is running.

Terminal 2: confirm the native Redis-compatible service is running.

Terminal 3:

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
powershell -ExecutionPolicy Bypass -File scripts\run-web.ps1
```

Terminal 4:

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
powershell -ExecutionPolicy Bypass -File scripts\run-celery.ps1
```

Terminal 5:

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
powershell -ExecutionPolicy Bypass -File scripts\run-beat.ps1
```

Open the URL printed by `run-web.ps1`.

## Cleanup

After acceptance testing:

```powershell
cd C:\IEMS
.\.venv\Scripts\Activate.ps1
python manage.py cleanup_acceptance_demo
```

Cleanup removes only clearly tagged acceptance/demo records. It never deletes unmarked records.

## Integration truth

- Telegram Channel: **NOT LIVE TESTED**
- Instagram: **NOT LIVE TESTED**
- Personal Telegram reminders: **TEST MODE** until real bot credentials are supplied
