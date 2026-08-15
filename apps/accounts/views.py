from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from apps.accounts.forms import ProfileForm
from apps.accounts.models import User


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Profile updated successfully."))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "nav_key": "profile",
                "assigned_count": user.responsible_events.count(),
                "management_count": user.management_events.count(),
                "telegram_connected": bool(
                    getattr(user, "telegram_connection", None)
                    and user.telegram_connection.is_active
                ),
            }
        )
        return context
