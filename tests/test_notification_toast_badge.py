import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.notifications.context_processors import unread_notifications
from apps.notifications.models import Notification


@pytest.fixture
def user_with_notifications(db):
    user = User.objects.create_user(
        username="notif.user", password="x", role=User.Role.INTERNATIONAL_ADMIN
    )
    Notification.objects.create(recipient=user, title="First", message="First message")
    Notification.objects.create(recipient=user, title="Second", message="Second message")
    return user


@pytest.mark.django_db
class TestUnreadNotificationsContextProcessor:
    def test_returns_count_and_latest_for_authenticated_user(self, rf, user_with_notifications):
        request = rf.get("/")
        request.user = user_with_notifications
        context = unread_notifications(request)
        assert context["unread_notification_count"] == 2
        assert context["latest_unread_notification"].title == "Second"

    def test_returns_empty_for_anonymous_user(self, rf):
        from django.contrib.auth.models import AnonymousUser

        request = rf.get("/")
        request.user = AnonymousUser()
        assert unread_notifications(request) == {}


@pytest.mark.django_db
class TestNotificationBellBadge:
    def test_badge_renders_on_a_workspace_page_with_unread_notifications(
        self, client, user_with_notifications
    ):
        client.force_login(user_with_notifications)
        res = client.get(reverse("profile"))
        assert res.status_code == 200
        assert b"notification-badge" in res.content

    def test_badge_absent_once_all_notifications_are_read(self, client, user_with_notifications):
        Notification.objects.filter(recipient=user_with_notifications).update(is_read=True)
        client.force_login(user_with_notifications)
        res = client.get(reverse("profile"))
        assert b"notification-badge" not in res.content


@pytest.mark.django_db
class TestNotificationListMarksAllRead:
    def test_viewing_the_list_marks_everything_read(self, client, user_with_notifications):
        client.force_login(user_with_notifications)
        assert Notification.objects.filter(
            recipient=user_with_notifications, is_read=False
        ).count() == 2

        client.get(reverse("notifications:list"))

        assert Notification.objects.filter(
            recipient=user_with_notifications, is_read=False
        ).count() == 0

    def test_badge_is_gone_on_the_next_page_after_viewing_the_list(
        self, client, user_with_notifications
    ):
        client.force_login(user_with_notifications)
        client.get(reverse("notifications:list"))

        res = client.get(reverse("profile"))
        assert b"notification-badge" not in res.content

    def test_newly_read_ids_still_highlights_what_was_unread_on_this_view(
        self, client, user_with_notifications
    ):
        client.force_login(user_with_notifications)
        res = client.get(reverse("notifications:list"))
        # Both notifications were unread when this exact page load started,
        # so both should still render with the "unread" highlight class.
        assert res.content.count(b"notification-item unread") == 2
