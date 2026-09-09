import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from django.conf import settings

from apps.notifications.telegram.client import TelegramClient, TelegramError


class PublicationAdapterError(RuntimeError):
    code = "publication_error"
    transient = False


class PublicationDisabledError(PublicationAdapterError):
    code = "disabled"


class PublicationTransientError(PublicationAdapterError):
    code = "network"
    transient = True


class PublicationPermanentError(PublicationAdapterError):
    code = "permission_or_validation"


@dataclass(frozen=True)
class PublishResult:
    post_id: str
    external_url: str = ""
    container_id: str = ""


class TelegramChannelAdapter:
    def __init__(self, client: TelegramClient | None = None):
        self.client = client or TelegramClient()

    def _channel_settings(self):
        from apps.notifications.models import TelegramChannelSettings

        return TelegramChannelSettings.objects.first()

    @property
    def chat_id(self) -> str:
        row = self._channel_settings()
        if row and row.is_enabled and row.chat_id:
            return row.chat_id
        return settings.TELEGRAM_CHANNEL_CHAT_ID

    @property
    def configured(self) -> bool:
        row = self._channel_settings()
        if row is not None:
            enabled = row.is_enabled
            chat_id = row.chat_id
        else:
            enabled = settings.TELEGRAM_CHANNEL_ENABLED
            chat_id = settings.TELEGRAM_CHANNEL_CHAT_ID
        return bool(enabled and chat_id and self.client.configured)

    def publish(self, image_url: str, caption: str) -> PublishResult:
        if not self.configured:
            raise PublicationDisabledError("Telegram channel publishing is disabled")
        try:
            result = self.client.send_photo(self.chat_id, image_url, caption)
        except TelegramError as exc:
            error = (
                PublicationTransientError if exc.code == "transient" else PublicationPermanentError
            )
            raise error(str(exc)) from exc
        return PublishResult(post_id=result.message_id)


class GraphTransport(Protocol):
    def post(self, url: str, payload: dict[str, str], timeout: float) -> dict[str, Any]: ...


class UrlLibGraphTransport:
    def post(self, url: str, payload: dict[str, str], timeout: float) -> dict[str, Any]:
        request = urllib.request.Request(url, data=urllib.parse.urlencode(payload).encode())
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            try:
                body = json.loads(exc.read())
                message = str(body.get("error", {}).get("message", "Meta API error"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                message = "Meta API error"
            error = (
                PublicationTransientError
                if exc.code == 429 or exc.code >= 500
                else PublicationPermanentError
            )
            raise error(message) from exc
        except (TimeoutError, urllib.error.URLError) as exc:
            raise PublicationTransientError("Meta network request failed") from exc


class InstagramAdapter:
    def __init__(self, transport: GraphTransport | None = None):
        self.transport = transport or UrlLibGraphTransport()
        self.base_url = f"https://graph.facebook.com/{settings.META_GRAPH_API_VERSION}"

    @property
    def configured(self) -> bool:
        return bool(
            settings.INSTAGRAM_ENABLED
            and settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
            and settings.META_ACCESS_TOKEN
        )

    def publish(self, image_url: str, caption: str) -> PublishResult:
        if not self.configured:
            raise PublicationDisabledError("Instagram publishing is disabled")
        account = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
        token = settings.META_ACCESS_TOKEN
        container = self.transport.post(
            f"{self.base_url}/{account}/media",
            {"image_url": image_url, "caption": caption, "access_token": token},
            10,
        )
        container_id = str(container["id"])
        result = self.transport.post(
            f"{self.base_url}/{account}/media_publish",
            {"creation_id": container_id, "access_token": token},
            10,
        )
        post_id = str(result["id"])
        return PublishResult(
            post_id=post_id,
            container_id=container_id,
            external_url=f"https://www.instagram.com/p/{post_id}/",
        )
