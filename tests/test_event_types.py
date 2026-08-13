import pytest
from django.db import IntegrityError
from django.urls import reverse
from django.utils import translation
from rest_framework import status

from apps.accounts.models import User
from apps.events.forms import EventTypeForm
from apps.events.models import EventType
from apps.events.selectors import active_event_types, get_event_type_by_code


@pytest.fixture
def international_admin(db):
    return User.objects.create_user(
        username="admin_user",
        password="password",
        role=User.Role.INTERNATIONAL_ADMIN,
    )


@pytest.fixture
def viewer(db):
    return User.objects.create_user(
        username="view_user",
        password="password",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )


@pytest.fixture
def sample_event_type(db):
    return EventType.objects.create(
        code="conference",
        name_uz="Konferensiya",
        name_ru="Конференция",
        name_en="Conference",
        description="International conference",
        color="#2563EB",
        icon="conference",
        is_active=True,
        requires_management_approval=False,
        allows_emergency_override=False,
        sort_order=10,
    )


@pytest.mark.django_db
class TestEventTypeModelAndSelectors:
    def test_event_type_str_and_localized(self, sample_event_type):
        with translation.override("en"):
            assert str(sample_event_type) == "Conference"
            assert sample_event_type.localized_name == "Conference"

        with translation.override("uz"):
            assert str(sample_event_type) == "Konferensiya"
            assert sample_event_type.localized_name == "Konferensiya"

    def test_event_type_code_uniqueness(self, sample_event_type):
        with pytest.raises(IntegrityError):
            EventType.objects.create(
                code="conference",
                name_uz="Duplicate",
                name_ru="Duplicate",
                name_en="Duplicate",
                color="#000000",
            )

    def test_event_type_selectors(self, sample_event_type):
        inactive = EventType.objects.create(
            code="inactive_type",
            name_uz="Inactive",
            name_ru="Inactive",
            name_en="Inactive",
            is_active=False,
        )

        actives = list(active_event_types())
        assert sample_event_type in actives
        assert inactive not in actives

        assert get_event_type_by_code("CONFERENCE") == sample_event_type
        assert get_event_type_by_code("UNKNOWN") is None


@pytest.mark.django_db
class TestEventTypeForm:
    def test_valid_event_type_form(self):
        data = {
            "code": "SYMPOSIUM",
            "name_uz": "Simpozium",
            "name_ru": "Симпозиум",
            "name_en": "Symposium",
            "description": "Scientific symposium",
            "color": "#8B5CF6",
            "icon": "symposium",
            "is_active": True,
            "requires_management_approval": True,
            "allows_emergency_override": False,
            "sort_order": 20,
        }
        form = EventTypeForm(data=data)
        assert form.is_valid(), form.errors
        obj = form.save()
        assert obj.code == "symposium"


@pytest.mark.django_db
class TestEventTypeWebViews:
    def test_event_type_list(self, client, viewer, sample_event_type):
        client.force_login(viewer)
        res = client.get(reverse("event-types:list"))
        assert res.status_code == status.HTTP_200_OK
        assert sample_event_type.name_uz in res.content.decode()

    def test_event_type_create(self, client, international_admin):
        client.force_login(international_admin)
        data = {
            "code": "seminar",
            "name_uz": "Seminar",
            "name_ru": "Семинар",
            "name_en": "Seminar",
            "color": "#06B6D4",
            "is_active": True,
            "sort_order": 30,
        }
        res = client.post(reverse("event-types:create"), data=data)
        assert res.status_code == status.HTTP_302_FOUND
        assert EventType.objects.filter(code="seminar").exists()

    def test_event_type_delete(self, client, international_admin, sample_event_type):
        client.force_login(international_admin)
        res = client.post(reverse("event-types:delete", kwargs={"pk": sample_event_type.pk}))
        assert res.status_code == status.HTTP_302_FOUND
        assert not EventType.objects.filter(pk=sample_event_type.pk).exists()


@pytest.mark.django_db
class TestEventTypeAPI:
    def test_event_type_api(self, client, viewer, sample_event_type):
        client.force_login(viewer)
        res = client.get(reverse("api-event-type-list"))
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) >= 1

        detail = client.get(reverse("api-event-type-detail", kwargs={"pk": sample_event_type.pk}))
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data["code"] == "conference"
