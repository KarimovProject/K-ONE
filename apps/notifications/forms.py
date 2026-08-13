from django import forms
from django.utils.translation import gettext_lazy as _

from apps.events.models import Event


class EventReminderForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "reminders_enabled",
            "reminder_7d",
            "reminder_3d",
            "reminder_1d",
            "reminder_3h",
            "reminder_30m",
        )
        labels = {
            "reminders_enabled": _("Enable Telegram reminders"),
            "reminder_7d": _("7 days before"),
            "reminder_3d": _("3 days before"),
            "reminder_1d": _("1 day before"),
            "reminder_3h": _("3 hours before"),
            "reminder_30m": _("30 minutes before"),
        }
