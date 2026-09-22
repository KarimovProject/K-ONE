from dataclasses import dataclass
from datetime import date, time
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from apps.events.models import Event
from apps.venues.models import Venue


@dataclass
class AvailabilityCheckResult:
    is_available: bool
    status_label: str
    message: str
    conflicting_event: Event | None
    capacity_warning: str | None
    alternative_venues: list[dict[str, Any]]


def find_conflicting_events(
    venue: Venue,
    planned_date: date,
    start_time: time,
    end_time: time,
    exclude_event_id: str | None = None,
) -> QuerySet[Event]:
    queryset = Event.objects.filter(
        venue=venue,
        planned_date=planned_date,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exclude(
        status__in=[
            Event.Status.DRAFT,
            Event.Status.CANCELLED,
            Event.Status.REJECTED,
            Event.Status.DISPLACED,
            Event.Status.POSTPONED,
        ]
    )

    if exclude_event_id:
        queryset = queryset.exclude(pk=exclude_event_id)

    return queryset.select_related("event_type", "venue")


def suggest_alternative_venues(
    planned_date: date,
    start_time: time,
    end_time: time,
    expected_attendees: int = 1,
    exclude_venue_id: int | None = None,
) -> list[dict[str, Any]]:
    active_venues = Venue.objects.filter(is_active=True, display_enabled=True)
    if exclude_venue_id:
        active_venues = active_venues.exclude(pk=exclude_venue_id)

    suggested = []
    for venue in active_venues.order_by("-capacity", "sort_order"):
        # Check capacity
        if venue.capacity < expected_attendees:
            continue

        # Check venue working hours
        if start_time < venue.working_start or end_time > venue.working_end:
            continue

        # Check conflicts
        conflicts = find_conflicting_events(venue, planned_date, start_time, end_time)
        if not conflicts.exists():
            suggested.append(
                {
                    "id": venue.pk,
                    "code": venue.code,
                    "name": venue.localized_name,
                    "capacity": venue.capacity,
                    "location": venue.location,
                }
            )

    return suggested


def check_venue_availability(
    venue: Venue,
    planned_date: date,
    start_time: time,
    end_time: time,
    expected_attendees: int = 1,
    exclude_event_id: str | None = None,
) -> AvailabilityCheckResult:
    # 1. Time ordering check
    if end_time <= start_time:
        return AvailabilityCheckResult(
            is_available=False,
            status_label="INVALID_TIME",
            message=_("End time must be later than start time."),
            conflicting_event=None,
            capacity_warning=None,
            alternative_venues=[],
        )

    # 2. Venue working hours check
    if start_time < venue.working_start or end_time > venue.working_end:
        message = _(
            "Event time (%(start)s - %(end)s) is outside "
            "venue working hours (%(v_start)s - %(v_end)s)."
        ) % {
            "start": start_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M"),
            "v_start": venue.working_start.strftime("%H:%M"),
            "v_end": venue.working_end.strftime("%H:%M"),
        }

        return AvailabilityCheckResult(
            is_available=False,
            status_label="OUTSIDE_HOURS",
            message=message,
            conflicting_event=None,
            capacity_warning=None,
            alternative_venues=[],
        )

    # 3. Capacity warning check
    capacity_warning = None
    if expected_attendees > venue.capacity:
        capacity_warning = _(
            "Expected attendees (%(attendees)d) exceeds venue capacity (%(capacity)d)."
        ) % {"attendees": expected_attendees, "capacity": venue.capacity}

    # 4. Overlap conflict check
    conflicts = find_conflicting_events(
        venue=venue,
        planned_date=planned_date,
        start_time=start_time,
        end_time=end_time,
        exclude_event_id=exclude_event_id,
    )

    if conflicts.exists():
        first_conflict = conflicts.first()
        message = _("Occupied by “%(title)s” (%(start)s – %(end)s).") % {
            "title": first_conflict.title,
            "start": first_conflict.start_time.strftime("%H:%M"),
            "end": first_conflict.end_time.strftime("%H:%M"),
        }

        alternatives = suggest_alternative_venues(
            planned_date=planned_date,
            start_time=start_time,
            end_time=end_time,
            expected_attendees=expected_attendees,
            exclude_venue_id=venue.pk,
        )

        return AvailabilityCheckResult(
            is_available=False,
            status_label="OCCUPIED",
            message=message,
            conflicting_event=first_conflict,
            capacity_warning=capacity_warning,
            alternative_venues=alternatives,
        )

    # Available!
    message = _("%(venue)s is available.") % {"venue": venue.localized_name}
    alternatives = []
    if capacity_warning:
        alternatives = suggest_alternative_venues(
            planned_date=planned_date,
            start_time=start_time,
            end_time=end_time,
            expected_attendees=expected_attendees,
            exclude_venue_id=venue.pk,
        )

    return AvailabilityCheckResult(
        is_available=True,
        status_label="AVAILABLE",
        message=message,
        conflicting_event=None,
        capacity_warning=capacity_warning,
        alternative_venues=alternatives,
    )


def validate_and_lock_event_reservation(
    venue: Venue,
    planned_date: date,
    start_time: time,
    end_time: time,
    status: str = Event.Status.PLANNED,
    expected_attendees: int = 1,
    exclude_event_id: str | None = None,
) -> None:
    """
    Executes in atomic transaction with row locks to prevent double-booking.
    """
    if end_time <= start_time:
        raise ValidationError(_("End time must be later than start time."))

    with transaction.atomic():
        # Lock the venue row to prevent simultaneous reservations
        locked_venue = Venue.objects.select_for_update().get(pk=venue.pk)

        if status == Event.Status.PLANNED:
            # Overcapacity check for PLANNED state
            if expected_attendees > locked_venue.capacity:
                raise ValidationError(
                    _(
                        "Cannot save as Planned: Expected attendees (%(attendees)d) "
                        "exceeds venue capacity (%(capacity)d)."
                    )
                    % {"attendees": expected_attendees, "capacity": locked_venue.capacity}
                )

            # Conflict check
            conflicts = find_conflicting_events(
                venue=locked_venue,
                planned_date=planned_date,
                start_time=start_time,
                end_time=end_time,
                exclude_event_id=exclude_event_id,
            )
            if conflicts.exists():
                raise ValidationError(
                    _("Tanlangan vaqtda ushbu zal band. Boshqa vaqt yoki zalni tanlang.")
                )
