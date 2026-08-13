from django import forms

from apps.organizations.models import Organization, Sponsor


class OrganizationForm(forms.ModelForm):
    website = forms.URLField(required=False, assume_scheme="https")

    class Meta:
        model = Organization
        fields = (
            "name",
            "short_name",
            "organization_type",
            "country",
            "city",
            "address",
            "website",
            "email",
            "phone",
            "contact_person",
            "logo",
            "notes",
            "is_active",
        )
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
            "logo": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        }


class SponsorForm(forms.ModelForm):
    website = forms.URLField(required=False, assume_scheme="https")

    class Meta:
        model = Sponsor
        fields = (
            "name",
            "description",
            "website",
            "contact_person",
            "phone",
            "email",
            "logo",
            "is_active",
            "notes",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "logo": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        }
