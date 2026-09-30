"""Event views, split by concern; re-exported so URLconfs keep importing
`apps.events.views.<ViewName>` unchanged."""

from apps.events.views.calendar_views import (
    CalendarView,
    VenueLiveStatusView,
)
from apps.events.views.core import (
    EventCancelView,
    EventDeleteView,
    EventDetailView,
    EventListView,
    EventUpdateView,
)
from apps.events.views.master_data import (
    EventTypeContextMixin,
    EventTypeCreateView,
    EventTypeDeleteView,
    EventTypeDetailView,
    EventTypeListView,
    EventTypeUpdateView,
)
from apps.events.views.program import (
    EventProgramEditView,
    SpeakerCreateView,
    SpeakerListView,
    SpeakerUpdateView,
)
from apps.events.views.public import (
    EventPrintQrView,
    EventQrCodePngView,
    EventQrCodeSvgView,
    PublicEventPageView,
    PublicKioskView,
)
from apps.events.views.workflow import (
    DisplacedEventsListView,
    EventApprovalListView,
    EventApproveView,
    EventEmergencyOverrideView,
    EventOverrideView,
    EventPostponeView,
    EventRejectView,
    EventRescheduleView,
    EventResubmitView,
    EventSubmitApprovalView,
)

__all__ = (
    "CalendarView",
    "DisplacedEventsListView",
    "EventApprovalListView",
    "EventApproveView",
    "EventCancelView",
    "EventDeleteView",
    "EventDetailView",
    "EventEmergencyOverrideView",
    "EventListView",
    "EventOverrideView",
    "EventPostponeView",
    "EventPrintQrView",
    "EventProgramEditView",
    "EventQrCodePngView",
    "EventQrCodeSvgView",
    "EventRejectView",
    "EventRescheduleView",
    "EventResubmitView",
    "EventSubmitApprovalView",
    "EventTypeContextMixin",
    "EventTypeCreateView",
    "EventTypeDeleteView",
    "EventTypeDetailView",
    "EventTypeListView",
    "EventTypeUpdateView",
    "EventUpdateView",
    "PublicEventPageView",
    "PublicKioskView",
    "SpeakerCreateView",
    "SpeakerListView",
    "SpeakerUpdateView",
    "VenueLiveStatusView",
)
