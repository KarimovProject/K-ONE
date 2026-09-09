from django.urls import path
from apps.audit.views import AdminAuditLogView

app_name = "audit"
urlpatterns = [
    path("view-logs/", AdminAuditLogView.as_view(), name="view-logs"),
]
