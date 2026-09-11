import csv
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_protect

from apps.accounts.models import User
from apps.accounts.rbac import Capability, user_has_capability
from apps.attendance.forms import (
    EventCheckinConfigForm,
    PublicCheckinForm,
    StaffManualCheckinForm,
)
from apps.attendance.models import EventAttendance
from apps.attendance.services import (
    CHECKIN_COOKIE_NAME,
    get_event_attendance_stats,
    is_already_checked_in,
    process_public_checkin,
    process_staff_manual_checkin,
)
from apps.audit.services import log_audit_event
from apps.events.models import Event
from config.rate_limit import is_rate_limited


def user_can_view_attendance(user, event) -> bool:
    """Returns True if user is authorized to view event attendance."""
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser or user.role in (User.Role.SUPER_ADMIN, User.Role.INTERNATIONAL_ADMIN):
        return True
    if user.role == User.Role.CONTENT_MANAGER:
        return False
    if user.role in (
        User.Role.MANAGEMENT_RESPONSIBLE,
        User.Role.LEADERSHIP_VIEWER,
        User.Role.RECEPTION_OPERATOR,
    ):
        return True
    if (
        user == event.responsible_employee
        or user == event.created_by
        or user == event.management_responsible
    ):
        return True
    if user_has_capability(user, Capability.MANAGE_EVENTS) or user_has_capability(
        user, Capability.MANAGE_ATTENDANCE
    ):
        return True
    return False


def user_can_manage_attendance(user, event) -> bool:
    """Returns True if user is authorized to edit config or submit manual check-in."""
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser or user.role in (User.Role.SUPER_ADMIN, User.Role.INTERNATIONAL_ADMIN):
        return True
    if user.role in (
        User.Role.CONTENT_MANAGER,
        User.Role.LEADERSHIP_VIEWER,
        User.Role.MANAGEMENT_RESPONSIBLE,
    ):
        return False
    if user.role == User.Role.RECEPTION_OPERATOR:
        return True
    if user == event.responsible_employee or user == event.created_by:
        return True
    if user_has_capability(user, Capability.MANAGE_EVENTS) or user_has_capability(
        user, Capability.MANAGE_ATTENDANCE
    ):
        return True
    return False


@method_decorator(csrf_protect, name="dispatch")
class PublicCheckinView(View):
    """Processes public QR attendance check-in submissions."""

    def post(self, request, public_token):
        if is_rate_limited(request, "public-checkin", 300, 60, public_token):
            return JsonResponse(
                {
                    "success": False,
                    "code": "rate_limited",
                    "message": str(_("Too many requests. Please try again later.")),
                },
                status=429,
            )
        event = get_object_or_404(Event, public_token=public_token)
        if not event.is_publicly_accessible:
            return JsonResponse(
                {
                    "success": False,
                    "code": "not_public",
                    "message": str(_("This event page is not currently published or unavailable.")),
                },
                status=404,
            )

        name = ""
        org = ""
        if request.content_type == "application/json":
            try:
                body = json.loads(request.body)
                name = str(body.get("attendee_name", ""))
                org = str(body.get("attendee_organization", ""))
            except Exception:
                pass
        else:
            form = PublicCheckinForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data.get("attendee_name", "")
                org = form.cleaned_data.get("attendee_organization", "")

        result = process_public_checkin(
            event=event,
            request=request,
            attendee_name=name,
            attendee_organization=org,
        )

        count = event.attendances.count()
        response_data = {
            "success": result["success"],
            "code": result["code"],
            "message": result["message"],
            "already_checked_in": result.get("already_checked_in", False),
            "count": count,
        }

        status_code = 200 if result["success"] or result.get("already_checked_in") else 400
        response = JsonResponse(response_data, status=status_code)

        # Set browser token cookie if newly generated or missing
        if result.get("new_token") or not request.COOKIES.get(CHECKIN_COOKIE_NAME):
            token = result.get("token")
            if token:
                response.set_cookie(
                    CHECKIN_COOKIE_NAME,
                    token,
                    max_age=365 * 24 * 3600,
                    samesite="Lax",
                    httponly=True,
                    secure=settings.SESSION_COOKIE_SECURE,
                )

        return response


class PublicAttendanceCountAPIView(View):
    """Returns public attendance count and check-in status for an event."""

    def get(self, request, token):
        if is_rate_limited(request, "public-attendance-count", 120, 60, token):
            return JsonResponse({"error": "Too many requests"}, status=429)
        event = get_object_or_404(Event, public_token=token)
        if not event.is_publicly_accessible:
            return JsonResponse({"error": "Event not found"}, status=404)

        count = event.attendances.count()
        status_info = event.checkin_status()
        checked_in, _ = is_already_checked_in(event, request)

        return JsonResponse(
            {
                "success": True,
                "count": count,
                "status": status_info["code"],
                "eligible": status_info["eligible"],
                "status_reason": status_info["reason"],
                "checked_in": checked_in,
            }
        )


