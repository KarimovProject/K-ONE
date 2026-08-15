from datetime import time

import pytest
from django.contrib import admin
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.attendance.admin import EventAttendanceAdmin
from apps.attendance.models import EventAttendance
from apps.audit.admin import AuditEventLogAdmin
from apps.audit.models import AuditEventLog
from apps.events.admin import EventAdmin
from apps.events.models import Event, EventType, Speaker
from apps.organizations.models import Organization, Sponsor
from apps.publications.admin import PublicationAdmin
from apps.publications.models import Publication
from apps.venues.models import Venue


@pytest.fixture
def phase11_event_data(db):
    owner = User.objects.create_user(username="p11-owner", password="test-only")
    manager = User.objects.create_user(
        username="p11-manager",
        password="test-only",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )
    venue = Venue.objects.create(
        code="P11",
        name_uz="P11 zali",
        name_ru="Зал P11",
        name_en="P11 Hall",
        capacity=50,
        working_start=time(8),
        working_end=time(20),
    )
    event_type = EventType.objects.create(
        code="p11-meeting", name_uz="Uchrashuv", name_ru="Встреча", name_en="Meeting"
    )

    def create(title, visibility, status=Event.Status.PLANNED):
        return Event.objects.create(
            title=title,
            event_type=event_type,
            venue=venue,
            planned_date=timezone.localdate(),
            start_time=time(10),
            end_time=time(11),
            responsible_employee=owner,
            management_responsible=manager,
            status=status,
            display_visibility=visibility,
            notes="SECRET-NOTE",
            emergency_justification="SECRET-JUSTIFICATION",
        )

    return create, owner, manager, venue, event_type


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    ("public-dashboard", "public-calendar", "public-live-venues", "public-dashboard-api"),
)
def test_public_surfaces_are_anonymous(client, url):
    assert client.get(reverse(url)).status_code == 200


@pytest.mark.django_db
def test_public_api_enforces_event_visibility(client, phase11_event_data):
    create, *_ = phase11_event_data
    create("Public conference", Event.DisplayVisibility.FULL)
    create("Private board title", Event.DisplayVisibility.GENERIC)
    create("Hidden diplomatic title", Event.DisplayVisibility.HIDDEN)
    content = client.get(reverse("public-dashboard-api")).content.decode()
    assert "Public conference" in content
    assert "Private board title" not in content
    assert "Hidden diplomatic title" not in content
    assert "SECRET-NOTE" not in content
    assert "SECRET-JUSTIFICATION" not in content
    assert "responsible_employee" not in content
    assert "public_token" not in content


@pytest.mark.django_db
def test_draft_event_is_not_public(client, phase11_event_data):
    create, *_ = phase11_event_data
    create("Draft secret", Event.DisplayVisibility.FULL, Event.Status.DRAFT)
    assert b"Draft secret" not in client.get(reverse("public-dashboard-api")).content


@pytest.mark.django_db
def test_workspace_and_profile_require_login(client):
    assert client.get(reverse("dashboard")).status_code == 302
    assert client.get(reverse("profile")).status_code == 302


@pytest.mark.django_db
def test_profile_does_not_accept_role_changes(client, user):
    client.force_login(user)
    response = client.post(
        reverse("profile"),
        {
            "first_name": "Updated",
            "last_name": "User",
            "email": "updated@example.test",
            "preferred_language": "en",
            "role": User.Role.SUPER_ADMIN,
        },
    )
    user.refresh_from_db()
    assert response.status_code == 302
    assert user.first_name == "Updated"
    assert user.role == User.Role.RESPONSIBLE_EMPLOYEE


@pytest.mark.django_db
def test_sidebar_is_role_aware(client, user, master_data_admin):
    client.force_login(user)
    normal = client.get(reverse("dashboard")).content.decode()
    assert reverse("venues:list") not in normal
    client.force_login(master_data_admin)
    admin_content = client.get(reverse("dashboard")).content.decode()
    assert reverse("venues:list") in admin_content


def test_critical_models_are_registered_in_admin():
    for model in (Event, EventAttendance, AuditEventLog, Publication):
        assert model in admin.site._registry


@pytest.mark.django_db
def test_event_delete_governance(rf, phase11_event_data):
    create, *_ = phase11_event_data
    draft = create("Disposable draft", Event.DisplayVisibility.FULL, Event.Status.DRAFT)
    planned = create("Protected planned", Event.DisplayVisibility.FULL, Event.Status.PLANNED)
    request = rf.get("/admin/")
    request.user = User.objects.create_superuser(username="p11-root", password="test-only")
    model_admin = EventAdmin(Event, admin.site)
    assert model_admin.has_delete_permission(request, draft)
    assert not model_admin.has_delete_permission(request, planned)
    assert "delete_selected" not in model_admin.get_actions(request)


@pytest.mark.django_db
def test_history_models_are_immutable_in_admin(rf):
    request = rf.get("/admin/")
    request.user = User.objects.create_superuser(username="history-root", password="test-only")
    for model_admin in (
        EventAttendanceAdmin(EventAttendance, admin.site),
        AuditEventLogAdmin(AuditEventLog, admin.site),
    ):
        assert not model_admin.has_add_permission(request)
        assert not model_admin.has_change_permission(request)
        assert not model_admin.has_delete_permission(request)


