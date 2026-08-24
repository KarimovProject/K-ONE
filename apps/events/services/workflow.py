from datetime import date, time

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.audit.services import log_audit_event
from apps.events.models import Event
from apps.events.services.conflicts import (
    find_conflicting_events,
    validate_and_lock_event_reservation,
)
from apps.notifications.models import Notification
from apps.notifications.services import send_notification
from apps.notifications.telegram.services import schedule_event_notification
from apps.venues.models import Venue


def submit_event_for_approval(event: Event, actor: User) -> Event:
    if event.status not in (Event.Status.DRAFT, Event.Status.REJECTED):
        raise ValidationError(
            _("Only events in Draft or Rejected status can be submitted for approval.")
        )

    event.status = Event.Status.PENDING_APPROVAL
    event.submitted_at = timezone.now()
    event.updated_by = actor
    event.save(update_fields=["status", "submitted_at", "updated_by", "updated_at"])

    log_audit_event("event.submitted", actor=actor, target=event)

    # Notify management responsible user
    if event.management_responsible:
        send_notification(
            recipient=event.management_responsible,
            title=_("Event Approval Request"),
            message=_("Event “%(title)s” submitted for management review by %(user)s.")
            % {"title": event.title, "user": actor.get_full_name() or actor.username},
            severity=Notification.Severity.INFO,
            target_url=f"/events/{event.pk}/",
        )

    schedule_event_notification(event, "submitted")
    return event


def approve_event(event: Event, actor: User, notes: str = "") -> Event:
    if event.status != Event.Status.PENDING_APPROVAL:
        raise ValidationError(_("Only events pending approval can be approved."))

    conflicts = find_conflicting_events(
        venue=event.venue,
        planned_date=event.planned_date,
        start_time=event.start_time,
        end_time=event.end_time,
        exclude_event_id=str(event.pk),
    )
    if conflicts.exists():
        raise ValidationError(
            _("Event conflicts with existing reservations. Requires priority override.")
        )

    event.status = Event.Status.APPROVED
    event.reviewed_at = timezone.now()
    event.reviewed_by = actor
    if notes:
        event.notes = (event.notes + f"\n\nApproval Note ({actor.username}): {notes}").strip()
    event.updated_by = actor
    event.save(
        update_fields=[
            "status",
            "reviewed_at",
            "reviewed_by",
            "notes",
            "updated_by",
            "updated_at",
        ]
    )

    log_audit_event("event.approved", actor=actor, target=event)

    # Notify responsible employee
    if event.responsible_employee:
        send_notification(
            recipient=event.responsible_employee,
            title=_("Event Approved"),
            message=_("Your event “%(title)s” has been approved by %(reviewer)s.")
            % {"title": event.title, "reviewer": actor.get_full_name() or actor.username},
            severity=Notification.Severity.INFO,
            target_url=f"/events/{event.pk}/",
        )

    schedule_event_notification(event, "approved")
    return event


def reject_event(event: Event, actor: User, reason: str) -> Event:
    clean_reason = (reason or "").strip()
    if not clean_reason:
        raise ValidationError(_("A rejection reason is mandatory."))

    if event.status != Event.Status.PENDING_APPROVAL:
        raise ValidationError(_("Only events pending approval can be rejected."))

    event.status = Event.Status.REJECTED
    event.reviewed_at = timezone.now()
    event.reviewed_by = actor
    event.rejection_reason = clean_reason
    event.updated_by = actor
    event.save(
        update_fields=[
            "status",
            "reviewed_at",
            "reviewed_by",
            "rejection_reason",
            "updated_by",
            "updated_at",
        ]
    )

    log_audit_event("event.rejected", actor=actor, target=event, payload={"reason": clean_reason})

    # Notify responsible employee
    if event.responsible_employee:
        send_notification(
            recipient=event.responsible_employee,
            title=_("Event Rejected"),
            message=_("Your event “%(title)s” was rejected by %(reviewer)s. Reason: %(reason)s")
            % {
                "title": event.title,
                "reviewer": actor.get_full_name() or actor.username,
                "reason": clean_reason,
            },
            severity=Notification.Severity.WARNING,
            target_url=f"/events/{event.pk}/",
        )

    schedule_event_notification(event, "rejected")
    return event


def resubmit_event(event: Event, actor: User) -> Event:
    if event.status != Event.Status.REJECTED:
        raise ValidationError(_("Only rejected events can be resubmitted."))

    event.status = Event.Status.PENDING_APPROVAL
    event.submitted_at = timezone.now()
    event.updated_by = actor
    event.save(update_fields=["status", "submitted_at", "updated_by", "updated_at"])

    log_audit_event("event.resubmitted", actor=actor, target=event)

    if event.management_responsible:
        send_notification(
            recipient=event.management_responsible,
            title=_("Event Resubmitted for Approval"),
            message=_("Event “%(title)s” has been corrected and resubmitted by %(user)s.")
            % {"title": event.title, "user": actor.get_full_name() or actor.username},
            severity=Notification.Severity.INFO,
            target_url=f"/events/{event.pk}/",
        )

    schedule_event_notification(event, "resubmitted")
    return event


