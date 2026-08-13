from datetime import date

from django.db.models import QuerySet

from apps.events.models import Event, EventType


def active_event_types() -> QuerySet[EventType]:
    return EventType.objects.filter(is_active=True)


def get_event_type_by_code(code: str) -> EventType | None:
    try:
        return EventType.objects.get(code__iexact=code.strip())
    except EventType.DoesNotExist:
        return None


def base_event_queryset() -> QuerySet[Event]:
    return Event.objects.select_related(
        "event_type",
        "venue",
        "responsible_employee",
        "management_responsible",
        "created_by",
        "updated_by",
    ).prefetch_related(
        "organizing_organizations",
        "sponsors",
    )


def active_events() -> QuerySet[Event]:
    return base_event_queryset().exclude(status=Event.Status.CANCELLED)


def calendar_events(
    start_date: date,
    end_date: date,
    venue_id: int | str | None = None,
    event_type_id: int | str | None = None,
    status_filter: str | None = None,
    responsible_id: int | str | None = None,
    organization_id: int | str | None = None,
) -> QuerySet[Event]:
    queryset = base_event_queryset().filter(
        planned_date__gte=start_date,
        planned_date__lte=end_date,
    )

    if venue_id:
        queryset = queryset.filter(venue_id=venue_id)
    if event_type_id:
        queryset = queryset.filter(event_type_id=event_type_id)
    if status_filter and status_filter != "all":
        queryset = queryset.filter(status=status_filter)
    if responsible_id:
        queryset = queryset.filter(responsible_employee_id=responsible_id)
    if organization_id:
        queryset = queryset.filter(organizing_organizations__id=organization_id).distinct()

    return queryset


def get_event_by_id(event_id: str) -> Event | None:
    try:
        return base_event_queryset().get(pk=event_id)
    except Event.DoesNotExist:
        return None
