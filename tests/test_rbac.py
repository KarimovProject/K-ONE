import pytest
from django.contrib.auth import get_user_model

from apps.accounts.rbac import Capability, user_has_capability


@pytest.mark.django_db
def test_rbac_grants_only_role_capabilities():
    user_model = get_user_model()
    approver = user_model.objects.create_user(
        username="approver",
        role=user_model.Role.MANAGEMENT_RESPONSIBLE,
    )

    assert user_has_capability(approver, Capability.APPROVE_EVENTS)
    assert user_has_capability(approver, Capability.VIEW_LEADERSHIP_DASHBOARD)
    assert not user_has_capability(approver, Capability.MANAGE_SYSTEM)


@pytest.mark.django_db
def test_superuser_bypasses_capability_matrix():
    user_model = get_user_model()
    admin = user_model.objects.create_superuser(username="root", password="test-password")

    assert user_has_capability(admin, Capability.MANAGE_SYSTEM)
