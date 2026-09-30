from celery import shared_task

from apps.notifications.services import deliver_email
from apps.notifications.telegram.tasks import (
    dispatch_due_reminders,
    send_telegram_delivery,
)


@shared_task(name="apps.notifications.tasks.send_notification_email_task")
def send_notification_email_task(address: str, subject: str, message: str) -> bool:
    return deliver_email(address, subject, message)


__all__ = ("dispatch_due_reminders", "send_notification_email_task", "send_telegram_delivery")
