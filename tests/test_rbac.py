import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from apps.accounts.rbac import ROLE_CAPABILITIES, Capability, user_has_capability


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


@pytest.mark.django_db
@pytest.mark.parametrize("role", list(ROLE_CAPABILITIES))
def test_each_role_grants_exactly_its_own_capabilities_and_nothing_else(role):
    # Exhaustive deny-by-default check: every role must have exactly the
    # capabilities ROLE_CAPABILITIES declares for it — no more, no less.
    # Previously only MANAGEMENT_RESPONSIBLE was exercised (3 of ~11
    # capabilities), leaving every other role's boundary unverified.
    user_model = get_user_model()
    user = user_model.objects.create_user(username=f"rbac-{role}", role=role)

    granted = ROLE_CAPABILITIES[role]
    for capability in Capability:
        expected = capability in granted
        assert user_has_capability(user, capability) is expected, (
            f"{role} capability {capability} expected {expected}"
        )


@pytest.mark.django_db
def test_doctor_role_has_no_capabilities():
    # DOCTOR is intentionally absent from ROLE_CAPABILITIES (see goals.md) —
    # user_has_capability must fail closed (empty frozenset default) rather
    # than raise or grant anything.
    user_model = get_user_model()
    doctor = user_model.objects.create_user(
        username="rbac-doctor", role=user_model.Role.DOCTOR
    )

    for capability in Capability:
        assert not user_has_capability(doctor, capability)


@pytest.mark.django_db
def test_inactive_user_has_no_capabilities_even_with_a_granted_role():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="rbac-inactive",
        role=user_model.Role.SUPER_ADMIN,
        is_active=False,
    )

    assert not user_has_capability(user, Capability.MANAGE_SYSTEM)


def test_anonymous_user_has_no_capabilities_instead_of_crashing():
    anon = AnonymousUser()

    for capability in Capability:
        assert not user_has_capability(anon, capability)


@pytest.mark.django_db
def test_unknown_capability_string_is_rejected_instead_of_crashing():
    user_model = get_user_model()
    admin = user_model.objects.create_superuser(username="root2", password="test-password")

    # A typo'd/removed capability name must fail closed for a non-superuser,
    # not raise ValueError from the Capability(...) coercion.
    non_admin = user_model.objects.create_user(
        username="rbac-typo", role=user_model.Role.RESPONSIBLE_EMPLOYEE
    )
    assert not user_has_capability(non_admin, "not_a_real_capability")
    # Superusers still bypass the matrix entirely, before the capability
    # name is even validated.
    assert user_has_capability(admin, "not_a_real_capability")
