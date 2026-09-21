from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.validators import validate_image_upload, validate_phone_number


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        INTERNATIONAL_ADMIN = "international_admin", "International Department Admin"
        RESPONSIBLE_EMPLOYEE = "responsible_employee", "Responsible Employee"
        MANAGEMENT_RESPONSIBLE = "management_responsible", "Management Responsible"
        LEADERSHIP_VIEWER = "leadership_viewer", "Leadership Viewer"
        CONTENT_MANAGER = "content_manager", "Content / SMM Manager"
        RECEPTION_OPERATOR = "reception_operator", "Reception / Check-in Operator"
        DOCTOR = "doctor", "Doctor"

    class Language(models.TextChoices):
        UZBEK = "uz", "O‘zbekcha"
        RUSSIAN = "ru", "Русский"
        ENGLISH = "en", "English"

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.RESPONSIBLE_EMPLOYEE)
    preferred_language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.UZBEK,
    )
    avatar = models.ImageField(
        _("avatar"), upload_to="avatars/%Y/%m/", blank=True, validators=[validate_image_upload]
    )
    approved_at = models.DateTimeField(
        _("approved at"),
        null=True,
        blank=True,
        help_text=_("When an administrator first activated this account."),
    )

    def has_capability(self, capability: str) -> bool:
        from apps.accounts.rbac import user_has_capability

        return user_has_capability(self, capability)

    @property
    def initials(self) -> str:
        letters = (self.first_name[:1] + self.last_name[:1]).strip().upper()
        if letters:
            return letters
        return (self.username[:2] or "?").upper()


class DoctorProfile(models.Model):
    """Extra questionnaire fields collected at doctor self-registration."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        verbose_name=_("user"),
    )
    specialty = models.CharField(_("specialty"), max_length=150)
    workplace = models.CharField(_("workplace"), max_length=200)
    position = models.CharField(_("position / academic degree"), max_length=150, blank=True)
    phone = models.CharField(_("phone"), max_length=32, validators=[validate_phone_number])
    languages = models.CharField(
        _("languages spoken"), max_length=150, blank=True, help_text=_("e.g. UZ, RU, EN")
    )
    license_number = models.CharField(_("license / ID number"), max_length=64, blank=True)
    bio = models.TextField(_("short bio"), blank=True)
    photo = models.ImageField(
        _("photo"), upload_to="doctors/%Y/%m/", blank=True, validators=[validate_image_upload]
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("doctor profile")
        verbose_name_plural = _("doctor profiles")

    def __str__(self) -> str:
        return f"{self.user.get_full_name() or self.user.username} — {self.specialty}"


class StaffUnavailability(models.Model):
    """A self-declared busy period with a required reason. May span more
    than one calendar day (e.g. start_date 2026-09-10 14:00 through end_date
    2026-09-12 09:00)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="unavailability_slots",
        verbose_name=_("user"),
    )
    start_date = models.DateField(_("start date"))
    start_time = models.TimeField(_("start time"))
    end_date = models.DateField(_("end date"))
    end_time = models.TimeField(_("end time"))
    reason = models.TextField(_("reason"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        ordering = ("-start_date", "-start_time")
        verbose_name = _("staff unavailability")
        verbose_name_plural = _("staff unavailability")
        indexes = [models.Index(fields=["user", "start_date", "end_date"])]

    def __str__(self) -> str:
        return f"{self.user}: {self.start_date} {self.start_time} – {self.end_date} {self.end_time}"

    @property
    def start_datetime(self) -> datetime:
        return datetime.combine(self.start_date, self.start_time)

    @property
    def end_datetime(self) -> datetime:
        return datetime.combine(self.end_date, self.end_time)
