from django.db.models import QuerySet

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
    if user and user.role == User.Role.RESPONSIBLE_EMPLOYEE and not user.is_superuser:
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
