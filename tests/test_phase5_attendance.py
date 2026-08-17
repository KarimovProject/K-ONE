from datetime import time, timedelta

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.attendance.models import EventAttendance
from apps.attendance.services import CHECKIN_COOKIE_NAME
from apps.audit.models import AuditEventLog
from apps.events.models import Event, EventType
from apps.venues.models import Venue


@pytest.fixture
def test_venue(db):
    return Venue.objects.create(
        code="main-hall-p5",
        name_uz="Bosh Anjumanlar Zali",
        name_ru="Главный Конференц-Зал",
        name_en="Main Conference Hall",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
        is_active=True,
    )


@pytest.fixture
def test_event_type(db):
    return EventType.objects.create(
        code="symposium-ph5",
        name_uz="Simpozium",
        name_ru="Симпозиум",
        name_en="Symposium",
        requires_management_approval=False,
    )


@pytest.fixture
def super_admin(db):
    return User.objects.create_superuser(
        username="admin_ph5",
        email="admin_ph5@example.com",
        password="password123",
        role=User.Role.SUPER_ADMIN,
    )


@pytest.fixture
def responsible_user(db):
    return User.objects.create_user(
        username="resp_user_ph5",
        password="password123",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )


@pytest.fixture
def mgmt_user(db):
    return User.objects.create_user(
        username="mgmt_user_ph5",
        password="password123",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )


@pytest.fixture
def content_manager_user(db):
    return User.objects.create_user(
        username="cm_user_ph5",
        password="password123",
        role=User.Role.CONTENT_MANAGER,
    )


@pytest.fixture
def approved_event(db, test_venue, test_event_type, responsible_user, mgmt_user):
    today = timezone.localdate()
    event = Event.objects.create(
        title="International Health Conference Phase 5",
        event_type=test_event_type,
        venue=test_venue,
        planned_date=today,
        start_time=time(0, 0),
        end_time=time(23, 59),
        responsible_employee=responsible_user,
        management_responsible=mgmt_user,
        created_by=responsible_user,
        status=Event.Status.APPROVED,
        expected_attendees=100,
        checkin_enabled=True,
    )
    return event


