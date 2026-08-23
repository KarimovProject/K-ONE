from datetime import date, time

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.events.models import Event, EventType
from apps.venues.models import Venue


@pytest.fixture
def api_setup(db):
    user = get_user_model().objects.create_user(
        username="api_user",
        password="password",
        role=get_user_model().Role.INTERNATIONAL_ADMIN,
    )
    venue = Venue.objects.create(
        code="ICH",
        name_uz="Hall",
        name_ru="Hall",
        name_en="Hall",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )
    etype = EventType.objects.create(
        code="symp",
        name_uz="Symp",
        name_ru="Symp",
        name_en="Symp",
        color="#8B5CF6",
    )

    event = Event.objects.create(
        title="Symposium 2026",
        event_type=etype,
        venue=venue,
        planned_date=date(2026, 11, 20),
        start_time=time(10, 0),
        end_time=time(12, 0),
        responsible_employee=user,
        management_responsible=user,
        status=Event.Status.PLANNED,
    )
    return {"user": user, "venue": venue, "etype": etype, "event": event}


@pytest.mark.django_db
class TestCalendarAndAvailabilityAPI:
    def test_event_list_and_detail_api(self, client, api_setup):
        client.force_login(api_setup["user"])

        res = client.get(reverse("api-event-list"))
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) >= 1

        detail = client.get(reverse("api-event-detail", kwargs={"pk": api_setup["event"].pk}))
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data["title"] == "Symposium 2026"

    def test_calendar_events_api_feed(self, client, api_setup):
        client.force_login(api_setup["user"])

        url = reverse("api-calendar-events") + "?start=2026-11-01&end=2026-11-30"
        res = client.get(url)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]["title"] == "Symposium 2026"
        assert res.data[0]["backgroundColor"] == "#2563EB"
        assert res.data[0]["extendedProps"]["venue_name"] == "Hall"

    def test_venue_availability_api(self, client, api_setup):
        client.force_login(api_setup["user"])

        # Check free slot
        free_url = (
            reverse("api-venue-availability", kwargs={"pk": api_setup["venue"].pk})
            + "?date=2026-11-20&start_time=14:00&end_time=16:00"
        )
        res_free = client.get(free_url)
        assert res_free.status_code == status.HTTP_200_OK
        assert res_free.data["is_available"]

        # Check occupied slot
        occ_url = (
            reverse("api-venue-availability", kwargs={"pk": api_setup["venue"].pk})
            + "?date=2026-11-20&start_time=10:30&end_time=11:30"
        )
        res_occ = client.get(occ_url)
        assert res_occ.status_code == status.HTTP_200_OK
        assert not res_occ.data["is_available"]
        assert res_occ.data["conflicting_event"]["title"] == "Symposium 2026"
