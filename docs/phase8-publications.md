# Phase 8: social publication composer

Phase 8 prepares approved event announcements, generates public-safe banners and provides fail-closed Telegram channel and official Instagram Graph API adapters. Personal Telegram reminders remain separate.

## Local configuration

All credentials belong only in the ignored `.env`. Telegram channel publication requires the bot to be a channel administrator. Instagram uses the official container creation then `media_publish` sequence and requires a publicly reachable `IEMS_BASE_URL` for the generated image.

Both integrations default to disabled. Automated tests and browser acceptance use fake adapters and never call Telegram or Meta.

## Scheduling

Celery Beat scans due publications once per minute. Workers lock each publication row and treat a previously published record as complete, preventing duplicate posts during retries or concurrent dispatch.

## Deferred

Social analytics, production credentials, production webhooks and deployment are not part of Phase 8.
