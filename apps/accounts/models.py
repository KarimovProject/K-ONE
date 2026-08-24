from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        INTERNATIONAL_ADMIN = "international_admin", "International Department Admin"
        RESPONSIBLE_EMPLOYEE = "responsible_employee", "Responsible Employee"
        MANAGEMENT_RESPONSIBLE = "management_responsible", "Management Responsible"
        LEADERSHIP_VIEWER = "leadership_viewer", "Leadership Viewer"
        CONTENT_MANAGER = "content_manager", "Content / SMM Manager"
        RECEPTION_OPERATOR = "reception_operator", "Reception / Check-in Operator"

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

    def has_capability(self, capability: str) -> bool:
        from apps.accounts.rbac import user_has_capability

        return user_has_capability(self, capability)
