from collections.abc import Iterable

from django.db.models import QuerySet

from apps.accounts.models import User


def selectable_staff() -> QuerySet[User]:
    return User.objects.filter(is_active=True).order_by("first_name", "last_name", "username")


def staff_for_roles(roles: Iterable[str]) -> QuerySet[User]:
    return selectable_staff().filter(role__in=tuple(roles))


def responsible_employees() -> QuerySet[User]:
    return staff_for_roles((User.Role.RESPONSIBLE_EMPLOYEE,))


def management_responsible_users() -> QuerySet[User]:
    return staff_for_roles((User.Role.MANAGEMENT_RESPONSIBLE,))


def international_admins() -> QuerySet[User]:
    return staff_for_roles((User.Role.INTERNATIONAL_ADMIN,))


def leadership_viewers() -> QuerySet[User]:
    return staff_for_roles((User.Role.LEADERSHIP_VIEWER,))


def content_managers() -> QuerySet[User]:
    return staff_for_roles((User.Role.CONTENT_MANAGER,))


def staff_choices(users: Iterable[User] | None = None) -> list[tuple[int, str]]:
    queryset = selectable_staff() if users is None else users
    return [(user.pk, user.get_full_name() or user.username) for user in queryset]
