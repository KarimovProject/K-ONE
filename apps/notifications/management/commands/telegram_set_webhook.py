from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.urls import reverse

from apps.notifications.telegram.client import TelegramClient, TelegramPermanentError


class Command(BaseCommand):
    help = "Register this site's Telegram webhook (run once after deploy or domain change)."

    def add_arguments(self, parser):
        parser.add_argument("--base-url", required=True, help="Public https origin, e.g. https://kone.example.uz")

    def handle(self, *args, **options):
        base_url = options["base_url"].rstrip("/")
        if not base_url.startswith("https://"):
            raise CommandError("Telegram requires an https:// base URL.")
        if not settings.TELEGRAM_WEBHOOK_SECRET:
            raise CommandError("TELEGRAM_WEBHOOK_SECRET is not set.")

        client = TelegramClient()
        if not client.configured:
            raise CommandError("Telegram is disabled or TELEGRAM_BOT_TOKEN is missing.")
        url = base_url + reverse("telegram-webhook")
        try:
            client.set_webhook(url, settings.TELEGRAM_WEBHOOK_SECRET)
        except TelegramPermanentError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(f"Webhook set: {url}")
