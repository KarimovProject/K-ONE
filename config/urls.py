from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.attendance.views import PublicCheckinView
from apps.events.urls import event_type_patterns
from apps.events.views import CalendarView, PublicEventPageView, VenueLiveStatusView
from apps.organizations.urls import organization_patterns, sponsor_patterns
from apps.reporting.views import (
    LeadershipDashboardView,
    TvWallboardView,
    dashboard,
)
from config import health
from config.views import ThrottledLoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", ThrottledLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("health/", health.application_health, name="application-health"),
    path("health/database/", health.database_health, name="database-health"),
    path("health/redis/", health.redis_health, name="redis-health"),
    path("health/ready/", health.readiness_health, name="readiness-health"),
    path(
        "event/<str:public_token>/checkin/",
        PublicCheckinView.as_view(),
        name="public-event-checkin",
    ),
    path("event/<str:public_token>/", PublicEventPageView.as_view(), name="public-event-page"),
    path("events/", include("apps.events.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("publications/", include("apps.publications.urls")),
    path("reports/", include("apps.reporting.urls")),
    path("calendar/", CalendarView.as_view(), name="calendar"),
    path("leadership/", LeadershipDashboardView.as_view(), name="leadership-dashboard"),
    path("display/venues/", TvWallboardView.as_view(), name="tv-wallboard"),
    path("display/<str:token>/", TvWallboardView.as_view(), name="tv-wallboard-token"),

    path(
        "master-data/venues/live-status/",
        VenueLiveStatusView.as_view(),
        name="venue-live-status",
    ),
    path("master-data/venues/", include("apps.venues.urls")),
    path("master-data/event-types/", include(event_type_patterns)),
    path("master-data/organizations/", include(organization_patterns)),
    path("master-data/sponsors/", include(sponsor_patterns)),
    path("api/v1/", include("config.api_urls")),
    path("", dashboard, name="dashboard"),
]

handler400 = "config.views.error_400"
handler403 = "config.views.error_403"
handler404 = "config.views.error_404"
handler500 = "config.views.error_500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
