import secrets
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from config.validators import validate_image_upload


def generate_display_token() -> str:
    return secrets.token_urlsafe(32)


class Venue(models.Model):
    code = models.CharField(_("code"), max_length=12, unique=True)
    name_uz = models.CharField(_("name in Uzbek"), max_length=160)
    name_ru = models.CharField(_("name in Russian"), max_length=160)
    name_en = models.CharField(_("name in English"), max_length=160)
    description = models.TextField(_("description"), blank=True)
    location = models.CharField(_("location"), max_length=255, blank=True)
    capacity = models.PositiveIntegerField(
        _("capacity"),
        validators=[MinValueValidator(1)],
    )
    working_start = models.TimeField(_("working start"))
    working_end = models.TimeField(_("working end"))
    is_active = models.BooleanField(_("active"), default=True)
    display_enabled = models.BooleanField(_("display enabled"), default=True)
    photo = models.FileField(
        _("photo"),
        upload_to="venues/%Y/%m/",
        validators=[validate_image_upload],
        blank=True,
    )
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        ordering = ("sort_order", "code")
        verbose_name = _("venue")
        verbose_name_plural = _("venues")
        constraints = [
            models.CheckConstraint(
                condition=Q(capacity__gt=0),
                name="venue_capacity_positive",
            ),
            models.CheckConstraint(
                condition=Q(working_end__gt=F("working_start")),
                name="venue_working_hours_ordered",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} · {self.localized_name}"

    @property
    def localized_name(self) -> str:
        language = (translation.get_language() or "uz").split("-")[0]
        return getattr(self, f"name_{language}", self.name_uz)


class DisplayToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(
        _("display token"),
        max_length=64,
        unique=True,
        db_index=True,
        default=generate_display_token,
        editable=False,
    )
    name = models.CharField(_("display name / location"), max_length=100)
    is_active = models.BooleanField(_("is active"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    last_used_at = models.DateTimeField(_("last used at"), null=True, blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("display token")
        verbose_name_plural = _("display tokens")

    def __str__(self) -> str:
        return f"{self.name} ({'Active' if self.is_active else 'Disabled'})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            from apps.audit.models import AuditEventLog
            from apps.audit.services import log_audit_event

            log_audit_event(AuditEventLog.Action.DISPLAY_TOKEN_CREATED, target=self)

    def rotate(self, actor=None) -> str:
        from apps.audit.models import AuditEventLog
        from apps.audit.services import log_audit_event

        self.token = generate_display_token()
        self.save(update_fields=["token"])
        log_audit_event(AuditEventLog.Action.DISPLAY_TOKEN_ROTATED, actor, self)
        return self.token

    def set_enabled(self, enabled: bool, actor=None) -> None:
        from apps.audit.models import AuditEventLog
        from apps.audit.services import log_audit_event

        if self.is_active == enabled:
            return
        self.is_active = enabled
        self.save(update_fields=["is_active"])
        action = (
            AuditEventLog.Action.DISPLAY_ENABLED
            if enabled
            else AuditEventLog.Action.DISPLAY_DISABLED
        )
        log_audit_event(action, actor, self)
