from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext

from apps.accounts.models import User
from apps.attendance.models import EventAttendance
from apps.audit.models import AuditEventLog
from apps.events.models import Event, EventType
from apps.reporting.services import get_leadership_dashboard_data, get_tv_wallboard_data
from apps.venues.models import DisplayToken, Venue
from apps.venues.services.live_status import venue_live_status


@pytest.fixture
def venue_ich(db):
    return Venue.objects.create(
        code="ICH-P6",
        name_uz="International Conference Hall",
        name_ru="Международный Конференц-Зал",
        name_en="International Conference Hall",
        capacity=300,
        working_start=time(8, 0),
        working_end=time(20, 0),
        is_active=True,
    )


@pytest.fixture
def venue_ssh(db):
    return Venue.objects.create(
        code="SSH-P6",
        name_uz="Scientific Seminar Hall",
        name_ru="Зал Научных Семинаров",
        name_en="Scientific Seminar Hall",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
        is_active=True,
    )


@pytest.fixture
def event_type(db):
    return EventType.objects.create(
        code="conf-p6",
        name_uz="Konferensiya",
        name_ru="Конференция",
        name_en="Conference",
        requires_management_approval=False,
    )


@pytest.fixture
def super_admin(db):
    return User.objects.create_superuser(
        username="admin_p6",
        email="admin_p6@example.com",
        password="password123",
        role=User.Role.SUPER_ADMIN,
    )


@pytest.fixture
def leadership_user(db):
    return User.objects.create_user(
        username="leader_p6",
        password="password123",
        role=User.Role.LEADERSHIP_VIEWER,
    )


@pytest.fixture
def content_manager(db):
    return User.objects.create_user(
        username="cm_p6",
        password="password123",
        role=User.Role.CONTENT_MANAGER,
    )


