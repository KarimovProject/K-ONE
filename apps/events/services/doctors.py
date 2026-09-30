from datetime import date, time

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.accounts.services import find_busy_doctors
from apps.events.models import Event
from apps.notifications.models import Notification
from apps.notifications.services import notify_users, queue_notification_email

# Statuses that do not actually hold the doctor's time — the same set the
# venue conflict engine ignores (apps.events.services.conflicts).
NON_BLOCKING_STATUSES = (
    Event.Status.DRAFT,
    Event.Status.CANCELLED,
    Event.Status.REJECTED,
    Event.Status.DISPLACED,
    Event.Status.POSTPONED,
)


def find_overlapping_doctor_event(
    doctor,
    planned_date: date,
    start_time: time,
    end_time: time,
    exclude_event_id=None,
) -> Event | None:
    """Returns another live event the doctor is already assigned to as a
    speaker at an overlapping time, or None when the slot is free."""
    queryset = Event.objects.filter(
        attending_doctors=doctor,
        planned_date=planned_date,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).exclude(status__in=NON_BLOCKING_STATUSES)
    if exclude_event_id:
        queryset = queryset.exclude(pk=exclude_event_id)
    return queryset.order_by("start_time").first()


def busy_attending_doctor_errors(
    doctors, planned_date, start_time, end_time, exclude_event_id=None
) -> list[str]:
    """Blocking check: an event cannot be saved with an attending doctor who
    is marked busy for that date/time or is already speaking at another
    overlapping event — a doctor can't be in two places at once, so this is
    a hard error, not a dismissible warning. Returns one translated error
    message per busy doctor (empty list means all clear)."""
    doctors = list(doctors)
    errors = []
    busy_ids = set()
    for doctor, reason in find_busy_doctors(doctors, planned_date, start_time, end_time):
        busy_ids.add(doctor.pk)
        doctor_name = doctor.get_full_name() or doctor.username
        errors.append(
            _("%(doctor)s is busy at this time and cannot be assigned — reason: %(reason)s")
            % {"doctor": doctor_name, "reason": reason}
        )
    for doctor in doctors:
        if doctor.pk in busy_ids:
            continue
        other = find_overlapping_doctor_event(
            doctor, planned_date, start_time, end_time, exclude_event_id
        )
        if other:
            doctor_name = doctor.get_full_name() or doctor.username
            errors.append(
                _(
                    "%(doctor)s is already assigned to “%(event)s” "
                    "(%(start)s–%(end)s) at this time and cannot be assigned"
                )
                % {
                    "doctor": doctor_name,
                    "event": other.title,
                    "start": other.start_time.strftime("%H:%M"),
                    "end": other.end_time.strftime("%H:%M"),
                }
            )
    return errors


def notify_assigned_doctors(event, doctors) -> None:
    """Tells each newly assigned speaker doctor about their assignment —
    an in-app notification plus a best-effort email queued to Celery, so a
    slow or unreachable mail server never delays the save that triggered
    this."""
    doctors = [d for d in doctors if d and d.pk]
    if not doctors:
        return

    title = _("You've been assigned as a speaker")
    message = _(
        "You have been assigned as a speaker doctor for the event "
        "“%(title)s” on %(date)s (%(start)s–%(end)s) at %(venue)s."
    ) % {
        "title": event.title,
        "date": event.planned_date,
        "start": event.start_time.strftime("%H:%M"),
        "end": event.end_time.strftime("%H:%M"),
        "venue": event.venue.localized_name,
    }
    # Doctors have no capability to open the internal event-detail page,
    # so the notification points at their own assigned-events list instead.
    target_url = reverse("doctor-assigned-events")

    notify_users(
        doctors,
        title=title,
        message=message,
        severity=Notification.Severity.INFO,
        target_url=target_url,
    )
    for doctor in doctors:
        queue_notification_email(doctor, subject=str(title), message=str(message))
