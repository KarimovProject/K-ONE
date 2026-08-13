from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.audit.services import log_audit_event
from apps.events.models import Event
from apps.events.services.conflicts import find_conflicting_events
from apps.notifications.models import Notification
from apps.notifications.services import send_notification
from apps.venues.models import Venue


def execute_emergency_override(
    event: Event,
    actor: User,
    justification: str,
) -> tuple[Event, list[Event]]:
    # Enforce RBAC server-side: super_admin or international_admin only
    if not (
        actor.is_superuser
        or actor.role in (User.Role.SUPER_ADMIN, User.Role.INTERNATIONAL_ADMIN)
    ):
        raise PermissionDenied(
            _("Only super admins and international admins can execute emergency overrides.")
        )

    clean_just = (justification or "").strip()
    if not clean_just:
        raise ValidationError(_("Emergency override justification is mandatory."))

    with transaction.atomic():
        # Lock target venue row to prevent concurrent modifications
        locked_venue = Venue.objects.select_for_update().get(pk=event.venue.pk)

        conflicts_qs = find_conflicting_events(
            venue=locked_venue,
            planned_date=event.planned_date,
            start_time=event.start_time,
            end_time=event.end_time,
            exclude_event_id=str(event.pk),
        )

        # Lock conflicting event rows
        conflict_ids = list(conflicts_qs.values_list("pk", flat=True))
        if conflict_ids:
            displaced_events = list(Event.objects.filter(pk__in=conflict_ids).select_for_update())
        else:
            displaced_events = []

        # Displace each conflicting event
        for conf_event in displaced_events:
            conf_event.status = Event.Status.DISPLACED
            conf_event.displaced_by_event = event
            conf_event.updated_by = actor
            conf_event.save(
                update_fields=[
                    "status",
                    "displaced_by_event",
                    "updated_by",
                    "updated_at",
                ]
            )

            log_audit_event(
                "event.displaced",
                actor=actor,
                target=conf_event,
                payload={
                    "displaced_by": str(event.pk),
                    "emergency_title": event.title,
                    "reason": clean_just,
                },
            )

            # High-severity alert notification
            if conf_event.responsible_employee:
                send_notification(
                    recipient=conf_event.responsible_employee,
                    title=_("CRITICAL: Event Displaced by Emergency Override"),
                    message=_(
                        "Your event “%(title)s” scheduled for %(date)s (%(start)s - %(end)s) "
                        "has been displaced by an emergency event “%(emerg)s”. Please reschedule."
                    )
                    % {
                        "title": conf_event.title,
                        "date": conf_event.planned_date,
                        "start": conf_event.start_time.strftime("%H:%M"),
                        "end": conf_event.end_time.strftime("%H:%M"),
                        "emerg": event.title,
                    },
                    severity=Notification.Severity.ALERT,
                    target_url=f"/events/{conf_event.pk}/",
                )

        # Set target event as PLANNED with EMERGENCY priority
        event.status = Event.Status.PLANNED
        event.priority = Event.Priority.EMERGENCY
        event.emergency_justification = clean_just
        event.updated_by = actor
        event.save(
            update_fields=[
                "status",
                "priority",
                "emergency_justification",
                "updated_by",
                "updated_at",
            ]
        )

        log_audit_event(
            "event.emergency_overridden",
            actor=actor,
            target=event,
            payload={
                "justification": clean_just,
                "displaced_count": len(displaced_events),
            },
        )

        return event, displaced_events
