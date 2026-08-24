from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from math import ceil
from typing import Any

from django.db.models import Prefetch
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.events.models import Event
from apps.venues.models import Venue

VALID_LIVE_STATUSES = (
    Event.Status.APPROVED,
    Event.Status.PLANNED,
    Event.Status.SCHEDULED,
    Event.Status.ONGOING,
    Event.Status.COMPLETED,
    Event.Status.EMERGENCY,
)


def _local_reference(reference_dt: datetime | None) -> datetime:
    value = reference_dt or timezone.now()
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return timezone.localtime(value)


def sanitize_event_title_for_display(event: Event | None) -> str:
    if event is None or event.display_visibility == Event.DisplayVisibility.HIDDEN:
        return ""
    if event.display_visibility == Event.DisplayVisibility.GENERIC:
        return _("Private Meeting")
    return event.title


def _status_from_events(
    venue: Venue,
    events: Iterable[Event],
    reference_dt: datetime,
    near_term_minutes: int,
) -> dict[str, Any]:
    today = reference_dt.date()
    now_time = reference_dt.time().replace(tzinfo=None)
    event_list = list(events)
    today_events = [event for event in event_list if event.planned_date == today]
    current_event = next(
        (event for event in today_events if event.start_time <= now_time < event.end_time),
        None,
    )
    next_event = next(
        (
            event
            for event in event_list
            if (event.planned_date, event.start_time) > (today, now_time)
        ),
        None,
    )

    minutes_remaining = None
    minutes_until_start = None
    if current_event:
        end = timezone.make_aware(
            datetime.combine(today, current_event.end_time),
            timezone.get_current_timezone(),
        )
        minutes_remaining = max(1, ceil((end - reference_dt).total_seconds() / 60))
        status = "OCCUPIED"
    elif next_event and next_event.planned_date == today:
        start = timezone.make_aware(
            datetime.combine(today, next_event.start_time),
            timezone.get_current_timezone(),
        )
        minutes_until_start = max(1, ceil((start - reference_dt).total_seconds() / 60))
        status = "UPCOMING" if minutes_until_start <= near_term_minutes else "AVAILABLE"
    else:
        status = "AVAILABLE"

    free_until = None
    if not current_event and next_event and next_event.planned_date == today:
        free_until = next_event.start_time.strftime("%H:%M")

    return {
        "venue": venue,
        "venue_id": str(venue.pk),
        "venue_code": venue.code,
        "venue_name": venue.localized_name,
        "current_status": status,
        "available_now": status == "AVAILABLE",
        "occupied_now": status == "OCCUPIED",
        "upcoming_now": status == "UPCOMING",
        "status_label": _(
            {"AVAILABLE": "Available", "OCCUPIED": "Occupied", "UPCOMING": "Upcoming"}[status]
        ),
        "current_event": current_event,
        "current_event_title": current_event.title if current_event else None,
        "current_event_start_time": (
            current_event.start_time.strftime("%H:%M") if current_event else None
        ),
        "current_event_end_time": (
            current_event.end_time.strftime("%H:%M") if current_event else None
        ),
        "minutes_remaining": minutes_remaining,
        "next_event": next_event,
        "next_event_title": next_event.title if next_event else None,
        "next_event_date": next_event.planned_date.isoformat() if next_event else None,
        "next_event_start_time": next_event.start_time.strftime("%H:%M") if next_event else None,
        "minutes_until_start": minutes_until_start,
        "free_until": free_until,
        "today_event_count": len(today_events),
        "tv_safe_title": sanitize_event_title_for_display(current_event),
        "tv_safe_next_title": sanitize_event_title_for_display(next_event),
    }


def venue_live_status(
    venue: Venue,
    reference_dt: datetime | None = None,
    near_term_minutes: int = 60,
) -> dict[str, Any]:
    reference = _local_reference(reference_dt)
    events = getattr(venue, "_live_events", None)
    if events is None:
        events = (
            Event.objects.filter(
                venue=venue,
                planned_date__gte=reference.date(),
                status__in=VALID_LIVE_STATUSES,
            )
            .select_related("event_type")
            .order_by("planned_date", "start_time")
        )
    return _status_from_events(venue, events, reference, near_term_minutes)


def all_venues_live_status(
    reference_dt: datetime | None = None,
    near_term_minutes: int = 60,
) -> list[dict[str, Any]]:
    reference = _local_reference(reference_dt)
    events = (
        Event.objects.filter(
            planned_date__gte=reference.date(),
            status__in=VALID_LIVE_STATUSES,
        )
        .select_related("event_type")
        .order_by("planned_date", "start_time")
    )
    venues = (
        Venue.objects.filter(is_active=True)
        .prefetch_related(Prefetch("events", queryset=events, to_attr="_live_events"))
        .order_by("sort_order", "code")
    )
    return [venue_live_status(venue, reference, near_term_minutes) for venue in venues]
