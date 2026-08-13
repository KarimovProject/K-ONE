from django import forms
from django.utils import timezone

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
