from apps.notifications.models import Notification


def unread_notifications(request):
    """Exposes the unread notification count and the most recent unread
    notification to every workspace template — powers the topbar bell
    badge and the first-view toast, without every view having to wire it
    up individually."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    unread_qs = Notification.objects.filter(recipient=user, is_read=False)
    count = unread_qs.count()
    latest = unread_qs.first() if count else None

    return {
        "unread_notification_count": count,
        "latest_unread_notification": latest,
    }
