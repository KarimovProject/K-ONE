from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import DoctorProfile, StaffUnavailability, User


class ProfileForm(forms.ModelForm):
    remove_avatar = forms.BooleanField(label=_("Remove current photo"), required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "preferred_language", "avatar")
        labels = {
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "email": _("Email"),
            "preferred_language": _("Preferred language"),
            "avatar": _("Profile photo"),
        }
        widgets = {
            "avatar": forms.FileInput(
                attrs={"accept": "image/png,image/jpeg,image/webp", "id": "id_avatar"}
            ),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get("remove_avatar") and not self.files.get("avatar"):
            if instance.avatar:
                instance.avatar.delete(save=False)
            instance.avatar = None
        if commit:
            instance.save()
        return instance


class DoctorRegistrationForm(UserCreationForm):
    """Self-registration for doctors. Accounts are created inactive and wait
    for an administrator to approve them in Django Admin (flip is_active)."""

    first_name = forms.CharField(
        label=_("First name"), max_length=150, widget=forms.TextInput(attrs={"class": "auth-input"})
    )
    last_name = forms.CharField(
        label=_("Last name"), max_length=150, widget=forms.TextInput(attrs={"class": "auth-input"})
    )
    email = forms.EmailField(
        label=_("Email"), widget=forms.EmailInput(attrs={"class": "auth-input"})
    )
    specialty = forms.CharField(
        label=_("Specialty"), max_length=150, widget=forms.TextInput(attrs={"class": "auth-input"})
    )
    workplace = forms.CharField(
        label=_("Workplace"), max_length=200, widget=forms.TextInput(attrs={"class": "auth-input"})
    )
    position = forms.CharField(
        label=_("Position / academic degree"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "auth-input"}),
    )
    phone = forms.CharField(
        label=_("Phone"), max_length=32, widget=forms.TextInput(attrs={"class": "auth-input"})
    )
    languages = forms.CharField(
        label=_("Languages spoken"),
        max_length=150,
        required=False,
        help_text=_("e.g. UZ, RU, EN"),
        widget=forms.TextInput(attrs={"class": "auth-input"}),
    )
    bio = forms.CharField(
        label=_("Short bio"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "class": "auth-input"}),
    )
    photo = forms.ImageField(
        label=_("Photo"),
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "auth-input"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("username", "password1", "password2"):
            self.fields[name].widget.attrs["class"] = "auth-input"

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_("This username is already taken."))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.DOCTOR
        user.is_active = False
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialty=self.cleaned_data["specialty"],
                workplace=self.cleaned_data["workplace"],
                position=self.cleaned_data["position"],
                phone=self.cleaned_data["phone"],
                languages=self.cleaned_data["languages"],
                bio=self.cleaned_data["bio"],
                photo=self.cleaned_data.get("photo") or None,
            )
        return user


MAX_UNAVAILABILITY_SLOTS_PER_YEAR = 4


class StaffUnavailabilityForm(forms.ModelForm):
    reason = forms.CharField(
        label=_("Reason"),
        required=True,
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control", "required": "required"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = StaffUnavailability
        fields = ("start_date", "start_time", "end_date", "end_time", "reason")
        common_attrs = {"class": "form-control", "required": "required"}
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", **common_attrs}),
            "start_time": forms.TimeInput(attrs={"type": "time", **common_attrs}),
            "end_date": forms.DateInput(attrs={"type": "date", **common_attrs}),
            "end_time": forms.TimeInput(attrs={"type": "time", **common_attrs}),
        }
        labels = {
            "start_date": _("Start date"),
            "start_time": _("Start time"),
            "end_date": _("End date"),
            "end_time": _("End time"),
        }

    def clean_reason(self):
        reason = self.cleaned_data["reason"].strip()
        if not reason:
            raise forms.ValidationError(_("Please explain why you're busy at this time."))
        return reason

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        start_time = cleaned_data.get("start_time")
        end_date = cleaned_data.get("end_date")
        end_time = cleaned_data.get("end_time")
        if start_date and start_time and end_date and end_time:
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)
            if end_dt <= start_dt:
                self.add_error(
                    "end_date", _("End date/time must be later than start date/time.")
                )

        if start_date and self.user is not None:
            existing_count = StaffUnavailability.objects.filter(
                user=self.user, start_date__year=start_date.year
            ).count()
            if existing_count >= MAX_UNAVAILABILITY_SLOTS_PER_YEAR:
                raise forms.ValidationError(
                    _(
                        "You can mark yourself busy at most %(limit)d times per year. "
                        "You've already used all %(limit)d for %(year)d — remove an "
                        "existing entry first if you need to add a new one."
                    )
                    % {"limit": MAX_UNAVAILABILITY_SLOTS_PER_YEAR, "year": start_date.year}
                )
        return cleaned_data
