from datetime import time, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import DoctorProfile, StaffUnavailability, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def doctor():
    user = User.objects.create_user(
        username="dr.busy", password="x", role=User.Role.DOCTOR
    )
    DoctorProfile.objects.create(
        user=user, specialty="Cardiology", workplace="Clinic", phone="+998"
    )
    return user


def test_page_loads_without_login(client):
    response = client.get(reverse("public-busy-doctors"))
    assert response.status_code == 200


def test_shows_a_doctor_busy_right_now(client, doctor):
    now = timezone.localtime()
    StaffUnavailability.objects.create(
        user=doctor,
        start_date=now.date(),
        start_time=(now - timedelta(hours=1)).time(),
        end_date=now.date(),
        end_time=(now + timedelta(hours=1)).time(),
        reason="Surgery in progress",
    )
    response = client.get(reverse("public-busy-doctors"))
    content = response.content.decode()
    assert "Surgery in progress" in content
    assert response.context["busy_now_count"] == 1
    assert response.context["busy_today_count"] == 1


def test_upcoming_slot_counts_as_busy_this_week_but_not_now(client, doctor):
    today = timezone.localdate()
    StaffUnavailability.objects.create(
        user=doctor,
        start_date=today + timedelta(days=3),
        start_time=time(9, 0),
        end_date=today + timedelta(days=3),
        end_time=time(11, 0),
        reason="Conference travel",
    )
    response = client.get(reverse("public-busy-doctors"))
    assert response.context["busy_now_count"] == 0
    assert response.context["busy_today_count"] == 0
    assert response.context["busy_week_count"] == 1
    assert "Conference travel" in response.content.decode()


def test_past_slot_is_not_shown(client, doctor):
    today = timezone.localdate()
    StaffUnavailability.objects.create(
        user=doctor,
        start_date=today - timedelta(days=10),
        start_time=time(9, 0),
        end_date=today - timedelta(days=10),
        end_time=time(11, 0),
        reason="Old reason",
    )
    response = client.get(reverse("public-busy-doctors"))
    assert "Old reason" not in response.content.decode()
    assert response.context["busy_now_count"] == 0


def test_empty_state_shown_when_no_one_is_busy(client):
    response = client.get(reverse("public-busy-doctors"))
    assert "Hozircha band shifokor yo'q" in response.content.decode()
