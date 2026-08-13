import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from django.conf import settings


class TelegramError(RuntimeError):
    code = "telegram_error"


class TelegramDisabledError(TelegramError):
    code = "disabled"


class TelegramTransientError(TelegramError):
    code = "transient"


class TelegramPermanentError(TelegramError):
    code = "permanent"


class TelegramTransport(Protocol):
    def post(self, url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]: ...


class UrlLibTelegramTransport:
    def post(self, url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            try:
                body = json.loads(exc.read())
                description = str(body.get("description", "Telegram HTTP error"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                description = "Telegram HTTP error"
            error = (
                TelegramTransientError
                if exc.code == 429 or exc.code >= 500
                else TelegramPermanentError
            )
            raise error(description) from exc
        except (TimeoutError, urllib.error.URLError) as exc:
            raise TelegramTransientError("Telegram network request failed") from exc


@dataclass(frozen=True)
class TelegramSendResult:
    message_id: str


class TelegramClient:
    def __init__(self, transport: TelegramTransport | None = None, timeout: float = 8.0):
        self.enabled = settings.TELEGRAM_BOT_ENABLED
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = settings.TELEGRAM_API_BASE_URL.rstrip("/")
        self.timeout = timeout
        self.transport = transport or UrlLibTelegramTransport()

    @property
    def configured(self) -> bool:
        return bool(self.enabled and self.token)

    def _call(self, method: str, payload: dict[str, Any]) -> Any:
        if not self.configured:
            raise TelegramDisabledError("Telegram integration is disabled")
        data = self.transport.post(
            f"{self.base_url}/bot{self.token}/{method}", payload, self.timeout
        )
        if not data.get("ok"):
            code = int(data.get("error_code", 0))
            description = str(data.get("description", "Telegram API error"))
            error = TelegramTransientError if code == 429 or code >= 500 else TelegramPermanentError
            raise error(description)
        return data.get("result")

    def send_message(self, chat_id: str, text: str) -> TelegramSendResult:
        result = self._call(
            "sendMessage",
            {"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        )
        return TelegramSendResult(message_id=str(result["message_id"]))

    def send_photo(self, chat_id: str, photo: str, caption: str = "") -> TelegramSendResult:
        result = self._call(
            "sendPhoto",
            {"chat_id": chat_id, "photo": photo, "caption": caption, "parse_mode": "HTML"},
        )
        return TelegramSendResult(message_id=str(result["message_id"]))

    def health(self) -> bool:
        return bool(self._call("getMe", {}))

    def get_updates(self, offset: int | None = None, timeout: int = 20) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {"timeout": timeout, "allowed_updates": ["message"]}
        if offset is not None:
            payload["offset"] = offset
        return list(self._call("getUpdates", payload) or [])
