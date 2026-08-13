# Phase 7: personal Telegram reminders

Phase 7 sends private staff reminders. It does not publish to Telegram channels or social media.

## Configuration

Set `TELEGRAM_BOT_ENABLED=true`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_BOT_USERNAME` only in the ignored local `.env`. When disabled or incomplete, the client fails closed. The settings UI never returns the token.

## Processes

```powershell
celery -A config worker -l info --pool=solo
celery -A config beat -l info
python manage.py telegram_poll
```

Beat runs one dispatcher every minute. It creates idempotent delivery records and enqueues individual sends. Local polling handles only `/start <one-time-token>` account links. A production webhook can reuse `consume_link_token`; no public webhook is required in this phase.

## Manual real-bot smoke test

Real Telegram calls are opt-in. Configure a dedicated test bot locally, start worker, beat and polling, connect a test user, send a test message, then remove the token from `.env`. Automated tests use a fake transport and never call Telegram.