def postpone_event(event: Event, actor: User, reason: str = "") -> Event:
    if event.status in (Event.Status.CANCELLED, Event.Status.COMPLETED):
        raise ValidationError(_("Cancelled or completed events cannot be postponed."))

    event.status = Event.Status.POSTPONED
    event.updated_by = actor
    if reason:
        event.notes = (event.notes + f"\n\nPostponed Note ({actor.username}): {reason}").strip()

    event.save(update_fields=["status", "notes", "updated_by", "updated_at"])

    log_audit_event("event.postponed", actor=actor, target=event, payload={"reason": reason})

    if event.responsible_employee:
        send_notification(
            recipient=event.responsible_employee,
            title=_("Event Postponed"),
            message=_("Event “%(title)s” has been postponed.") % {"title": event.title},
            severity=Notification.Severity.WARNING,
            target_url=f"/events/{event.pk}/",
        )

    schedule_event_notification(event, "postponed")
    return event


def reschedule_event(
    event: Event,
    actor: User,
    planned_date: date,
    start_time: time,
    end_time: time,
    venue: Venue | None = None,
) -> Event:
    target_venue = venue or event.venue

    with transaction.atomic():
        # Re-run conflict engine and lock venue reservation
        validate_and_lock_event_reservation(
            venue=target_venue,
            planned_date=planned_date,
            start_time=start_time,
            end_time=end_time,
            status=Event.Status.PLANNED,
            expected_attendees=event.expected_attendees,
            exclude_event_id=str(event.pk),
        )

        orig_date = str(event.planned_date)
        orig_start = event.start_time.strftime("%H:%M")
        orig_end = event.end_time.strftime("%H:%M")

        event.planned_date = planned_date
        event.start_time = start_time
        event.end_time = end_time
        event.venue = target_venue
        event.status = Event.Status.PLANNED
        event.displaced_by_event = None
        event.updated_by = actor
        event.save(
            update_fields=[
                "planned_date",
                "start_time",
                "end_time",
                "venue",
                "status",
                "displaced_by_event",
                "updated_by",
                "updated_at",
            ]
        )

        log_audit_event(
            "event.rescheduled",
            actor=actor,
            target=event,
            payload={
                "previous_date": orig_date,
                "previous_start": orig_start,
                "previous_end": orig_end,
                "new_date": str(planned_date),
                "new_start": start_time.strftime("%H:%M"),
                "new_end": end_time.strftime("%H:%M"),
                "venue_id": target_venue.pk,
            },
        )

        if event.responsible_employee:
            send_notification(
                recipient=event.responsible_employee,
                title=_("Event Rescheduled"),
                message=_(
                    "Your event “%(title)s” has been successfully rescheduled "
                    "to %(date)s (%(start)s - %(end)s)."
                )
                % {
                    "title": event.title,
                    "date": planned_date,
                    "start": start_time.strftime("%H:%M"),
                    "end": end_time.strftime("%H:%M"),
                },
                severity=Notification.Severity.INFO,
                target_url=f"/events/{event.pk}/",
            )

    schedule_event_notification(event, "rescheduled")
    return event


def override_event(event: Event, actor: User, reason: str) -> Event:
    clean_reason = (reason or "").strip()
    if not clean_reason:
        raise ValidationError(_("An override reason is mandatory."))

    if event.status != Event.Status.PENDING_APPROVAL:
        raise ValidationError(_("Only events pending approval can override others."))

    with transaction.atomic():
        conflicts = find_conflicting_events(
            venue=event.venue,
            planned_date=event.planned_date,
            start_time=event.start_time,
            end_time=event.end_time,
            exclude_event_id=str(event.pk),
        ).select_for_update()

        if not conflicts.exists():
            raise ValidationError(_("No conflicting events to override."))

        # Displace conflicts
        for conflict in conflicts:
            conflict.status = Event.Status.DISPLACED
            conflict.displaced_by_event = event
            conflict.updated_by = actor
            conflict.notes = (
                conflict.notes + f"\n\nDisplaced Note ({actor.username}): {clean_reason}"
            ).strip()
            conflict.save(
                update_fields=["status", "displaced_by_event", "updated_by", "notes", "updated_at"]
            )

            log_audit_event(
                "event.displaced",
                actor=actor,
                target=conflict,
                payload={"displaced_by": str(event.pk), "reason": clean_reason},
            )

            # Notify owner of displaced event
            if conflict.responsible_employee:
                send_notification(
                    recipient=conflict.responsible_employee,
                    title=_("Event Displaced"),
                    message=_(
                        "Your event '%(title)s' was displaced by a higher priority event. Reason: %(reason)s"
                    )
                    % {"title": conflict.title, "reason": clean_reason},
                    severity=Notification.Severity.WARNING,
                    target_url=f"/events/{conflict.pk}/",
                )

        # Now approve this event
        event.status = Event.Status.APPROVED
        event.reviewed_at = timezone.now()
        event.reviewed_by = actor
        event.notes = (
            event.notes + f"\n\nOverride Note ({actor.username}): {clean_reason}"
        ).strip()
        event.updated_by = actor
        event.save(
            update_fields=[
                "status",
                "reviewed_at",
                "reviewed_by",
                "notes",
                "updated_by",
                "updated_at",
            ]
        )

        log_audit_event(
            "event.approved_override", actor=actor, target=event, payload={"reason": clean_reason}
        )

        if event.responsible_employee:
            send_notification(
                recipient=event.responsible_employee,
                title=_("Event Approved (Override)"),
                message=_(
                    "Your event '%(title)s' has been approved via priority override by %(reviewer)s."
                )
                % {"title": event.title, "reviewer": actor.get_full_name() or actor.username},
                severity=Notification.Severity.INFO,
                target_url=f"/events/{event.pk}/",
            )

        schedule_event_notification(event, "approved")

    return event
