from datetime import date, time, timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.accounts.models import User
from apps.audit.models import AuditEventLog
from apps.events.models import Event, EventType, Speaker
from apps.events.services.program import (
    add_program_item,
    remove_program_item,
    remove_program_pdf,
    rotate_public_token,
    set_public_enabled,
    update_program_source,
    upload_program_pdf,
)
from apps.events.services.qr import generate_qr_code_png, generate_qr_code_svg
from apps.venues.models import Venue


@pytest.fixture
def phase4_setup(db):
    super_admin = User.objects.create_superuser(
        username="p4_super_admin",
        email="super@iems.uz",
        password="Password123!",
        role=User.Role.SUPER_ADMIN,
    )
    resp_user = User.objects.create_user(
        username="p4_resp_user",
        email="resp_private@iems.uz",
        password="Password123!",
        role=User.Role.RESPONSIBLE_EMPLOYEE,
    )
    mgmt_user = User.objects.create_user(
        username="p4_mgmt_user",
        email="mgmt@iems.uz",
        password="Password123!",
        role=User.Role.MANAGEMENT_RESPONSIBLE,
    )

    venue = Venue.objects.create(
        code="P4-HALL",
        name_uz="Phase 4 Zal",
        name_ru="Фаза 4 Зал",
        name_en="Phase 4 Hall",
        working_start="08:00",
        working_end="20:00",
        capacity=150,
    )
    event_type = EventType.objects.create(
        code="P4-SYMP",
        name_uz="Simpozium",
        name_ru="Симпозиум",
        name_en="Symposium",
    )

    planned_date = date.today() + timedelta(days=5)

    approved_event = Event.objects.create(
        title="International Tech Symposium 2026",
        event_type=event_type,
        venue=venue,
        planned_date=planned_date,
        start_time=time(9, 0),
        end_time=time(17, 0),
        responsible_employee=resp_user,
        management_responsible=mgmt_user,
        created_by=resp_user,
        status=Event.Status.APPROVED,
        zoom_url="https://zoom.us/j/999888777",
        registration_url="https://iems.uz/register",
        notes="Internal budget note: Confidential budget details.",
    )

    draft_event = Event.objects.create(
        title="Unpublished Draft Event",
        event_type=event_type,
        venue=venue,
        planned_date=planned_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        responsible_employee=resp_user,
        management_responsible=mgmt_user,
        created_by=resp_user,
        status=Event.Status.DRAFT,
    )

    speaker = Speaker.objects.create(
        full_name="Prof. John Doe",
        title="Chief Scientist",
        organization="Global Research Lab",
        country="Uzbekistan",
        bio="Leading expert in AI and Systems.",
        email="john.doe.private@example.com",
    )

    return {
        "super_admin": super_admin,
        "resp_user": resp_user,
        "mgmt_user": mgmt_user,
        "approved_event": approved_event,
        "draft_event": draft_event,
        "speaker": speaker,
    }


@pytest.mark.django_db
class TestProgramSourceAndPDF:
    def test_program_source_switch(self, phase4_setup):
        event = phase4_setup["approved_event"]
        user = phase4_setup["resp_user"]

        assert event.program_source == Event.ProgramSource.MANUAL
        update_program_source(event, user, Event.ProgramSource.PDF)

        event.refresh_from_db()
        assert event.program_source == Event.ProgramSource.PDF
        assert AuditEventLog.objects.filter(action="event.program_source_changed").exists()

    def test_pdf_upload_validation_and_cleanup(self, phase4_setup):
        event = phase4_setup["approved_event"]
        user = phase4_setup["resp_user"]

        # 1. Non-PDF extension blocked
        invalid_txt = SimpleUploadedFile("program.txt", b"Hello World", content_type="text/plain")
        with pytest.raises(Exception):
            upload_program_pdf(event, user, invalid_txt)

        # 2. Invalid header bytes blocked
        fake_pdf = SimpleUploadedFile(
            "fake.pdf", b"NOT_A_PDF_HEADER", content_type="application/pdf"
        )
        with pytest.raises(Exception):
            upload_program_pdf(event, user, fake_pdf)

        # 3. Valid PDF upload
        valid_pdf = SimpleUploadedFile(
            "program.pdf", b"%PDF-1.4\n%Valid PDF Content", content_type="application/pdf"
        )
        upload_program_pdf(event, user, valid_pdf)

        event.refresh_from_db()
        assert event.program_pdf is not None
        assert event.program_source == Event.ProgramSource.PDF
        assert AuditEventLog.objects.filter(action="event.program_pdf_uploaded").exists()

        # 4. Remove PDF
        remove_program_pdf(event, user)
        event.refresh_from_db()
        assert not event.program_pdf
        assert AuditEventLog.objects.filter(action="event.program_pdf_removed").exists()


