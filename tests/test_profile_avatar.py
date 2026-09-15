import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

pytestmark = pytest.mark.django_db


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture(autouse=True)
def _isolated_media(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path


def test_profile_page_has_no_staff_or_superuser_lines(client, user):
    client.force_login(user)
    response = client.get(reverse("profile"))
    assert response.status_code == 200
    assert b"Staff Status" not in response.content
    assert b"Superuser" not in response.content


def test_profile_shows_initials_when_no_avatar(client, user):
    client.force_login(user)
    response = client.get(reverse("profile"))
    assert user.initials.encode() in response.content


def test_uploading_a_photo_sets_the_user_avatar(client, user):
    client.force_login(user)
    photo = SimpleUploadedFile("me.png", _png_bytes(), content_type="image/png")
    response = client.post(
        reverse("profile"),
        {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "preferred_language": user.preferred_language,
            "avatar": photo,
        },
    )
    user.refresh_from_db()
    assert response.status_code == 302
    assert user.avatar


def test_removing_the_photo_clears_the_avatar(client, user):
    photo = SimpleUploadedFile("me.png", _png_bytes(), content_type="image/png")
    user.avatar = photo
    user.save()

    client.force_login(user)
    response = client.post(
        reverse("profile"),
        {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "preferred_language": user.preferred_language,
            "remove_avatar": "on",
        },
    )
    user.refresh_from_db()
    assert response.status_code == 302
    assert not user.avatar


def test_uploading_a_non_image_file_is_rejected(client, user):
    client.force_login(user)
    fake = SimpleUploadedFile("me.txt", b"not an image", content_type="text/plain")
    response = client.post(
        reverse("profile"),
        {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "preferred_language": user.preferred_language,
            "avatar": fake,
        },
    )
    user.refresh_from_db()
    assert response.status_code == 200
    assert not user.avatar
