from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView

from apps.notifications.models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def post(self, request):
        if "mark_all_read" in request.POST:
            Notification.objects.filter(recipient=request.user, is_read=False).update(
                is_read=True
            )
        return redirect("notifications:list")


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        if notif.target_url:
            return redirect(notif.target_url)
        return redirect("notifications:list")