@pytest.mark.django_db
class TestPhase5AttendanceModel:
    def test_attendance_creation(self, approved_event):
        record = EventAttendance.objects.create(
            event=approved_event,
            checkin_method=EventAttendance.Method.PUBLIC_QR,
            attendee_identifier_hash="hash_12345",
            attendee_name="Sardor Alimov",
            attendee_organization="Tashkent Univ",
        )
        assert record.pk is not None
        assert record.event == approved_event
        assert record.checkin_method == "public_qr"
        assert record.checked_in_at is not None
        assert str(record) != ""

    def test_unique_attendee_hash_constraint(self, approved_event):
        EventAttendance.objects.create(
            event=approved_event,
            checkin_method=EventAttendance.Method.PUBLIC_QR,
            attendee_identifier_hash="unique_hash_xyz",
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                EventAttendance.objects.create(
                    event=approved_event,
                    checkin_method=EventAttendance.Method.PUBLIC_QR,
                    attendee_identifier_hash="unique_hash_xyz",
                )

    def test_event_checkin_eligibility_helper(self, approved_event):
        now = approved_event.start_datetime
        status = approved_event.checkin_status(now=now)
        assert status["eligible"] is True
        assert status["code"] == "eligible"

        # Check before opening window
        early_time = approved_event.start_datetime - timedelta(hours=2)
        status_early = approved_event.checkin_status(now=early_time)
        assert status_early["eligible"] is False
        assert status_early["code"] == "not_open"

        # Check after closing window
        late_time = approved_event.end_datetime + timedelta(hours=1)
        status_late = approved_event.checkin_status(now=late_time)
        assert status_late["eligible"] is False
        assert status_late["code"] == "closed"


@pytest.mark.django_db
class TestPublicCheckinAndDuplicateProtection:
    def test_public_checkin_anonymous(self, client, approved_event):
        url = reverse("public-event-checkin", kwargs={"public_token": approved_event.public_token})
        response = client.post(url, {})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert CHECKIN_COOKIE_NAME in response.cookies

    def test_public_checkin_identified(self, client, approved_event):
        url = reverse("public-event-checkin", kwargs={"public_token": approved_event.public_token})
        response = client.post(
            url,
            {
                "attendee_name": "Dr. Jasur Abdullayev",
                "attendee_organization": "National Hospital",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1

        record = EventAttendance.objects.get(event=approved_event)
        assert record.attendee_name == "Dr. Jasur Abdullayev"
        assert record.attendee_organization == "National Hospital"

    def test_duplicate_checkin_blocked(self, client, approved_event):
        url = reverse("public-event-checkin", kwargs={"public_token": approved_event.public_token})
        # First submission
        res1 = client.post(url, {"attendee_name": "Guest 1"})
        assert res1.status_code == 200
        assert res1.json()["success"] is True

        # Second submission with same browser cookies
        res2 = client.post(url, {"attendee_name": "Guest 1"})
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["already_checked_in"] is True
        assert data2["count"] == 1
        assert "Siz avval ro‘yxatdan o‘tgansiz" in data2["message"]

    def test_disabled_checkin_blocked(self, client, approved_event):
        approved_event.checkin_enabled = False
        approved_event.save()

        url = reverse("public-event-checkin", kwargs={"public_token": approved_event.public_token})
        response = client.post(url, {})
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["code"] == "not_enabled"

    def test_draft_event_checkin_blocked(self, client, approved_event):
        approved_event.status = Event.Status.DRAFT
        approved_event.save()

        url = reverse("public-event-checkin", kwargs={"public_token": approved_event.public_token})
        response = client.post(url, {})
        assert response.status_code == 404

    def test_cancelled_event_checkin_blocked(self, client, approved_event):
        approved_event.status = Event.Status.CANCELLED
        approved_event.save()

        url = reverse("public-event-checkin", kwargs={"public_token": approved_event.public_token})
        response = client.post(url, {})
        assert response.status_code == 404

    def test_public_count_api_privacy(self, client, approved_event):
        EventAttendance.objects.create(
            event=approved_event,
            attendee_name="Private Name",
            attendee_organization="Private Org",
        )
        url = reverse("api-public-attendance-count", kwargs={"token": approved_event.public_token})
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["success"] is True
        # Verify no names or sensitive lists are exposed publicly
        assert "attendees" not in data
        assert "Private Name" not in response.content.decode()


@pytest.mark.django_db
class TestStaffManualCheckinAndDashboard:
    def test_staff_manual_checkin(self, client, super_admin, approved_event):
        client.force_login(super_admin)
        url = reverse("events:attendance", kwargs={"pk": approved_event.pk})

        response = client.post(
            url,
            {
                "action": "manual_checkin",
                "attendee_name": "VIP Delegate",
                "attendee_organization": "Ministry of Health",
                "attendee_role": "Director",
            },
        )
        assert response.status_code == 302
        assert EventAttendance.objects.filter(event=approved_event).count() == 1

        rec = EventAttendance.objects.get(event=approved_event)
        assert rec.checkin_method == "staff_manual"
        assert rec.attendee_name == "VIP Delegate"

    def test_csv_export(self, client, super_admin, approved_event):
        client.force_login(super_admin)
        EventAttendance.objects.create(
            event=approved_event,
            attendee_name="Test Export Name",
            attendee_organization="Export Org",
            checkin_method=EventAttendance.Method.PUBLIC_QR,
        )

        url = reverse("events:attendance-export", kwargs={"pk": approved_event.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/csv")
        content = response.content.decode("utf-8")
        assert "\ufeff" in content  # UTF-8 BOM
        assert "Test Export Name" in content
        assert "Export Org" in content
        assert "attendee_identifier_hash" not in content  # Privacy check


@pytest.mark.django_db
class TestRBACAndAuditLogging:
    def test_rbac_content_manager_denied(self, client, content_manager_user, approved_event):
        client.force_login(content_manager_user)
        url = reverse("events:attendance", kwargs={"pk": approved_event.pk})
        response = client.get(url)
        assert response.status_code == 403

    def test_rbac_super_admin_allowed(self, client, super_admin, approved_event):
        client.force_login(super_admin)
        url = reverse("events:attendance", kwargs={"pk": approved_event.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_audit_logs_recorded(self, client, super_admin, approved_event):
        # 1. Public checkin audit
        pub_url = reverse(
            "public-event-checkin",
            kwargs={"public_token": approved_event.public_token},
        )
        client.post(pub_url, {"attendee_name": "Audit Test"})
        assert AuditEventLog.objects.filter(action="attendance.public_checked_in").exists()

        # 2. Manual checkin audit
        client.force_login(super_admin)
        att_url = reverse("events:attendance", kwargs={"pk": approved_event.pk})
        client.post(att_url, {"action": "manual_checkin", "attendee_name": "Staff Manual Audit"})
        assert AuditEventLog.objects.filter(action="attendance.manual_checked_in").exists()

        # 3. Export audit
        exp_url = reverse("events:attendance-export", kwargs={"pk": approved_event.pk})
        client.get(exp_url)
        assert AuditEventLog.objects.filter(action="attendance.exported").exists()
