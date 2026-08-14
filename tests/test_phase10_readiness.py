import io
import json
from datetime import time

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import RequestFactory, override_settings
from django.test.utils import CaptureQueriesContext
from PIL import Image

from apps.events.models import Event, EventType, Speaker, generate_public_token
from apps.notifications.telegram.tasks import send_telegram_delivery
from apps.publications.models import Publication
from apps.reporting.selectors import allowed_report_sections
from apps.venues.models import Venue
from config.logging import JsonFormatter
from config.rate_limit import is_rate_limited
from config.validators import validate_image_upload, validate_pdf_upload

pytestmark = pytest.mark.django_db


@pytest.fixture
def p10_public_event():
    users = get_user_model()
    user = users.objects.create_user(
        "p10-public-owner", role=users.Role.INTERNATIONAL_ADMIN
    )
    venue = Venue.objects.create(
        code="P10-PUBLIC",
        name_uz="Public",
        name_ru="Public",
        name_en="Public",
        capacity=20,
        working_start=time(8),
        working_end=time(18),
    )
    event_type = EventType.objects.create(
        code="p10-public", name_uz="Public", name_ru="Public", name_en="Public"
    )
    return Event.objects.create(
        title="P10 Public",
        event_type=event_type,
        venue=venue,
        planned_date="2026-08-13",
        start_time=time(10),
        end_time=time(11),
        responsible_employee=user,
        management_responsible=user,
        created_by=user,
        status=Event.Status.APPROVED,
        expected_attendees=20,
    )


def image_file(name="photo.png", size=(20, 20)):
    output = io.BytesIO()
    Image.new("RGB", size, "blue").save(output, format="PNG")
    return SimpleUploadedFile(name, output.getvalue(), content_type="image/png")


def test_production_settings_are_secure(settings):
    from config.settings import production

    assert production.DEBUG is False
    assert production.SECURE_SSL_REDIRECT is True
    assert production.SESSION_COOKIE_SECURE and production.CSRF_COOKIE_SECURE
    assert production.SESSION_COOKIE_HTTPONLY
    assert production.SECURE_HSTS_SECONDS >= 31_536_000
    assert production.X_FRAME_OPTIONS == "DENY"


def test_security_headers_and_public_no_store(client):
    response = client.get("/health/")
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
    assert "camera=()" in response["Permissions-Policy"]
    assert "frame-ancestors 'none'" in response["Content-Security-Policy"]


def test_rate_limit_is_shared_and_returns_limit_state():
    cache.clear()
    request = RequestFactory().get("/", REMOTE_ADDR="192.0.2.20")
    assert is_rate_limited(request, "test", 2, 60) is False
    assert is_rate_limited(request, "test", 2, 60) is False
    assert is_rate_limited(request, "test", 2, 60) is True


def test_successful_login_resets_throttle_bucket(client):
    users = get_user_model()
    users.objects.create_user("p10-login", password="Phase10-Login-Safe!")
    cache.clear()
    for _ in range(5):
        response = client.post(
            "/accounts/login/", {"username": "p10-login", "password": "wrong"}
        )
        assert response.status_code == 200
    response = client.post(
        "/accounts/login/",
        {"username": "p10-login", "password": "Phase10-Login-Safe!"},
    )
    assert response.status_code == 302
    client.logout()
    for _ in range(10):
        response = client.post(
            "/accounts/login/", {"username": "p10-login", "password": "wrong"}
        )
        assert response.status_code == 200
    assert (
        client.post(
            "/accounts/login/", {"username": "p10-login", "password": "wrong"}
        ).status_code
        == 429
    )


