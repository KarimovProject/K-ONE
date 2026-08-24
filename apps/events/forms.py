from django import forms
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from apps.accounts.selectors import (
    management_responsible_users,
    responsible_employees,
    selectable_staff,
)
from apps.events.models import Event, EventProgramItem, EventType, Speaker
from apps.events.selectors import active_event_types
from apps.organizations.selectors import active_organizations, active_sponsors
from apps.venues.selectors import active_venues


class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = (
            "code",
            "name_uz",
            "name_ru",
            "name_en",
            "description",
            "color",
            "icon",
            "is_active",
            "requires_management_approval",
            "allows_emergency_override",
            "sort_order",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "color": forms.TextInput(attrs={"type": "color"}),
        }

    def clean_code(self) -> str:
        return self.cleaned_data["code"].strip().lower()


# --- Event Wizard Step Forms ---


class EventStep1Form(forms.Form):
    title = forms.CharField(
        label=_("Event Title"),
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": _("e.g., International Oncology Conference")}),
    )
    event_type = forms.ModelChoiceField(
        label=_("Event Type"),
        queryset=EventType.objects.none(),
    )
    display_visibility = forms.ChoiceField(
        label=_("Display / TV Visibility"),
        choices=Event.DisplayVisibility.choices,
        initial=Event.DisplayVisibility.FULL,
        required=False,
    )
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": _("Summary of event objectives and agenda..."),
            }
        ),
    )
    expected_attendees = forms.IntegerField(
        label=_("Expected Attendees"),
        min_value=1,
        initial=50,
        widget=forms.NumberInput(attrs={"min": 1}),
    )
    priority = forms.ChoiceField(
        label=_("Priority"),
        choices=Event.Priority.choices,
        initial=Event.Priority.NORMAL,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event_type"].queryset = active_event_types()


class EventStep2Form(forms.Form):
    planned_date = forms.DateField(
        label=_("Planned Date"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    start_time = forms.TimeField(
        label=_("Start Time"),
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    end_time = forms.TimeField(
        label=_("End Time"),
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    venue = forms.ModelChoiceField(
        label=_("Venue"),
        queryset=active_venues(),
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", _("End time must be later than start time."))
        return cleaned_data


class EventStep3Form(forms.Form):
    responsible_employee = forms.ModelChoiceField(
        label=_("Responsible Employee"),
        queryset=selectable_staff(),
    )
    management_responsible = forms.ModelChoiceField(
        label=_("Management Responsible Person"),
        queryset=selectable_staff(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        resps = responsible_employees()
        self.fields["responsible_employee"].queryset = (
            resps if resps.exists() else selectable_staff()
        )
        mgmts = management_responsible_users()
        self.fields["management_responsible"].queryset = (
            mgmts if mgmts.exists() else selectable_staff()
        )


class EventStep4Form(forms.Form):
    organizing_organizations = forms.ModelMultipleChoiceField(
        label=_("Organizing Organizations"),
        queryset=active_organizations(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select-multiple"}),
    )
    sponsors = forms.ModelMultipleChoiceField(
        label=_("Sponsors"),
        queryset=active_sponsors(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "select-multiple"}),
    )


class EventStep5Form(forms.Form):
    zoom_url = forms.URLField(
        label=_("Zoom / Meeting URL"),
        required=False,
        assume_scheme="https",
        widget=forms.URLInput(attrs={"placeholder": "https://zoom.us/j/..."}),
    )
    registration_url = forms.URLField(
        label=_("Registration URL"),
        required=False,
        assume_scheme="https",
        widget=forms.URLInput(attrs={"placeholder": "https://event.uz/register/..."}),
    )
    notes = forms.CharField(
        label=_("Internal Notes"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class EventUpdateForm(forms.ModelForm):
    zoom_url = forms.URLField(required=False, assume_scheme="https")
    registration_url = forms.URLField(required=False, assume_scheme="https")

    class Meta:
        model = Event
        fields = (
            "title",
            "event_type",
            "description",
            "venue",
            "planned_date",
            "start_time",
            "end_time",
            "responsible_employee",
            "management_responsible",
            "organizing_organizations",
            "sponsors",
            "zoom_url",
            "registration_url",
            "status",
            "priority",
            "expected_attendees",
            "notes",
        )


class EventCancelForm(forms.Form):
    reason = forms.CharField(
        label=_("Cancellation Reason"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": _("Provide brief rationale for event cancellation..."),
            }
        ),
    )


class EventRejectForm(forms.Form):
    reason = forms.CharField(
        label=_("Rejection Rationale"),
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": _("Provide clear rationale and feedback for rejection..."),
            }
        ),
    )


class EventEmergencyOverrideForm(forms.Form):
    justification = forms.CharField(
        label=_("Emergency Justification"),
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": _(
                    "Explain state-level emergency rationale justifying venue displacement..."
                ),
            }
        ),
    )


class EventPostponeForm(forms.Form):
    reason = forms.CharField(
        label=_("Postponement Reason"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": _("Provide rationale for postponing this event..."),
            }
        ),
    )


class EventRescheduleForm(forms.Form):
    planned_date = forms.DateField(
        label=_("New Planned Date"),
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    start_time = forms.TimeField(
        label=_("New Start Time"),
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    end_time = forms.TimeField(
        label=_("New End Time"),
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    venue = forms.ModelChoiceField(
        label=_("Venue"),
        queryset=active_venues(),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", _("End time must be later than start time."))
        return cleaned_data


# --- Phase 4 Program & Speaker Forms ---


class EventProgramModeForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("program_source", "program_intro", "program_notes")
        widgets = {
            "program_source": forms.RadioSelect,
            "program_intro": forms.Textarea(attrs={"rows": 3}),
            "program_notes": forms.Textarea(attrs={"rows": 3}),
        }


class EventProgramPdfForm(forms.Form):
    program_pdf = forms.FileField(
        label=_("Program PDF Document"),
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        widget=forms.FileInput(attrs={"accept": ".pdf"}),
    )


class EventProgramItemForm(forms.ModelForm):
    class Meta:
        model = EventProgramItem
        fields = (
            "start_time",
            "end_time",
            "title",
            "description",
            "speaker",
            "speaker_name_override",
            "sort_order",
        )
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = (
            "full_name",
            "title",
            "organization",
            "country",
            "bio",
            "photo",
            "email",
            "public_profile_enabled",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
