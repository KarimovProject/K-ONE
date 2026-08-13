from datetime import date, time

import pytest
from django.utils import translation

from apps.accounts.models import User
from apps.events.models import Event, EventType
from apps.venues.models import Venue


@pytest.mark.django_db
def test_weekday_and_status_localization(db):
    user = User.objects.create_user(username="loc_user", password="password")
    venue = Venue.objects.create(
        code="V",
        name_uz="V",
        name_ru="V",
        name_en="V",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )
    etype = EventType.objects.create(code="t", name_uz="T", name_ru="T", name_en="T")

    event = Event.objects.create(
        title="Localized Event",
        event_type=etype,
        venue=venue,
        planned_date=date(2026, 8, 12),  # Wednesday
        start_time=time(10, 0),
        end_time=time(11, 0),
        responsible_employee=user,
        management_responsible=user,
        status=Event.Status.PLANNED,
    )

    with translation.override("uz"):
        assert event.weekday_name == "Chorshanba"
        assert event.get_status_display() in ("Rejalashtirilgan", "Planned")

    with translation.override("ru"):
        assert event.weekday_name == "Среда"

    with translation.override("en"):
        assert event.weekday_name == "Wednesday"
        assert event.get_status_display() == "Planned"
