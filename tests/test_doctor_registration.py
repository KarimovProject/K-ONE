from datetime import date, time

import pytest
from django.contrib.auth import authenticate
from django.urls import reverse

from apps.accounts.models import DoctorProfile, StaffUnavailability, User
from apps.accounts.services import check_doctor_availability
from apps.events.forms import EventStep3Form, EventUpdateForm
from apps.events.models import Event, EventType
from apps.venues.models import Venue

REGISTER_DATA = {
    "username": "dr.aliyeva",
    "first_name": "Nilufar",
    "last_name": "Aliyeva",
    "email": "aliyeva@example.test",
    "specialty": "Oncology",
    "workplace": "Republican Oncology Center",
    "position": "MD, PhD",
    "phone": "+998901234567",
    "languages": "UZ, RU, EN",
    "license_number": "LIC-001",
    "bio": "Senior oncologist.",
    "password1": "a-very-safe-password-123",
    "password2": "a-very-safe-password-123",
}


@pytest.mark.django_db
class TestDoctorRegistration:
    def test_registration_creates_inactive_doctor_with_profile(self, client):
        res = client.post(reverse("register"), data=REGISTER_DATA)
        assert res.status_code == 302
        user = User.objects.get(username="dr.aliyeva")
        assert user.role == User.Role.DOCTOR
        assert user.is_active is False
        profile = DoctorProfile.objects.get(user=user)
        assert profile.specialty == "Oncology"
        assert profile.workplace == "Republican Oncology Center"

    def test_inactive_doctor_cannot_authenticate(self, client):
        client.post(reverse("register"), data=REGISTER_DATA)
        authenticated = authenticate(username="dr.aliyeva", password=REGISTER_DATA["password1"])
        assert authenticated is None

    def test_activated_doctor_can_authenticate(self, client):
        client.post(reverse("register"), data=REGISTER_DATA)
        user = User.objects.get(username="dr.aliyeva")
        user.is_active = True
        user.save(update_fields=["is_active"])
        authenticated = authenticate(username="dr.aliyeva", password=REGISTER_DATA["password1"])
        assert authenticated is not None
        assert authenticated.pk == user.pk

    def test_duplicate_username_is_rejected(self, client):
        User.objects.create_user(username="dr.aliyeva", password="x")
        res = client.post(reverse("register"), data=REGISTER_DATA)
        assert res.status_code == 200
        assert "already taken" in res.content.decode() or "band" in res.content.decode()
        assert not DoctorProfile.objects.filter(user__username="dr.aliyeva").exists()


@pytest.mark.django_db
class TestUserManagementPage:
    def test_non_admin_cannot_access(self, client):
        staff = User.objects.create_user(
            username="staff.plain", password="x", role=User.Role.RESPONSIBLE_EMPLOYEE
        )
        client.force_login(staff)
        res = client.get(reverse("user-management"))
        assert res.status_code == 403

    def test_international_admin_can_activate_a_pending_doctor(self, client):
        admin = User.objects.create_user(
            username="intl.admin", password="x", role=User.Role.INTERNATIONAL_ADMIN
        )
        pending = User.objects.create_user(
            username="dr.pending", password="x", role=User.Role.DOCTOR, is_active=False
        )
        client.force_login(admin)

        res = client.get(reverse("user-management"))
        assert res.status_code == 200
        assert "dr.pending" in res.content.decode()

        res = client.post(reverse("user-toggle-active", args=[pending.pk]))
        assert res.status_code == 302
        pending.refresh_from_db()
        assert pending.is_active is True

    def test_admin_cannot_toggle_own_status(self, client):
        admin = User.objects.create_user(
            username="intl.admin2", password="x", role=User.Role.INTERNATIONAL_ADMIN
        )
        client.force_login(admin)
        client.post(reverse("user-toggle-active", args=[admin.pk]))
        admin.refresh_from_db()
        assert admin.is_active is True

    def test_admin_privileged_accounts_are_hidden_from_the_list(self, client):
        admin = User.objects.create_user(
            username="intl.admin4", password="x", role=User.Role.INTERNATIONAL_ADMIN
        )
        other_admin = User.objects.create_user(
            username="intl.admin5", password="x", role=User.Role.INTERNATIONAL_ADMIN
        )
        super_admin = User.objects.create_user(
            username="super.admin1", password="x", role=User.Role.SUPER_ADMIN
        )
        User.objects.create_user(username="dr.visible", password="x", role=User.Role.DOCTOR)
        client.force_login(admin)

        res = client.get(reverse("user-management"))
        body = res.content.decode()
        assert "dr.visible" in body
        assert "intl.admin5" not in body
        assert "super.admin1" not in body

        res = client.post(reverse("user-toggle-active", args=[other_admin.pk]))
        assert res.status_code == 403
        res = client.post(reverse("user-toggle-active", args=[super_admin.pk]))
        assert res.status_code == 403

    def test_non_superuser_cannot_toggle_a_superuser(self, client):
        admin = User.objects.create_user(
            username="intl.admin3", password="x", role=User.Role.INTERNATIONAL_ADMIN
        )
        super_user = User.objects.create_superuser(
            username="root", password="x", email="root@example.test"
        )
        client.force_login(admin)
        res = client.post(reverse("user-toggle-active", args=[super_user.pk]))
        assert res.status_code == 403
        super_user.refresh_from_db()
        assert super_user.is_active is True


