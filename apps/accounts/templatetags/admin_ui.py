from django import template
from django.contrib.admin.models import LogEntry
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from apps.attendance.models import EventAttendance
from apps.events.models import Event
from apps.venues.models import Venue
from apps.venues.services.live_status import all_venues_live_status

register = template.Library()


@register.simple_tag
def iems_admin_metrics():
    today = timezone.localdate()
    return {
        "events": Event.objects.count(),
        "today": Event.objects.filter(planned_date=today).count(),
        "pending": Event.objects.filter(status=Event.Status.PENDING_APPROVAL).count(),
        "venues": Venue.objects.filter(is_active=True).count(),
        "attendance": EventAttendance.objects.filter(checked_in_at__date=today).count(),
    }


@register.simple_tag
def iems_recent_admin_actions(limit=7):
    return LogEntry.objects.select_related("user", "content_type")[:limit]


@register.simple_tag
def iems_admin_operations():
    today = timezone.localdate()
    clean = Event.objects.exclude(
        Q(title__istartswith="[ACCEPTANCE_DEMO]") | Q(title__istartswith="[P11]")
    ).select_related("venue")
    return {
        "today": clean.filter(planned_date=today).order_by("start_time")[:4],
        "pending": clean.filter(status=Event.Status.PENDING_APPROVAL).order_by("planned_date")[:4],
        "venues": [
            row
            for row in all_venues_live_status()
            if not row["venue_code"].upper().startswith(("ACCD", "TEST", "P11-"))
        ][:4],
    }


@register.filter
def iems_app_label(value):
    labels = {
        "accounts": _("Users and access"),
        "attendance": _("Attendance"),
        "audit": _("Audit log"),
        "auth": _("Roles and permissions"),
        "events": _("Events"),
        "notifications": _("Notifications"),
        "organizations": _("Organizations"),
        "publications": _("Publications"),
        "venues": _("Venues"),
    }
    return labels.get(str(value).lower(), value)
