import pytest
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import User
from apps.organizations.forms import OrganizationForm
from apps.organizations.models import Organization
from apps.organizations.selectors import active_organizations, organizations_by_type


@pytest.fixture
def intl_admin(db):
    return User.objects.create_user(
        username="org_admin",
        password="password",
        role=User.Role.INTERNATIONAL_ADMIN,
    )


@pytest.fixture
def viewer(db):
    return User.objects.create_user(
        username="org_viewer",
        password="password",
        role=User.Role.LEADERSHIP_VIEWER,
    )


@pytest.fixture
def local_org(db):
    return Organization.objects.create(
        name="Ministry of Higher Education",
        short_name="MOHESD",
        organization_type=Organization.Type.LOCAL,
        country="Uzbekistan",
        city="Tashkent",
        address="100000, Tashkent, St. Amir Temur 1",
        website="https://edu.uz",
        email="info@edu.uz",
        phone="+998712000000",
        contact_person="Alisher Navoiy",
        is_active=True,
    )


@pytest.fixture
def foreign_org(db):
    return Organization.objects.create(
        name="United Nations Development Programme",
        short_name="UNDP",
        organization_type=Organization.Type.FOREIGN,
        country="United States",
        city="New York",
        website="https://undp.org",
        email="contact@undp.org",
        is_active=True,
    )


@pytest.mark.django_db
class TestOrganizationModelAndSelectors:
    def test_organization_str(self, local_org):
        assert str(local_org) == "Ministry of Higher Education"

    def test_organization_selectors(self, local_org, foreign_org):
        inactive_org = Organization.objects.create(
            name="Archived Partner",
            organization_type=Organization.Type.PARTNER,
            is_active=False,
        )

        actives = list(active_organizations())
        assert local_org in actives
        assert foreign_org in actives
        assert inactive_org not in actives

        foreigns = list(organizations_by_type(Organization.Type.FOREIGN))
        assert foreign_org in foreigns
        assert local_org not in foreigns


@pytest.mark.django_db
class TestOrganizationForm:
    def test_valid_organization_form(self):
        data = {
            "name": "UNESCO Tashkent",
            "short_name": "UNESCO",
            "organization_type": Organization.Type.PARTNER,
            "country": "Uzbekistan",
            "city": "Tashkent",
            "website": "https://unesco.org",
            "email": "tashkent@unesco.org",
            "is_active": True,
        }
        form = OrganizationForm(data=data)
        assert form.is_valid(), form.errors
        org = form.save()
        assert org.name == "UNESCO Tashkent"

    def test_invalid_website_url(self):
        data = {
            "name": "Bad Web Org",
            "website": "invalid-url",
        }
        form = OrganizationForm(data=data)
        assert not form.is_valid()
        assert "website" in form.errors


@pytest.mark.django_db
class TestOrganizationWebViews:
    def test_organization_list_filtering(self, client, viewer, local_org, foreign_org):
        client.force_login(viewer)
        res = client.get(reverse("organizations:list"))
        assert res.status_code == status.HTTP_200_OK
        assert local_org.name in res.content.decode()

        res_foreign = client.get(reverse("organizations:list") + "?type=foreign")
        assert res_foreign.status_code == status.HTTP_200_OK
        content = res_foreign.content.decode()
        assert foreign_org.name in content
        assert local_org.name not in content

    def test_organization_create(self, client, intl_admin):
        client.force_login(intl_admin)
        data = {
            "name": "World Bank",
            "short_name": "WB",
            "organization_type": Organization.Type.FOREIGN,
            "country": "United States",
            "city": "Washington",
            "website": "https://worldbank.org",
            "is_active": True,
        }
        res = client.post(reverse("organizations:create"), data=data)
        assert res.status_code == status.HTTP_302_FOUND
        assert Organization.objects.filter(name="World Bank").exists()


@pytest.mark.django_db
class TestOrganizationAPI:
    def test_organization_api_list_and_detail(self, client, viewer, local_org, foreign_org):
        client.force_login(viewer)
        res = client.get(reverse("api-organization-list"))
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) >= 2

        res_filtered = client.get(reverse("api-organization-list") + "?type=foreign")
        assert res_filtered.status_code == status.HTTP_200_OK
        assert len(res_filtered.data) == 1
        assert res_filtered.data[0]["name"] == foreign_org.name

        detail = client.get(reverse("api-organization-detail", kwargs={"pk": local_org.pk}))
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data["name"] == local_org.name
