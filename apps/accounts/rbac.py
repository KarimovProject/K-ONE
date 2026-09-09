from collections.abc import Callable
from enum import StrEnum
from functools import wraps
from typing import Any, TypeVar, cast

from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from apps.accounts.models import User


class Capability(StrEnum):
    MANAGE_SYSTEM = "manage_system"
    MANAGE_EVENTS = "manage_events"
    CREATE_OWN_EVENTS = "create_own_events"
    APPROVE_EVENTS = "approve_events"
    OVERRIDE_EVENTS = "override_events"
    VIEW_LEADERSHIP_DASHBOARD = "view_leadership_dashboard"
    MANAGE_CONTENT = "manage_content"
    MANAGE_ATTENDANCE = "manage_attendance"
    VIEW_MASTER_DATA = "view_master_data"
    MANAGE_MASTER_DATA = "manage_master_data"


ROLE_CAPABILITIES: dict[str, frozenset[Capability]] = {
    User.Role.SUPER_ADMIN: frozenset(Capability),
    User.Role.INTERNATIONAL_ADMIN: frozenset(
        {
            Capability.MANAGE_EVENTS,
            Capability.CREATE_OWN_EVENTS,
            Capability.APPROVE_EVENTS,
            Capability.OVERRIDE_EVENTS,
            Capability.VIEW_LEADERSHIP_DASHBOARD,
            Capability.VIEW_MASTER_DATA,
            Capability.MANAGE_MASTER_DATA,
            Capability.MANAGE_CONTENT,
            Capability.MANAGE_ATTENDANCE,
        }
    ),
    User.Role.RESPONSIBLE_EMPLOYEE: frozenset(
        {Capability.CREATE_OWN_EVENTS, Capability.VIEW_MASTER_DATA}
    ),
    User.Role.MANAGEMENT_RESPONSIBLE: frozenset(
        {
            Capability.APPROVE_EVENTS,
            Capability.VIEW_LEADERSHIP_DASHBOARD,
            Capability.VIEW_MASTER_DATA,
        }
    ),
    User.Role.LEADERSHIP_VIEWER: frozenset(
        {Capability.VIEW_LEADERSHIP_DASHBOARD, Capability.VIEW_MASTER_DATA}
    ),
    User.Role.CONTENT_MANAGER: frozenset({Capability.MANAGE_CONTENT, Capability.VIEW_MASTER_DATA}),
    User.Role.RECEPTION_OPERATOR: frozenset(
        {Capability.MANAGE_ATTENDANCE, Capability.VIEW_MASTER_DATA}
    ),
}


def user_has_capability(user: User, capability: Capability | str) -> bool:
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    try:
        normalized = Capability(capability)
    except ValueError:
        return False
    return normalized in ROLE_CAPABILITIES.get(user.role, frozenset())


ViewFunction = TypeVar("ViewFunction", bound=Callable[..., HttpResponse])


def capability_required(capability: Capability) -> Callable[[ViewFunction], ViewFunction]:
    def decorator(view: ViewFunction) -> ViewFunction:
        @wraps(view)
        def wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not user_has_capability(cast(User, request.user), capability):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return cast(ViewFunction, wrapped)

    return decorator


class CapabilityRequiredMixin(UserPassesTestMixin):
    required_capability: Capability

    def test_func(self) -> bool:
        return user_has_capability(self.request.user, self.required_capability)

    def handle_no_permission(self) -> HttpResponse:
        if not self.request.user.is_authenticated:
            return cast(HttpResponse, super().handle_no_permission())
        raise PermissionDenied
