from datetime import date, time

import pytest
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import User
from apps.events.models import Event, EventType
from apps.venues.models import Venue


@pytest.fixture
def wizard_setup(db):
    user = User.objects.create_user(
        username="wizard_admin",
        password="password",
        role=User.Role.INTERNATIONAL_ADMIN,
    )
    venue = Venue.objects.create(
        code="ICH",
        name_uz="ICH",
        name_ru="ICH",
        name_en="ICH",
        capacity=300,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )
    etype = EventType.objects.create(
        code="conf",
        name_uz="Conf",
        name_ru="Conf",
        name_en="Conf",
    )
    return {"user": user, "venue": venue, "etype": etype}


@pytest.mark.django_db
class TestEventWizard:
    def test_wizard_step_1_get(self, client, wizard_setup):
        client.force_login(wizard_setup["user"])
        res = client.get(reverse("events:wizard"))
        assert res.status_code == status.HTTP_200_OK
        assert "1-qadam" in res.content.decode()

    def test_wizard_session_persistence_and_submission(self, client, wizard_setup):
        client.force_login(wizard_setup["user"])

        # Step 1 post
        s1_data = {
            "current_step": 1,
            "action": "next",
            "step1-title": "International Medical Forum",
            "step1-event_type": wizard_setup["etype"].pk,
            "step1-description": "Forum overview",
            "step1-expected_attendees": 100,
            "step1-priority": Event.Priority.NORMAL,
        }
        res = client.post(reverse("events:wizard"), data=s1_data)
        assert res.status_code == status.HTTP_302_FOUND
        assert "?step=2" in res.url

        # Step 2 post
        s2_data = {
            "current_step": 2,
            "action": "next",
            "step2-planned_date": "2026-10-15",
            "step2-start_time": "09:00",
            "step2-end_time": "12:00",
            "step2-venue": wizard_setup["venue"].pk,
        }
        res = client.post(reverse("events:wizard"), data=s2_data)
        assert res.status_code == status.HTTP_302_FOUND
        assert "?step=3" in res.url

        # Step 3 post
        s3_data = {
            "current_step": 3,
            "action": "next",
            "step3-responsible_employee": wizard_setup["user"].pk,
            "step3-management_responsible": wizard_setup["user"].pk,
        }
        res = client.post(reverse("events:wizard"), data=s3_data)
        assert res.status_code == status.HTTP_302_FOUND
        assert "?step=4" in res.url

        # Step 4 post
        s4_data = {
            "current_step": 4,
            "action": "next",
        }
        res = client.post(reverse("events:wizard"), data=s4_data)
        assert res.status_code == status.HTTP_302_FOUND
        assert "?step=5" in res.url

        # Step 5 finalize as PLANNED
        s5_data = {
            "current_step": 5,
            "action": "save_planned",
            "step5-zoom_url": "https://zoom.us/j/123456",
            "step5-notes": "Final notes",
        }
        res = client.post(reverse("events:wizard"), data=s5_data)
        assert res.status_code == status.HTTP_302_FOUND

        # Verify event created in DB
        event = Event.objects.get(title="International Medical Forum")
        assert event.status == Event.Status.PLANNED
        assert event.planned_date == date(2026, 10, 15)
        assert event.venue == wizard_setup["venue"]
        assert event.zoom_url == "https://zoom.us/j/123456"