def test_upload_binary_hardening():
    validate_image_upload(image_file())
    with pytest.raises(ValidationError):
        validate_image_upload(
            SimpleUploadedFile("bad.png", b"<script>alert(1)</script>", content_type="image/png")
        )
    validate_pdf_upload(
        SimpleUploadedFile("program.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
    )
    with pytest.raises(ValidationError):
        validate_pdf_upload(SimpleUploadedFile("program.pdf", b"not a pdf"))


def test_model_level_upload_validators_are_present():
    assert Speaker._meta.get_field("photo").validators
    assert Event._meta.get_field("program_pdf").validators
    assert Publication._meta.get_field("banner").validators


def test_public_tokens_have_adequate_entropy_and_are_unique():
    tokens = {generate_public_token() for _ in range(200)}
    assert len(tokens) == 200
    assert min(map(len, tokens)) >= 22


@pytest.mark.parametrize(
    ("role", "allowed"),
    [
        ("super_admin", {"summary", "attendance", "publications"}),
        ("international_admin", {"summary", "attendance", "publications"}),
        ("responsible_employee", {"summary", "attendance", "publications"}),
        ("management_responsible", {"summary", "attendance", "publications"}),
        ("leadership_viewer", {"summary", "attendance", "publications"}),
        ("content_manager", {"publications"}),
        ("reception_operator", {"attendance"}),
    ],
)
def test_reporting_role_matrix(role, allowed):
    user = get_user_model()(username=f"p10-{role}", role=role, is_active=True)
    assert allowed_report_sections(user).issuperset(allowed)
    if role in {"content_manager", "reception_operator"}:
        assert allowed_report_sections(user) == frozenset(allowed)


def test_error_pages_do_not_leak_paths(client):
    response = client.get("/definitely-missing-phase10/")
    text = response.content.decode()
    assert response.status_code == 404
    assert "C:\\IEMS" not in text and "Traceback" not in text


def test_readiness_endpoint_exposes_only_status(client, monkeypatch):
    class Result:
        is_healthy = True

    monkeypatch.setattr("config.health.check_application", lambda: Result())
    monkeypatch.setattr("config.health.check_database", lambda: Result())
    monkeypatch.setattr("config.health.check_redis", lambda: Result())
    response = client.get("/health/ready/")
    assert response.json() == {"status": "ok"}


def test_json_logs_are_structured_without_implicit_sensitive_fields():
    import logging

    formatter = JsonFormatter()
    record = logging.LogRecord("iems.security", logging.WARNING, "", 0, "rate limited", (), None)
    payload = json.loads(formatter.format(record))
    assert payload["message"] == "rate limited"
    assert set(payload) == {"timestamp", "level", "logger", "message"}


def test_telegram_task_lock_prevents_parallel_duplicate(monkeypatch):
    cache.clear()
    calls = []
    monkeypatch.setattr(
        "apps.notifications.telegram.tasks._send_locked_delivery",
        lambda task, delivery_id: calls.append(delivery_id) or "sent",
    )
    cache.set("telegram-delivery-lock:123", "1", 120)
    assert send_telegram_delivery.run(123) == "in_progress"
    cache.delete("telegram-delivery-lock:123")
    assert send_telegram_delivery.run(123) == "sent"
    assert calls == [123]


def test_backup_scripts_have_safety_and_no_embedded_password():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    backup = (root / "scripts" / "backup.ps1").read_text(encoding="utf-8")
    restore = (root / "scripts" / "restore.ps1").read_text(encoding="utf-8")
    verify = (root / "scripts" / "verify-backup.ps1").read_text(encoding="utf-8")
    assert "pg_dump" in backup and "checksums.json" in backup
    assert "iems_restore_" in restore and "Recreate" in restore
    assert "pg_restore" in verify and "sha256" in verify.lower()
    assert "DB_PASSWORD=" not in backup + restore + verify


@override_settings(SESSION_COOKIE_SECURE=False)
def test_public_page_preseeds_httponly_checkin_cookie(client, p10_public_event):
    response = client.get(f"/event/{p10_public_event.public_token}/")
    cookie = response.cookies["event_checkin_token"]
    assert cookie["httponly"] and cookie["samesite"] == "Lax"


def test_reports_query_count_remains_bounded(client):
    users = get_user_model()
    admin = users.objects.create_user("p10-query-admin", role=users.Role.INTERNATIONAL_ADMIN)
    client.force_login(admin)
    with CaptureQueriesContext(connection) as captured:
        response = client.get("/reports/")
    assert response.status_code == 200
    assert len(captured) <= 80
