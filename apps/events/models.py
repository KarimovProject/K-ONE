import secrets
import uuid
from datetime import UTC, datetime, timedelta

from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

from config.validators import validate_image_upload, validate_pdf_upload


def generate_public_token() -> str:
    return secrets.token_urlsafe(16)

WEEKDAY_NAMES = {
    "uz": (
        "Dushanba",
        "Seshanba",
        "Chorshanba",
        "Payshanba",
        "Juma",
        "Shanba",
        "Yakshanba",
    ),
    "ru": (
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ),
    "en": (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ),
}


class EventType(models.Model):
    code = models.SlugField(_("code"), max_length=48, unique=True)
    name_uz = models.CharField(_("name in Uzbek"), max_length=160)
    name_ru = models.CharField(_("name in Russian"), max_length=160)
    name_en = models.CharField(_("name in English"), max_length=160)
    description = models.TextField(_("description"), blank=True)
    color = models.CharField(
        _("color"),
        max_length=7,
        default="#2563EB",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message=_("Enter a color in #RRGGBB format."),
            )
        ],
    )
    icon = models.SlugField(_("icon"), max_length=48, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    requires_management_approval = models.BooleanField(
        _("requires management approval"),
        default=False,
    )
    allows_emergency_override = models.BooleanField(
        _("allows emergency override"),
        default=False,
    )
    sort_order = models.PositiveSmallIntegerField(_("sort order"), default=0)

    class Meta:
        ordering = ("sort_order", "code")
        verbose_name = _("event type")
        verbose_name_plural = _("event types")

    def __str__(self) -> str:
        return self.localized_name

    @property
    def localized_name(self) -> str:
        language = (translation.get_language() or "uz").split("-")[0]
        return getattr(self, f"name_{language}", self.name_uz)


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PENDING_APPROVAL = "pending_approval", _("Pending Approval")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")
        PLANNED = "planned", _("Planned")
        DISPLACED = "displaced", _("Displaced by Emergency")
        CANCELLED = "cancelled", _("Cancelled")
        SUBMITTED = "submitted", _("Submitted")
        UNDER_REVIEW = "under_review", _("Under Review")
        SCHEDULED = "scheduled", _("Scheduled")
        ONGOING = "ongoing", _("Ongoing")
        COMPLETED = "completed", _("Completed")
        POSTPONED = "postponed", _("Postponed")
        EMERGENCY = "emergency", _("Emergency")

    class Priority(models.TextChoices):
        NORMAL = "normal", _("Normal")
        HIGH = "high", _("High")
        EMERGENCY = "emergency", _("Emergency Override")

    class DisplayVisibility(models.TextChoices):
        FULL = "full", _("Full (Show Event Details)")
        GENERIC = "generic", _("Generic (Show 'Private Meeting')")
        HIDDEN = "hidden", _("Hidden (Show Occupied Only)")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("title"), max_length=255)
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name=_("event type"),
    )
    description = models.TextField(_("description"), blank=True)

    venue = models.ForeignKey(
        "venues.Venue",
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name=_("venue"),
    )

    planned_date = models.DateField(_("planned date"))
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"))

    responsible_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="responsible_events",
        verbose_name=_("responsible employee"),
    )
    management_responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="management_events",
        verbose_name=_("management responsible"),
    )

    organizing_organizations = models.ManyToManyField(
        "organizations.Organization",
        blank=True,
        related_name="events",
        verbose_name=_("organizing organizations"),
    )
    sponsors = models.ManyToManyField(
        "organizations.Sponsor",
        blank=True,
        related_name="events",
        verbose_name=_("sponsors"),
    )

    zoom_url = models.URLField(_("Zoom / Meeting URL"), blank=True)
    registration_url = models.URLField(_("Registration URL"), blank=True)

    status = models.CharField(
        _("status"),
        max_length=24,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    priority = models.CharField(
        _("priority"),
        max_length=24,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    display_visibility = models.CharField(
        _("display visibility"),
        max_length=16,
        choices=DisplayVisibility.choices,
        default=DisplayVisibility.FULL,
    )

    expected_attendees = models.PositiveIntegerField(
        _("expected attendees"),
        default=1,
        validators=[MinValueValidator(1)],
    )
    notes = models.TextField(_("notes"), blank=True)

    class ProgramSource(models.TextChoices):
        PDF = "pdf", _("PDF File")
        MANUAL = "manual", _("Manual Agenda")

    # Phase 3 Workflow Audit & Emergency Fields
    submitted_at = models.DateTimeField(_("submitted at"), null=True, blank=True)
    reviewed_at = models.DateTimeField(_("reviewed at"), null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_events",
        verbose_name=_("reviewed by"),
    )
    rejection_reason = models.TextField(_("rejection reason"), blank=True, default="")
    emergency_justification = models.TextField(
        _("emergency justification"), blank=True, default=""
    )
    displaced_by_event = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="displaced_events",
        verbose_name=_("displaced by event"),
    )

    # Phase 4 Program & Public Page Fields
    program_source = models.CharField(
        _("program source"),
        max_length=12,
        choices=ProgramSource.choices,
        default=ProgramSource.MANUAL,
    )
    program_pdf = models.FileField(
        _("program PDF"),
        upload_to="event_programs/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),
            validate_pdf_upload,
        ],
    )
    program_intro = models.TextField(_("program intro"), blank=True, default="")
    program_notes = models.TextField(_("program notes"), blank=True, default="")

    public_token = models.CharField(
        _("public token"),
        max_length=64,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )
    is_public_enabled = models.BooleanField(_("public page enabled"), default=True)

    # Phase 5 Event Check-in Configuration
    checkin_enabled = models.BooleanField(_("check-in enabled"), default=False)
    checkin_opens_at = models.DateTimeField(_("check-in opens at"), null=True, blank=True)
    checkin_closes_at = models.DateTimeField(_("check-in closes at"), null=True, blank=True)

    # Phase 7 personal staff reminder policy.
    reminders_enabled = models.BooleanField(_("Telegram reminders enabled"), default=True)
    reminder_7d = models.BooleanField(_("7 days before"), default=True)
    reminder_3d = models.BooleanField(_("3 days before"), default=True)
    reminder_1d = models.BooleanField(_("1 day before"), default=True)
    reminder_3h = models.BooleanField(_("3 hours before"), default=True)
    reminder_30m = models.BooleanField(_("30 minutes before"), default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
        verbose_name=_("created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_events",
        verbose_name=_("updated by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)


    class Meta:
        ordering = ("-planned_date", "start_time", "title")
        verbose_name = _("event")
        verbose_name_plural = _("events")
        indexes = [
            models.Index(fields=("venue", "planned_date", "status")),
            models.Index(fields=("planned_date", "status")),
            models.Index(fields=("status", "priority")),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.planned_date})"

    def save(self, *args, **kwargs):
        if not self.public_token:
            self.public_token = generate_public_token()
        super().save(*args, **kwargs)

    @property
    def weekday_name(self) -> str:
        if not self.planned_date:
            return ""
        lang = (translation.get_language() or "uz").split("-")[0]
        names = WEEKDAY_NAMES.get(lang, WEEKDAY_NAMES["uz"])
        return names[self.planned_date.weekday()]

    def weekday_name_for(self, language: str) -> str:
        names = WEEKDAY_NAMES.get(language, WEEKDAY_NAMES["uz"])
        return names[self.planned_date.weekday()] if self.planned_date else ""

    @property
    def start_datetime(self) -> datetime:
        dt = datetime.combine(self.planned_date, self.start_time)
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt

    @property
    def end_datetime(self) -> datetime:
        dt = datetime.combine(self.planned_date, self.end_time)
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt

    @property
    def duration_minutes(self) -> int:
        start_dt = datetime.combine(self.planned_date, self.start_time)
        end_dt = datetime.combine(self.planned_date, self.end_time)
        return max(0, int((end_dt - start_dt).total_seconds() / 60))

    @property
    def is_over_capacity(self) -> bool:
        if self.venue and self.expected_attendees:
            return self.expected_attendees > self.venue.capacity
        return False

    @property
    def is_publicly_accessible(self) -> bool:
        if not self.is_public_enabled:
            return False
        allowed_statuses = {
            Event.Status.APPROVED,
            Event.Status.PLANNED,
            Event.Status.SCHEDULED,
            Event.Status.ONGOING,
            Event.Status.COMPLETED,
        }
        return self.status in allowed_statuses

    @property
    def public_countdown_info(self) -> dict:
        import zoneinfo

        try:
            tashkent_tz = zoneinfo.ZoneInfo("Asia/Tashkent")
        except Exception:
            tashkent_tz = UTC

        now = timezone.now().astimezone(tashkent_tz)
        start_dt = datetime.combine(self.planned_date, self.start_time, tzinfo=tashkent_tz)
        end_dt = datetime.combine(self.planned_date, self.end_time, tzinfo=tashkent_tz)

        if now < start_dt:
            diff = start_dt - now
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, _m = divmod(remainder, 60)
            state = "upcoming"
            if days > 0:
                text = str(_("Starts in %(days)d days")) % {"days": days}
            elif hours > 0:
                text = str(_("Starts in %(hours)d hours %(minutes)d minutes")) % {
                    "hours": hours,
                    "minutes": minutes,
                }
            else:
                text = str(_("Starts in %(minutes)d minutes")) % {"minutes": max(1, minutes)}
        elif start_dt <= now <= end_dt:
            diff = end_dt - now
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, _m = divmod(remainder, 60)
            state = "ongoing"
            if hours > 0:
                text = str(_("Now in progress — Ends in %(hours)d hours %(minutes)d minutes")) % {
                    "hours": hours,
                    "minutes": minutes,
                }
            else:
                msg = str(_("Now in progress — Ends in %(minutes)d minutes"))
                text = msg % {"minutes": max(1, minutes)}
        else:
            state = "completed"
            text = str(_("Event completed"))

        return {
            "state": state,
            "text": text,
            "start_iso": start_dt.isoformat(),
            "end_iso": end_dt.isoformat(),
        }

    @property
    def effective_checkin_opens_at(self) -> datetime:
        if self.checkin_opens_at:
            return self.checkin_opens_at
        return self.start_datetime - timedelta(minutes=60)

    @property
    def effective_checkin_closes_at(self) -> datetime:
        if self.checkin_closes_at:
            return self.checkin_closes_at
        return self.end_datetime

    def checkin_status(self, now=None) -> dict:
        if now is None:
            now = timezone.now()

        if not self.is_publicly_accessible:
            return {
                "eligible": False,
                "code": "not_public",
                "reason": _("This event page is not currently published or unavailable."),
            }

        if not self.checkin_enabled:
            return {
                "eligible": False,
                "code": "not_enabled",
                "reason": _("Check-in is not enabled for this event."),
            }

        opens_at = self.effective_checkin_opens_at
        closes_at = self.effective_checkin_closes_at

        if now < opens_at:
            return {
                "eligible": False,
                "code": "not_open",
                "reason": _("Check-in hali ochilmagan."),
            }

        if now > closes_at:
            return {
                "eligible": False,
                "code": "closed",
                "reason": _("Check-in yakunlangan."),
            }

        return {
            "eligible": True,
            "code": "eligible",
            "reason": _("Check-in open."),
        }


class Speaker(models.Model):
    full_name = models.CharField(_("full name"), max_length=255)
    title = models.CharField(_("title / position"), max_length=255, blank=True)
    organization = models.CharField(_("organization"), max_length=255, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    bio = models.TextField(_("bio"), blank=True)
    photo = models.ImageField(
        _("photo"),
        upload_to="speakers/",
        null=True,
        blank=True,
        validators=[validate_image_upload],
    )
    email = models.EmailField(_("email"), blank=True)  # Private field
    public_profile_enabled = models.BooleanField(_("public profile enabled"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ("full_name",)
        verbose_name = _("speaker")
        verbose_name_plural = _("speakers")

    def __str__(self) -> str:
        return self.full_name


class EventProgramItem(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="program_items",
        verbose_name=_("event"),
    )
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"))
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    speaker = models.ForeignKey(
        Speaker,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="program_items",
        verbose_name=_("speaker"),
    )
    speaker_name_override = models.CharField(
        _("speaker name override"), max_length=255, blank=True, default=""
    )
    sort_order = models.PositiveIntegerField(_("sort order"), default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ("sort_order", "start_time")
        verbose_name = _("program item")
        verbose_name_plural = _("program items")

    def __str__(self) -> str:
        return f"{self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')} {self.title}"

    @property
    def speaker_display_name(self) -> str:
        if self.speaker and self.speaker.public_profile_enabled:
            return self.speaker.full_name
        return self.speaker_name_override
