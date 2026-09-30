from datetime import date, time
from unittest import mock

import pytest
from django.urls import reverse

from apps.accounts.models import DoctorProfile, User
from apps.events.models import Event, EventType
from apps.events.services.doctors import busy_attending_doctor_errors
from apps.notifications.services import queue_notification_email
from apps.venues.models import Venue


@pytest.fixture
def doctor(db):
    user = User.objects.create_user(
        username="dr.overlap", password="x", role=User.Role.DOCTOR, is_active=True
    )
    DoctorProfile.objects.create(
        user=user, specialty="Cardiology", workplace="Clinic", phone="+998"
    )
    return user


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username="overlap.admin", password="x", role=User.Role.INTERNATIONAL_ADMIN
    )


def make_event(admin, title, start, end, status=Event.Status.PLANNED, code="HALL"):
    venue, _ = Venue.objects.get_or_create(
        code=code,
        defaults={
            "name_uz": code,
            "name_ru": code,
            "name_en": code,
            "capacity": 200,
            "working_start": time(8, 0),
            "working_end": time(20, 0),
        },
    )
    etype, _ = EventType.objects.get_or_create(
        code="conf", defaults={"name_uz": "Conf", "name_ru": "Conf", "name_en": "Conf"}
    )
    return Event.objects.create(
        title=title,
        event_type=etype,
        venue=venue,
        planned_date=date(2026, 11, 1),
        start_time=start,
        end_time=end,
        status=status,
        responsible_employee=admin,
        management_responsible=admin,
        created_by=admin,
        updated_by=admin,
    )


@pytest.mark.django_db
class TestDoctorAlreadyAssignedElsewhere:
    """A doctor already speaking at another live event at an overlapping time
    must be blocked, even without a StaffUnavailability slot."""

    def test_overlapping_live_event_blocks_the_doctor(self, doctor, admin):
        other = make_event(admin, "Cardio Summit", time(10, 0), time(11, 0), code="A")
        other.attending_doctors.add(doctor)

        errors = busy_attending_doctor_errors([doctor], date(2026, 11, 1), time(9, 0), time(12, 0))
        assert len(errors) == 1
        assert "Cardio Summit" in str(errors[0])

    def test_non_overlapping_event_does_not_block(self, doctor, admin):
        other = make_event(admin, "Morning Talk", time(8, 0), time(9, 0), code="A")
        other.attending_doctors.add(doctor)

        assert (
            busy_attending_doctor_errors([doctor], date(2026, 11, 1), time(9, 0), time(12, 0)) == []
        )

    @pytest.mark.parametrize(
        "status", [Event.Status.DRAFT, Event.Status.CANCELLED, Event.Status.POSTPONED]
    )
    def test_inactive_events_do_not_block(self, doctor, admin, status):
        other = make_event(admin, "Dormant", time(10, 0), time(11, 0), status=status, code="A")
        other.attending_doctors.add(doctor)

        assert (
            busy_attending_doctor_errors([doctor], date(2026, 11, 1), time(9, 0), time(12, 0)) == []
        )

    def test_the_event_being_edited_does_not_conflict_with_itself(self, client, doctor, admin):
        event = make_event(admin, "Self", time(9, 0), time(12, 0))
        event.attending_doctors.add(doctor)
        client.force_login(admin)
        res = client.post(
            reverse("events:edit", kwargs={"pk": event.pk}),
            data={
                "title": event.title,
                "event_type": event.event_type_id,
                "description": "",
                "venue": event.venue_id,
                "planned_date": event.planned_date,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "responsible_employee": admin.pk,
                "management_responsible": admin.pk,
                "attending_doctors": [doctor.pk],
                "status": Event.Status.DRAFT,
                "priority": Event.Priority.NORMAL,
                "expected_attendees": 1,
            },
        )
        assert res.status_code == 302

    def test_editing_into_an_overlap_is_rejected(self, client, doctor, admin):
        other = make_event(admin, "Cardio Summit", time(10, 0), time(11, 0), code="A")
        other.attending_doctors.add(doctor)
        event = make_event(admin, "Oncology Forum", time(9, 0), time(12, 0), code="B")
        client.force_login(admin)
        res = client.post(
            reverse("events:edit", kwargs={"pk": event.pk}),
            data={
                "title": event.title,
                "event_type": event.event_type_id,
                "description": "",
                "venue": event.venue_id,
                "planned_date": event.planned_date,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "responsible_employee": admin.pk,
                "management_responsible": admin.pk,
                "attending_doctors": [doctor.pk],
                "status": Event.Status.DRAFT,
                "priority": Event.Priority.NORMAL,
                "expected_attendees": 1,
            },
        )
        assert res.status_code == 200
        assert "Cardio Summit" in res.content.decode()
        event.refresh_from_db()
        assert doctor not in event.attending_doctors.all()


@pytest.mark.django_db
class TestQueuedNotificationEmail:
    def test_email_is_handed_to_celery(self, doctor):
        doctor.email = "dr@example.test"
        with mock.patch("apps.notifications.tasks.send_notification_email_task.delay") as delay:
            assert queue_notification_email(doctor, "Subject", "Body") is True
        delay.assert_called_once_with("dr@example.test", "Subject", "Body")

    def test_falls_back_to_inline_send_when_broker_is_down(self, doctor):
        from django.core import mail

        doctor.email = "dr@example.test"
        with mock.patch(
            "apps.notifications.tasks.send_notification_email_task.delay",
            side_effect=ConnectionError("broker down"),
        ):
            assert queue_notification_email(doctor, "Subject", "Body") is True
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["dr@example.test"]

    def test_doctor_without_email_is_skipped(self, doctor):
        assert queue_notification_email(doctor, "Subject", "Body") is False
