from unittest.mock import patch

import pytest
from django.urls import reverse


def test_application_health(client):
    response = client.get(reverse("application-health"))

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_database_health(client):
    response = client.get(reverse("database-health"))

    assert response.status_code == 200
    assert response.json()["service"] == "database"


@patch("config.health_checks.redis.Redis.ping", return_value=True)
def test_redis_health(_ping, client):
    response = client.get(reverse("redis-health"))

    assert response.status_code == 200
    assert response.json()["service"] == "redis"
