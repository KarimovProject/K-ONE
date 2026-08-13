import pytest
from django.contrib.auth import get_user_model

from apps.accounts.selectors import (
    content_managers,
    international_admins,
    leadership_viewers,
    management_responsible_users,
    responsible_employees,
)


@pytest.mark.django_db
def test_role_specific_staff_selectors_return_only_active_users():
    user_model = get_user_model()
    roles_and_selectors = (
        (user_model.Role.RESPONSIBLE_EMPLOYEE, responsible_employees),
        (user_model.Role.MANAGEMENT_RESPONSIBLE, management_responsible_users),
        (user_model.Role.INTERNATIONAL_ADMIN, international_admins),
        (user_model.Role.LEADERSHIP_VIEWER, leadership_viewers),
        (user_model.Role.CONTENT_MANAGER, content_managers),
    )
    for index, (role, selector) in enumerate(roles_and_selectors):
        active = user_model.objects.create_user(username=f"active-{index}", role=role)
        user_model.objects.create_user(username=f"inactive-{index}", role=role, is_active=False)
        assert list(selector()) == [active]
