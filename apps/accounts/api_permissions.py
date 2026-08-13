from rest_framework.permissions import BasePermission

from apps.accounts.rbac import Capability, user_has_capability


class CanViewMasterData(BasePermission):
    message = "You do not have permission to view master data."

    def has_permission(self, request, view) -> bool:
        return user_has_capability(request.user, Capability.VIEW_MASTER_DATA)