class EventAttendanceView(LoginRequiredMixin, View):
    """Internal management page for viewing and managing event attendance."""

    def get_event(self, pk):
        return get_object_or_404(Event.objects.select_related("venue", "event_type"), pk=pk)

    def get(self, request, pk):
        event = self.get_event(pk)
        if not user_can_view_attendance(request.user, event):
            raise PermissionDenied(_("You do not have permission to view event attendance."))

        can_manage = user_can_manage_attendance(request.user, event)
        stats = get_event_attendance_stats(event)

        # Filtering and Search
        qs = event.attendances.all()
        q = request.GET.get("q", "").strip()
        method_filter = request.GET.get("method", "").strip()

        if q:
            qs = qs.filter(
                Q(attendee_name__icontains=q)
                | Q(attendee_organization__icontains=q)
                | Q(attendee_role__icontains=q)
            )

        if method_filter:
            qs = qs.filter(checkin_method=method_filter)

        paginator = Paginator(qs, 20)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        config_form = EventCheckinConfigForm(instance=event)
        manual_form = StaffManualCheckinForm()

        context = {
            "event": event,
            "stats": stats,
            "attendances": page_obj,
            "can_manage": can_manage,
            "can_view_only": not can_manage,
            "config_form": config_form,
            "manual_form": manual_form,
            "search_query": q,
            "method_filter": method_filter,
            "method_choices": EventAttendance.Method.choices,
        }
        return render(request, "events/event_attendance.html", context)

    def post(self, request, pk):
        event = self.get_event(pk)
        if not user_can_manage_attendance(request.user, event):
            raise PermissionDenied(_("You do not have permission to manage event attendance."))

        action = request.POST.get("action")

        if action == "update_config":
            old_enabled = event.checkin_enabled
            old_opens = event.checkin_opens_at
            old_closes = event.checkin_closes_at

            form = EventCheckinConfigForm(request.POST, instance=event)
            if form.is_valid():
                updated_event = form.save()
                messages.success(request, _("Check-in configuration updated."))

                # Audit logs
                if not old_enabled and updated_event.checkin_enabled:
                    log_audit_event("event.checkin_enabled", actor=request.user, target=event)
                elif old_enabled and not updated_event.checkin_enabled:
                    log_audit_event("event.checkin_disabled", actor=request.user, target=event)

                opens_changed = old_opens != updated_event.checkin_opens_at
                closes_changed = old_closes != updated_event.checkin_closes_at
                if opens_changed or closes_changed:
                    opens_iso = (
                        updated_event.checkin_opens_at.isoformat()
                        if updated_event.checkin_opens_at
                        else None
                    )
                    closes_iso = (
                        updated_event.checkin_closes_at.isoformat()
                        if updated_event.checkin_closes_at
                        else None
                    )
                    log_audit_event(
                        "event.checkin_window_changed",
                        actor=request.user,
                        target=event,
                        payload={
                            "opens_at": opens_iso,
                            "closes_at": closes_iso,
                        },
                    )
            else:
                messages.error(request, _("Please correct the errors in the configuration form."))

        elif action == "manual_checkin":
            form = StaffManualCheckinForm(request.POST)
            if form.is_valid():
                process_staff_manual_checkin(
                    event=event,
                    staff_user=request.user,
                    attendee_name=form.cleaned_data["attendee_name"],
                    attendee_organization=form.cleaned_data.get("attendee_organization", ""),
                    attendee_role=form.cleaned_data.get("attendee_role", ""),
                )
                messages.success(
                    request,
                    _("Attendee '%(name)s' checked in manually.")
                    % {"name": form.cleaned_data["attendee_name"]},
                )
            else:
                messages.error(
                    request,
                    _("Please provide a valid attendee name for manual check-in."),
                )

        return redirect("events:attendance", pk=event.pk)


class EventAttendanceExportView(LoginRequiredMixin, View):
    """Exports attendance records as a UTF-8 BOM encoded CSV file."""

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not user_can_view_attendance(request.user, event):
            raise PermissionDenied(_("You do not have permission to export attendance data."))

        log_audit_event("attendance.exported", actor=request.user, target=event)

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        filename = f"attendance_event_{event.pk}.csv"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # Write UTF-8 BOM for Microsoft Excel compatibility
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow(
            [
                str(_("checked_in_at")),
                str(_("attendee_name")),
                str(_("attendee_organization")),
                str(_("checkin_method")),
            ]
        )

        for item in event.attendances.all().order_by("checked_in_at"):
            name = item.attendee_name or str(_("Anonymous"))
            org = item.attendee_organization or "—"
            method_display = item.get_checkin_method_display()
            writer.writerow(
                [
                    item.checked_in_at.strftime("%Y-%m-%d %H:%M:%S"),
                    name,
                    org,
                    method_display,
                ]
            )

        return response


class EventAttendanceStatsAPIView(LoginRequiredMixin, View):
    """Internal JSON endpoint for real-time stats polling."""

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not user_can_view_attendance(request.user, event):
            return JsonResponse({"error": "Permission denied"}, status=403)

        stats = get_event_attendance_stats(event)
        return JsonResponse({"success": True, "stats": stats})


class EventAttendanceListAPIView(LoginRequiredMixin, View):
    """Internal JSON endpoint for fetching recent attendees."""

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not user_can_view_attendance(request.user, event):
            return JsonResponse({"error": "Permission denied"}, status=403)

        records = []
        for item in event.attendances.all()[:50]:
            records.append(
                {
                    "id": str(item.id),
                    "checked_in_at": item.checked_in_at.strftime("%H:%M:%S"),
                    "name": item.attendee_name or str(_("Anonymous")),
                    "organization": item.attendee_organization or "—",
                    "method": item.get_checkin_method_display(),
                }
            )
        return JsonResponse({"success": True, "attendees": records})
