from datetime import date, time

import pytest
from django.contrib.auth import get_user_model
from django.utils import translation

from apps.events.models import Event, EventType
from apps.venues.models import Venue


@pytest.fixture
def test_setup(db):
    user_model = get_user_model()
    resp = user_model.objects.create_user(username="resp_emp", password="password")
    mgmt = user_model.objects.create_user(username="mgmt_resp", password="password")

    venue = Venue.objects.create(
        code="ICH",
        name_uz="Xalqaro konferensiyalar zali",
        name_ru="Международный конференц-зал",
        name_en="International Conference Hall",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )

    event_type = EventType.objects.create(
        code="conference",
        name_uz="Konferensiya",
        name_ru="Конференция",
        name_en="Conference",
        color="#2563EB",
    )

    return {
        "resp": resp,
        "mgmt": mgmt,
        "venue": venue,
        "event_type": event_type,
    }


@pytest.mark.django_db
class TestEventModel:
    def test_event_creation_and_properties(self, test_setup):
        event = Event.objects.create(
            title="Global Health Summit",
            event_type=test_setup["event_type"],
            venue=test_setup["venue"],
            planned_date=date(2026, 8, 12),  # Wednesday
            start_time=time(10, 0),
            end_time=time(12, 30),
            responsible_employee=test_setup["resp"],
            management_responsible=test_setup["mgmt"],
            status=Event.Status.PLANNED,
            priority=Event.Priority.HIGH,
            expected_attendees=80,
        )

        assert str(event) == "Global Health Summit (2026-08-12)"
        assert event.duration_minutes == 150
        assert not event.is_over_capacity

        with translation.override("uz"):
            assert event.weekday_name == "Chorshanba"

        with translation.override("en"):
            assert event.weekday_name == "Wednesday"

        with translation.override("ru"):
            assert event.weekday_name == "Среда"

    def test_event_over_capacity_property(self, test_setup):
        event = Event.objects.create(
            title="Overcrowded Summit",
            event_type=test_setup["event_type"],
            venue=test_setup["venue"],  # capacity 100
            planned_date=date(2026, 8, 15),
            start_time=time(9, 0),
            end_time=time(11, 0),
            responsible_employee=test_setup["resp"],
            management_responsible=test_setup["mgmt"],
            expected_attendees=150,
        )

        assert event.is_over_capacity
