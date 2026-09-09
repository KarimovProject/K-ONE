from django import forms
from django.utils.translation import gettext_lazy as _

from apps.events.models import Event
from apps.notifications.models import TelegramChannelSettings


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


class TelegramChannelSettingsForm(forms.ModelForm):
    class Meta:
        model = TelegramChannelSettings
        fields = ("label", "chat_id", "is_enabled")
        labels = {
            "label": _("Channel/group name"),
            "chat_id": _("Chat ID"),
            "is_enabled": _("Send event publications to this channel/group"),
        }
        widgets = {
            "label": forms.TextInput(attrs={"placeholder": _("e.g. K-ONE Events Channel")}),
            "chat_id": forms.TextInput(attrs={"placeholder": "-1001234567890"}),
        }
        help_texts = {
            "chat_id": _(
                "The numeric Telegram chat ID of the channel or group "
                "(add the bot as an admin there first)."
            ),
        }
