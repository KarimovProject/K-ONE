from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.attendance.models import EventAttendance
from apps.events.models import Event
from apps.venues.services.live_status import (
    VALID_LIVE_STATUSES,
    all_venues_live_status,
    sanitize_event_title_for_display,
)


def _reference(value: datetime | None) -> datetime:
    value = value or timezone.now()
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return timezone.localtime(value)


def _event_payload(event: Event, now_time=None) -> dict[str, Any]:
    return {
        "event_id": str(event.pk),
        "title": event.title,
        "planned_date": event.planned_date.isoformat(),
        "weekday": event.weekday_name,
        "start_time": event.start_time.strftime("%H:%M"),
        "end_time": event.end_time.strftime("%H:%M"),
        "venue_name": event.venue.localized_name,
        "event_type_name": event.event_type.localized_name,
        "status": event.status,
        "status_display": event.get_status_display(),
        "priority": event.priority,
        "expected_attendees": event.expected_attendees,
        "organizers": ", ".join(item.name for item in event.organizing_organizations.all()),
        "is_ongoing": bool(now_time and event.start_time <= now_time < event.end_time),
        "is_past": bool(now_time and event.end_time <= now_time),
        "is_upcoming": bool(now_time and event.start_time > now_time),
        "checkins_count": getattr(event, "checkins_count", 0),
    }


def get_leadership_dashboard_data(reference_dt: datetime | None = None) -> dict[str, Any]:
    reference = _reference(reference_dt)
    today = reference.date()
    now_time = reference.time().replace(tzinfo=None)
    week_end = today + timedelta(days=7)
    venues = all_venues_live_status(reference)

    base_events = Event.objects.filter(status__in=VALID_LIVE_STATUSES).select_related(
        "venue", "event_type", "responsible_employee"
    ).prefetch_related("organizing_organizations")
    today_events = list(
        base_events.filter(planned_date=today)
        .annotate(checkins_count=Count("attendances"))
        .order_by("start_time")
    )
    upcoming_events = list(
        base_events.filter(planned_date__gt=today, planned_date__lte=week_end)
        .order_by("planned_date", "start_time")
    )
    priority_events = [
        event
        for event in [*today_events, *upcoming_events]
        if event.priority in {Event.Priority.HIGH, Event.Priority.EMERGENCY}
    ]
    expected = sum(event.expected_attendees for event in today_events)
    checkins = EventAttendance.objects.filter(
        event__planned_date=today,
        event__status__in=VALID_LIVE_STATUSES,
    ).count()
    occupied = sum(item["current_status"] == "OCCUPIED" for item in venues)
    return {
        "reference_dt": reference.isoformat(),
        "today_date": today.isoformat(),
        "today_events_count": len(today_events),
        "in_progress_count": occupied,
        "available_venues_count": sum(
            item["current_status"] == "AVAILABLE" for item in venues
        ),
        "occupied_venues_count": occupied,
        "today_checkins_count": checkins,
        "today_expected_attendees": expected,
        "attendance_rate": round(checkins / expected * 100, 1) if expected else 0.0,
        "venues": venues,
        "today_timeline": [_event_payload(event, now_time) for event in today_events],
        "upcoming_events": [_event_payload(event) for event in upcoming_events],
        "priority_events": [_event_payload(event) for event in priority_events],
    }


def _tv_venue_payload(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "venue_id": item["venue_id"],
        "venue_code": item["venue_code"],
        "venue_name": item["venue_name"],
        "current_status": item["current_status"],
        "status_label": item["status_label"],
        "current_event_title": item["tv_safe_title"],
        "current_event_start_time": item["current_event_start_time"],
        "current_event_end_time": item["current_event_end_time"],
        "minutes_remaining": item["minutes_remaining"],
        "next_event_title": item["tv_safe_next_title"],
        "next_event_start_time": item["next_event_start_time"],
        "minutes_until_start": item["minutes_until_start"],
        "free_until": item["free_until"],
        "today_event_count": item["today_event_count"],
    }


def get_tv_wallboard_data(reference_dt: datetime | None = None) -> dict[str, Any]:
    reference = _reference(reference_dt)
    venue_statuses = all_venues_live_status(reference)
    timeline_events = Event.objects.filter(
        planned_date=reference.date(),
        status__in=VALID_LIVE_STATUSES,
    ).exclude(display_visibility=Event.DisplayVisibility.HIDDEN).select_related(
        "venue"
    ).order_by("start_time")
    timeline = [
        {
            "title": sanitize_event_title_for_display(event),
            "venue_code": event.venue.code,
            "venue_name": event.venue.localized_name,
            "start_time": event.start_time.strftime("%H:%M"),
            "end_time": event.end_time.strftime("%H:%M"),
            "is_ongoing": event.start_time
            <= reference.time().replace(tzinfo=None)
            < event.end_time,
        }
        for event in timeline_events
    ]
    return {
        "timestamp": reference.isoformat(),
        "date_str": timezone.localdate(reference).strftime("%d.%m.%Y"),
        "time_str": reference.strftime("%H:%M:%S"),
        "venues": [_tv_venue_payload(item) for item in venue_statuses],
        "timeline": timeline,
        "empty_title": _("Private Meeting"),
    }
