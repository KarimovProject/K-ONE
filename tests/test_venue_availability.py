from datetime import date, datetime, time

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.events.models import Event, EventType
from apps.events.services.conflicts import check_venue_availability
from apps.venues.models import Venue
from apps.venues.services.live_status import all_venues_live_status, venue_live_status


@pytest.fixture
def availability_setup(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="avail_user", password="password")

    v1 = Venue.objects.create(
        code="ICH",
        name_uz="Conference Hall",
        name_ru="Conference Hall",
        name_en="Conference Hall",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
        is_active=True,
        display_enabled=True,
    )
    v2 = Venue.objects.create(
        code="SSH",
        name_uz="Seminar Hall",
        name_ru="Seminar Hall",
        name_en="Seminar Hall",
        capacity=200,
        working_start=time(8, 0),
        working_end=time(20, 0),
        is_active=True,
        display_enabled=True,
    )

    etype = EventType.objects.create(code="sem", name_uz="Sem", name_ru="Sem", name_en="Sem")

    event = Event.objects.create(
        title="Oncology Symposium",
        event_type=etype,
        venue=v1,
        planned_date=date(2026, 8, 12),
        start_time=time(14, 0),
        end_time=time(16, 0),
        responsible_employee=user,
        management_responsible=user,
        status=Event.Status.PLANNED,
        expected_attendees=80,
    )

    return {"user": user, "v1": v1, "v2": v2, "etype": etype, "event": event}


@pytest.mark.django_db
class TestVenueAvailability:
    def test_free_venue_availability(self, availability_setup):
        result = check_venue_availability(
            venue=availability_setup["v1"],
            planned_date=date(2026, 8, 12),
            start_time=time(9, 0),
            end_time=time(11, 0),
        )
        assert result.is_available
        assert result.status_label == "AVAILABLE"

    def test_occupied_venue_availability_and_alternatives(self, availability_setup):
        result = check_venue_availability(
            venue=availability_setup["v1"],
            planned_date=date(2026, 8, 12),
            start_time=time(14, 30),
            end_time=time(15, 30),
            expected_attendees=50,
        )
        assert not result.is_available
        assert result.status_label == "OCCUPIED"
        assert result.conflicting_event == availability_setup["event"]
        assert len(result.alternative_venues) >= 1
        assert result.alternative_venues[0]["code"] == "SSH"

    def test_capacity_warning(self, availability_setup):
        result = check_venue_availability(
            venue=availability_setup["v1"],  # capacity 100
            planned_date=date(2026, 8, 12),
            start_time=time(9, 0),
            end_time=time(11, 0),
            expected_attendees=150,  # exceeds 100
        )
        assert result.is_available
        assert result.capacity_warning is not None
        assert "sig'imidan" in result.capacity_warning
        assert "oshib ketmoqda" in result.capacity_warning

    def test_live_status_service(self, availability_setup):
        # Test reference time at 14:30 today
        ref_dt = timezone.make_aware(datetime(2026, 8, 12, 14, 30))
        status_v1 = venue_live_status(availability_setup["v1"], ref_dt)
        assert status_v1["occupied_now"]
        assert status_v1["current_event"] == availability_setup["event"]

        statuses_all = all_venues_live_status(ref_dt)
        assert len(statuses_all) == 2
