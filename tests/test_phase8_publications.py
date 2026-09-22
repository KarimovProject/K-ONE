import io
from datetime import time, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.events.models import Event, EventType
from apps.organizations.models import Sponsor
from apps.publications.adapters import (
    InstagramAdapter,
    PublicationDisabledError,
)
from apps.publications.banner import SIZES, generate_banner
from apps.publications.models import Publication
from apps.publications.policies import (
    can_approve,
    can_prepare,
    can_publish,
    ensure_event_publishable,
)
from apps.publications.rendering import render_caption
from apps.publications.services import (
    approve_publication,
    prepare_publication,
    publish_publication,
    schedule_publication,
)
from apps.publications.tasks import dispatch_scheduled_publications
from apps.publications.testing import (
    FakeInstagramTransport,
    FakeTelegramChannelTransport,
)
from apps.venues.models import Venue

pytestmark = pytest.mark.django_db


@pytest.fixture
def publication_data(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    settings.IEMS_BASE_URL = "http://iems.test"
    users = get_user_model()
    admin = users.objects.create_user(
        "p8_admin", role=users.Role.INTERNATIONAL_ADMIN, password="test-password"
    )
    content = users.objects.create_user(
        "p8_content", role=users.Role.CONTENT_MANAGER, password="test-password"
    )
    manager = users.objects.create_user(
        "p8_manager", role=users.Role.MANAGEMENT_RESPONSIBLE, password="test-password"
    )
    responsible = users.objects.create_user(
        "p8_responsible", role=users.Role.RESPONSIBLE_EMPLOYEE, password="test-password"
    )
    viewer = users.objects.create_user(
        "p8_viewer", role=users.Role.LEADERSHIP_VIEWER, password="test-password"
    )
    venue = Venue.objects.create(
        code="P8-HALL",
        name_uz="Xalqaro zal",
        name_ru="Международный зал",
        name_en="International Hall",
        capacity=200,
        working_start=time(8),
        working_end=time(20),
    )
    event_type = EventType.objects.create(
        code="p8-forum", name_uz="Forum", name_ru="Форум", name_en="Forum"
    )
    event = Event.objects.create(
        title="International Medical Cooperation Forum",
        description="Public event description",
        event_type=event_type,
        venue=venue,
        planned_date=(timezone.localtime() + timedelta(days=5)).date(),
        start_time=time(10),
        end_time=time(13),
        responsible_employee=responsible,
        management_responsible=manager,
        created_by=admin,
        status=Event.Status.APPROVED,
        zoom_url="https://zoom.example.test/meeting",
        registration_url="https://register.example.test/event",
        notes="PRIVATE INTERNAL NOTES",
        emergency_justification="PRIVATE JUSTIFICATION",
    )
    return admin, content, manager, responsible, viewer, event


def make_publication(data, platform=Publication.Platform.TELEGRAM_CHANNEL, language="uz"):
    admin, _, _, _, _, event = data
    return Publication.objects.create(
        event=event,
        platform=platform,
        language=language,
        headline=event.title,
        short_description="Official announcement text",
        caption="Welcome to the international forum.",
        created_by=admin,
    )


@pytest.mark.parametrize(
    ("status", "allowed"),
    [
        (Event.Status.APPROVED, True),
        (Event.Status.PLANNED, True),
        (Event.Status.DRAFT, False),
        (Event.Status.REJECTED, False),
        (Event.Status.CANCELLED, False),
        (Event.Status.DISPLACED, False),
    ],
)
def test_event_publication_eligibility(publication_data, status, allowed):
    event = publication_data[-1]
    event.status = status
    event.save(update_fields=["status"])
    if allowed:
        ensure_event_publishable(event)
    else:
        with pytest.raises(ValidationError):
            ensure_event_publishable(event)


def test_publication_lifecycle_and_audit(publication_data):
    admin, _, manager, _, _, _ = publication_data
    publication = make_publication(publication_data)
    prepare_publication(publication, admin)
    assert publication.status == Publication.Status.READY
    assert publication.banner
    approve_publication(publication, manager)
    assert publication.status == Publication.Status.APPROVED
    schedule_publication(publication, admin, timezone.now() + timedelta(hours=1))
    assert publication.status == Publication.Status.SCHEDULED


@pytest.mark.parametrize("variant", list(SIZES))
def test_banner_all_sizes_and_long_title(publication_data, variant):
    publication = make_publication(publication_data)
    publication.headline = (
        "International Multidisciplinary Medical Cooperation and Innovation Symposium"
    )
    content = generate_banner(publication, variant)
    image = Image.open(io.BytesIO(content))
    assert image.size == SIZES[variant]
    assert image.format == "PNG"


def test_banner_handles_missing_and_present_sponsor_logos(publication_data):
    publication = make_publication(publication_data)
    sponsor = Sponsor.objects.create(name="Safe Sponsor")
    logo = Image.new("RGBA", (300, 80), "#10b981")
    buffer = io.BytesIO()
    logo.save(buffer, "PNG")
    sponsor.logo.save("p8-logo.png", ContentFile(buffer.getvalue()), save=True)
    publication.event.sponsors.add(sponsor)
    assert len(generate_banner(publication)) > 10_000


@pytest.mark.parametrize("language", ["uz", "ru", "en"])
def test_platform_specific_localized_captions(publication_data, language):
    telegram = make_publication(publication_data, language=language)
    tg_text = render_caption(telegram)
    assert "https://zoom.example.test" in tg_text
    instagram = make_publication(publication_data, Publication.Platform.INSTAGRAM, language)
    ig_text = render_caption(instagram)
    assert "https://zoom.example.test" not in ig_text
    assert "PRIVATE" not in tg_text + ig_text


def test_fake_telegram_publish_is_idempotent(publication_data):
    admin, _, manager, _, _, _ = publication_data
    publication = make_publication(publication_data)
    prepare_publication(publication, admin)
    approve_publication(publication, manager)
    fake = FakeTelegramChannelTransport()
    publish_publication(publication.pk, adapter=fake)
    publish_publication(publication.pk, adapter=fake)
    publication.refresh_from_db()
    assert publication.status == Publication.Status.PUBLISHED
    assert publication.external_post_id == "tg-test-1001"
    assert len(fake.calls) == 1


def test_fake_instagram_publish_sequence_and_idempotency(publication_data):
    admin, _, manager, _, _, _ = publication_data
    publication = make_publication(publication_data, Publication.Platform.INSTAGRAM, "en")
    prepare_publication(publication, admin)
    approve_publication(publication, manager)
    fake = FakeInstagramTransport()
    publish_publication(publication.pk, adapter=fake)
    publish_publication(publication.pk, adapter=fake)
    publication.refresh_from_db()
    assert publication.external_container_id == "ig-container-2001"
    assert len(fake.calls) == 1


class FakeGraphTransport:
    def __init__(self):
        self.calls = []

    def post(self, url, payload, timeout):
        self.calls.append((url, payload))
        return {"id": "container" if url.endswith("/media") else "post"}


@override_settings(
    INSTAGRAM_ENABLED=True,
    INSTAGRAM_BUSINESS_ACCOUNT_ID="test-account",
    META_ACCESS_TOKEN="test-token",
)
def test_official_instagram_container_then_publish():
    transport = FakeGraphTransport()
    result = InstagramAdapter(transport).publish("https://example.test/image.png", "caption")
    assert transport.calls[0][0].endswith("/media")
    assert transport.calls[1][0].endswith("/media_publish")
    assert result.container_id == "container" and result.post_id == "post"


@override_settings(INSTAGRAM_ENABLED=False, META_ACCESS_TOKEN="")
def test_instagram_disabled_fails_closed():
    with pytest.raises(PublicationDisabledError):
        InstagramAdapter(FakeGraphTransport()).publish("https://example.test/a.png", "x")


def test_due_dispatcher_enqueues_without_changing_published_state(publication_data, monkeypatch):
    publication = make_publication(publication_data)
    publication.status = Publication.Status.SCHEDULED
    publication.scheduled_for = timezone.now() - timedelta(minutes=1)
    publication.save()
    calls = []
    monkeypatch.setattr(
        "apps.publications.tasks.publish_publication_task.delay", lambda pk: calls.append(pk)
    )
    assert dispatch_scheduled_publications() == 1
    assert calls == [str(publication.pk)]


def test_rbac_policy(publication_data):
    admin, content, manager, responsible, viewer, event = publication_data
    assert can_prepare(admin) and can_prepare(content) and can_prepare(responsible, event)
    assert not can_prepare(viewer, event)
    assert can_approve(manager) and not can_approve(content)
    assert can_publish(admin) and can_publish(content) and not can_publish(manager)


def test_policies_reject_anonymous_user_instead_of_crashing():
    # Regression: `user.is_superuser or user.role in (...)` crashed with
    # AttributeError for AnonymousUser (no `.role`) instead of just
    # returning False, because `is_superuser` is False so `or` fell
    # through to the unguarded `.role` access.
    from django.contrib.auth.models import AnonymousUser

    anon = AnonymousUser()
    assert can_prepare(anon) is False
    assert can_approve(anon) is False
    assert can_publish(anon) is False


def test_create_and_edit_views_redirect_anonymous_instead_of_crashing(client, publication_data):
    _, _, _, _, _, event = publication_data
    publication = make_publication(publication_data)
    create_response = client.get(reverse("publications:create", args=[event.pk]))
    assert create_response.status_code == 302
    assert create_response.url.startswith(reverse("login"))
    edit_response = client.get(reverse("publications:edit", args=[publication.pk]))
    assert edit_response.status_code == 302
    assert edit_response.url.startswith(reverse("login"))


def test_ui_security_and_draft_event_block(client, publication_data, settings):
    admin, _, _, _, viewer, event = publication_data
    settings.TELEGRAM_BOT_TOKEN = "must-not-appear"
    settings.META_ACCESS_TOKEN = "must-not-appear-meta"
    publication = make_publication(publication_data)
    client.force_login(viewer)
    response = client.get(reverse("publications:detail", args=[publication.pk]))
    assert response.status_code == 200
    assert b"must-not-appear" not in response.content
    assert client.post(reverse("publications:publish", args=[publication.pk])).status_code == 403
    event.status = Event.Status.DRAFT
    event.save(update_fields=["status"])
    client.force_login(admin)
    assert client.get(reverse("publications:create", args=[event.pk])).status_code == 404


@override_settings(
    TELEGRAM_CHANNEL_ENABLED=False,
    TELEGRAM_CHANNEL_CHAT_ID="",
    TELEGRAM_BOT_ENABLED=False,
)
def test_disabled_ui_publish_fails_closed_with_tracked_error(client, publication_data):
    admin, _, manager, _, _, _ = publication_data
    publication = make_publication(publication_data)
    prepare_publication(publication, admin)
    approve_publication(publication, manager)
    client.force_login(admin)
    response = client.post(reverse("publications:publish", args=[publication.pk]))
    assert response.status_code == 302
    publication.refresh_from_db()
    assert publication.status == Publication.Status.FAILED
    assert publication.error_code == "disabled"


@pytest.mark.parametrize(
    ("language", "expected"),
    [("uz", "Nashrlar"), ("ru", "Публикации"), ("en", "Publications")],
)
def test_publication_ui_localization(client, publication_data, language, expected):
    admin = publication_data[0]
    client.force_login(admin)
    client.post(reverse("set_language"), {"language": language, "next": "/publications/"})
    response = client.get(reverse("publications:list"))
    assert expected in response.content.decode()