@pytest.mark.django_db
class TestVenueLiveStatusEngine:
    def test_available_status_when_no_events(self, venue_ich):
        now = timezone.localtime()
        with translation.override("en"):
            status = venue_live_status(venue_ich, reference_dt=now)
        assert status["current_status"] == "AVAILABLE"
        assert status["current_event"] is None

    def test_occupied_status_during_event(self, venue_ich, event_type, super_admin):
        now = timezone.localtime()
        today = now.date()

        Event.objects.create(
            title="Live Oncology Forum",
            event_type=event_type,
            venue=venue_ich,
            planned_date=today,
            start_time=time(0, 0),
            end_time=time(23, 59),
            responsible_employee=super_admin,
            management_responsible=super_admin,
            created_by=super_admin,
            status=Event.Status.APPROVED,
            expected_attendees=150,
        )

        status = venue_live_status(venue_ich, reference_dt=now)
        assert status["current_status"] == "OCCUPIED"
        assert status["current_event"].title == "Live Oncology Forum"
        assert status["minutes_remaining"] is not None

    def test_cancelled_displaced_events_ignored(self, venue_ich, event_type, super_admin):
        now = timezone.localtime()
        today = now.date()

        Event.objects.create(
            title="Cancelled Forum",
            event_type=event_type,
            venue=venue_ich,
            planned_date=today,
            start_time=time(0, 0),
            end_time=time(23, 59),
            responsible_employee=super_admin,
            management_responsible=super_admin,
            created_by=super_admin,
            status=Event.Status.CANCELLED,
        )

        status = venue_live_status(venue_ich, reference_dt=now)
        assert status["current_status"] == "AVAILABLE"

    def test_display_privacy_sanitization(self, venue_ich, event_type, super_admin):
        now = timezone.localtime()
        today = now.date()

        event_generic = Event.objects.create(
            title="Confidential Executive Session",
            event_type=event_type,
            venue=venue_ich,
            planned_date=today,
            start_time=time(0, 0),
            end_time=time(23, 59),
            responsible_employee=super_admin,
            management_responsible=super_admin,
            created_by=super_admin,
            status=Event.Status.APPROVED,
            display_visibility=Event.DisplayVisibility.GENERIC,
        )

        with translation.override("en"):
            status = venue_live_status(venue_ich, reference_dt=now)
        assert status["tv_safe_title"] == "Private Meeting"
        assert status["tv_safe_title"] != event_generic.title

    def test_exact_start_and_end_boundaries(self, venue_ich, event_type, super_admin):
        reference = datetime(2026, 8, 13, 10, 0, tzinfo=ZoneInfo("Asia/Tashkent"))
        Event.objects.create(
            title="Boundary event",
            event_type=event_type,
            venue=venue_ich,
            planned_date=reference.date(),
            start_time=time(10),
            end_time=time(11),
            responsible_employee=super_admin,
            management_responsible=super_admin,
            created_by=super_admin,
            status=Event.Status.APPROVED,
        )
        assert venue_live_status(venue_ich, reference)["current_status"] == "OCCUPIED"
        assert (
            venue_live_status(
                venue_ich,
                reference + timedelta(hours=1),
            )["current_status"]
            == "AVAILABLE"
        )

    def test_upcoming_next_event_and_venue_isolation(
        self, venue_ich, venue_ssh, event_type, super_admin
    ):
        reference = datetime(2026, 8, 13, 10, 0, tzinfo=ZoneInfo("Asia/Tashkent"))
        event = Event.objects.create(
            title="Starts soon",
            event_type=event_type,
            venue=venue_ich,
            planned_date=reference.date(),
            start_time=time(10, 30),
            end_time=time(11, 30),
            responsible_employee=super_admin,
            management_responsible=super_admin,
            created_by=super_admin,
            status=Event.Status.APPROVED,
        )
        first = venue_live_status(venue_ich, reference)
        second = venue_live_status(venue_ssh, reference)
        assert first["current_status"] == "UPCOMING"
        assert first["next_event"] == event
        assert first["free_until"] == "10:30"
        assert second["current_status"] == "AVAILABLE"
        assert second["next_event"] is None

    def test_displaced_event_is_ignored(self, venue_ich, event_type, super_admin):
        reference = datetime(2026, 8, 13, 10, 0, tzinfo=ZoneInfo("Asia/Tashkent"))
        Event.objects.create(
            title="Displaced",
            event_type=event_type,
            venue=venue_ich,
            planned_date=reference.date(),
            start_time=time(9),
            end_time=time(11),
            responsible_employee=super_admin,
            management_responsible=super_admin,
            created_by=super_admin,
            status=Event.Status.DISPLACED,
        )
        assert venue_live_status(venue_ich, reference)["current_status"] == "AVAILABLE"

    @pytest.mark.parametrize(
        ("visibility", "expected"),
        (("full", "Secret title"), ("generic", "Private Meeting"), ("hidden", "")),
    )
    def test_all_display_privacy_modes(
        self, venue_ich, event_type, super_admin, visibility, expected
    ):
        reference = datetime(2026, 8, 13, 10, 0, tzinfo=ZoneInfo("Asia/Tashkent"))
        Event.objects.create(
            title="Secret title",
            event_type=event_type,
            venue=venue_ich,
            planned_date=reference.date(),
            start_time=time(9),
            end_time=time(11),
            responsible_employee=super_admin,
            management_responsible=super_admin,
            created_by=super_admin,
            status=Event.Status.APPROVED,
            display_visibility=visibility,
        )
        with translation.override("en"):
            result = venue_live_status(venue_ich, reference)
        assert result["current_status"] == "OCCUPIED"
        assert result["tv_safe_title"] == expected

    def test_all_venues_status_has_bounded_queries(self, venue_ich, venue_ssh):
        from apps.venues.services.live_status import all_venues_live_status

        with CaptureQueriesContext(connection) as queries:
            results = all_venues_live_status()
        assert len(results) == 2
        assert len(queries) <= 2

    def test_timezone_is_tashkent(self):
        assert timezone.get_current_timezone_name() == "Asia/Tashkent"


@pytest.mark.django_db
class TestLeadershipSummaryService:
    def test_summary_metrics_and_kpis(self, venue_ich, venue_ssh, event_type, super_admin):
        now = timezone.localtime()
        today = now.date()

        event = Event.objects.create(
            title="Cardiology Summit",
            event_type=event_type,
            venue=venue_ich,
            planned_date=today,
            start_time=time(0, 0),
            end_time=time(23, 59),
            responsible_employee=super_admin,
            management_responsible=super_admin,
            created_by=super_admin,
            status=Event.Status.APPROVED,
            expected_attendees=100,
            checkin_enabled=True,
        )

        EventAttendance.objects.create(
            event=event,
            checkin_method=EventAttendance.Method.PUBLIC_QR,
            attendee_identifier_hash="test_hash_p6_1",
            attendee_name="Dr. Alimov",
        )

        data = get_leadership_dashboard_data(reference_dt=now)
        assert data["today_events_count"] >= 1
        assert data["in_progress_count"] >= 1
        assert data["today_checkins_count"] >= 1
        assert data["attendance_rate"] >= 1.0
        assert data["available_venues_count"] == 1
        assert data["occupied_venues_count"] == 1
        assert data["today_expected_attendees"] == 100

    @pytest.mark.parametrize("language", ("uz", "ru", "en"))
    def test_status_localization(self, language):
        with translation.override(language):
            label = gettext("Available")
        assert label
        assert label == "Available" if language == "en" else label != "Available"