@pytest.fixture
def doctor(db):
    user = User.objects.create_user(
        username="dr.karimov", password="x", role=User.Role.DOCTOR, is_active=True
    )
    DoctorProfile.objects.create(
        user=user, specialty="Cardiology", workplace="Clinic", phone="+998"
    )
    return user


@pytest.mark.django_db
class TestAvailabilitySelfService:
    def test_doctor_can_add_and_delete_own_slot(self, client, doctor):
        client.force_login(doctor)
        res = client.post(
            reverse("doctor-availability"),
            data={
                "start_date": "2026-11-01",
                "start_time": "09:00",
                "end_date": "2026-11-01",
                "end_time": "11:00",
                "reason": "Surgery",
            },
        )
        assert res.status_code == 302
        slot = StaffUnavailability.objects.get(user=doctor)
        assert slot.reason == "Surgery"

    def test_doctor_can_add_a_multi_day_slot(self, client, doctor):
        client.force_login(doctor)
        res = client.post(
            reverse("doctor-availability"),
            data={
                "start_date": "2026-11-01",
                "start_time": "18:00",
                "end_date": "2026-11-03",
                "end_time": "09:00",
                "reason": "Conference travel",
            },
        )
        assert res.status_code == 302
        slot = StaffUnavailability.objects.get(user=doctor)
        assert slot.start_date == date(2026, 11, 1)
        assert slot.end_date == date(2026, 11, 3)

        res = client.post(reverse("doctor-availability-delete", args=[slot.pk]))
        assert res.status_code == 302
        assert not StaffUnavailability.objects.filter(pk=slot.pk).exists()

    def test_reason_is_required(self, client, doctor):
        client.force_login(doctor)
        res = client.post(
            reverse("doctor-availability"),
            data={
                "start_date": "2026-11-01",
                "start_time": "09:00",
                "end_date": "2026-11-01",
                "end_time": "11:00",
                "reason": "",
            },
        )
        assert res.status_code == 200
        assert not StaffUnavailability.objects.filter(user=doctor).exists()

    def test_whitespace_only_reason_is_rejected(self, client, doctor):
        client.force_login(doctor)
        res = client.post(
            reverse("doctor-availability"),
            data={
                "start_date": "2026-11-01",
                "start_time": "09:00",
                "end_date": "2026-11-01",
                "end_time": "11:00",
                "reason": "   ",
            },
        )
        assert res.status_code == 200
        assert not StaffUnavailability.objects.filter(user=doctor).exists()

    def test_end_before_start_is_rejected(self, client, doctor):
        client.force_login(doctor)
        res = client.post(
            reverse("doctor-availability"),
            data={
                "start_date": "2026-11-02",
                "start_time": "09:00",
                "end_date": "2026-11-01",
                "end_time": "11:00",
                "reason": "Bad range",
            },
        )
        assert res.status_code == 200
        assert not StaffUnavailability.objects.filter(user=doctor).exists()

    def test_yearly_limit_blocks_a_fifth_slot(self, client, doctor):
        client.force_login(doctor)
        for month in (1, 3, 5, 7):
            StaffUnavailability.objects.create(
                user=doctor,
                start_date=date(2026, month, 1),
                start_time=time(9, 0),
                end_date=date(2026, month, 1),
                end_time=time(11, 0),
                reason=f"slot {month}",
            )
        assert StaffUnavailability.objects.filter(user=doctor, start_date__year=2026).count() == 4

        res = client.post(
            reverse("doctor-availability"),
            data={
                "start_date": "2026-09-01",
                "start_time": "09:00",
                "end_date": "2026-09-01",
                "end_time": "11:00",
                "reason": "One too many",
            },
        )
        assert res.status_code == 200
        reasons = [s.reason for s in StaffUnavailability.objects.filter(user=doctor)]
        assert "One too many" not in reasons
        assert StaffUnavailability.objects.filter(user=doctor, start_date__year=2026).count() == 4

    def test_yearly_limit_is_per_year(self, client, doctor):
        client.force_login(doctor)
        for month in (1, 3, 5, 7):
            StaffUnavailability.objects.create(
                user=doctor,
                start_date=date(2026, month, 1),
                start_time=time(9, 0),
                end_date=date(2026, month, 1),
                end_time=time(11, 0),
                reason=f"slot {month}",
            )
        # A 2027 slot should still be allowed — the limit is per calendar year.
        res = client.post(
            reverse("doctor-availability"),
            data={
                "start_date": "2027-01-10",
                "start_time": "09:00",
                "end_date": "2027-01-10",
                "end_time": "11:00",
                "reason": "Next year",
            },
        )
        assert res.status_code == 302
        assert StaffUnavailability.objects.filter(user=doctor, start_date__year=2027).count() == 1

    def test_deleting_a_slot_frees_up_the_yearly_quota(self, client, doctor):
        client.force_login(doctor)
        slots = [
            StaffUnavailability.objects.create(
                user=doctor,
                start_date=date(2026, month, 1),
                start_time=time(9, 0),
                end_date=date(2026, month, 1),
                end_time=time(11, 0),
                reason=f"slot {month}",
            )
            for month in (1, 3, 5, 7)
        ]
        client.post(reverse("doctor-availability-delete", args=[slots[0].pk]))

        res = client.post(
            reverse("doctor-availability"),
            data={
                "start_date": "2026-09-01",
                "start_time": "09:00",
                "end_date": "2026-09-01",
                "end_time": "11:00",
                "reason": "Now there's room",
            },
        )
        assert res.status_code == 302
        assert StaffUnavailability.objects.filter(user=doctor, start_date__year=2026).count() == 4

    def test_doctor_cannot_delete_another_doctors_slot(self, client, doctor):
        other = User.objects.create_user(username="dr.other", password="x", role=User.Role.DOCTOR)
        slot = StaffUnavailability.objects.create(
            user=other,
            start_date=date(2026, 11, 1),
            start_time=time(9, 0),
            end_date=date(2026, 11, 1),
            end_time=time(11, 0),
            reason="x",
        )
        client.force_login(doctor)
        client.post(reverse("doctor-availability-delete", args=[slot.pk]))
        assert StaffUnavailability.objects.filter(pk=slot.pk).exists()

    def test_non_doctor_cannot_access_availability_page(self, client):
        staff = User.objects.create_user(
            username="staff.member", password="x", role=User.Role.RESPONSIBLE_EMPLOYEE
        )
        client.force_login(staff)
        res = client.get(reverse("doctor-availability"))
        assert res.status_code == 403


