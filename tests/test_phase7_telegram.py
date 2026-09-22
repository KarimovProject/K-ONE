from datetime import time, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from apps.events.models import Event, EventType
from apps.events.services.emergency import execute_emergency_override
from apps.events.services.workflow import approve_event, reject_event, reschedule_event
from apps.notifications.models import (
    TelegramConnection,
    TelegramDelivery,
    TelegramLinkToken,
)
from apps.notifications.telegram.client import (
    TelegramClient,
    TelegramPermanentError,
    TelegramTransientError,
)
from apps.notifications.telegram.formatters import format_reminder
from apps.notifications.telegram.linking import consume_link_token, create_link_token
from apps.notifications.telegram.services import schedule_due_reminders
from apps.notifications.telegram.tasks import send_telegram_delivery
from apps.organizations.models import Organization
from apps.venues.models import Venue

pytestmark = pytest.mark.django_db


@pytest.fixture
def phase7_data():
    users = get_user_model()
    responsible = users.objects.create_user(
        username="p7_responsible",
        password="test-password",
        role=users.Role.RESPONSIBLE_EMPLOYEE,
        preferred_language="uz",
    )
    management = users.objects.create_user(
        username="p7_management",
        password="test-password",
        role=users.Role.MANAGEMENT_RESPONSIBLE,
        preferred_language="ru",
    )
    admin = users.objects.create_user(
        username="p7_admin",
        password="test-password",
        role=users.Role.INTERNATIONAL_ADMIN,
    )
    venue = Venue.objects.create(
        code="P7-HALL",
        name_uz="Anjuman zali",
        name_ru="Конференц-зал",
        name_en="Conference Hall",
        capacity=100,
        working_start=time(8),
        working_end=time(20),
    )
    event_type = EventType.objects.create(
        code="p7-forum", name_uz="Forum", name_ru="Форум", name_en="Forum"
    )
    event = Event.objects.create(
        title="Phase 7 Forum",
        event_type=event_type,
        venue=venue,
        planned_date=(timezone.localtime() + timedelta(days=7)).date(),
        start_time=(timezone.localtime() + timedelta(minutes=1)).time().replace(microsecond=0),
        end_time=time(18),
        responsible_employee=responsible,
        management_responsible=management,
        created_by=admin,
        status=Event.Status.APPROVED,
    )
    event.organizing_organizations.add(Organization.objects.create(name="International Department"))
    return responsible, management, admin, event


def test_link_token_is_hashed_short_lived_and_one_time(phase7_data):
    responsible, _, _, _ = phase7_data
    raw = create_link_token(responsible)
    stored = TelegramLinkToken.objects.get(user=responsible)
    assert raw not in stored.token_hash
    connection = consume_link_token(raw, "12345", 987, "linked_user")
    assert connection and connection.user == responsible
    assert consume_link_token(raw, "999", 999) is None


def test_expired_and_wrong_tokens_are_rejected(phase7_data):
    responsible, _, _, _ = phase7_data
    raw = create_link_token(responsible)
    TelegramLinkToken.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    assert consume_link_token(raw, "1", 1) is None
    assert consume_link_token("wrong-token", "1", 1) is None


@pytest.mark.parametrize(
    ("field", "delta"),
    [
        ("reminder_7d", timedelta(days=7)),
        ("reminder_3d", timedelta(days=3)),
        ("reminder_1d", timedelta(days=1)),
        ("reminder_3h", timedelta(hours=3)),
        ("reminder_30m", timedelta(minutes=30)),
    ],
)
def test_each_due_reminder_is_scheduled_once(phase7_data, field, delta):
    _, _, _, event = phase7_data
    now = timezone.now().replace(second=0, microsecond=0)
    start = now + delta
    event.planned_date = timezone.localtime(start).date()
    event.start_time = timezone.localtime(start).time().replace(tzinfo=None)
    event.save()
    assert schedule_due_reminders(now) == 2
    assert schedule_due_reminders(now) == 0
    assert TelegramDelivery.objects.filter(notification_type=field).count() == 2


@pytest.mark.parametrize("status", [Event.Status.CANCELLED, Event.Status.DISPLACED])
def test_ineligible_events_are_ignored(phase7_data, status):
    _, _, _, event = phase7_data
    event.status = status
    event.save(update_fields=["status"])
    assert schedule_due_reminders(event.start_datetime - timedelta(days=7)) == 0


def test_disabled_event_is_ignored(phase7_data):
    _, _, _, event = phase7_data
    event.reminders_enabled = False
    event.save(update_fields=["reminders_enabled"])
    assert schedule_due_reminders(event.start_datetime - timedelta(days=7)) == 0


@pytest.mark.parametrize("language", ["uz", "ru", "en"])
def test_reminder_localization(phase7_data, language):
    _, _, _, event = phase7_data
    message = format_reminder(event, "reminder_3h", language)
    assert event.title in message
    assert event.venue.name_uz in message


def test_unconnected_recipient_is_safely_skipped(phase7_data):
    responsible, _, _, event = phase7_data
    delivery = TelegramDelivery.objects.create(
        event=event,
        recipient_user=responsible,
        notification_type="approved",
        scheduled_for=timezone.now(),
        message_text="hello",
    )
    assert send_telegram_delivery.run(delivery.pk) == TelegramDelivery.Status.SKIPPED


class FakeTransport:
    def __init__(self, response=None, error=None):
        self.response = response or {"ok": True, "result": {"message_id": 42}}
        self.error = error

    def post(self, url, payload, timeout):
        if self.error:
            raise self.error("failed")
        return self.response


