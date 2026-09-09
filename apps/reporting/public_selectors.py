from datetime import date, datetime, time, timedelta

from django.db.models import Q
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext as _

from apps.events.models import Event, EventType
from apps.venues.models import Venue
from apps.venues.services.live_status import all_venues_live_status

PUBLIC_STATUSES = (
    Event.Status.APPROVED,
    Event.Status.PLANNED,
    Event.Status.SCHEDULED,
    Event.Status.ONGOING,
    Event.Status.COMPLETED,
    Event.Status.EMERGENCY,
)


def _iso(day: date, value: time) -> str:
    return timezone.make_aware(datetime.combine(day, value)).isoformat()


def public_event_queryset(start: date, end: date):
    return (
        Event.objects.filter(planned_date__range=(start, end), status__in=PUBLIC_STATUSES)
        .exclude(title__istartswith="[ACCEPTANCE_DEMO]")
        .select_related("venue", "event_type", "responsible_employee")
        .prefetch_related("organizing_organizations")
        .order_by("planned_date", "start_time")
    )


def serialize_public_event(event: Event) -> dict:
    visibility = event.display_visibility
    base = {
        "start": _iso(event.planned_date, event.start_time),
        "end": _iso(event.planned_date, event.end_time),
        "date": event.planned_date.isoformat(),
        "start_time": event.start_time.strftime("%H:%M"),
        "end_time": event.end_time.strftime("%H:%M"),
        "venue": event.venue.localized_name,
        "venue_code": event.venue.code,
        "visibility": visibility,
    }
    if visibility == Event.DisplayVisibility.HIDDEN:
        return {
            **base,
            "title": str(_("Venue occupied")),
            "status": "occupied",
            "status_label": str(_("Occupied")),
        }
    if visibility == Event.DisplayVisibility.GENERIC:
        return {
            **base,
            "title": str(_("Private meeting")),
            "status": event.status,
            "status_label": event.get_status_display(),
        }
    return {
        **base,
        "title": event.title,
        "event_type": event.event_type.localized_name,
        "event_type_code": event.event_type.code,
        "color": event.event_type.color,
        "status": event.status,
        "status_label": event.get_status_display(),
        "priority": event.priority,
        "priority_label": event.get_priority_display(),
        "responsible": event.responsible_employee.get_full_name(),
        "organization": ", ".join(
            organization.name for organization in event.organizing_organizations.all()[:3]
        ),
        "description": "" if event.description.startswith(("P11", "[")) else event.description,
        "public_url": (
            f"/event/{event.public_token}/"
            if event.is_public_enabled and event.public_token
            else ""
        ),
        "banner_url": event.banner_image.url if event.banner_image else "",
        "venue_full": event.venue.localized_name,
    }


def public_events(start: date, end: date) -> list[dict]:
    return [serialize_public_event(event) for event in public_event_queryset(start, end)]


def public_venue_statuses(featured_only: bool = False) -> list[dict]:
    rows = []
    for item in all_venues_live_status():
        venue = item["venue"]
        if venue.code.upper().startswith(("ACCD", "TEST", "P11-")):
            continue
        if featured_only and not (0 < venue.sort_order < 900):
            continue
        rows.append(
            {
                "code": item["venue_code"],
                "name": item["venue_name"],
                "status": item["current_status"],
                "status_label": item["status_label"],
                "current_title": item.get("tv_safe_title") or "",
                "ends_at": item.get("current_event_end_time"),
                "next_title": item.get("tv_safe_next_title") or "",
                "next_start": item.get("next_event_start_time"),
                "free_until": item.get("free_until"),
                "today_count": item.get("today_event_count", 0),
                "minutes_remaining": item.get("minutes_remaining"),
                "minutes_until_start": item.get("minutes_until_start"),
            }
        )
    if featured_only and not rows:
        return public_venue_statuses()[:4]
    return rows[:4] if featured_only else rows


def public_dashboard_data() -> dict:
    now = timezone.localtime()
    today = now.date()
    week_end = today + timedelta(days=7)
    events = public_events(today, week_end)
    today_events = [row for row in events if row["date"] == today.isoformat()]
    current = [row for row in today_events if row["start"] <= now.isoformat() <= row["end"]]
    soon_limit = now + timedelta(minutes=60)
    soon = [row for row in today_events if now.isoformat() < row["start"] <= soon_limit.isoformat()]
    venues = public_venue_statuses(featured_only=True)
    available = sum(row["status"] == "AVAILABLE" for row in venues)
    occupied = sum(row["status"] == "OCCUPIED" for row in venues)
    return {
        "generated_at": now.isoformat(),
        "today": today.isoformat(),
        "metrics": {
            "today": len(today_events),
            "in_progress": len(current),
            "starting_soon": len(soon),
            "available_venues": available,
            "occupied_venues": occupied,
        },
        "today_events": today_events,
        "upcoming_events": [row for row in events if row["start"] > now.isoformat()][:8],
        "venues": venues,
        "calendar_days": [
            {
                "date": (today + timedelta(days=offset)).isoformat(),
                "day": (today + timedelta(days=offset)).day,
                "weekday": date_format(today + timedelta(days=offset), "D"),
                "count": sum(
                    row["date"] == (today + timedelta(days=offset)).isoformat() for row in events
                ),
                "next_title": next(
                    (
                        row["title"]
                        for row in events
                        if row["date"] == (today + timedelta(days=offset)).isoformat()
                    ),
                    "",
                ),
            }
            for offset in range(7)
        ],
    }


def public_filter_options() -> dict:
    return {
        "venues": Venue.objects.filter(is_active=True, display_enabled=True)
        .exclude(
            Q(code__istartswith="ACCD") | Q(code__istartswith="TEST") | Q(code__istartswith="P11-")
        )
        .order_by("sort_order", "code"),
        "event_types": EventType.objects.filter(is_active=True).order_by("sort_order", "code"),
        "statuses": [
            (value, str(label)) for value, label in Event.Status.choices if value in PUBLIC_STATUSES
        ],
    }
