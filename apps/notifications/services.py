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


def get_unread_count(user: User) -> int:
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=user, is_read=False).count()


def get_user_notifications(user: User, limit: int = 20) -> list[Notification]:
    if not user.is_authenticated:
        return []
    return list(Notification.objects.filter(recipient=user)[:limit])
