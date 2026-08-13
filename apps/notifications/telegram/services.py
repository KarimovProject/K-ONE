from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.services import log_audit_event
from apps.events.models import Event
from apps.notifications.models import TelegramDelivery
from apps.notifications.telegram.formatters import (
    format_event_notification,
    format_reminder,
)

REMINDERS = {
    "reminder_7d": timedelta(days=7),
    "reminder_3d": timedelta(days=3),
    "reminder_1d": timedelta(days=1),
    "reminder_3h": timedelta(hours=3),
    "reminder_30m": timedelta(minutes=30),
}
ELIGIBLE_STATUSES = (Event.Status.APPROVED, Event.Status.PLANNED)


def event_recipients(event: Event, include_admins: bool = False) -> list[User]:
    recipients = [event.responsible_employee, event.management_responsible]
    if include_admins:
        recipients.extend(
            User.objects.filter(
                is_active=True,
                role__in=(User.Role.SUPER_ADMIN, User.Role.INTERNATIONAL_ADMIN),
            )
        )
    return list({user.pk: user for user in recipients if user}.values())


def _language(user: User) -> str:
    return getattr(user, "preferred_language", "uz") or "uz"


def schedule_due_reminders(now=None) -> int:
    now = now or timezone.now()
    window_start = now - timedelta(minutes=2)
    window_end = now + timedelta(minutes=2)
    count = 0
    events = Event.objects.filter(
        reminders_enabled=True,
        status__in=ELIGIBLE_STATUSES,
        planned_date__gte=now.date(),
    ).select_related("venue", "responsible_employee", "management_responsible")
    for event in events:
        for reminder_type, delta in REMINDERS.items():
            if not getattr(event, reminder_type):
                continue
            scheduled_for = event.start_datetime - delta
            if not window_start <= scheduled_for <= window_end:
                continue
            for recipient in event_recipients(event):
                delivery, created = TelegramDelivery.objects.get_or_create(
                    event=event,
                    recipient_user=recipient,
                    notification_type=reminder_type,
                    scheduled_for=scheduled_for,
                    defaults={
                        "message_text": format_reminder(
                            event,
                            reminder_type,
                            _language(recipient),
                            settings.IEMS_BASE_URL,
                        )
                    },
                )
                if created:
                    count += 1
                    log_audit_event(
                        "telegram.reminder_scheduled",
                        target=event,
                        payload={"delivery_id": delivery.pk, "type": reminder_type},
                    )
                    transaction.on_commit(lambda pk=delivery.pk: _enqueue_delivery(pk))
    return count


def schedule_event_notification(event: Event, action: str, include_admins: bool = False) -> int:
    now = timezone.now().replace(microsecond=0)
    count = 0
    for recipient in event_recipients(event, include_admins=include_admins):
        delivery, created = TelegramDelivery.objects.get_or_create(
            event=event,
            recipient_user=recipient,
            notification_type=action,
            scheduled_for=now,
            defaults={
                "message_text": format_event_notification(
                    event,
                    action,
                    _language(recipient),
                    settings.IEMS_BASE_URL,
                )
            },
        )
        if created:
            count += 1
            transaction.on_commit(lambda pk=delivery.pk: _enqueue_delivery(pk))
    return count


def _enqueue_delivery(delivery_id: int) -> None:
    if not settings.TELEGRAM_BOT_ENABLED:
        return
    from apps.notifications.telegram.tasks import send_telegram_delivery

    send_telegram_delivery.delay(delivery_id)
