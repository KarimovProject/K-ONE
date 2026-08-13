from django.urls import path

from apps.notifications import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="list"),
    path("telegram/", views.TelegramSettingsView.as_view(), name="telegram-settings"),
    path("telegram/link/", views.TelegramLinkView.as_view(), name="telegram-link"),
    path(
        "telegram/disconnect/",
        views.TelegramDisconnectView.as_view(),
        name="telegram-disconnect",
    ),
    path("telegram/test/", views.TelegramTestView.as_view(), name="telegram-test"),
    path(
        "telegram/events/<uuid:pk>/",
        views.EventReminderSettingsView.as_view(),
        name="event-reminders",
    ),
    path("<int:pk>/read/", views.NotificationMarkReadView.as_view(), name="mark-read"),
]
