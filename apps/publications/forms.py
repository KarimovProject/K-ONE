from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.publications.models import Publication


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = (
            "platform",
            "language",
            "headline",
            "short_description",
            "caption",
            "banner_template",
            "include_qr",
            "include_sponsors",
            "scheduled_for",
        )
        labels = {
            "platform": _("Platform"),
            "language": _("Language"),
            "headline": _("Headline"),
            "short_description": _("Short description"),
            "caption": _("Caption"),
            "banner_template": _("Banner template"),
            "include_qr": _("Include QR code"),
            "include_sponsors": _("Include sponsors"),
            "scheduled_for": _("Scheduled for"),
        }
        widgets = {
            "short_description": forms.Textarea(attrs={"rows": 3}),
            "caption": forms.Textarea(attrs={"rows": 8}),
            "scheduled_for": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean_scheduled_for(self):
        value = self.cleaned_data.get("scheduled_for")
        if value and value <= timezone.now():
            raise forms.ValidationError("Publication time must be in the future.")
        return value
