from datetime import timedelta

from django import forms
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.selectors import selectable_staff
from apps.events.models import Event, EventType
from apps.organizations.models import Organization, Sponsor
from apps.publications.models import Publication
from apps.venues.models import Venue


class ReportFilterForm(forms.Form):
    class Period(models.TextChoices):
        TODAY = "today", _("Today")
        WEEK = "week", _("This Week")
        MONTH = "month", _("This Month")
        QUARTER = "quarter", _("This Quarter")
        YEAR = "year", _("This Year")
        CUSTOM = "custom", _("Custom Date Range")

    period = forms.ChoiceField(
        label=_("Period"), choices=Period.choices, required=False, initial=Period.MONTH
    )
    start_date = forms.DateField(
        label=_("Start date"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_date = forms.DateField(
        label=_("End date"),
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    venue = forms.ModelChoiceField(Venue.objects.all(), label=_("Venue"), required=False)
    event_type = forms.ModelChoiceField(
        EventType.objects.all(), label=_("Event type"), required=False
    )
    status = forms.ChoiceField(
        label=_("Status"),
        choices=(("", _("All statuses")), *Event.Status.choices),
        required=False,
    )
    priority = forms.ChoiceField(
        label=_("Priority"),
        choices=(("", _("All priorities")), *Event.Priority.choices),
        required=False,
    )
    responsible = forms.ModelChoiceField(selectable_staff(), label=_("Responsible"), required=False)
    organization = forms.ModelChoiceField(
        Organization.objects.all(), label=_("Organization"), required=False
    )
    sponsor = forms.ModelChoiceField(Sponsor.objects.all(), label=_("Sponsor"), required=False)
    publication_platform = forms.ChoiceField(
        label=_("Publication platform"),
        choices=(("", _("All platforms")), *Publication.Platform.choices),
        required=False,
    )
    language = forms.ChoiceField(
        label=_("Language"),
        choices=(("", _("Current language")), ("uz", "UZ"), ("ru", "RU"), ("en", "EN")),
        required=False,
    )

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("start_date"), cleaned.get("end_date")
        explicit_range = bool(start and end)
        if cleaned.get("period") == self.Period.CUSTOM and not explicit_range:
            raise forms.ValidationError(_("Custom range requires both dates."))
        if explicit_range:
            if end < start:
                raise forms.ValidationError(_("End date must not precede start date."))
            if end - start > timedelta(days=730):
                raise forms.ValidationError(_("Report range cannot exceed two years."))
        return cleaned

    def date_range(self):
        today = timezone.localdate()
        start, end = self.cleaned_data.get("start_date"), self.cleaned_data.get("end_date")
        if start and end:
            # Explicit dates always win — the period selector is only a
            # convenience shortcut, so a user who typed real dates should
            # never have them silently overridden by a stale period choice.
            return start, end
        period = self.cleaned_data.get("period") or self.Period.MONTH
        if period == self.Period.TODAY:
            return today, today
        if period == self.Period.WEEK:
            start = today - timedelta(days=today.weekday())
            return start, start + timedelta(days=6)
        if period == self.Period.QUARTER:
            month = ((today.month - 1) // 3) * 3 + 1
            start = today.replace(month=month, day=1)
            end_month = month + 2
            following = (
                start.replace(year=start.year + 1, month=1)
                if end_month == 12
                else start.replace(month=end_month + 1)
            )
            return start, following - timedelta(days=1)
        if period == self.Period.YEAR:
            return today.replace(month=1, day=1), today.replace(month=12, day=31)
        start = today.replace(day=1)
        following = (
            start.replace(year=start.year + 1, month=1)
            if start.month == 12
            else start.replace(month=start.month + 1)
        )
        return start, following - timedelta(days=1)
