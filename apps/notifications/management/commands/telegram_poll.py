import time

from django.core.management.base import BaseCommand, CommandError

from apps.notifications.telegram.client import TelegramClient, TelegramError
from apps.notifications.telegram.linking import consume_link_token


class Command(BaseCommand):
    help = "Poll Telegram updates for local account-linking development."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true")

    def handle(self, *args, **options):
        client = TelegramClient()
        if not client.configured:
            raise CommandError("Telegram is disabled or TELEGRAM_BOT_TOKEN is missing.")
        offset = None
        self.stdout.write("Telegram polling started. Press Ctrl+C to stop.")
        try:
            while True:
                for update in client.get_updates(offset=offset):
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
                    client.send_message(str(chat.get("id", "")), reply)
                if options["once"]:
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Telegram polling stopped."))
        except TelegramError as exc:
            raise CommandError(str(exc)) from exc