@pytest.mark.django_db
class TestDisplayTokenAndAPI:
    def test_display_venues_api_security(self, db):
        token_obj = DisplayToken.objects.create(
            token="valid_p6_test_token_12345",
            name="Main Lobby Wallboard",
            is_active=True,
        )

        url = reverse("api-display-venues", kwargs={"token": token_obj.token})
        from django.test import Client

        client = Client()

        resp = client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert "venues" in data
        assert "timestamp" in data

    def test_invalid_display_token_blocked(self, db):
        url = reverse("api-display-venues", kwargs={"token": "invalid_fake_token_999"})
        from django.test import Client

        client = Client()

        resp = client.get(url)
        assert resp.status_code == 403

    def test_disabled_display_token_blocked(self, db):
        token_obj = DisplayToken.objects.create(
            token="disabled_p6_token_555",
            name="Disabled Screen",
            is_active=False,
        )
        url = reverse("api-display-venues", kwargs={"token": token_obj.token})
        from django.test import Client

        client = Client()

        resp = client.get(url)
        assert resp.status_code == 403

    def test_token_rotation_invalidates_old_token_and_is_audited(self, db):
        token_obj = DisplayToken.objects.create(name="Rotatable")
        old_token = token_obj.token
        new_token = token_obj.rotate()
        from django.test import Client

        client = Client()
        assert old_token != new_token
        assert (
            client.get(reverse("api-display-venues", kwargs={"token": old_token})).status_code
            == 403
        )
        assert (
            client.get(reverse("api-display-venues", kwargs={"token": new_token})).status_code
            == 200
        )
        assert AuditEventLog.objects.filter(
            action=AuditEventLog.Action.DISPLAY_TOKEN_ROTATED,
            target_id=str(token_obj.pk),
        ).exists()

    def test_generated_tokens_are_secure_unique_and_state_changes_are_audited(self, db):
        first = DisplayToken.objects.create(name="First")
        second = DisplayToken.objects.create(name="Second")
        assert first.token != second.token
        assert len(first.token) >= 40
        first.set_enabled(False)
        first.set_enabled(True)
        actions = set(
            AuditEventLog.objects.filter(target_id=str(first.pk)).values_list("action", flat=True)
        )
        assert {
            AuditEventLog.Action.DISPLAY_TOKEN_CREATED,
            AuditEventLog.Action.DISPLAY_DISABLED,
            AuditEventLog.Action.DISPLAY_ENABLED,
        } <= actions

    def test_tv_payload_contains_no_private_fields(self, venue_ich):
        payload = str(get_tv_wallboard_data()).lower()
        for forbidden in (
            "email",
            "phone",
            "notes",
            "rejection",
            "justification",
            "attendee_name",
            "audit",
        ):
            assert forbidden not in payload


@pytest.mark.django_db
class TestLeadershipRBAC:
    def test_leadership_viewer_allowed(self, client, leadership_user):
        client.force_login(leadership_user)
        url = reverse("leadership-dashboard")
        resp = client.get(url)
        assert resp.status_code == 200

    def test_content_manager_denied(self, client, content_manager):
        client.force_login(content_manager)
        url = reverse("leadership-dashboard")
        resp = client.get(url)
        assert resp.status_code == 403

    @pytest.mark.parametrize(
        ("role", "expected"),
        (
            (User.Role.SUPER_ADMIN, 200),
            (User.Role.INTERNATIONAL_ADMIN, 200),
            (User.Role.LEADERSHIP_VIEWER, 200),
            (User.Role.MANAGEMENT_RESPONSIBLE, 200),
            (User.Role.RESPONSIBLE_EMPLOYEE, 403),
            (User.Role.RECEPTION_OPERATOR, 403),
            (User.Role.CONTENT_MANAGER, 403),
        ),
    )
    def test_leadership_role_matrix(self, client, db, role, expected):
        user = User.objects.create_user(username=f"role-{role}", role=role)
        client.force_login(user)
        assert client.get(reverse("leadership-dashboard")).status_code == expected

    def test_reception_can_read_operational_venues_only(self, client, db):
        user = User.objects.create_user(
            username="reception-p6",
            role=User.Role.RECEPTION_OPERATOR,
        )
        client.force_login(user)
        assert client.get(reverse("api-leadership-venues")).status_code == 200
        assert client.get(reverse("api-leadership-summary")).status_code == 403

    def test_leadership_today_and_upcoming_api(self, client, leadership_user):
        client.force_login(leadership_user)
        assert client.get(reverse("api-leadership-today")).status_code == 200
        assert client.get(reverse("api-leadership-upcoming")).status_code == 200

    def test_wallboard_page_requires_valid_token(self, client, db):
        token = DisplayToken.objects.create(name="Lobby")
        assert (
            client.get(reverse("tv-wallboard-token", kwargs={"token": token.token})).status_code
            == 200
        )
        assert client.get(reverse("tv-wallboard")).status_code == 403
