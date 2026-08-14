from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.models import User
from apps.accounts.rbac import Capability, user_has_capability
from apps.audit.services import log_audit_event
from apps.reporting.exports import csv_response, pdf_response, xlsx_response
from apps.reporting.reports import report_context
from apps.reporting.selectors import (
    allowed_report_sections,
    get_dashboard_shell_data,
    reporting_user_allowed,
    user_can_export,
)
from apps.reporting.services import get_leadership_dashboard_data, get_tv_wallboard_data
from apps.venues.models import DisplayToken
from apps.venues.services.live_status import all_venues_live_status
from config.rate_limit import is_rate_limited
from config.views import rate_limited_response


def user_can_view_leadership(user) -> bool:
    return user_has_capability(user, Capability.VIEW_LEADERSHIP_DASHBOARD)


def user_can_view_operational_venues(user) -> bool:
    return user_can_view_leadership(user) or (
        user.is_authenticated and user.is_active and user.role == User.Role.RECEPTION_OPERATOR
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
        if is_rate_limited(request, "display-api", 180, 60, token):
            return JsonResponse({"error": "Too many requests"}, status=429)
        display_token = DisplayToken.objects.filter(token=token, is_active=True).first()
        if not display_token:
            return JsonResponse({"error": "Invalid or disabled display token"}, status=403)
        DisplayToken.objects.filter(pk=display_token.pk).update(last_used_at=timezone.now())
        return JsonResponse(get_tv_wallboard_data())


class ReportingRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not reporting_user_allowed(request.user):
            raise PermissionDenied(_("You do not have permission to view reports."))
        return super().dispatch(request, *args, **kwargs)


class ReportDashboardView(ReportingRequiredMixin, TemplateView):
    template_name = "reporting/reports_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form, events, report = report_context(self.request.GET, self.request.user)
        sections = allowed_report_sections(self.request.user)
        context.update(
            {
                "nav_key": "reports",
                "filter_form": form,
                "report": report,
                "event_rows": list(events[:100]) if events is not None else [],
                "active_query": self.request.GET.urlencode(),
                "report_sections": sections,
                "full_exports": user_can_export(self.request.user, "xlsx"),
                "attendance_export": user_can_export(
                    self.request.user, "csv", "attendance"
                ),
                "publication_export": user_can_export(
                    self.request.user, "csv", "publications"
                ),
            }
        )
        return context


class ReportExportView(ReportingRequiredMixin, View):
    format = "csv"

    def get(self, request):
        kind = request.GET.get("kind", "events")
        if is_rate_limited(request, "report-export", 20, 60, str(request.user.pk)):
            return rate_limited_response(request)
        if not user_can_export(request.user, self.format, kind):
            raise PermissionDenied(_("You do not have permission to export this report."))
        language = request.GET.get("language") or translation.get_language() or "uz"
        with translation.override(language):
            form, events, report = report_context(request.GET, request.user)
            if not report:
                return JsonResponse({"errors": form.errors}, status=400)
            action = f"report.{self.format}_exported"
            log_audit_event(
                action,
                actor=request.user,
                payload={"start": str(report["start"]), "end": str(report["end"])},
            )
            if self.format == "xlsx":
                return xlsx_response(events, report)
            if self.format == "pdf":
                return pdf_response(report)
            return csv_response(events, report, kind)
