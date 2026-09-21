from django.db import models
from django.utils.translation import gettext_lazy as _

from config.validators import validate_image_upload, validate_phone_number


class Organization(models.Model):
    class Type(models.TextChoices):
        LOCAL = "local", _("Local organization")
        FOREIGN = "foreign", _("Foreign organization")
        PARTNER = "partner", _("Partner organization")

    name = models.CharField(_("name"), max_length=255)
    short_name = models.CharField(_("short name"), max_length=100, blank=True)
    organization_type = models.CharField(
        _("organization type"),
        max_length=16,
        choices=Type.choices,
        default=Type.LOCAL,
    )
    country = models.CharField(_("country"), max_length=120, blank=True)
    city = models.CharField(_("city"), max_length=120, blank=True)
    address = models.CharField(_("address"), max_length=255, blank=True)
    website = models.URLField(_("website"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(
        _("phone"), max_length=48, blank=True, validators=[validate_phone_number]
    )
    contact_person = models.CharField(_("contact person"), max_length=160, blank=True)
    logo = models.FileField(
        _("logo"),
        upload_to="organizations/%Y/%m/",
        validators=[validate_image_upload],
        blank=True,
    )
    notes = models.TextField(_("notes"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")
        indexes = [models.Index(fields=("is_active", "organization_type"))]

    def __str__(self) -> str:
        return self.name


class Sponsor(models.Model):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    website = models.URLField(_("website"), blank=True)
    contact_person = models.CharField(_("contact person"), max_length=160, blank=True)
    phone = models.CharField(
        _("phone"), max_length=48, blank=True, validators=[validate_phone_number]
    )
    email = models.EmailField(_("email"), blank=True)
    logo = models.FileField(
        _("logo"),
        upload_to="sponsors/%Y/%m/",
        validators=[validate_image_upload],
        blank=True,
    )
    is_active = models.BooleanField(_("active"), default=True)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("sponsor")
        verbose_name_plural = _("sponsors")
        indexes = [models.Index(fields=("is_active",))]

    def __str__(self) -> str:
        return self.name