@pytest.mark.django_db
def test_publication_delete_governance(rf, phase11_event_data):
    create, owner, *_ = phase11_event_data
    event = create("Publication event", Event.DisplayVisibility.FULL)
    draft = Publication.objects.create(
        event=event,
        platform=Publication.Platform.TELEGRAM_CHANNEL,
        headline="Draft",
        created_by=owner,
    )
    published = Publication.objects.create(
        event=event,
        platform=Publication.Platform.INSTAGRAM,
        headline="Published",
        status=Publication.Status.PUBLISHED,
        created_by=owner,
    )
    request = rf.get("/admin/")
    request.user = User.objects.create_superuser(username="publication-root", password="test-only")
    model_admin = PublicationAdmin(Publication, admin.site)
    assert model_admin.has_delete_permission(request, draft)
    assert not model_admin.has_delete_permission(request, published)


@pytest.mark.django_db
def test_public_dashboard_query_count_is_bounded(
    client, phase11_event_data, django_assert_max_num_queries
):
    create, *_ = phase11_event_data
    for index in range(6):
        create(f"Public event {index}", Event.DisplayVisibility.FULL)
    with django_assert_max_num_queries(8):
        response = client.get(reverse("public-dashboard-api"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_safe_venue_admin_crud_and_delete(client):
    root = User.objects.create_superuser(username="venue-root", password="test-only")
    client.force_login(root)
    add_url = reverse("admin:venues_venue_add")
    response = client.post(
        add_url,
        {
            "code": "CRUD",
            "name_uz": "CRUD zal",
            "name_ru": "CRUD зал",
            "name_en": "CRUD hall",
            "capacity": 40,
            "working_start": "08:00",
            "working_end": "18:00",
            "is_active": "on",
            "display_enabled": "on",
            "sort_order": 90,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    venue = Venue.objects.get(code="CRUD")
    change_url = reverse("admin:venues_venue_change", args=(venue.pk,))
    response = client.post(
        change_url,
        {
            "code": "CRUD",
            "name_uz": "Yangilangan zal",
            "name_ru": "CRUD зал",
            "name_en": "CRUD hall",
            "capacity": 40,
            "working_start": "08:00",
            "working_end": "18:00",
            "is_active": "on",
            "display_enabled": "on",
            "sort_order": 90,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    venue.refresh_from_db()
    assert venue.name_uz == "Yangilangan zal"
    delete_url = reverse("admin:venues_venue_delete", args=(venue.pk,))
    assert client.post(delete_url, {"post": "yes"}).status_code == 302
    assert not Venue.objects.filter(pk=venue.pk).exists()


@pytest.mark.django_db
def test_referenced_venue_admin_delete_is_protected(client, phase11_event_data):
    _, _, _, venue, _ = phase11_event_data
    root = User.objects.create_superuser(username="protected-root", password="test-only")
    client.force_login(root)
    response = client.get(reverse("admin:venues_venue_delete", args=(venue.pk,)))
    assert response.status_code == 200
    assert b"delet" in response.content.lower()
    assert Venue.objects.filter(pk=venue.pk).exists()


@pytest.mark.django_db
def test_safe_master_and_draft_event_delete_through_admin(client, phase11_event_data):
    create, *_ = phase11_event_data
    root = User.objects.create_superuser(username="delete-root", password="test-only")
    client.force_login(root)
    records = (
        (
            EventType.objects.create(code="delete-type", name_uz="T", name_ru="T", name_en="T"),
            "events_eventtype_delete",
        ),
        (
            Organization.objects.create(name="Delete organization"),
            "organizations_organization_delete",
        ),
        (Sponsor.objects.create(name="Delete sponsor"), "organizations_sponsor_delete"),
        (Speaker.objects.create(full_name="Delete speaker"), "events_speaker_delete"),
        (
            create("Delete draft event", Event.DisplayVisibility.FULL, Event.Status.DRAFT),
            "events_event_delete",
        ),
    )
    for record, route in records:
        response = client.post(reverse(f"admin:{route}", args=(record.pk,)), {"post": "yes"})
        assert response.status_code == 302
        assert not record.__class__.objects.filter(pk=record.pk).exists()


@pytest.mark.django_db
def test_phase11d_calendar_search_and_public_detail_safety(client, phase11_event_data):
    create, owner, *_ = phase11_event_data
    owner.first_name = "Public"
    owner.last_name = "Coordinator"
    owner.save(update_fields=("first_name", "last_name"))
    create("International Oncology Symposium", Event.DisplayVisibility.FULL)
    create("Confidential Leadership Session", Event.DisplayVisibility.GENERIC)
    response = client.get(reverse("public-calendar-api"), {"search": "oncology"})
    assert response.status_code == 200
    payload = response.json()["events"]
    assert len(payload) == 1
    assert payload[0]["responsible"] == "Public Coordinator"
    content = client.get(reverse("public-calendar-api")).content.decode()
    assert "Confidential Leadership Session" not in content
    assert "SECRET-NOTE" not in content


@pytest.mark.django_db
def test_phase11d_language_switch_preserves_authenticated_route(client, user):
    client.force_login(user)
    response = client.post(
        reverse("set_language"),
        {"language": "ru", "next": reverse("profile")},
    )
    assert response.status_code == 302
    assert response.url == reverse("profile")
    assert client.get(reverse("profile")).status_code == 200


def test_phase11d_brand_assets_are_local_and_present(settings):
    static_root = settings.BASE_DIR / "static" / "brand"
    assert (static_root / "oncology-center.png").stat().st_size > 1000
    assert (static_root / "gustave-roussy-uzbekistan.png").stat().st_size > 1000
