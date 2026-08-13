import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.services import log_audit_event
from apps.notifications.models import TelegramConnection, TelegramLinkToken


def hash_link_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_link_token(user: User) -> str:
    raw_token = secrets.token_urlsafe(24)
    TelegramLinkToken.objects.filter(user=user, used_at__isnull=True).delete()
    TelegramLinkToken.objects.create(
        user=user,
        token_hash=hash_link_token(raw_token),
        expires_at=timezone.now() + timedelta(seconds=settings.TELEGRAM_LINK_TOKEN_TTL_SECONDS),
    )
    return raw_token


@transaction.atomic
def consume_link_token(
    raw_token: str,
    chat_id: str,
    telegram_user_id: int,
    telegram_username: str = "",
) -> TelegramConnection | None:
    now = timezone.now()
    token = (
        TelegramLinkToken.objects.select_for_update()
        .filter(
            token_hash=hash_link_token(raw_token),
            used_at__isnull=True,
            expires_at__gt=now,
        )
        .first()
    )
    if not token:
        return None
    connection, _ = TelegramConnection.objects.update_or_create(
        user=token.user,
        defaults={
            "chat_id": str(chat_id),
            "telegram_user_id": telegram_user_id,
            "telegram_username": telegram_username[:64],
            "is_active": True,
            "last_verified_at": now,
        },
    )
    token.used_at = now
    token.save(update_fields=["used_at"])
    log_audit_event("telegram.connection_created", actor=token.user, target=token.user)
    return connection
