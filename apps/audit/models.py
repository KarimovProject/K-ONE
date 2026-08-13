from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditEventLog(models.Model):
    class Action(models.TextChoices):
        EVENT_CREATED = "event.created", _("Event Created")
        EVENT_UPDATED = "event.updated", _("Event Updated")
        EVENT_PLANNED = "event.planned", _("Event Planned")
        EVENT_CANCELLED = "event.cancelled", _("Event Cancelled")
        EVENT_SUBMITTED = "event.submitted", _("Event Submitted for Approval")
        EVENT_APPROVED = "event.approved", _("Event Approved")
        EVENT_REJECTED = "event.rejected", _("Event Rejected")
        EVENT_RESUBMITTED = "event.resubmitted", _("Event Resubmitted")
        EVENT_POSTPONED = "event.postponed", _("Event Postponed")
        EVENT_RESCHEDULED = "event.rescheduled", _("Event Rescheduled")
        EVENT_EMERGENCY_REQUESTED = "event.emergency_requested", _("Emergency Requested")
        EVENT_EMERGENCY_OVERRIDDEN = "event.emergency_overridden", _("Emergency Override Executed")
        EMERGENCY_OVERRIDE = "event.emergency_override", _("Emergency Override Executed")
        EVENT_DISPLACED = "event.displaced", _("Event Displaced by Emergency")
        PROGRAM_SOURCE_CHANGED = "event.program_source_changed", _("Program Source Changed")
        PROGRAM_PDF_UPLOADED = "event.program_pdf_uploaded", _("Program PDF Uploaded")
        PROGRAM_PDF_REPLACED = "event.program_pdf_replaced", _("Program PDF Replaced")
        PROGRAM_PDF_REMOVED = "event.program_pdf_removed", _("Program PDF Removed")
        PROGRAM_ITEM_ADDED = "event.program_item_added", _("Program Item Added")
        PROGRAM_ITEM_UPDATED = "event.program_item_updated", _("Program Item Updated")
        PROGRAM_ITEM_REMOVED = "event.program_item_removed", _("Program Item Removed")
        PUBLIC_PAGE_ENABLED = "event.public_page_enabled", _("Public Page Enabled")
        PUBLIC_TOKEN_ROTATED = "event.public_token_rotated", _("Public Token Rotated")
        QR_GENERATED = "event.qr_generated", _("QR Code Generated")
        QR_PRINTED = "event.qr_printed", _("QR Code Printed")
        DISPLAY_TOKEN_CREATED = "display.token_created", _("Display Token Created")
        DISPLAY_TOKEN_ROTATED = "display.token_rotated", _("Display Token Rotated")
        DISPLAY_ENABLED = "display.enabled", _("Display Enabled")
        DISPLAY_DISABLED = "display.disabled", _("Display Disabled")
        TELEGRAM_CONNECTION_CREATED = "telegram.connection_created", _("Telegram Connected")
        TELEGRAM_CONNECTION_REMOVED = "telegram.connection_removed", _("Telegram Disconnected")
        TELEGRAM_TEST_SENT = "telegram.test_sent", _("Telegram Test Sent")
        TELEGRAM_REMINDER_SCHEDULED = (
            "telegram.reminder_scheduled",
            _("Telegram Reminder Scheduled"),
        )
        TELEGRAM_REMINDER_SENT = "telegram.reminder_sent", _("Telegram Reminder Sent")
        TELEGRAM_REMINDER_FAILED = "telegram.reminder_failed", _("Telegram Reminder Failed")
        TELEGRAM_EVENT_NOTIFICATION_SENT = (
            "telegram.event_notification_sent",
            _("Telegram Event Notification Sent"),
        )
        PUBLICATION_CREATED = "publication.created", _("Publication Created")
        PUBLICATION_UPDATED = "publication.updated", _("Publication Updated")
        PUBLICATION_APPROVED = "publication.approved", _("Publication Approved")
        PUBLICATION_SCHEDULED = "publication.scheduled", _("Publication Scheduled")
        PUBLICATION_PUBLISHED = "publication.published", _("Publication Published")
        PUBLICATION_FAILED = "publication.failed", _("Publication Failed")
        PUBLICATION_CANCELLED = "publication.cancelled", _("Publication Cancelled")
        PUBLICATION_RETRIED = "publication.retried", _("Publication Retried")
        BANNER_GENERATED = "banner.generated", _("Banner Generated")
        BANNER_REGENERATED = "banner.regenerated", _("Banner Regenerated")

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(_("action"), max_length=64, choices=Action.choices)
    target_id = models.CharField(_("target ID"), max_length=128, blank=True)
    target_repr = models.CharField(_("target representation"), max_length=255, blank=True)
    payload = models.JSONField(_("payload"), default=dict, blank=True)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
        verbose_name = _("audit log entry")
        verbose_name_plural = _("audit log entries")
        indexes = [
            models.Index(fields=("action", "timestamp")),
            models.Index(fields=("target_id", "action")),
        ]

    def __str__(self) -> str:
        actor_name = self.actor.username if self.actor else "system"
        ts = f"{self.timestamp:%Y-%m-%d %H:%M}"
        return f"[{ts}] {actor_name} -> {self.action} ({self.target_repr})"
