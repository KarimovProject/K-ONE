from datetime import date, time

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.events.models import Event, EventType
from apps.venues.models import Venue


@pytest.fixture
def rbac_setup(db):
    user_model = get_user_model()
    admin = user_model.objects.create_user(
        username="adm",
        password="password",
        role=user_model.Role.INTERNATIONAL_ADMIN,
    )
    resp = user_model.objects.create_user(
        username="resp",
        password="password",
        role=user_model.Role.RESPONSIBLE_EMPLOYEE,
    )
    other = user_model.objects.create_user(
        username="other",
        password="password",
        role=user_model.Role.RESPONSIBLE_EMPLOYEE,
    )
    viewer = user_model.objects.create_user(
        username="view",
        password="password",
        role=user_model.Role.LEADERSHIP_VIEWER,
    )

    venue = Venue.objects.create(
        code="ICH",
        name_uz="H",
        name_ru="H",
        name_en="H",
        capacity=100,
        working_start=time(8, 0),
        working_end=time(20, 0),
    )
    etype = EventType.objects.create(code="c", name_uz="C", name_ru="C", name_en="C")

    event = Event.objects.create(
        title="Resp Employee Event",
        event_type=etype,
        venue=venue,
        planned_date=date(2026, 12, 1),
        start_time=time(10, 0),
        end_time=time(12, 0),
        responsible_employee=resp,
        management_responsible=admin,
        status=Event.Status.PLANNED,
    )

    return {"admin": admin, "resp": resp, "other": other, "viewer": viewer, "event": event}


@pytest.mark.django_db
class TestEventsRBAC:
    def test_viewer_can_read_events_list_and_detail(self, client, rbac_setup):
        client.force_login(rbac_setup["viewer"])
        res_list = client.get(reverse("events:list"))
        assert res_list.status_code == status.HTTP_200_OK

        res_detail = client.get(reverse("events:detail", kwargs={"pk": rbac_setup["event"].pk}))
        assert res_detail.status_code == status.HTTP_200_OK

    def test_viewer_denied_write_routes(self, client, rbac_setup):
        client.force_login(rbac_setup["viewer"])
        res_edit = client.get(reverse("events:edit", kwargs={"pk": rbac_setup["event"].pk}))
        assert res_edit.status_code == status.HTTP_403_FORBIDDEN

        res_cancel = client.get(reverse("events:cancel", kwargs={"pk": rbac_setup["event"].pk}))
        assert res_cancel.status_code == status.HTTP_403_FORBIDDEN

    def test_responsible_employee_can_edit_own_event_but_denied_others(self, client, rbac_setup):
        # Own event edit allowed
        client.force_login(rbac_setup["resp"])
        res_edit_own = client.get(reverse("events:edit", kwargs={"pk": rbac_setup["event"].pk}))
        assert res_edit_own.status_code == status.HTTP_200_OK

        # Other employee denied edit
        client.force_login(rbac_setup["other"])
        res_edit_other = client.get(reverse("events:edit", kwargs={"pk": rbac_setup["event"].pk}))
        assert res_edit_other.status_code == status.HTTP_403_FORBIDDEN