@pytest.fixture
def event(db, doctor):
    admin = User.objects.create_user(
        username="event.admin", password="x", role=User.Role.INTERNATIONAL_ADMIN
    )
    venue = Venue.objects.create(
        code="ICH", name_uz="ICH", name_ru="ICH", name_en="ICH",
        capacity=200, working_start=time(8, 0), working_end=time(20, 0),
    )
    etype = EventType.objects.create(code="conf", name_uz="Conf", name_ru="Conf", name_en="Conf")
    return Event.objects.create(
        title="International Oncology Forum",
        event_type=etype,
        venue=venue,
        planned_date=date(2026, 11, 1),
        start_time=time(9, 0),
        end_time=time(12, 0),
        responsible_employee=admin,
        management_responsible=admin,
        created_by=admin,
        updated_by=admin,
    )


@pytest.mark.django_db
class TestDoctorAvailabilityConflictBlocking:
    """A busy doctor must not be assignable at all — an attempt is rejected
    outright, not merely warned about (a doctor can't be in two places)."""

    def test_busy_doctor_conflict_is_detected(self, doctor, event):
        StaffUnavailability.objects.create(
            user=doctor,
            start_date=date(2026, 11, 1),
            start_time=time(8, 0),
            end_date=date(2026, 11, 1),
            end_time=time(13, 0),
            reason="On leave",
        )
        result = check_doctor_availability(
            doctor, event.planned_date, event.start_time, event.end_time
        )
        assert result.is_available is False
        assert result.reason == "On leave"

    def test_multi_day_slot_conflicts_with_event_on_a_covered_day(self, doctor, event):
        # Busy from Oct 30 through Nov 2 — event on Nov 1 falls inside the range.
        StaffUnavailability.objects.create(
            user=doctor,
            start_date=date(2026, 10, 30),
            start_time=time(18, 0),
            end_date=date(2026, 11, 2),
            end_time=time(9, 0),
            reason="Multi-day travel",
        )
        result = check_doctor_availability(
            doctor, event.planned_date, event.start_time, event.end_time
        )
        assert result.is_available is False
        assert result.reason == "Multi-day travel"

    def test_free_doctor_produces_no_conflict(self, doctor, event):
        result = check_doctor_availability(
            doctor, event.planned_date, event.start_time, event.end_time
        )
        assert result.is_available is True

    def test_editing_an_event_with_a_busy_doctor_is_rejected(self, client, doctor, event):
        StaffUnavailability.objects.create(
            user=doctor,
            start_date=event.planned_date,
            start_time=time(0, 0),
            end_date=event.planned_date,
            end_time=time(23, 59),
            reason="On leave",
        )
        client.force_login(event.responsible_employee)
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
                "responsible_employee": event.responsible_employee_id,
                "management_responsible": event.management_responsible_id,
                "attending_doctors": [doctor.pk],
                "status": Event.Status.DRAFT,
                "priority": Event.Priority.NORMAL,
                "expected_attendees": 1,
            },
        )
        assert res.status_code == 200  # re-rendered with an error, not redirected
        assert "On leave" in res.content.decode()
        event.refresh_from_db()
        assert doctor not in event.attending_doctors.all()

    def test_editing_an_event_with_a_free_doctor_succeeds(self, client, doctor, event):
        client.force_login(event.responsible_employee)
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
                "responsible_employee": event.responsible_employee_id,
                "management_responsible": event.management_responsible_id,
                "attending_doctors": [doctor.pk],
                "status": Event.Status.DRAFT,
                "priority": Event.Priority.NORMAL,
                "expected_attendees": 1,
            },
        )
        assert res.status_code == 302
        event.refresh_from_db()
        assert doctor in event.attending_doctors.all()


