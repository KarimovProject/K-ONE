from datetime import time

import pytest
from django.db import IntegrityError
from django.urls import reverse
from django.utils import translation
from rest_framework import status

from apps.accounts.models import User
from apps.venues.forms import VenueForm
from apps.venues.models import Venue
from apps.venues.selectors import active_venues, displayable_venues, get_venue_by_code


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(username="admin", password="password")


@pytest.fixture
def international_admin(db):
    return User.objects.create_user(
        username="intl_admin",
        password="password",
        role=User.Role.INTERNATIONAL_ADMIN,
    )


@pytest.fixture
def viewer(db):
    return User.objects.create_user(
        username="viewer_user",
        password="password",
        role=User.Role.LEADERSHIP_VIEWER,
    )


@pytest.fixture
def sample_venue(db):
    return Venue.objects.create(
        code="ICH",
        name_uz="Xalqaro konferensiyalar zali",
        name_ru="Международный конференц-зал",
        name_en="International Conference Hall",
        capacity=300,
        working_start=time(8, 0),
        working_end=time(20, 0),
        is_active=True,
        display_enabled=True,
        sort_order=10,
    )


@pytest.mark.django_db
class TestVenueModelAndSelectors:
    def test_venue_str_and_localized_name(self, sample_venue):
        with translation.override("en"):
            assert str(sample_venue) == "ICH · International Conference Hall"
            assert sample_venue.localized_name == "International Conference Hall"

        with translation.override("uz"):
            assert str(sample_venue) == "ICH · Xalqaro konferensiyalar zali"
            assert sample_venue.localized_name == "Xalqaro konferensiyalar zali"

    def test_venue_code_uniqueness(self, sample_venue):
        with pytest.raises(IntegrityError):
            Venue.objects.create(
                code="ICH",
                name_uz="Duplicate",
                name_ru="Duplicate",
                name_en="Duplicate",
                capacity=50,
                working_start=time(9, 0),
                working_end=time(18, 0),
            )

    def test_venue_selectors(self, sample_venue):
        inactive_venue = Venue.objects.create(
            code="INACT",
            name_uz="Inactive",
            name_ru="Inactive",
            name_en="Inactive",
            capacity=10,
            working_start=time(9, 0),
            working_end=time(17, 0),
            is_active=False,
            display_enabled=False,
        )

        active = list(active_venues())
        assert sample_venue in active
        assert inactive_venue not in active

        displayable = list(displayable_venues())
        assert sample_venue in displayable
        assert inactive_venue not in displayable

        fetched = get_venue_by_code("ich")
        assert fetched == sample_venue
        assert get_venue_by_code("NONEXISTENT") is None


@pytest.mark.django_db
class TestVenueFormValidation:
    def test_valid_venue_form(self):
        data = {
            "code": "ssh",
            "name_uz": "Ilmiy seminarlar zali",
            "name_ru": "Зал научных семинаров",
            "name_en": "Scientific Seminar Hall",
            "capacity": 100,
            "working_start": "09:00",
            "working_end": "18:00",
            "is_active": True,
            "display_enabled": True,
            "sort_order": 5,
        }
        form = VenueForm(data=data)
        assert form.is_valid(), form.errors
        venue = form.save()
        assert venue.code == "SSH"

    def test_venue_form_invalid_working_hours(self):
        data = {
            "code": "ERR",
            "name_uz": "Error",
            "name_ru": "Error",
            "name_en": "Error",
            "capacity": 50,
            "working_start": "18:00",
            "working_end": "09:00",
        }
        form = VenueForm(data=data)
        assert not form.is_valid()
        assert "working_end" in form.errors


@pytest.mark.django_db
class TestVenueWebViews:
    def test_venue_list_view(self, client, viewer, sample_venue):
        client.force_login(viewer)
        response = client.get(reverse("venues:list"))
        assert response.status_code == status.HTTP_200_OK
        assert sample_venue.name_uz in response.content.decode()

    def test_venue_detail_view(self, client, viewer, sample_venue):
        client.force_login(viewer)
        response = client.get(reverse("venues:detail", kwargs={"pk": sample_venue.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert "ICH" in response.content.decode()

    def test_venue_create_view(self, client, international_admin):
        client.force_login(international_admin)
        data = {
            "code": "emr",
            "name_uz": "Rahbariyat majlislar xonasi",
            "name_ru": "Зал заседаний",
            "name_en": "Executive Meeting Room",
            "capacity": 24,
            "working_start": "08:00",
            "working_end": "20:00",
            "is_active": True,
            "display_enabled": True,
            "sort_order": 1,
        }
        response = client.post(reverse("venues:create"), data=data)
        assert response.status_code == status.HTTP_302_FOUND
        assert Venue.objects.filter(code="EMR").exists()

    def test_venue_delete_view(self, client, international_admin, sample_venue):
        client.force_login(international_admin)
        response = client.post(reverse("venues:delete", kwargs={"pk": sample_venue.pk}))
        assert response.status_code == status.HTTP_302_FOUND
        assert not Venue.objects.filter(pk=sample_venue.pk).exists()


@pytest.mark.django_db
class TestVenueAPIViews:
    def test_venue_api_list_and_detail(self, client, viewer, sample_venue):
        client.force_login(viewer)
        list_url = reverse("api-venue-list")
        response = client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

        detail_url = reverse("api-venue-detail", kwargs={"pk": sample_venue.pk})
        detail_res = client.get(detail_url)
        assert detail_res.status_code == status.HTTP_200_OK
        assert detail_res.data["code"] == "ICH"
