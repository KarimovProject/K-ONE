import pytest

from apps.accounts.models import User
from apps.accounts.selectors import (
    content_managers,
    international_admins,
    leadership_viewers,
    management_responsible_users,
    responsible_employees,
    selectable_staff,
    staff_choices,
)


@pytest.fixture
def staff_users(db):
    u1 = User.objects.create_user(
        username="resp_emp",
        first_name="Jasur",
        last_name="Karimov",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
        is_active=True,
    )
    u2 = User.objects.create_user(
        username="mgmt_resp",
        first_name="Bekzod",
        last_name="Rakhimov",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
        is_active=True,
    )
    u3 = User.objects.create_user(
        username="intl_adm",
        first_name="Dilshod",
        last_name="Tursunov",
        role=User.Role.INTERNATIONAL_ADMIN,
        is_active=True,
    )
    u4 = User.objects.create_user(
        username="lead_view",
        first_name="Aziz",
        last_name="Kamilov",
        role=User.Role.LEADERSHIP_VIEWER,
        is_active=True,
    )
    u5 = User.objects.create_user(
        username="cnt_mgr",
        first_name="Madina",
        last_name="Saidova",
        role=User.Role.CONTENT_MANAGER,
        is_active=True,
    )
    u_inactive = User.objects.create_user(
        username="inactive_emp",
        first_name="Old",
        last_name="Staff",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
        is_active=False,
    )
    return {
        "responsible": u1,
        "management": u2,
        "intl": u3,
        "leadership": u4,
        "content": u5,
        "inactive": u_inactive,
    }


@pytest.mark.django_db
class TestResponsibleStaffSelectors:
    def test_selectable_staff_excludes_inactive(self, staff_users):
        staff = list(selectable_staff())
        assert staff_users["responsible"] in staff
        assert staff_users["inactive"] not in staff

    def test_role_specific_selectors(self, staff_users):
        resps = list(responsible_employees())
        assert staff_users["responsible"] in resps
        assert len(resps) == 1

        mgmts = list(management_responsible_users())
        assert staff_users["management"] in mgmts
        assert len(mgmts) == 1

        intls = list(international_admins())
        assert staff_users["intl"] in intls
        assert len(intls) == 1

        leads = list(leadership_viewers())
        assert staff_users["leadership"] in leads
        assert len(leads) == 1

        cnts = list(content_managers())
        assert staff_users["content"] in cnts
        assert len(cnts) == 1

    def test_staff_choices_helper(self, staff_users):
        choices = staff_choices()
        assert len(choices) == 5  # 5 active staff
        usernames_in_choices = [c[1] for c in choices]
        assert "Jasur Karimov" in usernames_in_choices