@pytest.mark.django_db
class TestDoctorsExcludedFromResponsiblePickers:
    """A doctor picked into responsible_employee/management_responsible would
    silently bypass the attending_doctors busy-conflict check entirely — this
    is exactly how a real mix-up happened (a doctor with no
    MANAGEMENT_RESPONSIBLE-role users to compete with ended up in that
    fallback-to-all-active-users dropdown)."""

    def test_doctor_not_in_wizard_step3_fallback_querysets(self, doctor):
        form = EventStep3Form()
        assert doctor not in form.fields["responsible_employee"].queryset
        assert doctor not in form.fields["management_responsible"].queryset
        assert doctor in form.fields["attending_doctors"].queryset

    def test_doctor_not_in_event_update_form_querysets(self, doctor, event):
        form = EventUpdateForm(instance=event)
        assert doctor not in form.fields["responsible_employee"].queryset
        assert doctor not in form.fields["management_responsible"].queryset
        assert doctor in form.fields["attending_doctors"].queryset

    def test_attending_doctors_checkbox_widget_actually_has_choices(self, doctor, event):
        """Regression guard: swapping the field's widget to
        CheckboxSelectMultiple AFTER assigning its queryset leaves the new
        widget with an empty choice list (Django populates widget.choices
        only at the moment queryset is set) — rendering a checkbox list
        with nothing in it. The widget must be set before the queryset."""
        form = EventUpdateForm(instance=event)
        widget_choices = list(form.fields["attending_doctors"].widget.choices)
        assert len(widget_choices) == 1
        assert widget_choices[0][1] == doctor.username


