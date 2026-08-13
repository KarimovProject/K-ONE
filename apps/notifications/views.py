from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, ListView, TemplateView

from apps.accounts.models import User
from apps.accounts.rbac import Capability, user_has_capability
from apps.audit.services import log_audit_event
from apps.events.models import Event
from apps.notifications.forms import EventReminderForm
from apps.notifications.models import Notification, TelegramConnection, TelegramDelivery
from apps.notifications.telegram.client import TelegramClient, TelegramError
from apps.notifications.telegram.linking import create_link_token


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def post(self, request):
        if "mark_all_read" in request.POST:
            Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return redirect("notifications:list")


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        if notif.target_url:
            return redirect(notif.target_url)
        return redirect("notifications:list")


class TelegramSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/telegram_settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connection = TelegramConnection.objects.filter(user=self.request.user).first()
        is_admin = self.request.user.is_superuser or self.request.user.role in (
            User.Role.SUPER_ADMIN,
            User.Role.INTERNATIONAL_ADMIN,
        )
        context.update(
            {
                "connection": connection,
                "telegram_enabled": settings.TELEGRAM_BOT_ENABLED,
                "bot_configured": bool(settings.TELEGRAM_BOT_TOKEN),
                "bot_username": settings.TELEGRAM_BOT_USERNAME,
                "is_telegram_admin": is_admin,
                "last_success": TelegramDelivery.objects.filter(
                    status=TelegramDelivery.Status.SENT
                ).first()
                if is_admin
                else None,
                "recent_failures": TelegramDelivery.objects.filter(
                    status=TelegramDelivery.Status.FAILED
                )[:5]
                if is_admin
                else [],
                "telegram_link_url": self.request.session.pop("telegram_link_url", ""),
                "nav_key": "telegram",
            }
        )
        return context


class TelegramLinkView(LoginRequiredMixin, View):
    def post(self, request):
        key = f"telegram-link:{request.user.pk}"
        if not cache.add(key, "1", timeout=60):
            messages.warning(request, "Please wait before creating another link.")
            return redirect("notifications:telegram-settings")
        if not settings.TELEGRAM_BOT_ENABLED or not settings.TELEGRAM_BOT_USERNAME:
            messages.error(request, "Telegram integration is not configured.")
            return redirect("notifications:telegram-settings")
        token = create_link_token(request.user)
        request.session["telegram_link_url"] = (
            f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={token}"
        )
        return redirect("notifications:telegram-settings")


class TelegramDisconnectView(LoginRequiredMixin, View):
    def post(self, request):
        TelegramConnection.objects.filter(user=request.user).delete()
        log_audit_event("telegram.connection_removed", actor=request.user, target=request.user)
        messages.success(request, "Telegram disconnected.")
        return redirect("notifications:telegram-settings")


class TelegramTestView(LoginRequiredMixin, View):
    def post(self, request):
        key = f"telegram-test:{request.user.pk}"
        if not cache.add(key, "1", timeout=60):
            messages.warning(request, "Please wait before sending another test.")
            return redirect("notifications:telegram-settings")
        connection = get_object_or_404(TelegramConnection, user=request.user, is_active=True)
        try:
            TelegramClient().send_message(connection.chat_id, "✅ IEMS Telegram connection works.")
        except TelegramError:
            messages.error(request, "Test message could not be sent.")
        else:
            log_audit_event("telegram.test_sent", actor=request.user, target=request.user)
            messages.success(request, "Test message sent.")
        return redirect("notifications:telegram-settings")


class EventReminderSettingsView(LoginRequiredMixin, FormView):
    template_name = "notifications/event_reminders.html"
    form_class = EventReminderForm

    def dispatch(self, request, *args, **kwargs):
        if not (
            request.user.is_superuser or user_has_capability(request.user, Capability.MANAGE_EVENTS)
        ):
            raise PermissionDenied
        self.event = get_object_or_404(Event, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.event
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Telegram reminder policy updated.")
        return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "event": self.event,
                "deliveries": self.event.telegram_deliveries.select_related("recipient_user")[:20],
            }
        )
        return context
