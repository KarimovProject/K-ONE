import time

from django.core.management.base import BaseCommand, CommandError

from apps.notifications.telegram.client import (
    TelegramClient,
    TelegramPermanentError,
    TelegramTransientError,
)
from apps.notifications.telegram.linking import consume_link_token

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
                    message = update.get("message") or {}
                    text = str(message.get("text", ""))
                    if not text.startswith("/start "):
                        continue
                    raw_token = text.split(maxsplit=1)[1].strip()
                    sender = message.get("from") or {}
                    chat = message.get("chat") or {}
                    connection = consume_link_token(
                        raw_token,
                        chat_id=str(chat.get("id", "")),
                        telegram_user_id=int(sender.get("id", 0)),
                        telegram_username=str(sender.get("username", "")),
                    )
                    reply = (
                        "✅ IEMS account connected."
                        if connection
                        else "This link is invalid, expired, or already used."
                    )
                    try:
                        client.send_message(str(chat.get("id", "")), reply)
                    except TelegramTransientError as exc:
                        self.stderr.write(self.style.WARNING(f"Reply send failed: {exc}"))
                if options["once"]:
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Telegram polling stopped."))
        except TelegramPermanentError as exc:
            raise CommandError(str(exc)) from exc
