from django.urls import path

from apps.reporting import views

app_name = "reporting"

urlpatterns = [
    path("", views.ReportDashboardView.as_view(), name="dashboard"),
    path("export/csv/", views.ReportExportView.as_view(format="csv"), name="csv"),
    path("export/xlsx/", views.ReportExportView.as_view(format="xlsx"), name="xlsx"),
    path("export/pdf/", views.ReportExportView.as_view(format="pdf"), name="pdf"),
]
