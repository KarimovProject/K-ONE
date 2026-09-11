from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, time

from apps.accounts.models import StaffUnavailability, User


@dataclass
class DoctorAvailabilityResult:
    is_available: bool
    reason: str | None
    conflicting_slot: StaffUnavailability | None


def find_unavailability_conflicts(
    doctor: User,
    planned_date: date,
    start_time: time,
    end_time: time,
) -> list[StaffUnavailability]:
    """Events are single-day, but a busy slot can span multiple days, so the
    exact overlap (start_date/start_time vs end_date/end_time) is checked in
    Python after a cheap DB-level date-range prefilter."""
    event_start = datetime.combine(planned_date, start_time)
    event_end = datetime.combine(planned_date, end_time)
    candidates = StaffUnavailability.objects.filter(
        user=doctor,
        start_date__lte=planned_date,
        end_date__gte=planned_date,
    )
    return [
        slot
        for slot in candidates
        if slot.start_datetime < event_end and slot.end_datetime > event_start
    ]


def check_doctor_availability(
    doctor: User,
    planned_date: date,
    start_time: time,
    end_time: time,
) -> DoctorAvailabilityResult:
    conflicts = find_unavailability_conflicts(doctor, planned_date, start_time, end_time)
    if conflicts:
        conflict = conflicts[0]
        return DoctorAvailabilityResult(
            is_available=False,
            reason=conflict.reason,
            conflicting_slot=conflict,
        )
    return DoctorAvailabilityResult(is_available=True, reason=None, conflicting_slot=None)


def find_busy_doctors(
    doctors: Iterable[User],
    planned_date: date,
    start_time: time,
    end_time: time,
) -> list[tuple[User, str]]:
    """Checks every given doctor and returns (doctor, reason) pairs for the
    ones who are busy at the given time — used to block assigning a busy
    doctor to an event rather than just warning about it."""
    busy = []
    for doctor in doctors:
        result = check_doctor_availability(doctor, planned_date, start_time, end_time)
        if not result.is_available:
            busy.append((doctor, result.reason))
    return busy
