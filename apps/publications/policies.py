from django.core.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import User
from apps.events.models import Event

ELIGIBLE_STATUSES = (
    Event.Status.APPROVED,
    Event.Status.PLANNED,
    Event.Status.SCHEDULED,
    Event.Status.ONGOING,
)


def ensure_event_publishable(event: Event) -> None:
    if event.status not in ELIGIBLE_STATUSES:
        raise ValidationError("This event is not eligible for public publication.")


def can_prepare(user: User, event: Event | None = None) -> bool:
    # AnonymousUser has no `.role` — `is_superuser` is False for it, so the
    # `or` below would otherwise fall through to `.role` and raise
    # AttributeError instead of just returning False.
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role in (
        User.Role.SUPER_ADMIN,
        User.Role.INTERNATIONAL_ADMIN,
        User.Role.CONTENT_MANAGER,
    ):
        return True
    return bool(
        event
        and user.role == User.Role.RESPONSIBLE_EMPLOYEE
        and event.responsible_employee_id == user.pk
    )


def can_approve(user: User) -> bool:
    if not user.is_authenticated:
        return False
    return bool(
        user.is_superuser
        or user.role
        in (
            User.Role.SUPER_ADMIN,
            User.Role.INTERNATIONAL_ADMIN,
            User.Role.MANAGEMENT_RESPONSIBLE,
        )
    )


def can_publish(user: User) -> bool:
    if not user.is_authenticated:
        return False
    return bool(
        user.is_superuser
        or user.role
        in (
            User.Role.SUPER_ADMIN,
            User.Role.INTERNATIONAL_ADMIN,
            User.Role.CONTENT_MANAGER,
        )
    )


def require_permission(allowed: bool) -> None:
    if not allowed:
        raise PermissionDenied