@pytest.mark.django_db
class TestManualAgendaAndSpeakers:
    def test_manual_agenda_items(self, phase4_setup):
        event = phase4_setup["approved_event"]
        user = phase4_setup["resp_user"]
        speaker = phase4_setup["speaker"]

        item1 = add_program_item(
            event,
            user,
            title="Opening Ceremony",
            start_time=time(9, 0),
            end_time=time(9, 30),
            description="Welcome remarks",
            sort_order=1,
        )
        item2 = add_program_item(
            event,
            user,
            title="Keynote Presentation",
            start_time=time(9, 30),
            end_time=time(10, 30),
            speaker=speaker,
            sort_order=2,
        )

        assert event.program_items.count() == 2
        assert item2.speaker_display_name == "Prof. John Doe"

        remove_program_item(item1, user)
        assert event.program_items.count() == 1

    def test_speaker_private_email_protection(self, phase4_setup):
        speaker = phase4_setup["speaker"]
        assert speaker.email == "john.doe.private@example.com"
        # Ensure email is marked private and never serialized in public API


@pytest.mark.django_db
class TestPublicTokenAndEligibility:
    def test_token_generation_and_rotation(self, phase4_setup):
        event = phase4_setup["approved_event"]
        user = phase4_setup["resp_user"]

        token1 = event.public_token
        assert token1 is not None
        assert len(token1) > 10

        rotate_public_token(event, user)
        event.refresh_from_db()
        token2 = event.public_token
        assert token1 != token2
        assert AuditEventLog.objects.filter(action="event.public_token_rotated").exists()

    def test_public_eligibility_policy(self, phase4_setup):
        approved_event = phase4_setup["approved_event"]
        draft_event = phase4_setup["draft_event"]

        assert approved_event.is_publicly_accessible is True
        assert draft_event.is_publicly_accessible is False

        set_public_enabled(approved_event, phase4_setup["resp_user"], False)
        assert approved_event.is_publicly_accessible is False


@pytest.mark.django_db
class TestPublicEventPageView:
    def test_public_page_accessible_without_login(self, client, phase4_setup):
        approved_event = phase4_setup["approved_event"]
        url = reverse("public-event-page", kwargs={"public_token": approved_event.public_token})

        response = client.get(url)
        assert response.status_code == 200
        assert approved_event.title in response.content.decode("utf-8")
        # Ensure confidential notes and email are NOT present in output
        assert "Confidential budget details" not in response.content.decode("utf-8")
        assert "resp_private@iems.uz" not in response.content.decode("utf-8")

    def test_draft_event_public_page_returns_404(self, client, phase4_setup):
        draft_event = phase4_setup["draft_event"]
        url = reverse("public-event-page", kwargs={"public_token": draft_event.public_token})

        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestQRCodeGeneration:
    def test_qr_code_png_and_svg(self, phase4_setup):
        approved_event = phase4_setup["approved_event"]
        target_url = f"http://127.0.0.1:8000/event/{approved_event.public_token}/"

        png_bytes = generate_qr_code_png(target_url)
        assert png_bytes.startswith(b"\x89PNG")

        svg_str = generate_qr_code_svg(target_url)
        assert "<svg" in svg_str

    def test_print_qr_route(self, client, phase4_setup):
        approved_event = phase4_setup["approved_event"]
        client.force_login(phase4_setup["resp_user"])

        url = reverse("events:print-qr", kwargs={"pk": approved_event.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert "Scan to Open Event Program" in response.content.decode("utf-8")


@pytest.mark.django_db
class TestPhase4API:
    def test_public_api_endpoint(self, client, phase4_setup):
        approved_event = phase4_setup["approved_event"]
        url = reverse("api-public-event", kwargs={"token": approved_event.public_token})

        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == approved_event.title
        assert "notes" not in data
        assert "responsible_employee_email" not in data

    def test_authenticated_program_api_endpoint(self, client, phase4_setup):
        approved_event = phase4_setup["approved_event"]
        client.force_login(phase4_setup["resp_user"])

        url = reverse("api-event-program", kwargs={"pk": approved_event.pk})
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["public_token"] == approved_event.public_token
