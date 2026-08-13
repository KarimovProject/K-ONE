from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.models import User
from apps.accounts.rbac import Capability, user_has_capability
from apps.reporting.selectors import get_dashboard_shell_data
from apps.reporting.services import get_leadership_dashboard_data, get_tv_wallboard_data
from apps.venues.models import DisplayToken
from apps.venues.services.live_status import all_venues_live_status


def user_can_view_leadership(user) -> bool:
    return user_has_capability(user, Capability.VIEW_LEADERSHIP_DASHBOARD)


def user_can_view_operational_venues(user) -> bool:
    return user_can_view_leadership(user) or (
        user.is_authenticated
        and user.is_active
        and user.role == User.Role.RECEPTION_OPERATOR
    )


def _serialize_venues(venues):
    keys = (
        "venue_id",
        "venue_code",
        "venue_name",
        "current_status",
        "status_label",
        "current_event_title",
        "current_event_start_time",
        "current_event_end_time",
        "minutes_remaining",
        "next_event_title",
        "next_event_date",
        "next_event_start_time",
        "minutes_until_start",
        "free_until",
        "today_event_count",
    )
    return [{key: item[key] for key in keys} for item in venues]


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    context = get_dashboard_shell_data()
    context["nav_key"] = "dashboard"
    return render(request, "dashboard.html", context)


class LeadershipRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not user_can_view_leadership(request.user):
            raise PermissionDenied(
                _("You do not have permission to view the Leadership Dashboard.")
            )
        return super().dispatch(request, *args, **kwargs)


class LeadershipDashboardView(LeadershipRequiredMixin, TemplateView):
    template_name = "reporting/leadership_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_leadership_dashboard_data())
        context["nav_key"] = "leadership"
        context["page_title"] = _("Leadership Dashboard")
        return context


class TvWallboardView(TemplateView):
    template_name = "reporting/tv_wallboard.html"

    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get("token", "")
        self.display_token = DisplayToken.objects.filter(
            token=token,
            is_active=True,
        ).first()
        if not self.display_token:
            raise PermissionDenied(_("Invalid or disabled display token."))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_tv_wallboard_data())
        context["display_token"] = self.display_token.token
        context["page_title"] = _("IEMS TV Wallboard")
        return context


class LeadershipSummaryAPIView(LeadershipRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data = get_leadership_dashboard_data()
        keys = (
            "reference_dt",
            "today_date",
            "today_events_count",
            "in_progress_count",
            "available_venues_count",
            "occupied_venues_count",
            "today_checkins_count",
            "today_expected_attendees",
            "attendance_rate",
        )
        return JsonResponse({key: data[key] for key in keys})


class LeadershipVenuesAPIView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not user_can_view_operational_venues(request.user):
            return JsonResponse({"error": "Forbidden"}, status=403)
        return JsonResponse({"venues": _serialize_venues(all_venues_live_status())})


class LeadershipTodayAPIView(LeadershipRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data = get_leadership_dashboard_data()
        return JsonResponse({"events": data["today_timeline"]})


class LeadershipUpcomingAPIView(LeadershipRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data = get_leadership_dashboard_data()
        return JsonResponse({"events": data["upcoming_events"]})


class DisplayVenuesAPIView(View):
    def get(self, request, token, *args, **kwargs):
        display_token = DisplayToken.objects.filter(token=token, is_active=True).first()
        if not display_token:
            return JsonResponse({"error": "Invalid or disabled display token"}, status=403)
        DisplayToken.objects.filter(pk=display_token.pk).update(last_used_at=timezone.now())
        return JsonResponse(get_tv_wallboard_data())
