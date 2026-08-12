import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_user_can_authenticate(client, user):
    response = client.post(
        reverse("login"),
        {"username": user.username, "password": "safe-test-password"},
    )

    assert response.status_code == 302
    assert response.url == reverse("dashboard")
    assert client.session["_auth_user_id"] == str(user.pk)

