import time

from django.core.management.base import BaseCommand, CommandError

from apps.notifications.telegram.client import (
    TelegramClient,
    TelegramPermanentError,
    TelegramTransientError,
)
from apps.notifications.telegram.updates import handle_update

MAX_BACKOFF_SECONDS = 30


class Command(BaseCommand):
    help = "Poll Telegram updates for local account-linking development."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true")

    def handle(self, *args, **options):
        client = TelegramClient()
        if not client.configured:
            raise CommandError("Telegram is disabled or TELEGRAM_BOT_TOKEN is missing.")
        offset = None
        backoff = 1
        self.stdout.write("Telegram polling started. Press Ctrl+C to stop.")
        try:
            while True:
                try:
                    updates = client.get_updates(offset=offset)
                except TelegramTransientError as exc:
                    # Network hiccups/rate limits are expected over a long-running
                    # poll loop; retry with backoff instead of crashing the process.
                    self.stderr.write(
                        self.style.WARNING(f"Telegram poll failed ({exc}); retrying in {backoff}s")
                    )
                    time.sleep(backoff)
                    backoff = min(backoff * 2, MAX_BACKOFF_SECONDS)
                    continue
                backoff = 1
                for update in updates:
                    offset = int(update["update_id"]) + 1
                    try:
                        handle_update(client, update)
                    except TelegramTransientError as exc:
                        self.stderr.write(self.style.WARNING(f"Reply send failed: {exc}"))
                if options["once"]:
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Telegram polling stopped."))
        except TelegramPermanentError as exc:
            raise CommandError(str(exc)) from exc
