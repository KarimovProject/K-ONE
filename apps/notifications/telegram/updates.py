from typing import Any

from apps.notifications.telegram.client import TelegramClient
from apps.notifications.telegram.linking import consume_link_token

START_WITH_TOKEN_PREFIX = "/start "
START_REPLY_LINKED = "✅ IEMS hisobingiz ulandi."
START_REPLY_INVALID = (
    "Bu havola yaroqsiz, eskirgan yoki allaqachon ishlatilgan. IEMS saytida "
    "\"Sozlamalar → Telegram\" bo'limidan yangi havola oling."
)
START_REPLY_PLAIN = (
    "Salom! Hisobingizni ulash uchun IEMS saytida \"Sozlamalar → Telegram\" bo'limiga "
    "o'ting va \"Telegram'ni ulash\" tugmasini bosing."
)


def handle_update(client: TelegramClient, update: dict[str, Any]) -> None:
    """Process one Telegram update (shared by long-polling and webhook delivery)."""
    message = update.get("message") or {}
    text = str(message.get("text", ""))
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", ""))

    if text.startswith(START_WITH_TOKEN_PREFIX) and text.split(maxsplit=1)[1].strip():
        raw_token = text.split(maxsplit=1)[1].strip()
        sender = message.get("from") or {}
        connection = consume_link_token(
            raw_token,
            chat_id=chat_id,
            telegram_user_id=int(sender.get("id", 0)),
            telegram_username=str(sender.get("username", "")),
        )
        reply = START_REPLY_LINKED if connection else START_REPLY_INVALID
    elif text.strip() == "/start":
        # No token attached: the user opened the bot directly instead of via the deep link.
        reply = START_REPLY_PLAIN
    else:
        return

    client.send_message(chat_id, reply)
