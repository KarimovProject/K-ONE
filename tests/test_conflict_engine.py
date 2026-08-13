from datetime import date, time

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.events.models import Event, EventType
from apps.events.services.conflicts import (
    find_conflicting_events,
    validate_and_lock_event_reservation,
)
from apps.venues.models import Venue


@pytest.fixture
def setup_conflict_data(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="test_user", password="password")

    v1 = Venue.objects.create(
        code="V1",
        name_uz="Venue 1",
        name_ru="Venue 1",
        name_en="Venue 1",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )
    v2 = Venue.objects.create(
        code="V2",
        name_uz="Venue 2",
        name_ru="Venue 2",
        name_en="Venue 2",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )

    etype = EventType.objects.create(code="conf", name_uz="Conf", name_ru="Conf", name_en="Conf")

    base_event = Event.objects.create(
        title="Existing Conference",
        event_type=etype,
        venue=v1,
        planned_date=date(2026, 9, 1),
        start_time=time(10, 0),
        end_time=time(12, 0),
        responsible_employee=user,
        management_responsible=user,
        status=Event.Status.PLANNED,
    )

    return {
        "user": user,
        "v1": v1,
        "v2": v2,
        "etype": etype,
        "base_event": base_event,
    }


@pytest.mark.django_db
class TestConflictEngine:
    def test_exact_overlap_conflict(self, setup_conflict_data):
        conflicts = find_conflicting_events(
            venue=setup_conflict_data["v1"],
            planned_date=date(2026, 9, 1),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        assert setup_conflict_data["base_event"] in conflicts

    def test_partial_overlap_conflict(self, setup_conflict_data):
        # 11:00 to 13:00 overlaps 10:00 to 12:00
        conflicts = find_conflicting_events(
            venue=setup_conflict_data["v1"],
            planned_date=date(2026, 9, 1),
            start_time=time(11, 0),
            end_time=time(13, 0),
        )
        assert setup_conflict_data["base_event"] in conflicts

    def test_containment_conflict(self, setup_conflict_data):
        # 09:00 to 13:00 contains 10:00 to 12:00
        conflicts = find_conflicting_events(
            venue=setup_conflict_data["v1"],
            planned_date=date(2026, 9, 1),
            start_time=time(9, 0),
            end_time=time(13, 0),
        )
        assert setup_conflict_data["base_event"] in conflicts

    def test_touching_boundaries_no_conflict(self, setup_conflict_data):
        # 08:00 to 10:00 touches 10:00 to 12:00 -> NO conflict
        before = find_conflicting_events(
            venue=setup_conflict_data["v1"],
            planned_date=date(2026, 9, 1),
            start_time=time(8, 0),
            end_time=time(10, 0),
        )
        assert not before.exists()

        # 12:00 to 14:00 touches 10:00 to 12:00 -> NO conflict
        after = find_conflicting_events(
            venue=setup_conflict_data["v1"],
            planned_date=date(2026, 9, 1),
            start_time=time(12, 0),
            end_time=time(14, 0),
        )
        assert not after.exists()

    def test_cancelled_event_ignored(self, setup_conflict_data):
        setup_conflict_data["base_event"].status = Event.Status.CANCELLED
        setup_conflict_data["base_event"].save()

        conflicts = find_conflicting_events(
            venue=setup_conflict_data["v1"],
            planned_date=date(2026, 9, 1),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        assert not conflicts.exists()

    def test_different_venue_allowed(self, setup_conflict_data):
        conflicts = find_conflicting_events(
            venue=setup_conflict_data["v2"],
            planned_date=date(2026, 9, 1),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        assert not conflicts.exists()

    def test_validate_and_lock_raises_on_conflict(self, setup_conflict_data):
        with pytest.raises(ValidationError):
            validate_and_lock_event_reservation(
                venue=setup_conflict_data["v1"],
                planned_date=date(2026, 9, 1),
                start_time=time(10, 30),
                end_time=time(11, 30),
                status=Event.Status.PLANNED,
            )
