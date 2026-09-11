from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView


class AdminAuditLogView(UserPassesTestMixin, TemplateView):
    template_name = "audit/admin_audit_log.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_file = getattr(settings, "BASE_DIR", Path(".")) / "logs" / "admin_audit.log"
        logs = []
        if log_file.exists():
            with open(log_file, encoding="utf-8") as f:
                # Read last 1000 lines for performance
                lines = f.readlines()
                logs = lines[-1000:]
        context["logs"] = reversed(logs)
        return context
