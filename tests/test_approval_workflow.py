import datetime

import pytest
from django.core.exceptions import ValidationError

from apps.events.models import Event, EventType
from apps.events.services.workflow import approve_event, override_event, reject_event
from apps.venues.models import Venue

pytestmark = pytest.mark.django_db


def test_override_event_displaces_conflicts(client, admin_user, user):
    venue = Venue.objects.create(
        name_en="Test Venue",
        code="TV",
        capacity=10,
        working_start=datetime.time(8, 0),
        working_end=datetime.time(20, 0),
    )
    event_type = EventType.objects.create(name_en="Test Type", code="TT")

    # Setup conflicting events
    event1 = Event.objects.create(
        title="Event 1",
        status=Event.Status.APPROVED,
        responsible_employee=user,
        management_responsible=admin_user,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    event2 = Event.objects.create(
        title="Event 2",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=user,
        management_responsible=admin_user,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 1),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
        priority=Event.Priority.EMERGENCY,
    )

    # Normal approve should fail
    with pytest.raises(ValidationError):
        approve_event(event2, admin_user, notes="Standard approval")

    # Override should succeed and displace event1
    override_event(event2, admin_user, reason="Emergency VIP visit")

    event1.refresh_from_db()
    event2.refresh_from_db()

    assert event2.status == Event.Status.APPROVED
    assert event1.status == Event.Status.DISPLACED


def test_reject_event_releases_room(client, admin_user, user):
    venue = Venue.objects.create(
        name_en="Test Venue 2",
        code="TV2",
        capacity=10,
        working_start=datetime.time(8, 0),
        working_end=datetime.time(20, 0),
    )
    event_type = EventType.objects.create(name_en="Test Type 2", code="TT2")
    event = Event.objects.create(
        title="Event 3",
        status=Event.Status.PENDING_APPROVAL,
        responsible_employee=user,
        management_responsible=admin_user,
        venue=venue,
        event_type=event_type,
        planned_date=datetime.date(2027, 1, 2),
        start_time=datetime.time(10, 0),
        end_time=datetime.time(12, 0),
    )
    reject_event(event, admin_user, reason="Not appropriate")

    event.refresh_from_db()
    assert event.status == Event.Status.REJECTED
