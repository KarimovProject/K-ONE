from celery import shared_task
from django.utils import timezone

from apps.audit.services import log_audit_event
from apps.notifications.models import TelegramConnection, TelegramDelivery
from apps.notifications.telegram.client import (
    TelegramClient,
    TelegramDisabledError,
    TelegramPermanentError,
    TelegramTransientError,
)
from apps.notifications.telegram.services import schedule_due_reminders


@shared_task(name="apps.notifications.telegram.tasks.dispatch_due_reminders")
def dispatch_due_reminders() -> int:
    return schedule_due_reminders()


@shared_task(
    bind=True,
    autoretry_for=(),
    max_retries=3,
    retry_backoff=True,
    name="apps.notifications.telegram.tasks.send_telegram_delivery",
)
def send_telegram_delivery(self, delivery_id: int) -> str:
    delivery = TelegramDelivery.objects.select_related("recipient_user", "event").get(
        pk=delivery_id
    )
    if delivery.status == TelegramDelivery.Status.SENT:
        return delivery.status
    connection = TelegramConnection.objects.filter(
        user=delivery.recipient_user, is_active=True
    ).first()
    if not connection:
        delivery.status = TelegramDelivery.Status.SKIPPED
        delivery.error_code = "not_connected"
        delivery.attempted_at = timezone.now()
        delivery.save(update_fields=("status", "error_code", "attempted_at"))
        return delivery.status
    delivery.attempted_at = timezone.now()
    try:
        result = TelegramClient().send_message(connection.chat_id, delivery.message_text)
    except TelegramTransientError as exc:
        delivery.retry_count += 1
        delivery.error_code = exc.code
        delivery.save(update_fields=("attempted_at", "retry_count", "error_code"))
        if delivery.retry_count >= 3:
            delivery.status = TelegramDelivery.Status.FAILED
            delivery.save(update_fields=("status",))
            log_audit_event("telegram.reminder_failed", target=delivery.event)
            return delivery.status
        raise self.retry(exc=exc) from exc
    except (TelegramPermanentError, TelegramDisabledError) as exc:
        delivery.status = TelegramDelivery.Status.FAILED
        delivery.error_code = exc.code
        delivery.save(update_fields=("status", "error_code", "attempted_at"))
        if isinstance(exc, TelegramPermanentError):
            connection.is_active = False
            connection.save(update_fields=("is_active",))
        log_audit_event("telegram.reminder_failed", target=delivery.event)
        return delivery.status
    delivery.status = TelegramDelivery.Status.SENT
    delivery.sent_at = timezone.now()
    delivery.telegram_message_id = result.message_id
    delivery.error_code = ""
    delivery.save(
        update_fields=("status", "sent_at", "telegram_message_id", "error_code", "attempted_at")
    )
    action = (
        "telegram.reminder_sent"
        if delivery.notification_type.startswith("reminder_")
        else "telegram.event_notification_sent"
    )
    log_audit_event(action, target=delivery.event, payload={"delivery_id": delivery.pk})
    return delivery.status
