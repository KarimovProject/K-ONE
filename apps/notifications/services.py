from django.conf import settings
from django.core.mail import send_mail

from apps.accounts.models import User
from apps.notifications.models import Notification


def send_notification(
    recipient: User,
    title: str,
    message: str,
    severity: str = Notification.Severity.INFO,
    target_url: str = "",
) -> Notification:
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        severity=severity,
        target_url=target_url,
    )


def notify_users(
    recipients: list[User],
    title: str,
    message: str,
    severity: str = Notification.Severity.INFO,
    target_url: str = "",
) -> list[Notification]:
    created = []
    seen_ids = set()
    for user in recipients:
        if user and user.pk not in seen_ids:
            seen_ids.add(user.pk)
            created.append(
                send_notification(
                    recipient=user,
                    title=title,
                    message=message,
                    severity=severity,
                    target_url=target_url,
                )
            )
    return created


def send_notification_email(recipient: User, subject: str, message: str) -> bool:
    """Best-effort email delivery — never raises, so a misconfigured or
    unreachable mail server can never block the action that triggered it."""
    if not recipient.email:
        return False
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def get_unread_count(user: User) -> int:
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=user, is_read=False).count()


def get_user_notifications(user: User, limit: int = 20) -> list[Notification]:
    if not user.is_authenticated:
        return []
    return list(Notification.objects.filter(recipient=user)[:limit])
