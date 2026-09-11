from collections.abc import Iterable

from django.db.models import Q, QuerySet

from apps.accounts.models import User

ADMIN_ROLES = (User.Role.SUPER_ADMIN, User.Role.INTERNATIONAL_ADMIN)


def selectable_staff(*, exclude_doctors: bool = False) -> QuerySet[User]:
    queryset = User.objects.filter(is_active=True).order_by("first_name", "last_name", "username")
    if exclude_doctors:
        queryset = queryset.exclude(role=User.Role.DOCTOR)
    return queryset


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


def doctors() -> QuerySet[User]:
    return staff_for_roles((User.Role.DOCTOR,))


def manageable_users() -> QuerySet[User]:
    """Users eligible to appear on the /users/ approval page — excludes anyone
    with admin-level privileges (superusers, super admins, international
    admins), who manage themselves via their own accounts, not each other."""
    return User.objects.exclude(Q(is_superuser=True) | Q(role__in=ADMIN_ROLES))


def is_admin_privileged(user: User) -> bool:
    return user.is_superuser or user.role in ADMIN_ROLES


def staff_choices(users: Iterable[User] | None = None) -> list[tuple[int, str]]:
    queryset = selectable_staff() if users is None else users
    return [(user.pk, user.get_full_name() or user.username) for user in queryset]
