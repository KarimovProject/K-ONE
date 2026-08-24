import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.audit.models import AuditEventLog
from apps.events.models import Event, EventType
from apps.events.services.workflow import approve_event, override_event, reject_event
from apps.venues.models import Venue

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def venue():
    return Venue.objects.create(
        name_en="Test Venue",
        code="TV",
        capacity=10,
        working_start=datetime.time(8, 0),
        working_end=datetime.time(20, 0),
        display_enabled=True,
    )


@pytest.fixture
def event_type():
    return EventType.objects.create(name_en="Test Type", code="TT")


@pytest.fixture
def standard_user(django_user_model):
    return django_user_model.objects.create_user(username="std_user", password="password")


@pytest.fixture
def admin_user2(django_user_model):
    return django_user_model.objects.create_superuser(username="admin_user2", password="password")


def test_pending_visible_to_approver(client, admin_user2, standard_user, venue, event_type):
    Event.objects.create(
        title="Pending Event",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    client.force_login(admin_user2)
    response = client.get(reverse("events:approval-list"))
    assert response.status_code == 200
    assert "Pending Event" in response.content.decode()


def test_unauthorized_user_cannot_approve(client, standard_user, admin_user2, venue, event_type):
    event = Event.objects.create(
        title="Pending Event",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    client.force_login(standard_user)
    response = client.post(reverse("events:approve", kwargs={"pk": event.pk}))
    assert response.status_code == 403


def test_unauthorized_direct_post_cannot_approve(
    client, standard_user, admin_user2, venue, event_type
):
    event = Event.objects.create(
        title="Pending Event",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    client.force_login(standard_user)
    # direct POST to override
    response = client.post(
        reverse("events:override", kwargs={"pk": event.pk}), data={"reason": "test"}
    )
    assert response.status_code == 403


def test_approve_success(client, admin_user2, standard_user, venue, event_type):
    event = Event.objects.create(
        title="Pending Event",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    approve_event(event, admin_user2)
    event.refresh_from_db()
    assert event.status == Event.Status.APPROVED


def test_reject_without_reason_blocked(admin_user2, standard_user, venue, event_type):
    event = Event.objects.create(
        title="Pending Event",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    with pytest.raises(ValidationError):
        reject_event(event, admin_user2, reason="")


def test_reject_with_reason_success(admin_user2, standard_user, venue, event_type):
    event = Event.objects.create(
        title="Pending Event",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    reject_event(event, admin_user2, reason="Not appropriate")
    event.refresh_from_db()
    assert event.status == Event.Status.REJECTED


def test_rejected_event_releases_room(admin_user2, standard_user, venue, event_type):
    event = Event.objects.create(
        title="Pending Event",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    reject_event(event, admin_user2, reason="Not appropriate")

    # Try to approve a new event at the same time
    event2 = Event.objects.create(
        title="New Event",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    approve_event(event2, admin_user2)
    event2.refresh_from_db()
    assert event2.status == Event.Status.APPROVED


def test_conflict_detected_for_pending_high_priority_event(
    admin_user2, standard_user, venue, event_type
):
    Event.objects.create(
        title="Event 1",
        status=Event.Status.APPROVED,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    event2 = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    with pytest.raises(ValidationError):
        approve_event(event2, admin_user2)


def test_equal_priority_override_blocked(admin_user2, standard_user, venue, event_type):
    Event.objects.create(
        title="Event 1",
        status=Event.Status.APPROVED,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    event2 = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    with pytest.raises(ValidationError):
        override_event(event2, admin_user2, reason="test")


def test_lower_priority_override_blocked(admin_user2, standard_user, venue, event_type):
    Event.objects.create(
        title="Event 1",
        status=Event.Status.APPROVED,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    event2 = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.NORMAL,
    )
    with pytest.raises(ValidationError):
        override_event(event2, admin_user2, reason="test")


def test_higher_priority_override_allowed(admin_user2, standard_user, venue, event_type):
    Event.objects.create(
        title="Event 1",
        status=Event.Status.APPROVED,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.NORMAL,
    )
    event2 = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    override_event(event2, admin_user2, reason="test")
    event2.refresh_from_db()
    assert event2.status == Event.Status.APPROVED


def test_approver_without_override_capability_blocked(client, standard_user, venue, event_type):
    # standard_user doesn't have override capability
    event = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=standard_user,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    client.force_login(standard_user)
    response = client.post(
        reverse("events:override", kwargs={"pk": event.pk}), data={"reason": "test"}
    )
    assert response.status_code == 403


def test_override_without_reason_blocked(admin_user2, standard_user, venue, event_type):
    Event.objects.create(
        title="Event 1",
        status=Event.Status.APPROVED,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    event2 = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    with pytest.raises(ValidationError):
        override_event(event2, admin_user2, reason="")


def test_displaced_event_status_correct(admin_user2, standard_user, venue, event_type):
    event1 = Event.objects.create(
        title="Event 1",
        status=Event.Status.APPROVED,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    event2 = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    override_event(event2, admin_user2, reason="test")
    event1.refresh_from_db()
    assert event1.status == Event.Status.DISPLACED


def test_displaced_event_releases_room(admin_user2, standard_user, venue, event_type):
    Event.objects.create(
        title="Event 1",
        status=Event.Status.DISPLACED,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )

    event3 = Event.objects.create(
        title="Event 3",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    approve_event(event3, admin_user2)
    event3.refresh_from_db()
    assert event3.status == Event.Status.APPROVED


def test_override_audit_logs(admin_user2, standard_user, venue, event_type):
    event1 = Event.objects.create(
        title="Event 1",
        status=Event.Status.APPROVED,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    event2 = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=standard_user,
        management_responsible=admin_user2,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.HIGH,
    )
    override_event(event2, admin_user2, reason="Urgent matters")

    logs = AuditEventLog.objects.filter(target_id=str(event2.pk), action="event.approved_override")
    assert logs.exists()
    assert logs.first().actor == admin_user2
    assert "Urgent matters" in logs.first().payload.get("reason", "")

    displaced_logs = AuditEventLog.objects.filter(
        target_id=str(event1.pk), action="event.displaced"
    )
    assert displaced_logs.exists()
    assert displaced_logs.first().actor == admin_user2
    assert "Urgent matters" in displaced_logs.first().payload.get("reason", "")
    assert str(event2.pk) in displaced_logs.first().payload.get("displaced_by", "")
