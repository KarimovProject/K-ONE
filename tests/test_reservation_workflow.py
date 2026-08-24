from datetime import date, time

import pytest
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import User
from apps.events.models import Event, EventType
from apps.venues.models import Venue


@pytest.fixture
def reservation_setup(db):
    admin_user = User.objects.create_user(
        username="workflow_admin",
        password="password",
        role=User.Role.INTERNATIONAL_ADMIN,
    )
    mgmt_user = User.objects.create_user(
        username="mgmt_user",
        password="password",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )
    normal_user = User.objects.create_user(
        username="normal_user",
        password="password",
        role=User.Role.CONTENT_MANAGER,
    )
    venue1 = Venue.objects.create(
        code="ROOM1",
        name_uz="Room 1",
        name_ru="Room 1",
        name_en="Room 1",
        capacity=50,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )
    venue2 = Venue.objects.create(
        code="ROOM2",
        name_uz="Room 2",
        name_ru="Room 2",
        name_en="Room 2",
        capacity=50,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )
    etype = EventType.objects.create(
        code="meeting",
        name_uz="Meeting",
        name_ru="Meeting",
        name_en="Meeting",
    )

    # Create an existing event
    existing_event = Event.objects.create(
        title="Existing Meeting",
        event_type=etype,
        venue=venue1,
        planned_date=date(2026, 11, 10),
        start_time=time(10, 0),
        end_time=time(11, 0),
        status=Event.Status.PLANNED,
        responsible_employee=admin_user,
        management_responsible=admin_user,
    )

    return {
        "admin": admin_user,
        "mgmt": mgmt_user,
        "user": normal_user,
        "venue1": venue1,
        "venue2": venue2,
        "etype": etype,
        "existing_event": existing_event,
    }


@pytest.mark.django_db
class TestReservationWorkflow:
    def get_wizard_data(
        self, client, setup, venue, start_time, end_time, status_action="save_planned", title="Test"
    ):
        session = client.session
        session["event_wizard_data"] = {
            "step1": {
                "title": title,
                "event_type": setup["etype"].pk,
                "expected_attendees": 10,
                "priority": Event.Priority.NORMAL,
                "description": "test",
            },
            "step2": {
                "planned_date": "2026-11-10",
                "start_time": start_time,
                "end_time": end_time,
                "venue": venue.pk,
            },
            "step3": {
                "responsible_employee": setup["admin"].pk,
                "management_responsible": setup["admin"].pk,
            },
            "step4": {},
            "step5": {},
        }
        session.save()
        return {
            "current_step": 5,
            "action": status_action,
        }

    def test_invalid_start_end(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "11:00", "10:00"
        )
        res = client.post(reverse("events:wizard"), data=data, follow=True)
        assert (
            "End time must be later than start time" in res.content.decode()
            or "invalid" in res.content.decode().lower()
            or "?step=2" in res.redirect_chain[-1][0]
        )

    def test_free_room_accepted(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "12:00", "13:00"
        )
        res = client.post(reverse("events:wizard"), data=data)
        assert res.status_code == status.HTTP_302_FOUND
        assert Event.objects.filter(title="Test", status=Event.Status.PLANNED).exists()

    def test_exact_overlap_rejected(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "10:00", "11:00"
        )
        res = client.post(reverse("events:wizard"), data=data, follow=True)
        assert "Tanlangan vaqtda" in res.content.decode()

    def test_partial_overlap_rejected(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "09:30", "10:30"
        )
        res = client.post(reverse("events:wizard"), data=data, follow=True)
        assert "Tanlangan vaqtda" in res.content.decode()

    def test_contained_overlap_rejected(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "10:15", "10:45"
        )
        res = client.post(reverse("events:wizard"), data=data, follow=True)
        assert "Tanlangan vaqtda" in res.content.decode()

    def test_enclosing_overlap_rejected(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "09:00", "12:00"
        )
        res = client.post(reverse("events:wizard"), data=data, follow=True)
        assert "Tanlangan vaqtda" in res.content.decode()

    def test_adjacent_booking_allowed(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "09:00", "10:00"
        )
        res = client.post(reverse("events:wizard"), data=data)
        assert res.status_code == status.HTTP_302_FOUND
        assert Event.objects.filter(title="Test").exists()

        data2 = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "11:00", "12:00", title="Test2"
        )
        res2 = client.post(reverse("events:wizard"), data=data2)
        assert res2.status_code == status.HTTP_302_FOUND
        assert Event.objects.filter(title="Test2").exists()

    def test_different_room_same_time_allowed(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue2"], "10:00", "11:00"
        )
        res = client.post(reverse("events:wizard"), data=data)
        assert res.status_code == status.HTTP_302_FOUND
        assert Event.objects.filter(title="Test").exists()

    def test_cancelled_rejected_event_handling(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        existing = reservation_setup["existing_event"]
        existing.status = Event.Status.CANCELLED
        existing.save()

        data = self.get_wizard_data(
            client, reservation_setup, reservation_setup["venue1"], "10:00", "11:00"
        )
        res = client.post(reverse("events:wizard"), data=data)
        assert res.status_code == status.HTTP_302_FOUND
        assert Event.objects.filter(title="Test").exists()

    def test_editing_event_does_not_conflict_with_itself(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        existing = reservation_setup["existing_event"]

        post_data = {
            "title": "Updated Title",
            "event_type": reservation_setup["etype"].pk,
            "description": "test",
            "venue": reservation_setup["venue1"].pk,
            "planned_date": "2026-11-10",
            "start_time": "10:00",
            "end_time": "11:00",
            "responsible_employee": reservation_setup["admin"].pk,
            "management_responsible": reservation_setup["admin"].pk,
            "status": Event.Status.PLANNED,
            "priority": Event.Priority.NORMAL,
            "expected_attendees": 10,
        }
        res = client.post(reverse("events:edit", kwargs={"pk": existing.pk}), data=post_data)
        assert res.status_code == status.HTTP_302_FOUND
        existing.refresh_from_db()
        assert existing.title == "Updated Title"

    def test_unauthorized_create_blocked(self, client, reservation_setup):
        client.force_login(reservation_setup["user"])
        # Assuming normal_user does not have CREATE_OWN_EVENTS capability by default
        res = client.get(reverse("events:wizard"))
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthorized_approval_blocked(self, client, reservation_setup):
        client.force_login(reservation_setup["user"])
        existing = reservation_setup["existing_event"]
        existing.status = Event.Status.PENDING_APPROVAL
        existing.save()

        res = client.post(reverse("events:approve", kwargs={"pk": existing.pk}))
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_approval_transition_works(self, client, reservation_setup):
        client.force_login(reservation_setup["mgmt"])
        existing = reservation_setup["existing_event"]
        existing.status = Event.Status.PENDING_APPROVAL
        existing.save()

        res = client.post(reverse("events:approve", kwargs={"pk": existing.pk}))
        assert res.status_code == status.HTTP_302_FOUND
        existing.refresh_from_db()
        assert existing.status == Event.Status.APPROVED

    def test_calendar_list_reflects_saved_event(self, client, reservation_setup):
        client.force_login(reservation_setup["admin"])
        res = client.get(reverse("events:list") + "?q=Existing Meeting")
        assert "Existing Meeting" in res.content.decode()

        res_cal = client.get(reverse("calendar"))
        assert res_cal.status_code == status.HTTP_200_OK
