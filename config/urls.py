from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import RedirectView

from apps.accounts.views import (
    AvailabilityDeleteView,
    AvailabilityListView,
    DoctorAssignedEventsView,
    DoctorRegisterView,
    ManagementEventsListView,
    ProfileView,
    ResponsibleEventsListView,
    UserManagementListView,
    UserToggleActiveView,
)
from apps.attendance.views import PublicCheckinView
from apps.events.urls import event_type_patterns
from apps.events.views import (
    CalendarView,
    PublicEventPageView,
    PublicKioskView,
    VenueLiveStatusView,
)
from apps.organizations.urls import organization_patterns, sponsor_patterns
from apps.reporting.views import (
    LeadershipDashboardView,
    PublicCalendarAPIView,
    PublicCalendarView,
    PublicDashboardAPIView,
    PublicDashboardView,
    PublicLiveVenuesView,
    PublicVenuesAPIView,
    TvWallboardView,
    dashboard,
    home,
)
from config import health
from config.views import ThrottledLoginView

urlpatterns = [
    path("admin/audit/", include("apps.audit.urls")),
    path("admin/", admin.site.urls),
    path("dashboard/", PublicDashboardView.as_view(), name="public-dashboard"),
    path("dashboard/calendar/", PublicCalendarView.as_view(), name="public-calendar"),
    path("venues/", RedirectView.as_view(pattern_name="venues:list", permanent=False)),
    path("venues/live/", PublicLiveVenuesView.as_view(), name="public-live-venues"),
    path("api/public/dashboard/", PublicDashboardAPIView.as_view(), name="public-dashboard-api"),
    path("api/public/calendar/", PublicCalendarAPIView.as_view(), name="public-calendar-api"),
    path("api/public/venues/", PublicVenuesAPIView.as_view(), name="public-venues-api"),
    path("workspace/", dashboard, name="dashboard"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("users/", UserManagementListView.as_view(), name="user-management"),
    path(
        "users/<int:pk>/toggle-active/",
        UserToggleActiveView.as_view(),
        name="user-toggle-active",
    ),
    path(
        "profile/assigned-events/",
        DoctorAssignedEventsView.as_view(),
        name="doctor-assigned-events",
    ),
    path(
        "profile/responsible-events/",
        ResponsibleEventsListView.as_view(),
        name="responsible-events",
    ),
    path(
        "profile/management-events/",
        ManagementEventsListView.as_view(),
        name="management-events",
    ),
    path("profile/availability/", AvailabilityListView.as_view(), name="doctor-availability"),
    path(
        "profile/availability/<int:pk>/delete/",
        AvailabilityDeleteView.as_view(),
        name="doctor-availability-delete",
    ),
    path("accounts/register/", DoctorRegisterView.as_view(), name="register"),
    path("accounts/login/", ThrottledLoginView.as_view(), name="login"),
    path("login/", RedirectView.as_view(pattern_name="login", permanent=False)),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("logout/", RedirectView.as_view(pattern_name="logout", permanent=False)),
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
    path("public-events/", PublicKioskView.as_view(), name="public-kiosk"),
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
    path("", home, name="home"),
]

handler400 = "config.views.error_400"
handler403 = "config.views.error_403"
handler404 = "config.views.error_404"
handler500 = "config.views.error_500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
