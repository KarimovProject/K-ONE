from datetime import time

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext

from apps.accounts.models import User
from apps.accounts.rbac import Capability, user_has_capability
from apps.events.forms import EventTypeForm
from apps.events.models import EventType
from apps.organizations.forms import OrganizationForm, SponsorForm
from apps.organizations.models import Organization, Sponsor
from apps.venues.forms import VenueForm
from apps.venues.models import Venue


def venue_form_data() -> dict:
    return {
        "code": "TEST",
        "name_uz": "Sinov xonasi",
        "name_ru": "Тестовое помещение",
        "name_en": "Test venue",
        "capacity": 10,
        "working_start": time(9),
        "working_end": time(18),
        "is_active": True,
        "display_enabled": True,
        "sort_order": 0,
    }


@pytest.mark.django_db
def test_master_data_management_is_limited_to_admin_roles(client):
    viewer = User.objects.create_user(
        username="read-only",
        password="password",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )
    manager = User.objects.create_user(
        username="master-data-manager",
        password="password",
        role=User.Role.INTERNATIONAL_ADMIN,
    )

    assert user_has_capability(viewer, Capability.VIEW_MASTER_DATA)
    assert not user_has_capability(viewer, Capability.MANAGE_MASTER_DATA)
    assert user_has_capability(manager, Capability.MANAGE_MASTER_DATA)

    client.force_login(viewer)
    assert client.get(reverse("venues:list")).status_code == 200
    assert client.get(reverse("venues:create")).status_code == 403


@pytest.mark.parametrize(
    ("language", "expected"),
    (("uz", "Xonalar"), ("ru", "Помещения"), ("en", "Venues")),
)
def test_master_data_navigation_is_localized(language, expected):
    with translation.override(language):
        assert gettext("Venues") == expected


@pytest.mark.django_db
def test_venue_rejects_non_positive_capacity():
    data = venue_form_data()
    data["capacity"] = 0
    form = VenueForm(data=data)
    assert not form.is_valid()
    assert "capacity" in form.errors


@pytest.mark.django_db
def test_upload_rejects_spoofed_image_signature():
    upload = SimpleUploadedFile("logo.png", b"not an image", content_type="image/png")
    form = SponsorForm(data={"name": "Example", "is_active": True}, files={"logo": upload})
    assert not form.is_valid()
    assert "logo" in form.errors


@pytest.mark.django_db
def test_upload_rejects_oversized_image():
    upload = SimpleUploadedFile(
        "logo.png",
        b"\x89PNG\r\n\x1a\n" + b"0" * (5 * 1024 * 1024),
        content_type="image/png",
    )
    form = OrganizationForm(data={"name": "Example", "is_active": True}, files={"logo": upload})
    assert not form.is_valid()
    assert "logo" in form.errors


@pytest.mark.django_db
def test_valid_png_signature_is_accepted():
    upload = SimpleUploadedFile(
        "venue.png",
        b"\x89PNG\r\n\x1a\n" + b"valid-test-payload",
        content_type="image/png",
    )
    form = VenueForm(data=venue_form_data(), files={"photo": upload})
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_upload_rejects_unsupported_extension():
    upload = SimpleUploadedFile("logo.gif", b"GIF89a", content_type="image/gif")
    form = SponsorForm(data={"name": "Example", "is_active": True}, files={"logo": upload})
    assert not form.is_valid()
    assert "logo" in form.errors


@pytest.mark.django_db
def test_event_type_rejects_invalid_color():
    form = EventTypeForm(
        data={
            "code": "briefing",
            "name_uz": "Brifing",
            "name_ru": "Брифинг",
            "name_en": "Briefing",
            "color": "blue",
            "sort_order": 0,
        }
    )
    assert not form.is_valid()
    assert "color" in form.errors


@pytest.mark.django_db
def test_localized_master_data_page_renders_ru(client, leadership_viewer):
    client.force_login(leadership_viewer)
    response = client.get(reverse("venues:list"), HTTP_ACCEPT_LANGUAGE="ru")
    assert response.status_code == 200
    assert "Помещения" in response.content.decode()


@pytest.mark.django_db
def test_admin_can_update_and_delete_each_master_data_resource(client, master_data_admin):
    venue = Venue.objects.create(**venue_form_data())
    event_type = EventType.objects.create(
        code="conference",
        name_uz="Konferensiya",
        name_ru="Конференция",
        name_en="Conference",
    )
    organization = Organization.objects.create(name="Original organization")
    sponsor = Sponsor.objects.create(name="Original sponsor")
    client.force_login(master_data_admin)

    venue_update = {**venue_form_data(), "name_en": "Updated venue"}
    venue_response = client.post(
        reverse("venues:edit", kwargs={"pk": venue.pk}),
        venue_update,
    )
    assert venue_response.status_code == 302
    assert client.post(
        reverse("event-types:edit", kwargs={"pk": event_type.pk}),
        {
            "code": "conference",
            "name_uz": "Konferensiya",
            "name_ru": "Конференция",
            "name_en": "Updated conference",
            "color": "#2563EB",
            "sort_order": 0,
            "is_active": True,
        },
    ).status_code == 302
    assert client.post(
        reverse("organizations:edit", kwargs={"pk": organization.pk}),
        {
            "name": "Updated organization",
            "organization_type": Organization.Type.LOCAL,
            "is_active": True,
        },
    ).status_code == 302
    assert client.post(
        reverse("sponsors:edit", kwargs={"pk": sponsor.pk}),
        {"name": "Updated sponsor", "is_active": True},
    ).status_code == 302

    venue.refresh_from_db()
    event_type.refresh_from_db()
    organization.refresh_from_db()
    sponsor.refresh_from_db()
    assert venue.name_en == "Updated venue"
    assert event_type.name_en == "Updated conference"
    assert organization.name == "Updated organization"
    assert sponsor.name == "Updated sponsor"

    for namespace, instance in (
        ("venues", venue),
        ("event-types", event_type),
        ("organizations", organization),
        ("sponsors", sponsor),
    ):
        response = client.post(reverse(f"{namespace}:delete", kwargs={"pk": instance.pk}))
        assert response.status_code == 302
        assert not type(instance).objects.filter(pk=instance.pk).exists()