@pytest.mark.django_db
class TestDoctorAssignmentNotification:
    """A doctor assigned as a speaker must be told — in-app and by email —
    since previously nothing informed them at all."""

    def test_assigning_a_doctor_creates_notification_and_email(self, client, doctor, event):
        from django.core import mail

        from apps.notifications.models import Notification

        doctor.email = "karimov@example.test"
        doctor.save(update_fields=["email"])

        client.force_login(event.responsible_employee)
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
                "responsible_employee": event.responsible_employee_id,
                "management_responsible": event.management_responsible_id,
                "attending_doctors": [doctor.pk],
                "status": Event.Status.DRAFT,
                "priority": Event.Priority.NORMAL,
                "expected_attendees": 1,
            },
        )
        assert res.status_code == 302

        notif = Notification.objects.filter(recipient=doctor).first()
        assert notif is not None
        assert event.title in notif.message

        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [doctor.email]
        assert event.title in mail.outbox[0].body

    def test_reassigning_the_same_doctor_does_not_duplicate_notification(
        self, client, doctor, event
    ):
        from apps.notifications.models import Notification

        event.attending_doctors.add(doctor)
        client.force_login(event.responsible_employee)
        client.post(
            reverse("events:edit", kwargs={"pk": event.pk}),
            data={
                "title": event.title,
                "event_type": event.event_type_id,
                "description": "",
                "venue": event.venue_id,
                "planned_date": event.planned_date,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "responsible_employee": event.responsible_employee_id,
                "management_responsible": event.management_responsible_id,
                "attending_doctors": [doctor.pk],
                "status": Event.Status.DRAFT,
                "priority": Event.Priority.NORMAL,
                "expected_attendees": 1,
            },
        )
        assert Notification.objects.filter(recipient=doctor).count() == 0

    def test_doctor_without_email_still_gets_in_app_notification(self, client, doctor, event):
        from apps.notifications.models import Notification

        assert doctor.email == ""
        client.force_login(event.responsible_employee)
        client.post(
            reverse("events:edit", kwargs={"pk": event.pk}),
            data={
                "title": event.title,
                "event_type": event.event_type_id,
                "description": "",
                "venue": event.venue_id,
                "planned_date": event.planned_date,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "responsible_employee": event.responsible_employee_id,
                "management_responsible": event.management_responsible_id,
                "attending_doctors": [doctor.pk],
                "status": Event.Status.DRAFT,
                "priority": Event.Priority.NORMAL,
                "expected_attendees": 1,
            },
        )
        assert Notification.objects.filter(recipient=doctor).exists()


@pytest.mark.django_db
class TestDoctorAssignedEventsView:
    def test_profile_shows_speaker_events_count(self, client, doctor, event):
        event.attending_doctors.add(doctor)
        client.force_login(doctor)
        res = client.get(reverse("profile"))
        assert res.status_code == 200
        assert "1" in res.content.decode()

    def test_assigned_events_page_lists_the_event(self, client, doctor, event):
        event.attending_doctors.add(doctor)
        client.force_login(doctor)
        res = client.get(reverse("doctor-assigned-events"))
        assert res.status_code == 200
        assert event.title in res.content.decode()

    def test_non_doctor_cannot_access_assigned_events_page(self, client, event):
        client.force_login(event.responsible_employee)
        res = client.get(reverse("doctor-assigned-events"))
        assert res.status_code == 403
