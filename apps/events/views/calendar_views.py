
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    TemplateView,
)

from apps.accounts.rbac import Capability, CapabilityRequiredMixin
from apps.events.models import Event
from apps.events.selectors import active_event_types
from apps.organizations.selectors import active_organizations
from apps.venues.selectors import active_venues
from apps.venues.services.live_status import all_venues_live_status

# --- Calendar & Live Status Views ---


class CalendarView(LoginRequiredMixin, CapabilityRequiredMixin, TemplateView):
    required_capability = Capability.VIEW_MASTER_DATA
    template_name = "events/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "nav_key": "calendar",
                "page_title": _("Event Calendar"),
                "venues": active_venues(),
                "event_types": active_event_types(),
                "statuses": Event.Status.choices,
                "organizations": active_organizations(),
            }
        )
        return context


class VenueLiveStatusView(LoginRequiredMixin, CapabilityRequiredMixin, TemplateView):
    required_capability = Capability.VIEW_MASTER_DATA
    template_name = "venues/live_status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "nav_key": "venues",
                "page_title": _("Live Venue Status"),
                "venue_statuses": all_venues_live_status(),
            }
        )
        return context
