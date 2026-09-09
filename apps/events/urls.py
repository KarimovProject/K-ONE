from django.urls import path

from apps.attendance import views as attendance_views
from apps.events import views, wizard

event_type_patterns = (
    [
        path("", views.EventTypeListView.as_view(), name="list"),
        path("new/", views.EventTypeCreateView.as_view(), name="create"),
        path("<int:pk>/", views.EventTypeDetailView.as_view(), name="detail"),
        path("<int:pk>/edit/", views.EventTypeUpdateView.as_view(), name="edit"),
        path("<int:pk>/delete/", views.EventTypeDeleteView.as_view(), name="delete"),
    ],
    "event-types",
)

event_patterns = (
    [
        path("", views.EventListView.as_view(), name="list"),
        path("wizard/", wizard.EventWizardView.as_view(), name="wizard"),
        path("approvals/", views.EventApprovalListView.as_view(), name="approval-list"),
        path("displaced/", views.DisplacedEventsListView.as_view(), name="displaced-list"),
        path("<uuid:pk>/", views.EventDetailView.as_view(), name="detail"),
        path("<uuid:pk>/edit/", views.EventUpdateView.as_view(), name="edit"),
        path("<uuid:pk>/cancel/", views.EventCancelView.as_view(), name="cancel"),
        path("<uuid:pk>/delete/", views.EventDeleteView.as_view(), name="delete"),
        path("<uuid:pk>/submit/", views.EventSubmitApprovalView.as_view(), name="submit"),
        path("<uuid:pk>/approve/", views.EventApproveView.as_view(), name="approve"),
        path("<uuid:pk>/reject/", views.EventRejectView.as_view(), name="reject"),
        path("<uuid:pk>/override/", views.EventOverrideView.as_view(), name="override"),
        path("<uuid:pk>/resubmit/", views.EventResubmitView.as_view(), name="resubmit"),
        path("<uuid:pk>/postpone/", views.EventPostponeView.as_view(), name="postpone"),
        path("<uuid:pk>/reschedule/", views.EventRescheduleView.as_view(), name="reschedule"),
        path(
            "<uuid:pk>/emergency-override/",
            views.EventEmergencyOverrideView.as_view(),
            name="emergency-override",
        ),
        path("<uuid:pk>/program/", views.EventProgramEditView.as_view(), name="program"),
        path(
            "<uuid:pk>/attendance/",
            attendance_views.EventAttendanceView.as_view(),
            name="attendance",
        ),
        path(
            "<uuid:pk>/attendance/export.csv",
            attendance_views.EventAttendanceExportView.as_view(),
            name="attendance-export",
        ),
        path("<uuid:pk>/qr.png", views.EventQrCodePngView.as_view(), name="qr-png"),
        path("<uuid:pk>/qr.svg", views.EventQrCodeSvgView.as_view(), name="qr-svg"),
        path("<uuid:pk>/print-qr/", views.EventPrintQrView.as_view(), name="print-qr"),
        path("speakers/", views.SpeakerListView.as_view(), name="speaker-list"),
        path("speakers/create/", views.SpeakerCreateView.as_view(), name="speaker-create"),
        path("speakers/<int:pk>/edit/", views.SpeakerUpdateView.as_view(), name="speaker-edit"),
    ],
    "events",
)

app_name = "events"
urlpatterns = [
    path("", views.EventListView.as_view(), name="list"),
    path("wizard/", wizard.EventWizardView.as_view(), name="wizard"),
    path("approvals/", views.EventApprovalListView.as_view(), name="approval-list"),
    path("displaced/", views.DisplacedEventsListView.as_view(), name="displaced-list"),
    path("speakers/", views.SpeakerListView.as_view(), name="speaker-list"),
    path("speakers/create/", views.SpeakerCreateView.as_view(), name="speaker-create"),
    path("speakers/<int:pk>/edit/", views.SpeakerUpdateView.as_view(), name="speaker-edit"),
    path("<uuid:pk>/", views.EventDetailView.as_view(), name="detail"),
    path("<uuid:pk>/edit/", views.EventUpdateView.as_view(), name="edit"),
    path("<uuid:pk>/cancel/", views.EventCancelView.as_view(), name="cancel"),
    path("<uuid:pk>/delete/", views.EventDeleteView.as_view(), name="delete"),
    path("<uuid:pk>/submit/", views.EventSubmitApprovalView.as_view(), name="submit"),
    path("<uuid:pk>/approve/", views.EventApproveView.as_view(), name="approve"),
    path("<uuid:pk>/reject/", views.EventRejectView.as_view(), name="reject"),
    path("<uuid:pk>/override/", views.EventOverrideView.as_view(), name="override"),
    path("<uuid:pk>/resubmit/", views.EventResubmitView.as_view(), name="resubmit"),
    path("<uuid:pk>/postpone/", views.EventPostponeView.as_view(), name="postpone"),
    path("<uuid:pk>/reschedule/", views.EventRescheduleView.as_view(), name="reschedule"),
    path(
        "<uuid:pk>/emergency-override/",
        views.EventEmergencyOverrideView.as_view(),
        name="emergency-override",
    ),
    path("<uuid:pk>/program/", views.EventProgramEditView.as_view(), name="program"),
    path(
        "<uuid:pk>/attendance/",
        attendance_views.EventAttendanceView.as_view(),
        name="attendance",
    ),
    path(
        "<uuid:pk>/attendance/export.csv",
        attendance_views.EventAttendanceExportView.as_view(),
        name="attendance-export",
    ),
    path("<uuid:pk>/qr.png", views.EventQrCodePngView.as_view(), name="qr-png"),
    path("<uuid:pk>/qr.svg", views.EventQrCodeSvgView.as_view(), name="qr-svg"),
    path("<uuid:pk>/print-qr/", views.EventPrintQrView.as_view(), name="print-qr"),
]
