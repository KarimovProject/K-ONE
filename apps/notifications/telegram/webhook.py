import hmac
import json
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.notifications.telegram.client import TelegramClient, TelegramTransientError
from apps.notifications.telegram.updates import handle_update

logger = logging.getLogger(__name__)

SECRET_HEADER = "HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN"


@csrf_exempt
@require_POST
def telegram_webhook(request: HttpRequest) -> HttpResponse:
    """Receive Telegram updates pushed by Telegram (alternative to long-polling).

    Telegram sends the secret configured via setWebhook in a header; anything else
    is rejected. Always answer 200 once authenticated, otherwise Telegram re-delivers
    the same update and link tokens would be retried.
    """
    expected = settings.TELEGRAM_WEBHOOK_SECRET
    provided = request.META.get(SECRET_HEADER, "")
    if not expected or not hmac.compare_digest(provided, expected):
        return HttpResponseForbidden()

    try:
        update = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest()
    if not isinstance(update, dict):
        return HttpResponseBadRequest()

    client = TelegramClient()
    if not client.configured:
        return HttpResponse(status=503)
    try:
        handle_update(client, update)
    except TelegramTransientError:
        logger.warning("Telegram webhook: reply could not be sent", exc_info=True)
    return HttpResponse(status=200)
