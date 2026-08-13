from datetime import date, time, timedelta

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import User
from apps.audit.models import AuditEventLog
from apps.events.models import Event, EventType
from apps.events.services.emergency import execute_emergency_override
from apps.events.services.workflow import (
    approve_event,
    postpone_event,
    reject_event,
    reschedule_event,
    resubmit_event,
    submit_event_for_approval,
)
from apps.notifications.models import Notification
from apps.venues.models import Venue


@pytest.fixture
def workflow_setup(db):
    super_admin = User.objects.create_user(
        username="superadmin",
        role=User.Role.SUPER_ADMIN,
        is_superuser=True,
    )
    intl_admin = User.objects.create_user(
        username="intladmin",
        role=User.Role.INTERNATIONAL_ADMIN,
    )
    mgmt_user = User.objects.create_user(
        username="mgmtuser",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )
    resp_user = User.objects.create_user(
        username="respuser",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )
    unauth_user = User.objects.create_user(
        username="viewer",
        role=User.Role.LEADERSHIP_VIEWER,
    )

    venue = Venue.objects.create(
        code="CONF-A",
        name_uz="Zal A",
        name_ru="Зал А",
        name_en="Hall A",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )

    event_type = EventType.objects.create(
        code="CONF",
        name_uz="Konferensiya",
        name_ru="Конференция",
        name_en="Conference",
        requires_management_approval=True,
    )

    planned_date = date.today() + timedelta(days=5)

    draft_event = Event.objects.create(
        title="Draft Test Event",
        event_type=event_type,
        venue=venue,
        planned_date=planned_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        responsible_employee=resp_user,
        management_responsible=mgmt_user,
        created_by=resp_user,
        status=Event.Status.DRAFT,
    )

    return {
        "super_admin": super_admin,
        "intl_admin": intl_admin,
        "mgmt_user": mgmt_user,
        "resp_user": resp_user,
        "unauth_user": unauth_user,
        "venue": venue,
        "event_type": event_type,
        "planned_date": planned_date,
        "draft_event": draft_event,
    }


@pytest.mark.django_db
def test_submit_event_flow(workflow_setup):
    event = workflow_setup["draft_event"]
    actor = workflow_setup["resp_user"]

    submit_event_for_approval(event, actor)

    event.refresh_from_db()
    assert event.status == Event.Status.PENDING_APPROVAL
    assert event.submitted_at is not None

    # Check notification created for management
    notif = Notification.objects.filter(recipient=workflow_setup["mgmt_user"]).first()
    assert notif is not None
    assert "submitted" in notif.message.lower() or "approval" in notif.title.lower()

    # Check audit log
    audit = AuditEventLog.objects.filter(
        target_id=str(event.pk), action="event.submitted"
    ).first()
    assert audit is not None
    assert audit.actor == actor


@pytest.mark.django_db
def test_approve_event_flow(workflow_setup):
    event = workflow_setup["draft_event"]
    submit_event_for_approval(event, workflow_setup["resp_user"])

    mgmt = workflow_setup["mgmt_user"]
    approve_event(event, mgmt, notes="Looks great")

    event.refresh_from_db()
    assert event.status == Event.Status.APPROVED
    assert event.reviewed_at is not None
    assert event.reviewed_by == mgmt
    assert "Looks great" in event.notes

    # Notification to responsible employee
    notif = Notification.objects.filter(recipient=workflow_setup["resp_user"]).first()
    assert notif is not None
    assert "approved" in notif.title.lower()

    # Audit log
    audit = AuditEventLog.objects.filter(
        target_id=str(event.pk), action="event.approved"
    ).first()
    assert audit is not None


@pytest.mark.django_db
def test_reject_event_with_and_without_reason(workflow_setup):
    event = workflow_setup["draft_event"]
    submit_event_for_approval(event, workflow_setup["resp_user"])

    mgmt = workflow_setup["mgmt_user"]

    # Reject without reason should fail
    with pytest.raises(ValidationError):
        reject_event(event, mgmt, reason="  ")

    # Reject with valid reason
    reject_event(event, mgmt, reason="Venue unavailable")

    event.refresh_from_db()
    assert event.status == Event.Status.REJECTED
    assert event.rejection_reason == "Venue unavailable"

    # Audit log
    audit = AuditEventLog.objects.filter(
        target_id=str(event.pk), action="event.rejected"
    ).first()
    assert audit is not None
    assert audit.payload.get("reason") == "Venue unavailable"