@override_settings(TELEGRAM_BOT_ENABLED=True, TELEGRAM_BOT_TOKEN="test-only-token")
def test_fake_transport_send_and_permanent_error():
    result = TelegramClient(transport=FakeTransport()).send_message("1", "hello")
    assert result.message_id == "42"
    client = TelegramClient(
        transport=FakeTransport({"ok": False, "error_code": 403, "description": "blocked"})
    )
    with pytest.raises(TelegramPermanentError):
        client.send_message("1", "hello")


def test_transient_delivery_retries(phase7_data, monkeypatch):
    responsible, _, _, event = phase7_data
    TelegramConnection.objects.create(user=responsible, chat_id="1", telegram_user_id=1)
    delivery = TelegramDelivery.objects.create(
        event=event,
        recipient_user=responsible,
        notification_type="approved",
        scheduled_for=timezone.now(),
        message_text="hello",
    )

    def fail(*args, **kwargs):
        raise TelegramTransientError("network")

    monkeypatch.setattr(TelegramClient, "send_message", fail)
    with pytest.raises(Exception):
        send_telegram_delivery.run(delivery.pk)
    delivery.refresh_from_db()
    assert delivery.retry_count == 1


def test_settings_ui_rbac_and_no_secret_or_chat_id(client, phase7_data):
    responsible, _, admin, event = phase7_data
    TelegramConnection.objects.create(
        user=responsible, chat_id="secret-chat-id", telegram_user_id=1
    )
    client.force_login(responsible)
    response = client.get(reverse("notifications:telegram-settings"))
    assert response.status_code == 200
    assert b"secret-chat-id" not in response.content
    assert b"TELEGRAM_BOT_TOKEN" not in response.content
    assert client.get(reverse("notifications:event-reminders", args=[event.pk])).status_code == 403
    client.force_login(admin)
    assert client.get(reverse("notifications:event-reminders", args=[event.pk])).status_code == 200


def test_disconnect_is_post_only_and_scoped(client, phase7_data):
    responsible, management, _, _ = phase7_data
    TelegramConnection.objects.create(user=responsible, chat_id="1", telegram_user_id=1)
    TelegramConnection.objects.create(user=management, chat_id="2", telegram_user_id=2)
    client.force_login(responsible)
    assert client.get(reverse("notifications:telegram-disconnect")).status_code == 405
    assert client.post(reverse("notifications:telegram-disconnect")).status_code == 302
    assert not TelegramConnection.objects.filter(user=responsible).exists()
    assert TelegramConnection.objects.filter(user=management).exists()


def test_approved_and_rejected_create_immediate_deliveries(phase7_data):
    _, management, _, event = phase7_data
    event.status = Event.Status.PENDING_APPROVAL
    event.save(update_fields=["status"])
    approve_event(event, management)
    assert event.telegram_deliveries.filter(notification_type="approved").count() == 2
    event.status = Event.Status.PENDING_APPROVAL
    event.save(update_fields=["status"])
    reject_event(event, management, "Needs correction")
    assert event.telegram_deliveries.filter(notification_type="rejected").count() == 2


def test_rescheduled_creates_immediate_delivery(phase7_data):
    _, _, admin, event = phase7_data
    new_date = event.planned_date + timedelta(days=1)
    reschedule_event(event, admin, new_date, time(9), time(10))
    assert event.telegram_deliveries.filter(notification_type="rescheduled").count() == 2


def test_emergency_notifies_staff_and_international_admins(phase7_data):
    _, _, admin, event = phase7_data
    event.status = Event.Status.DRAFT
    event.save(update_fields=["status"])
    execute_emergency_override(event, admin, "Authorized test justification")
    deliveries = event.telegram_deliveries.filter(notification_type="emergency")
    assert deliveries.filter(recipient_user=admin).exists()
    assert all("justification" not in item.message_text.lower() for item in deliveries)


def test_assigned_responsible_notifies_only_that_employee(phase7_data):
    from apps.notifications.telegram.services import schedule_responsible_assignment

    responsible, management, _, event = phase7_data
    count = schedule_responsible_assignment(event)
    assert count == 1
    deliveries = event.telegram_deliveries.filter(notification_type="assigned_responsible")
    assert deliveries.count() == 1
    assert deliveries.get().recipient_user == responsible
    assert not event.telegram_deliveries.filter(
        notification_type="assigned_responsible", recipient_user=management
    ).exists()
    # A second call for the same recipient is a no-op (get_or_create).
    assert schedule_responsible_assignment(event) == 0


def test_reassigning_responsible_employee_notifies_new_assignee(client, phase7_data):
    from apps.accounts.models import User

    _, management, admin, event = phase7_data
    new_responsible = User.objects.create_user(
        username="p7_new_responsible",
        password="test-password",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )
    client.force_login(admin)
    post_data = {
        "title": event.title,
        "event_type": event.event_type_id,
        "description": "updated",
        "venue": event.venue_id,
        "planned_date": event.planned_date.isoformat(),
        "start_time": "09:00",
        "end_time": "10:00",
        "responsible_employee": new_responsible.pk,
        "management_responsible": management.pk,
        "status": Event.Status.APPROVED,
        "priority": Event.Priority.NORMAL,
        "expected_attendees": 10,
    }
    response = client.post(reverse("events:edit", kwargs={"pk": event.pk}), data=post_data)
    assert response.status_code == 302
    event.refresh_from_db()
    assert event.responsible_employee == new_responsible
    assert event.telegram_deliveries.filter(
        notification_type="assigned_responsible", recipient_user=new_responsible
    ).exists()


@override_settings(TELEGRAM_BOT_ENABLED=False, TELEGRAM_BOT_TOKEN="")
def test_disabled_client_fails_closed():
    from apps.notifications.telegram.client import TelegramDisabledError

    with pytest.raises(TelegramDisabledError):
        TelegramClient(transport=FakeTransport()).send_message("1", "hello")
