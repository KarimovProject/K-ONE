import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username="phase0.user",
        email="phase0@example.test",
        password="safe-test-password",
        first_name="Phase",
    )


@pytest.fixture
def master_data_admin(db):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username="master.admin",
        password="safe-test-password",
        role=user_model.Role.INTERNATIONAL_ADMIN,
    )


@pytest.fixture
def leadership_viewer(db):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username="leadership.viewer",
        password="safe-test-password",
        role=user_model.Role.LEADERSHIP_VIEWER,
    )
