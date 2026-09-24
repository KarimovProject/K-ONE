import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.attendance.models import EventAttendance
from apps.audit.services import log_audit_event

CHECKIN_COOKIE_NAME = "event_checkin_token"


def get_or_create_browser_checkin_token(request) -> tuple[str, bool]:
    """Retrieves existing browser check-in token from cookie or returns a new one."""
    token = request.COOKIES.get(CHECKIN_COOKIE_NAME)
    created = False
    if not token or len(token) < 16:
        token = uuid.uuid4().hex
        created = True
    return token, created


def hash_attendee_identifier(event_id: Any, token_str: str) -> str:
    """Computes a SHA-256 hash derived from the event UUID and browser token."""
    raw = f"{event_id}:{token_str}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def is_already_checked_in(event, request) -> tuple[bool, str]:
    """Checks if the current browser session has already checked in for the event."""
    token, _ = get_or_create_browser_checkin_token(request)
    identifier_hash = hash_attendee_identifier(event.pk, token)
    checked_in = EventAttendance.objects.filter(
        event=event,
        attendee_identifier_hash=identifier_hash,
    ).exists()
    return checked_in, token


def find_ongoing_other_checkin(event, token: str, now=None):
    """Returns an event this browser is already checked into that is still
    running, other than `event` — or None.

    Derived from attendance rows rather than the session, so the "one meeting
    at a time" rule survives a lost/cleared session (a QR scanned in a
    different in-app browser still can't be caught: public check-in is
    anonymous and the browser token is the only identity available).
    """
    from apps.events.models import Event

    now = now or timezone.now()
    # Events are same-day by construction (end_time must be after start_time),
    # so only today's and yesterday's rows can still be running.
    candidates = (
        Event.objects.filter(
            planned_date__gte=(now - timedelta(days=1)).date(),
            planned_date__lte=now.date(),
        )
        .exclude(pk=event.pk)
        .only("id", "title", "planned_date", "start_time", "end_time")
    )
    running = {
        hash_attendee_identifier(candidate.pk, token): candidate
        for candidate in candidates
        if candidate.end_datetime > now
    }
    if not running:
        return None

    match = EventAttendance.objects.filter(
        attendee_identifier_hash__in=list(running),
    ).values_list("attendee_identifier_hash", flat=True).first()
    return running.get(match) if match else None


def process_public_checkin(
    event,
    request,
    attendee_name: str = "",
    attendee_organization: str = "",
) -> dict[str, Any]:
    """Processes a public QR check-in attempt with duplicate protection."""
    status = event.checkin_status()
    if not status["eligible"]:
        return {
            "success": False,
            "code": status["code"],
            "message": status["reason"],
            "already_checked_in": False,
        }

    token, new_token = get_or_create_browser_checkin_token(request)
    identifier_hash = hash_attendee_identifier(event.pk, token)

    if EventAttendance.objects.filter(
        event=event,
        attendee_identifier_hash=identifier_hash,
    ).exists():
        return {
            "success": False,
            "code": "already_checked_in",
            "message": str(_("Siz avval ro‘yxatdan o‘tgansiz.")),
            "already_checked_in": True,
            "token": token,
            "new_token": new_token,
        }

    conflict_message = str(
        _(
            "Siz hozirda boshqa uchrashuvdasiz. Uning vaqti "
            "tugamaguncha yangisiga yozila olmaysiz."
        )
    )
    conflict_response = {
        "success": False,
        "code": "conflict",
        "message": conflict_message,
        "already_checked_in": False,
        "token": token,
        "new_token": new_token,
    }

    # Primary, durable check: an attendance row for this browser on another
    # event that is still running.
    if find_ongoing_other_checkin(event, token) is not None:
        return conflict_response

    # Secondary check, for a browser that kept its session but lost the
    # check-in cookie (a fresh token would otherwise look like a new person).
    active_end_iso = request.session.get("active_event_end")
    if active_end_iso:
        try:
            active_end = datetime.fromisoformat(active_end_iso)
            if active_end > timezone.now():
                active_event_id = request.session.get("active_event_id")
                if str(event.pk) != active_event_id:
                    return conflict_response
        except ValueError:
            pass

    try:
        with transaction.atomic():
            attendance = EventAttendance.objects.create(
                event=event,
                checkin_method=EventAttendance.Method.PUBLIC_QR,
                attendee_identifier_hash=identifier_hash,
                attendee_name=attendee_name.strip(),
                attendee_organization=attendee_organization.strip(),
            )
            log_audit_event(
                "attendance.public_checked_in",
                actor=request.user if request.user.is_authenticated else None,
                target=event,
                payload={
                    "attendance_id": str(attendance.id),
                    "has_name": bool(attendee_name.strip()),
                    "has_org": bool(attendee_organization.strip()),
                },
            )
    except IntegrityError:
        return {
            "success": False,
            "code": "already_checked_in",
            "message": str(_("Siz avval ro‘yxatdan o‘tgansiz.")),
            "already_checked_in": True,
            "token": token,
            "new_token": new_token,
        }

    request.session["active_event_id"] = str(event.pk)
    request.session["active_event_end"] = event.end_datetime.isoformat()

    return {
        "success": True,
        "code": "success",
        "message": str(_("Ishtirokingiz qayd etildi.")),
        "already_checked_in": False,
        "attendance": attendance,
        "token": token,
        "new_token": new_token,
    }


def process_staff_manual_checkin(
    event,
    staff_user,
    attendee_name: str,
    attendee_organization: str = "",
    attendee_role: str = "",
) -> EventAttendance:
    """Creates a manual staff check-in entry."""
    unique_str = f"manual:{event.pk}:{uuid.uuid4()}"
    identifier_hash = hashlib.sha256(unique_str.encode("utf-8")).hexdigest()

    with transaction.atomic():
        attendance = EventAttendance.objects.create(
            event=event,
            checkin_method=EventAttendance.Method.STAFF_MANUAL,
            attendee_identifier_hash=identifier_hash,
            attendee_name=attendee_name.strip(),
            attendee_organization=attendee_organization.strip(),
            attendee_role=attendee_role.strip(),
        )
        log_audit_event(
            "attendance.manual_checked_in",
            actor=staff_user,
            target=event,
            payload={
                "attendance_id": str(attendance.id),
                "attendee_name": attendee_name.strip(),
            },
        )
    return attendance


def get_event_attendance_stats(event) -> dict[str, Any]:
    """Calculates attendance summary statistics for internal display."""
    total = event.attendances.count()
    anonymous_count = event.attendances.filter(
        Q(attendee_name="") | Q(attendee_name__isnull=True)
    ).count()
    identified_count = total - anonymous_count

    expected = event.expected_attendees or 0
    if expected > 0:
        rate = round((total / expected) * 100, 1)
    else:
        rate = 0.0

    latest_record = event.attendances.order_by("-checked_in_at").first()
    latest_at = latest_record.checked_in_at.isoformat() if latest_record else None

    return {
        "total_checked_in": total,
        "anonymous_count": anonymous_count,
        "identified_count": identified_count,
        "expected_attendees": expected,
        "attendance_rate": rate,
        "latest_checkin_at": latest_at,
        "checkin_enabled": event.checkin_enabled,
        "checkin_status": event.checkin_status(),
    }
