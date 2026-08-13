from django import forms
from django.utils.translation import gettext_lazy as _

from apps.venues.models import Venue


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = (
            "code",
            "name_uz",
            "name_ru",
            "name_en",
            "description",
            "location",
            "capacity",
            "working_start",
            "working_end",
            "is_active",
            "display_enabled",
            "photo",
            "sort_order",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "working_start": forms.TimeInput(attrs={"type": "time"}),
            "working_end": forms.TimeInput(attrs={"type": "time"}),
            "photo": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        }

    def clean_code(self) -> str:
        return self.cleaned_data["code"].strip().upper()

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("working_start")
        end = cleaned_data.get("working_end")
        if start and end and end <= start:
            self.add_error("working_end", _("Working end must be later than working start."))
        return cleaned_data
