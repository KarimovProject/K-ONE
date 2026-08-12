from django.conf import settings
from django.core.checks import run_checks


def test_django_boots_without_system_check_errors():
    errors = run_checks()

    assert errors == []
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert settings.TIME_ZONE == "Asia/Tashkent"

