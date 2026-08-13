import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EventAttendance(models.Model):
    class Method(models.TextChoices):
        PUBLIC_QR = "public_qr", _("Public QR")
        STAFF_MANUAL = "staff_manual", _("Staff Manual")
        REGISTRATION_IMPORT = "registration_import", _("Registration Import")
        INVITATION = "invitation", _("Invitation")
        KIOSK = "kiosk", _("Kiosk")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("event"),
    )
    checked_in_at = models.DateTimeField(
        _("checked in at"),
        default=timezone.now,
        db_index=True,
    )
    checkin_method = models.CharField(
        _("check-in method"),
        max_length=32,
        choices=Method.choices,
        default=Method.PUBLIC_QR,
    )
    attendee_identifier_hash = models.CharField(
        _("attendee identifier hash"),
        max_length=64,
        db_index=True,
    )
    attendee_name = models.CharField(
        _("full name"),
        max_length=255,
        blank=True,
        default="",
    )
    attendee_organization = models.CharField(
        _("organization"),
        max_length=255,
        blank=True,
        default="",
    )
    attendee_role = models.CharField(
        _("role / title"),
        max_length=255,
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ("-checked_in_at",)
        verbose_name = _("event attendance")
        verbose_name_plural = _("event attendances")
        constraints = [
            models.UniqueConstraint(
                fields=["event", "attendee_identifier_hash"],
                name="unique_event_attendee_hash",
            )
        ]

    def __str__(self) -> str:
        name = self.attendee_name or _("Anonymous")
        return f"{name} - {self.event.title} ({self.checked_in_at.strftime('%Y-%m-%d %H:%M')})"
