from datetime import UTC, datetime

import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
def test_user_can_authenticate(client, user):
    response = client.post(
        reverse("login"),
        {"username": user.username, "password": "safe-test-password"},
    )

    assert response.status_code == 302
    assert response.url == reverse("dashboard")
    assert client.session["_auth_user_id"] == str(user.pk)


@pytest.mark.django_db
def test_correct_credentials_for_never_approved_account_show_pending_message(client):
    User.objects.create_user(
        username="dr.pending", password="safe-test-password", is_active=False
    )
    response = client.post(
        reverse("login"),
        {"username": "dr.pending", "password": "safe-test-password"},
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "administrator tomonidan" in content
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_correct_credentials_for_previously_approved_now_deactivated_account_show_contact_admin(
    client,
):
    User.objects.create_user(
        username="dr.deactivated",
        password="safe-test-password",
        is_active=False,
        approved_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    response = client.post(
        reverse("login"),
        {"username": "dr.deactivated", "password": "safe-test-password"},
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "faollashtirilmagan" in content
    assert "administrator tomonidan" not in content


@pytest.mark.django_db
def test_wrong_password_for_inactive_account_does_not_leak_pending_status(client):
    User.objects.create_user(
        username="dr.pending2", password="the-real-password", is_active=False
    )
    response = client.post(
        reverse("login"),
        {"username": "dr.pending2", "password": "totally-wrong-password"},
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "administrator tomonidan" not in content
    assert "faollashtirilmagan" not in content
