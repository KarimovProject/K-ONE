from collections import defaultdict

from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.accounts.models import User
from apps.events.models import Event

ALL_REPORT_SECTIONS = frozenset(
    {
        "summary",
        "events",
        "venues",
        "attendance",
        "approvals",
        "emergency",
        "organizations",
        "sponsors",
        "workload",
        "publications",
        "telegram",
    }
)


def filtered_events(filters: dict, start, end, user: User | None = None) -> QuerySet:
    queryset = (
        Event.objects.filter(planned_date__range=(start, end))
        .select_related("venue", "event_type", "responsible_employee", "management_responsible")
        .prefetch_related("organizing_organizations", "sponsors")
    )
    field_map = {
        "venue": "venue",
        "event_type": "event_type",
        "status": "status",
        "priority": "priority",
        "responsible": "responsible_employee",
        "organization": "organizing_organizations",
        "sponsor": "sponsors",
    }
    for key, lookup in field_map.items():
        value = filters.get(key)
        if value:
            queryset = queryset.filter(**{lookup: value})
    if (
        user
        and user.is_authenticated
        and user.role == User.Role.RESPONSIBLE_EMPLOYEE
        and not user.is_superuser
    ):
        queryset = queryset.filter(responsible_employee=user)
    return queryset.distinct()


def reporting_user_allowed(user: User) -> bool:
    return bool(allowed_report_sections(user))


def allowed_report_sections(user: User) -> frozenset[str]:
    if not user.is_authenticated or not user.is_active:
        return frozenset()
    if user.is_superuser or user.role in {
        User.Role.SUPER_ADMIN,
        User.Role.INTERNATIONAL_ADMIN,
        User.Role.LEADERSHIP_VIEWER,
        User.Role.MANAGEMENT_RESPONSIBLE,
        User.Role.RESPONSIBLE_EMPLOYEE,
    }:
        return ALL_REPORT_SECTIONS
    if user.role == User.Role.RECEPTION_OPERATOR:
        return frozenset({"attendance"})
    if user.role == User.Role.CONTENT_MANAGER:
        return frozenset({"publications"})
    return frozenset()


def user_can_export(user: User, export_format: str, kind: str = "events") -> bool:
    sections = allowed_report_sections(user)
    if export_format == "csv":
        return kind in sections and kind in {
            "events",
            "venues",
            "attendance",
            "approvals",
            "publications",
        }
    return ALL_REPORT_SECTIONS.issubset(sections)


def get_dashboard_shell_data():
    return {"metrics": [], "venues": []}


def get_workspace_data(user: User) -> dict:
    today = timezone.localdate()
    now = timezone.localtime()
    base = (
        Event.objects.select_related("venue", "event_type")
        .order_by("planned_date", "start_time")
        .exclude(Q(title__istartswith="[ACCEPTANCE_DEMO]") | Q(title__istartswith="[P11]"))
    )
    if user.is_superuser or user.role in {
        User.Role.SUPER_ADMIN,
        User.Role.INTERNATIONAL_ADMIN,
    }:
        relevant = base.filter(planned_date__gte=today)
    elif user.role == User.Role.MANAGEMENT_RESPONSIBLE:
        relevant = base.filter(
            Q(management_responsible=user) | Q(status=Event.Status.PENDING_APPROVAL)
        )
    else:
        relevant = base.filter(Q(responsible_employee=user) | Q(created_by=user))
    upcoming = list(relevant[:8])
    today_events = list(
        base.filter(
            planned_date=today,
            status__in=(
                Event.Status.APPROVED,
                Event.Status.PLANNED,
                Event.Status.SCHEDULED,
                Event.Status.ONGOING,
                Event.Status.COMPLETED,
            ),
        )[:10]
    )

    from apps.publications.models import Publication
    from apps.venues.services.live_status import all_venues_live_status

    venues_status = all_venues_live_status()
    venues_free_count = sum(1 for v in venues_status if v.get("current_status") == "AVAILABLE")
    venues_total_count = len(venues_status)

    not_started_statuses = (
        Event.Status.DRAFT,
        Event.Status.PENDING_APPROVAL,
        Event.Status.APPROVED,
        Event.Status.PLANNED,
        Event.Status.SUBMITTED,
        Event.Status.UNDER_REVIEW,
        Event.Status.SCHEDULED,
    )
    delayed_events_count = base.filter(
        planned_date=today,
        start_time__lt=now.time(),
        status__in=not_started_statuses,
    ).count()

    active_today_events = list(
        base.filter(planned_date=today).exclude(
            status__in=(
                Event.Status.DRAFT,
                Event.Status.CANCELLED,
                Event.Status.REJECTED,
                Event.Status.DISPLACED,
                Event.Status.POSTPONED,
            )
        )
    )
    # Overlap detection done in-memory against the list already fetched
    # above instead of issuing one find_conflicting_events() query per
    # event — same-day event counts are small, so this stays O(n^2) within
    # each venue group rather than N extra round trips to the database.
    by_venue: dict[int, list[Event]] = defaultdict(list)
    for event in active_today_events:
        if event.venue_id:
            by_venue[event.venue_id].append(event)

    conflicting_pairs = set()
    for venue_events in by_venue.values():
        for i, event in enumerate(venue_events):
            for other in venue_events[i + 1 :]:
                if event.start_time < other.end_time and other.start_time < event.end_time:
                    conflicting_pairs.add(frozenset({event.pk, other.pk}))
    room_conflicts_count = len(conflicting_pairs)

    return {
        "upcoming": upcoming,
        "upcoming_count": relevant.count(),
        "today_events": today_events,
        "venues_status": venues_status,
        "venues_free_count": venues_free_count,
        "venues_total_count": venues_total_count,
        "delayed_events_count": delayed_events_count,
        "room_conflicts_count": room_conflicts_count,
        "needs_action_count": relevant.filter(
            status__in=(Event.Status.DRAFT, Event.Status.REJECTED, Event.Status.DISPLACED)
        ).count(),
        "pending_approval_count": base.filter(status=Event.Status.PENDING_APPROVAL).count(),
        "notification_count": user.notifications.filter(is_read=False).count(),
        "content_pending_count": Publication.objects.filter(
            status__in=(
                Publication.Status.DRAFT,
                Publication.Status.READY,
                Publication.Status.FAILED,
            )
        ).count()
        if user.role == User.Role.CONTENT_MANAGER
        else 0,
        "checkin_today_count": base.filter(
            planned_date=today,
            checkin_enabled=True,
            status__in=(Event.Status.APPROVED, Event.Status.PLANNED, Event.Status.SCHEDULED),
        ).count()
        if user.role == User.Role.RECEPTION_OPERATOR
        else 0,
    }
