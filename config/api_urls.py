from django.urls import path

from apps.attendance.views import (
    EventAttendanceListAPIView,
    EventAttendanceStatsAPIView,
    PublicAttendanceCountAPIView,
)
from apps.events.api import (
    CalendarEventsAPIView,
    EventApproveAPIView,
    EventDetailAPIView,
    EventEmergencyOverrideAPIView,
    EventListAPIView,
    EventPostponeAPIView,
    EventProgramAPIView,
    EventRejectAPIView,
    EventRescheduleAPIView,
    EventResubmitAPIView,
    EventSubmitAPIView,
    EventTypeDetailAPIView,
    EventTypeListAPIView,
    PublicEventAPIView,
    VenueAvailabilityAPIView,
)
from apps.organizations.api import (
    OrganizationDetailAPIView,
    OrganizationListAPIView,
    SponsorDetailAPIView,
    SponsorListAPIView,
)
from apps.reporting.views import (
    DisplayVenuesAPIView,
    LeadershipSummaryAPIView,
    LeadershipTodayAPIView,
    LeadershipUpcomingAPIView,
    LeadershipVenuesAPIView,
)
from apps.venues.api import VenueDetailAPIView, VenueListAPIView

urlpatterns = [
    path("venues/", VenueListAPIView.as_view(), name="api-venue-list"),
    path("venues/<int:pk>/", VenueDetailAPIView.as_view(), name="api-venue-detail"),
    path(
        "venues/<int:pk>/availability/",
        VenueAvailabilityAPIView.as_view(),
        name="api-venue-availability",
    ),
    path("event-types/", EventTypeListAPIView.as_view(), name="api-event-type-list"),
    path("event-types/<int:pk>/", EventTypeDetailAPIView.as_view(), name="api-event-type-detail"),
    path("organizations/", OrganizationListAPIView.as_view(), name="api-organization-list"),
    path(
        "organizations/<int:pk>/",
        OrganizationDetailAPIView.as_view(),
        name="api-organization-detail",
    ),
    path("sponsors/", SponsorListAPIView.as_view(), name="api-sponsor-list"),
    path("sponsors/<int:pk>/", SponsorDetailAPIView.as_view(), name="api-sponsor-detail"),
    path("public/events/<str:token>/", PublicEventAPIView.as_view(), name="api-public-event"),
    path(
        "public/events/<str:token>/attendance-count/",
        PublicAttendanceCountAPIView.as_view(),
        name="api-public-attendance-count",
    ),
    path("display/<str:token>/venues/", DisplayVenuesAPIView.as_view(), name="api-display-venues"),
    path("leadership/summary/", LeadershipSummaryAPIView.as_view(), name="api-leadership-summary"),
    path("leadership/venues/", LeadershipVenuesAPIView.as_view(), name="api-leadership-venues"),
    path("leadership/today/", LeadershipTodayAPIView.as_view(), name="api-leadership-today"),
    path(
        "leadership/upcoming/",
        LeadershipUpcomingAPIView.as_view(),
        name="api-leadership-upcoming",
    ),
    path("events/", EventListAPIView.as_view(), name="api-event-list"),
    path("events/<uuid:pk>/", EventDetailAPIView.as_view(), name="api-event-detail"),
    path("events/<uuid:pk>/program/", EventProgramAPIView.as_view(), name="api-event-program"),
    path(
        "events/<uuid:pk>/attendance/",
        EventAttendanceListAPIView.as_view(),
        name="api-event-attendance-list",
    ),
    path(
        "events/<uuid:pk>/attendance/stats/",
        EventAttendanceStatsAPIView.as_view(),
        name="api-event-attendance-stats",
    ),
    path("events/<uuid:pk>/submit/", EventSubmitAPIView.as_view(), name="api-event-submit"),
    path("events/<uuid:pk>/approve/", EventApproveAPIView.as_view(), name="api-event-approve"),
    path("events/<uuid:pk>/reject/", EventRejectAPIView.as_view(), name="api-event-reject"),
    path("events/<uuid:pk>/resubmit/", EventResubmitAPIView.as_view(), name="api-event-resubmit"),
    path("events/<uuid:pk>/postpone/", EventPostponeAPIView.as_view(), name="api-event-postpone"),
    path(
        "events/<uuid:pk>/reschedule/",
        EventRescheduleAPIView.as_view(),
        name="api-event-reschedule",
    ),
    path(
        "events/<uuid:pk>/emergency-override/",
        EventEmergencyOverrideAPIView.as_view(),
        name="api-event-emergency-override",
    ),
    path("calendar/events/", CalendarEventsAPIView.as_view(), name="api-calendar-events"),
]
