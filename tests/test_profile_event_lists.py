from datetime import time, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.events.models import Event, EventType
from apps.venues.models import Venue

pytestmark = pytest.mark.django_db


@pytest.fixture
def venue():
    return Venue.objects.create(
        code="MAIN",
        name_uz="Asosiy zal",
        name_ru="Asosiy zal",
        name_en="Asosiy zal",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )


@pytest.fixture
def event_type():
    return EventType.objects.create(
        code="conf", name_uz="Conf", name_ru="Conf", name_en="Conf"
    )


def _make_event(*, venue, event_type, user, days_offset, **extra):
    today = timezone.localdate()
    defaults = {
        "title": f"Event {days_offset}",
        "event_type": event_type,
        "venue": venue,
        "planned_date": today + timedelta(days=days_offset),
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "responsible_employee": user,
        "management_responsible": user,
        "created_by": user,
        "updated_by": user,
    }
    defaults.update(extra)
    return Event.objects.create(**defaults)


@pytest.fixture
def employee():
    return User.objects.create_user(
        username="responsible.staff", password="x", role=User.Role.RESPONSIBLE_EMPLOYEE
    )


class TestResponsibleEventsListView:
    def test_splits_events_into_past_and_upcoming(self, client, employee, venue, event_type):
        past = _make_event(
            venue=venue, event_type=event_type, user=employee, days_offset=-5,
            title="Past Conference",
        )
        upcoming = _make_event(
            venue=venue, event_type=event_type, user=employee, days_offset=5,
            title="Upcoming Conference",
        )
        client.force_login(employee)
        response = client.get(reverse("responsible-events"))
        assert response.status_code == 200
        content = response.content.decode()
        assert past.title in content
        assert upcoming.title in content
        # Past section must render above the Upcoming section.
        assert content.index(past.title) < content.index(upcoming.title)

    def test_empty_state_message_shown(self, client, employee):
        client.force_login(employee)
        response = client.get(reverse("responsible-events"))
        assert response.status_code == 200
        assert "Hozircha sizga biriktirilgan tadbir" in response.content.decode()

    def test_requires_login(self, client):
        assert client.get(reverse("responsible-events")).status_code == 302


class TestManagementEventsListView:
    def test_lists_management_events(self, client, employee, venue, event_type):
        event = _make_event(
            venue=venue, event_type=event_type, user=employee, days_offset=1,
            title="Board Meeting",
        )
        other_employee = User.objects.create_user(username="other.staff", password="x")
        event.responsible_employee = other_employee
        event.save(update_fields=["responsible_employee"])

        client.force_login(employee)
        response = client.get(reverse("management-events"))
        assert response.status_code == 200
        assert event.title in response.content.decode()


class TestProfilePageUpcomingAssignedMeetings:
    def test_shows_only_upcoming_assigned_meetings(self, client, employee, venue, event_type):
        past = _make_event(
            venue=venue, event_type=event_type, user=employee, days_offset=-3,
            title="Past Assigned Meeting",
        )
        upcoming = _make_event(
            venue=venue, event_type=event_type, user=employee, days_offset=3,
            title="Upcoming Assigned Meeting",
        )
        client.force_login(employee)
        response = client.get(reverse("profile"))
        content = response.content.decode()
        assert response.status_code == 200
        assert upcoming.title in content
        assert past.title not in content

    def test_section_hidden_when_no_upcoming_meetings(self, client, employee):
        client.force_login(employee)
        response = client.get(reverse("profile"))
        assert response.status_code == 200
        assert "Yaqinlashayotgan biriktirilgan uchrashuvlar" not in response.content.decode()

    def test_shows_events_where_user_is_only_the_management_responsible(
        self, client, employee, venue, event_type
    ):
        owner = User.objects.create_user(username="owner.staff", password="x")
        event = _make_event(
            venue=venue, event_type=event_type, user=owner, days_offset=2,
            title="Management-only Meeting", management_responsible=employee,
        )
        client.force_login(employee)
        response = client.get(reverse("profile"))
        assert event.title in response.content.decode()

    def test_shows_events_where_user_is_the_speaker_doctor(
        self, client, venue, event_type
    ):
        owner = User.objects.create_user(username="owner.staff2", password="x")
        doctor = User.objects.create_user(
            username="speaker.doc", password="x", role=User.Role.DOCTOR
        )
        event = _make_event(
            venue=venue, event_type=event_type, user=owner, days_offset=2,
            title="Speaker Meeting",
        )
        event.attending_doctors.add(doctor)

        client.force_login(doctor)
        response = client.get(reverse("profile"))
        assert event.title in response.content.decode()
