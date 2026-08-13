from pathlib import Path

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _has_valid_image_signature(upload, extension: str) -> bool:
    position = upload.tell() if hasattr(upload, "tell") else None
    header = upload.read(12)
    if hasattr(upload, "seek"):
        upload.seek(position or 0)
    if extension in {".jpg", ".jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if extension == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    return header.startswith(b"RIFF") and header[8:12] == b"WEBP"


def validate_image_upload(upload) -> None:
    extension = Path(upload.name).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _("Upload a JPG, PNG, or WebP image."),
            code="invalid_image_extension",
        )
    if upload.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            _("Image size must not exceed 5 MB."),
            code="image_too_large",
        )
    content_type = getattr(upload, "content_type", None)
    if content_type and content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError(
            _("The uploaded file content is not a supported image."),
            code="invalid_image_content_type",
        )
    if not _has_valid_image_signature(upload, extension):
        raise ValidationError(
            _("The uploaded file content is not a supported image."),
            code="invalid_image_signature",
        )
