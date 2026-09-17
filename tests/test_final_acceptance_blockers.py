import re
import secrets

import pytest
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.rbac import Capability
from config import views as config_views

MAJOR_ROUTES = (
    ("dashboard", "dashboard.html"),
    ("events:list", "events/event_list.html"),
    ("calendar", "events/calendar.html"),
    ("events:approval-list", "events/approval_center.html"),
    ("events:displaced-list", "events/event_list.html"),
    ("venues:list", "venues/venue_list.html"),
    ("event-types:list", "events/event_type_list.html"),
    ("organizations:list", "organizations/organization_list.html"),
    ("sponsors:list", "organizations/sponsor_list.html"),
    ("events:speaker-list", "events/speaker_list.html"),
    ("leadership-dashboard", "reporting/leadership_dashboard.html"),
    ("notifications:telegram-settings", "notifications/telegram_settings.html"),
    ("publications:list", "publications/list.html"),
    ("reporting:dashboard", "reporting/reports_dashboard.html"),
)


def create_super_admin(username="acceptance_admin"):
    return User.objects.create_user(
        username=username,
        role=User.Role.SUPER_ADMIN,
        is_active=True,
        is_staff=True,
        is_superuser=False,
    )


@pytest.mark.django_db
def test_locale_switch_preserves_authenticated_session_and_current_page(client):
    user = create_super_admin()
    client.force_login(user)
    route_sequence = (
        ("ru", reverse("events:list")),
        ("en", reverse("calendar")),
        ("uz", reverse("leadership-dashboard")),
    )

    for language, current_page in route_sequence:
        auth_user_id = client.session[SESSION_KEY]
        response = client.post(
            reverse("set_language"),
            {"language": language, "next": current_page},
        )
        assert response.status_code == 302
        assert response.url == current_page
        assert client.session[SESSION_KEY] == auth_user_id

        page = client.get(current_page)
        assert page.status_code == 200
        assert page.wsgi_request.user == user
        assert b'id="primary-navigation"' in page.content
        assert b"acceptance_admin" in page.content


@pytest.mark.django_db
def test_iems_super_admin_role_can_open_every_major_internal_route(client):
    user = create_super_admin()
    assert not user.is_superuser
    assert all(user.has_capability(capability) for capability in Capability)
    client.force_login(user)

    for route_name, expected_template in MAJOR_ROUTES:
        response = client.get(reverse(route_name))
        assert response.status_code == 200, route_name
        assert expected_template in [template.name for template in response.templates], route_name
        assert len(response.content.strip()) > 500, route_name
        assert re.search(rb"<h1(?:\s[^>]*)?>.+?</h1>", response.content, re.DOTALL), route_name


@pytest.mark.django_db
def test_unauthorized_user_gets_visible_localized_403_page():
    user = User.objects.create_user(
        username="acceptance_ordinary",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )
    client = Client(raise_request_exception=False)
    client.force_login(user)

    response = client.get(reverse("events:approval-list"))
    assert response.status_code == 403
    assert b"error-page" in response.content
    assert b"<h1" in response.content
    assert "Kirish taqiqlangan" in response.content.decode()
    assert b'href="/"' in response.content
    assert len(response.content.strip()) > 500

    client.logout()
    anonymous_response = client.get(reverse("tv-wallboard-token", args=["invalid-token"]))
    assert anonymous_response.status_code == 403
    assert b"error-page" in anonymous_response.content
    assert b"<h1" in anonymous_response.content
    assert len(anonymous_response.content.strip()) > 500


def test_all_error_handlers_render_visible_anonymous_bodies():
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    handlers = (
        config_views.error_400,
        config_views.error_403,
        config_views.error_404,
        config_views.error_500,
        config_views.rate_limited_response,
    )

    for handler in handlers:
        response = handler(request)
        assert response.status_code in {400, 403, 404, 429, 500}
        assert b"error-page" in response.content
        assert b"<h1" in response.content
        assert b'href="/"' in response.content


@pytest.mark.django_db
def test_valid_login_honors_safe_next_redirect(client):
    password = f"Acceptance-{secrets.token_urlsafe(24)}!"
    user = create_super_admin()
    user.set_password(password)
    user.save(update_fields=["password"])
    target = reverse("events:speaker-list")

    response = client.post(
        f"{reverse('login')}?next={target}",
        {"username": user.username, "password": password, "next": target},
    )

    assert response.status_code == 302
    assert response.url == target
    assert client.get(target).status_code == 200


@pytest.mark.django_db
def test_sidebar_named_links_render_and_resolve(client):
    client.force_login(create_super_admin())
    dashboard = client.get(reverse("dashboard"))
    assert dashboard.status_code == 200

    for route_name, _template in MAJOR_ROUTES:
        url = reverse(route_name)
        assert f'href="{url}"'.encode() in dashboard.content, route_name
        assert client.get(url).status_code == 200, route_name


@pytest.mark.django_db
def test_speaker_pages_highlight_the_speakers_sidebar_item_not_events():
    """SpeakerListView/Create/Update used to hardcode nav_key="events",
    so the sidebar highlighted "Tadbirlar" while viewing "Ma'ruzachilar"."""
    client = Client()
    client.force_login(create_super_admin())

    res = client.get(reverse("events:speaker-list"))
    assert res.status_code == 200
    assert res.context["nav_key"] == "speakers"

    res = client.get(reverse("events:speaker-create"))
    assert res.status_code == 200
    assert res.context["nav_key"] == "speakers"


def test_local_settings_isolate_http_acceptance_cookies():
    from config.settings import local

    assert local.SESSION_COOKIE_NAME != "sessionid"
    assert local.CSRF_COOKIE_NAME != "csrftoken"
    assert local.SESSION_COOKIE_SECURE is False
    assert local.CSRF_COOKIE_SECURE is False
