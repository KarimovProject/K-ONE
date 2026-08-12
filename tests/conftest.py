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

