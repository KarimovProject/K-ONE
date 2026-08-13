import pytest
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import User
from apps.organizations.forms import SponsorForm
from apps.organizations.models import Sponsor
from apps.organizations.selectors import active_sponsors


@pytest.fixture
def intl_admin(db):
    return User.objects.create_user(
        username="sponsor_admin",
        password="password",
        role=User.Role.INTERNATIONAL_ADMIN,
    )


@pytest.fixture
def viewer(db):
    return User.objects.create_user(
        username="sponsor_viewer",
        password="password",
        role=User.Role.RECEPTION_OPERATOR,
    )


@pytest.fixture
def sample_sponsor(db):
    return Sponsor.objects.create(
        name="Global Education Fund",
        description="Providing technology grants for international seminars.",
        website="https://globaled.org",
        contact_person="Jane Doe",
        phone="+12025550199",
        email="grants@globaled.org",
        is_active=True,
    )


@pytest.mark.django_db
class TestSponsorModelAndSelectors:
    def test_sponsor_str(self, sample_sponsor):
        assert str(sample_sponsor) == "Global Education Fund"

    def test_active_sponsors_selector(self, sample_sponsor):
        inactive = Sponsor.objects.create(
            name="Past Sponsor",
            is_active=False,
        )

        actives = list(active_sponsors())
        assert sample_sponsor in actives
        assert inactive not in actives


@pytest.mark.django_db
class TestSponsorForm:
    def test_valid_sponsor_form(self):
        data = {
            "name": "Innovation Tech Group",
            "description": "Sponsoring IT equipment",
            "website": "https://innotech.io",
            "contact_person": "John Smith",
            "email": "contact@innotech.io",
            "is_active": True,
        }
        form = SponsorForm(data=data)
        assert form.is_valid(), form.errors
        sponsor = form.save()
        assert sponsor.name == "Innovation Tech Group"


@pytest.mark.django_db
class TestSponsorWebViews:
    def test_sponsor_list(self, client, viewer, sample_sponsor):
        client.force_login(viewer)
        res = client.get(reverse("sponsors:list"))
        assert res.status_code == status.HTTP_200_OK
        assert sample_sponsor.name in res.content.decode()

    def test_sponsor_create(self, client, intl_admin):
        client.force_login(intl_admin)
        data = {
            "name": "Digital Future Foundation",
            "website": "https://digitalfuture.org",
            "is_active": True,
        }
        res = client.post(reverse("sponsors:create"), data=data)
        assert res.status_code == status.HTTP_302_FOUND
        assert Sponsor.objects.filter(name="Digital Future Foundation").exists()

    def test_sponsor_delete(self, client, intl_admin, sample_sponsor):
        client.force_login(intl_admin)
        res = client.post(reverse("sponsors:delete", kwargs={"pk": sample_sponsor.pk}))
        assert res.status_code == status.HTTP_302_FOUND
        assert not Sponsor.objects.filter(pk=sample_sponsor.pk).exists()


@pytest.mark.django_db
class TestSponsorAPI:
    def test_sponsor_api(self, client, viewer, sample_sponsor):
        client.force_login(viewer)
        res = client.get(reverse("api-sponsor-list"))
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) >= 1

        detail = client.get(reverse("api-sponsor-detail", kwargs={"pk": sample_sponsor.pk}))
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data["name"] == sample_sponsor.name