@pytest.mark.django_db
def test_resubmit_event_flow(workflow_setup):
    event = workflow_setup["draft_event"]
    submit_event_for_approval(event, workflow_setup["resp_user"])
    reject_event(event, workflow_setup["mgmt_user"], reason="Fix details")

    # Resubmit
    resubmit_event(event, workflow_setup["resp_user"])

    event.refresh_from_db()
    assert event.status == Event.Status.PENDING_APPROVAL

    # Audit log for resubmission
    audit = AuditEventLog.objects.filter(
        target_id=str(event.pk), action="event.resubmitted"
    ).first()
    assert audit is not None


@pytest.mark.django_db
def test_postpone_and_reschedule_flow(workflow_setup):
    event = workflow_setup["draft_event"]
    event.status = Event.Status.PLANNED
    event.save()

    resp = workflow_setup["resp_user"]

    # Postpone
    postpone_event(event, resp, reason="Speaker unavailable")
    event.refresh_from_db()
    assert event.status == Event.Status.POSTPONED

    # Reschedule to new date
    new_date = workflow_setup["planned_date"] + timedelta(days=2)
    reschedule_event(
        event,
        resp,
        planned_date=new_date,
        start_time=time(14, 0),
        end_time=time(16, 0),
    )

    event.refresh_from_db()
    assert event.status == Event.Status.PLANNED
    assert event.planned_date == new_date
    assert event.start_time == time(14, 0)

    # Check audit log
    audit = AuditEventLog.objects.filter(
        target_id=str(event.pk), action="event.rescheduled"
    ).first()
    assert audit is not None


@pytest.mark.django_db
def test_emergency_override_and_displaced_event(workflow_setup):
    venue = workflow_setup["venue"]
    pdate = workflow_setup["planned_date"]

    # Existing planned event
    existing = Event.objects.create(
        title="Existing Normal Event",
        event_type=workflow_setup["event_type"],
        venue=venue,
        planned_date=pdate,
        start_time=time(10, 0),
        end_time=time(12, 0),
        responsible_employee=workflow_setup["resp_user"],
        management_responsible=workflow_setup["mgmt_user"],
        status=Event.Status.PLANNED,
    )

    # Emergency event draft conflicting with existing
    emergency = Event.objects.create(
        title="Emergency State Summit",
        event_type=workflow_setup["event_type"],
        venue=venue,
        planned_date=pdate,
        start_time=time(10, 30),
        end_time=time(11, 30),
        responsible_employee=workflow_setup["resp_user"],
        management_responsible=workflow_setup["mgmt_user"],
        status=Event.Status.DRAFT,
    )

    # Non-authorized user override attempt should fail
    with pytest.raises(PermissionDenied):
        execute_emergency_override(
            emergency,
            workflow_setup["resp_user"],
            justification="State emergency",
        )

    # Super admin override
    execute_emergency_override(
        emergency,
        workflow_setup["super_admin"],
        justification="High level diplomatic delegation",
    )

    emergency.refresh_from_db()
    existing.refresh_from_db()

    assert emergency.status == Event.Status.PLANNED
    assert emergency.priority == Event.Priority.EMERGENCY
    assert emergency.emergency_justification == "High level diplomatic delegation"

    assert existing.status == Event.Status.DISPLACED
    assert existing.displaced_by_event == emergency

    # Verify audit entries
    audit_disp = AuditEventLog.objects.filter(
        target_id=str(existing.pk), action="event.displaced"
    ).first()
    assert audit_disp is not None

    audit_over = AuditEventLog.objects.filter(
        target_id=str(emergency.pk), action="event.emergency_overridden"
    ).first()
    assert audit_over is not None

    # Alert notification to responsible employee of displaced event
    alert = Notification.objects.filter(
        recipient=workflow_setup["resp_user"],
        severity=Notification.Severity.ALERT,
    ).first()
    assert alert is not None
    assert "displaced" in alert.message.lower() or "critical" in alert.title.lower()


@pytest.mark.django_db
def test_workflow_api_endpoints(client, workflow_setup):
    event = workflow_setup["draft_event"]

    # Authenticate as responsible employee
    client.force_login(workflow_setup["resp_user"])

    # Submit API
    response = client.post(reverse("api-event-submit", kwargs={"pk": event.pk}))
    assert response.status_code == status.HTTP_200_OK
    event.refresh_from_db()
    assert event.status == Event.Status.PENDING_APPROVAL

    # Approve API as management user
    client.force_login(workflow_setup["mgmt_user"])
    response = client.post(
        reverse("api-event-approve", kwargs={"pk": event.pk}),
        data={"notes": "Approved via API"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK
    event.refresh_from_db()
    assert event.status == Event.Status.APPROVED

    # Emergency Override API as Super Admin
    client.force_login(workflow_setup["super_admin"])
    response = client.post(
        reverse("api-event-emergency-override", kwargs={"pk": event.pk}),
        data={"justification": "Emergency state meeting via API"},
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK
    event.refresh_from_db()
    assert event.priority == Event.Priority.EMERGENCY
