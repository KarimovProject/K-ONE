from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "preferred_language")
        labels = {
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "email": _("Email"),
            "preferred_language": _("Preferred language"),
        }

