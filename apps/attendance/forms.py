from django import forms
from django.utils.translation import gettext_lazy as _

from apps.events.models import Event


class EventCheckinConfigForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("checkin_enabled", "checkin_opens_at", "checkin_closes_at")
        widgets = {
            "checkin_opens_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "checkin_closes_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        opens_at = cleaned_data.get("checkin_opens_at")
        closes_at = cleaned_data.get("checkin_closes_at")

        if opens_at and closes_at and closes_at <= opens_at:
            self.add_error("checkin_closes_at", _("Check-in close time must be after open time."))
        return cleaned_data


class StaffManualCheckinForm(forms.Form):
    attendee_name = forms.CharField(
        label=_("Full Name / F.I.Sh."),
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": _("e.g. Abdullayev Jasur"), "data-testid": "manual-name-input"}
        ),
    )
    attendee_organization = forms.CharField(
        label=_("Organization / Tashkilot"),
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("e.g. Tashkent State Medical University"),
                "data-testid": "manual-org-input",
            }
        ),
    )
    attendee_role = forms.CharField(
        label=_("Role / Title"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("e.g. Senior Researcher")}),
    )


class PublicCheckinForm(forms.Form):
    attendee_name = forms.CharField(
        label=_("Full Name / F.I.Sh."),
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": _("F.I.Sh. (ixtiyoriy)"), "data-testid": "public-checkin-name"}
        ),
    )
    attendee_organization = forms.CharField(
        label=_("Organization / Tashkilot"),
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Tashkilot nomi (ixtiyoriy)"),
                "data-testid": "public-checkin-org",
            }
        ),
    )
