import pytest
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import User
from apps.venues.models import Venue


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(username="super", password="password")


@pytest.fixture
def intl_admin(db):
    return User.objects.create_user(
        username="intl",
        password="password",
        role=User.Role.INTERNATIONAL_ADMIN,
    )


@pytest.fixture
def resp_employee(db):
    return User.objects.create_user(
        username="resp",
        password="password",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )


@pytest.fixture
def mgmt_resp(db):
    return User.objects.create_user(
        username="mgmt",
        password="password",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )


@pytest.fixture
def lead_viewer(db):
    return User.objects.create_user(
        username="lead",
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
        working_start="08:00",
        working_end="20:00",
    )


@pytest.mark.django_db
class TestMasterDataRBACPermissions:
    def test_unauthenticated_user_denied_access(self, client, sample_venue):
        res = client.get(reverse("venues:list"))
        assert res.status_code == status.HTTP_302_FOUND
        assert res.url == f"{reverse('login')}?next={reverse('venues:list')}"

    def test_read_access_for_all_master_data_roles(
        self, client, resp_employee, mgmt_resp, lead_viewer, sample_venue
    ):
        for user in (resp_employee, mgmt_resp, lead_viewer):
            client.force_login(user)
            res = client.get(reverse("venues:list"))
            assert res.status_code == status.HTTP_200_OK

            res_detail = client.get(reverse("venues:detail", kwargs={"pk": sample_venue.pk}))
            assert res_detail.status_code == status.HTTP_200_OK

    def test_read_only_roles_denied_management_actions(self, client, resp_employee, sample_venue):
        client.force_login(resp_employee)
        create_res = client.get(reverse("venues:create"))
        assert create_res.status_code == status.HTTP_403_FORBIDDEN

        edit_res = client.get(reverse("venues:edit", kwargs={"pk": sample_venue.pk}))
        assert edit_res.status_code == status.HTTP_403_FORBIDDEN

        delete_res = client.post(reverse("venues:delete", kwargs={"pk": sample_venue.pk}))
        assert delete_res.status_code == status.HTTP_403_FORBIDDEN

    def test_intl_admin_and_superuser_allowed_management_actions(
        self, client, intl_admin, superuser, sample_venue
    ):
        for user in (intl_admin, superuser):
            client.force_login(user)
            create_res = client.get(reverse("venues:create"))
            assert create_res.status_code == status.HTTP_200_OK

            edit_res = client.get(reverse("venues:edit", kwargs={"pk": sample_venue.pk}))
            assert edit_res.status_code == status.HTTP_200_OK
