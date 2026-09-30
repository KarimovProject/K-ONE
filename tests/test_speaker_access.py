import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.events.models import Speaker


@pytest.fixture
def speaker(db):
    return Speaker.objects.create(full_name="Dr. Real Speaker", public_profile_enabled=True)


def speaker_urls(speaker):
    return (
        reverse("events:speaker-list"),
        reverse("events:speaker-create"),
        reverse("events:speaker-edit", kwargs={"pk": speaker.pk}),
    )


@pytest.mark.django_db
class TestSpeakerPagesAreStaffOnly:
    """Speaker profiles appear on public event pages, so roles that don't
    build events must not be able to list, add or edit them."""

    @pytest.mark.parametrize(
        "role",
        [
            User.Role.DOCTOR,
            User.Role.RECEPTION_OPERATOR,
            User.Role.LEADERSHIP_VIEWER,
            User.Role.MANAGEMENT_RESPONSIBLE,
        ],
    )
    def test_non_event_roles_get_403(self, client, speaker, role):
        user = User.objects.create_user(username=f"u-{role}", password="x", role=role)
        client.force_login(user)
        for url in speaker_urls(speaker):
            assert client.get(url).status_code == 403, url

    def test_doctor_cannot_overwrite_another_speaker(self, client, speaker):
        doctor = User.objects.create_user(username="doc", password="x", role=User.Role.DOCTOR)
        client.force_login(doctor)
        res = client.post(
            reverse("events:speaker-edit", kwargs={"pk": speaker.pk}),
            data={"full_name": "Hijacked"},
        )
        assert res.status_code == 403
        speaker.refresh_from_db()
        assert speaker.full_name == "Dr. Real Speaker"

    @pytest.mark.parametrize(
        "role",
        [
            User.Role.RESPONSIBLE_EMPLOYEE,
            User.Role.INTERNATIONAL_ADMIN,
            User.Role.CONTENT_MANAGER,
        ],
    )
    def test_event_staff_and_content_roles_are_allowed(self, client, speaker, role):
        user = User.objects.create_user(username=f"u-{role}", password="x", role=role)
        client.force_login(user)
        for url in speaker_urls(speaker):
            assert client.get(url).status_code == 200, url

    def test_anonymous_user_is_redirected_to_login(self, client, speaker):
        res = client.get(reverse("events:speaker-list"))
        assert res.status_code == 302
        assert reverse("login") in res.url
