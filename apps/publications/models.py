import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.validators import validate_image_upload


class Publication(models.Model):
    class Platform(models.TextChoices):
        TELEGRAM_CHANNEL = "telegram_channel", _("Telegram channel")
        INSTAGRAM = "instagram", _("Instagram")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        READY = "ready", _("Ready for approval")
        APPROVED = "approved", _("Approved")
        SCHEDULED = "scheduled", _("Scheduled")
        PUBLISHING = "publishing", _("Publishing")
        PUBLISHED = "published", _("Published")
        FAILED = "failed", _("Failed")
        CANCELLED = "cancelled", _("Cancelled")

    class BannerTemplate(models.TextChoices):
        CONFERENCE = "conference", _("Conference")
        SYMPOSIUM = "symposium", _("Symposium")
        SEMINAR = "seminar", _("Seminar")
        DELEGATION = "delegation", _("Delegation Visit")
        MEETING = "meeting", _("Meeting")
        EMERGENCY = "emergency", _("Emergency Announcement")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("events.Event", on_delete=models.CASCADE, related_name="publications")
    platform = models.CharField(max_length=24, choices=Platform.choices)
    language = models.CharField(
        max_length=2,
        choices=(("uz", "Uzbek"), ("ru", "Russian"), ("en", "English")),
        default="uz",
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    headline = models.CharField(max_length=180)
    short_description = models.TextField(blank=True, default="")
    caption = models.TextField(blank=True, default="")
    rendered_caption = models.TextField(blank=True, default="")
    banner_template = models.CharField(
        max_length=24, choices=BannerTemplate.choices, default=BannerTemplate.CONFERENCE
    )
    include_qr = models.BooleanField(default=True)
    include_sponsors = models.BooleanField(default=True)
    banner = models.ImageField(
        upload_to="publications/%Y/%m/", blank=True, validators=[validate_image_upload]
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_publications",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_publications",
    )
    external_post_id = models.CharField(max_length=255, blank=True, default="")
    external_container_id = models.CharField(max_length=255, blank=True, default="")
    external_url = models.URLField(blank=True, default="")
    error_code = models.CharField(max_length=64, blank=True, default="")
    error_message = models.CharField(max_length=255, blank=True, default="")
    retry_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "scheduled_for")),
            models.Index(fields=("platform", "language")),
        ]

    def __str__(self) -> str:
        return f"{self.get_platform_display()}: {self.headline}"
