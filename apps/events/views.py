from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.accounts.rbac import Capability, CapabilityRequiredMixin, user_has_capability
from apps.attendance.services import (
    CHECKIN_COOKIE_NAME,
    get_or_create_browser_checkin_token,
    is_already_checked_in,
)
from apps.audit.services import log_audit_event
from apps.events.forms import (
    EventBannerImageForm,
    EventCancelForm,
    EventProgramItemForm,
    EventProgramModeForm,
    EventProgramPdfForm,
    EventTypeForm,
    EventUpdateForm,
    SpeakerForm,
)
from apps.events.models import Event, EventProgramItem, EventType, Speaker
from apps.events.selectors import active_event_types, base_event_queryset
from apps.events.services.conflicts import validate_and_lock_event_reservation
from apps.organizations.selectors import active_organizations
from apps.venues.selectors import active_venues
from apps.venues.services.live_status import all_venues_live_status
from config.master_data import (
    MasterDataContextMixin,
    MasterDataDeleteMixin,
    MasterDataFormMixin,
    MasterDataListMixin,
    MasterDataManageMixin,
    MasterDataReadMixin,
)


class EventTypeContextMixin(MasterDataContextMixin):
    model = EventType
    nav_key = "event_types"
    page_title = _("Event types")
    page_description = _("Control the reusable categories available to future event workflows.")
    resource_name = _("Event type")
    resource_name_plural = _("event types")
    list_url_name = "event-types:list"
    create_url_name = "event-types:create"


class EventTypeListView(
    MasterDataReadMixin,
    MasterDataListMixin,
    EventTypeContextMixin,
    ListView,
):
    template_name = "events/event_type_list.html"
    context_object_name = "event_types"
    search_fields = ("code", "name_uz", "name_ru", "name_en")


class EventTypeDetailView(MasterDataReadMixin, EventTypeContextMixin, DetailView):
    template_name = "events/event_type_detail.html"
    context_object_name = "event_type"


class EventTypeCreateView(
    MasterDataManageMixin,
    MasterDataFormMixin,
    EventTypeContextMixin,
    CreateView,
):
    form_class = EventTypeForm
    page_title = _("Create event type")


class EventTypeUpdateView(
    MasterDataManageMixin,
    MasterDataFormMixin,
    EventTypeContextMixin,
    UpdateView,
):
    form_class = EventTypeForm
    page_title = _("Edit event type")


class EventTypeDeleteView(
    MasterDataManageMixin,
    MasterDataDeleteMixin,
    EventTypeContextMixin,
    DeleteView,
):
    page_title = _("Delete event type")


# --- Event Core Views ---


class EventListView(LoginRequiredMixin, CapabilityRequiredMixin, ListView):
    required_capability = Capability.VIEW_MASTER_DATA
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        queryset = base_event_queryset().exclude(
            Q(title__istartswith="[ACCEPTANCE_DEMO]") | Q(title__istartswith="[P11]")
        )
        query = self.request.GET.get("q", "").strip()
        venue_id = self.request.GET.get("venue")
        event_type_id = self.request.GET.get("type")
        status_filter = self.request.GET.get("status")
        resp_id = self.request.GET.get("responsible")
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))

        if venue_id:
            queryset = queryset.filter(venue_id=venue_id)
        if event_type_id:
            queryset = queryset.filter(event_type_id=event_type_id)
        if status_filter and status_filter != "all":
            queryset = queryset.filter(status=status_filter)
        if resp_id:
            queryset = queryset.filter(responsible_employee_id=resp_id)
        if start_date_str:
            try:
                s_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(planned_date__gte=s_date)
            except ValueError:
                pass
        if end_date_str:
            try:
                e_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(planned_date__lte=e_date)
            except ValueError:
                pass

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "nav_key": "events",
                "page_title": _("Planned Events"),
                "search_query": self.request.GET.get("q", "").strip(),
                "status_filter": self.request.GET.get("status", "all"),
                "selected_venue": self.request.GET.get("venue", ""),
                "selected_type": self.request.GET.get("type", ""),
                "selected_responsible": self.request.GET.get("responsible", ""),
                "start_date": self.request.GET.get("start_date", ""),
                "end_date": self.request.GET.get("end_date", ""),
                "venues": active_venues(),
                "event_types": active_event_types(),
                "statuses": Event.Status.choices,
                "can_create": user_has_capability(self.request.user, Capability.CREATE_OWN_EVENTS),
            }
        )
        return context


class EventDetailView(LoginRequiredMixin, CapabilityRequiredMixin, DetailView):
    required_capability = Capability.VIEW_MASTER_DATA
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_object(self, queryset=None):
        return get_object_or_404(base_event_queryset(), pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        user = self.request.user

        is_owner = user == event.responsible_employee or user == event.created_by
        is_mgmt = (
            user == event.management_responsible
            or user_has_capability(user, Capability.APPROVE_EVENTS)
            or user.is_superuser
        )
        is_admin = user_has_capability(user, Capability.MANAGE_EVENTS) or user.is_superuser
        is_override_authorized = user.is_superuser or user_has_capability(
            user, Capability.OVERRIDE_EVENTS
        )

        from apps.audit.models import AuditEventLog
        from apps.events.services.conflicts import find_conflicting_events
        from apps.publications.policies import can_prepare

        can_edit = (is_owner or is_admin) and event.status != Event.Status.CANCELLED
        can_cancel = (is_owner or is_admin) and event.status != Event.Status.CANCELLED

        conflicting_events = []
        if event.status == Event.Status.PENDING_APPROVAL:
            conflicts_qs = find_conflicting_events(
                venue=event.venue,
                planned_date=event.planned_date,
                start_time=event.start_time,
                end_time=event.end_time,
                exclude_event_id=str(event.pk),
            )
            if conflicts_qs.exists():
                conflicting_events = list(conflicts_qs)

        context.update(
            {
                "nav_key": "events",
                "page_title": event.title,
                "can_edit": can_edit,
                "can_cancel": can_cancel,
                "can_submit": (
                    (is_owner or is_admin)
                    and event.status in (Event.Status.DRAFT, Event.Status.REJECTED, Event.Status.PLANNED)
                ),
                "can_approve": is_mgmt and event.status == Event.Status.PENDING_APPROVAL,
                "can_reject": is_mgmt and event.status == Event.Status.PENDING_APPROVAL,
                "can_resubmit": (is_owner or is_admin) and event.status == Event.Status.REJECTED,
                "can_postpone": (
                    (is_owner or is_admin)
                    and event.status
                    not in (Event.Status.CANCELLED, Event.Status.COMPLETED, Event.Status.POSTPONED)
                ),
                "can_reschedule": (
                    (is_owner or is_admin)
                    and event.status
                    in (
                        Event.Status.PLANNED,
                        Event.Status.APPROVED,
                        Event.Status.DISPLACED,
                        Event.Status.POSTPONED,
                    )
                ),
                "can_override": (
                    is_override_authorized
                    and event.status == Event.Status.PENDING_APPROVAL
                    and len(conflicting_events) > 0
                ),
                "has_conflicts": len(conflicting_events) > 0,
                "conflicting_events": conflicting_events,
                "can_manage_reminders": is_admin,
                "can_create_publication": can_prepare(user, event),
                "audit_logs": AuditEventLog.objects.filter(target_id=str(event.pk))[:15],
            }
        )
        return context


class EventUpdateView(LoginRequiredMixin, CapabilityRequiredMixin, UpdateView):
    required_capability = Capability.CREATE_OWN_EVENTS
    model = Event
    form_class = EventUpdateForm
    template_name = "events/event_edit.html"

    def get_object(self, queryset=None):
        event = get_object_or_404(Event, pk=self.kwargs["pk"])
        if not (
            user_has_capability(self.request.user, Capability.MANAGE_EVENTS)
            or event.responsible_employee_id == self.request.user.pk
            or self.request.user.is_superuser
        ):
            raise PermissionDenied
        return event

    def form_valid(self, form):
        event = form.save(commit=False)
        event.updated_by = self.request.user

        # Run conflict check if PLANNED
        if event.status == Event.Status.PLANNED:
            try:
                validate_and_lock_event_reservation(
                    venue=event.venue,
                    planned_date=event.planned_date,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    status=event.status,
                    expected_attendees=event.expected_attendees,
                    exclude_event_id=str(event.pk),
                )
            except ValidationError as exc:
                form.add_error(None, exc.message)
                return self.form_invalid(form)

        event.save()
        form.save_m2m()

        log_audit_event("event.updated", actor=self.request.user, target=event)
        messages.success(self.request, _("Event “%(title)s” updated.") % {"title": event.title})
        return redirect(reverse("events:detail", kwargs={"pk": event.pk}))


class EventCancelView(LoginRequiredMixin, CapabilityRequiredMixin, FormView):
    required_capability = Capability.CREATE_OWN_EVENTS
    form_class = EventCancelForm
    template_name = "events/event_confirm_cancel.html"

    def get_success_url(self):
        return reverse_lazy("events:detail", kwargs={"pk": self.event.pk})

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs["pk"])
        if not (
            user_has_capability(request.user, Capability.MANAGE_EVENTS)
            or self.event.responsible_employee_id == request.user.pk
            or request.user.is_superuser
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "nav_key": "events",
                "event": self.event,
                "page_title": _("Cancel Event “%(title)s”") % {"title": self.event.title},
            }
        )
        return context

    def form_valid(self, form):
        reason = form.cleaned_data.get("reason", "")
        self.event.status = Event.Status.CANCELLED
        self.event.updated_by = self.request.user
        if reason:
            self.event.notes = f"{self.event.notes}\n[Cancelled]: {reason}".strip()
        self.event.save()

        log_audit_event(
            "event.cancelled",
            actor=self.request.user,
            target=self.event,
            payload={"reason": reason},
        )
        messages.success(
            self.request,
            _("Event “%(title)s” cancelled.") % {"title": self.event.title},
        )

        return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))


class EventDeleteView(LoginRequiredMixin, CapabilityRequiredMixin, MasterDataDeleteMixin, DeleteView):
    required_capability = Capability.MANAGE_EVENTS
    model = Event
    list_url_name = "events:list"
    resource_name = _("Event")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Delete Event “%(title)s”") % {"title": self.object.title}
        context["nav_key"] = "events"
        context["list_url_name"] = self.list_url_name
        context["resource_name"] = self.resource_name
        return context


# --- Phase 3 Approval & Emergency Views ---


class EventSubmitApprovalView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_owner = request.user == event.responsible_employee or request.user == event.created_by
        is_admin = user_has_capability(request.user, Capability.MANAGE_EVENTS)
        if not (is_owner or is_admin):
            raise PermissionDenied(_("Only the responsible employee or admin can submit."))

        try:
            from apps.events.services.workflow import submit_event_for_approval

            submit_event_for_approval(event, request.user)
            messages.success(
                request,
                _("Event “%(title)s” submitted for management approval.") % {"title": event.title},
            )
        except ValidationError as exc:
            messages.error(request, exc.message)

        return redirect(reverse("events:detail", kwargs={"pk": event.pk}))


class EventApprovalListView(LoginRequiredMixin, CapabilityRequiredMixin, ListView):
    required_capability = Capability.APPROVE_EVENTS
    template_name = "events/approval_center.html"
    context_object_name = "events"
    paginate_by = 15

    def get_queryset(self):
        qs = Event.objects.select_related(
            "event_type", "venue", "responsible_employee", "management_responsible"
        )

        status_filter = self.request.GET.get("status", Event.Status.PENDING_APPROVAL)
        priority_filter = self.request.GET.get("priority")
        venue_id = self.request.GET.get("venue")
        event_type_id = self.request.GET.get("type")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if status_filter == "my_pending":
            qs = qs.filter(
                management_responsible=self.request.user, status=Event.Status.PENDING_APPROVAL
            )
        elif status_filter in Event.Status.values:
            qs = qs.filter(status=status_filter)
        else:
            qs = qs.filter(status=Event.Status.PENDING_APPROVAL)

        if priority_filter in Event.Priority.values:
            qs = qs.filter(priority=priority_filter)
        if venue_id:
            qs = qs.filter(venue_id=venue_id)
        if event_type_id:
            qs = qs.filter(event_type_id=event_type_id)
        if start_date:
            try:
                from datetime import datetime

                qs = qs.filter(planned_date__gte=datetime.strptime(start_date, "%Y-%m-%d").date())
            except ValueError:
                pass
        if end_date:
            try:
                from datetime import datetime

                qs = qs.filter(planned_date__lte=datetime.strptime(end_date, "%Y-%m-%d").date())
            except ValueError:
                pass

        # Annotate with conflict flag
        # We can't easily annotate conflicts purely in ORM
        # without complex raw SQL (overlapping time checks).
        # Conflicts are checked in python in get_context_data.
        return qs

    def get_context_data(self, **kwargs):
        from apps.events.models import EventType
        from apps.events.services.conflicts import find_conflicting_events
        from apps.venues.models import Venue

        context = super().get_context_data(**kwargs)

        # Calculate conflicts for pending events
        events_with_conflicts = []
        for event in context["events"]:
            conflicts = []
            if event.status == Event.Status.PENDING_APPROVAL:
                conflicts_qs = find_conflicting_events(
                    venue=event.venue,
                    planned_date=event.planned_date,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    exclude_event_id=str(event.pk),
                )
                if conflicts_qs.exists():
                    conflicts = list(conflicts_qs)

            event.conflicting_events = conflicts
            event.can_override = self.request.user.is_superuser or user_has_capability(
                self.request.user, Capability.OVERRIDE_EVENTS
            )
            events_with_conflicts.append(event)

        context["events"] = events_with_conflicts

        context.update(
            {
                "nav_key": "approvals",
                "page_title": _("Approval Center"),
                "current_status": self.request.GET.get("status", Event.Status.PENDING_APPROVAL),
                "current_priority": self.request.GET.get("priority", ""),
                "selected_venue": self.request.GET.get("venue", ""),
                "selected_type": self.request.GET.get("type", ""),
                "start_date": self.request.GET.get("start_date", ""),
                "end_date": self.request.GET.get("end_date", ""),
                "pending_count": Event.objects.filter(status=Event.Status.PENDING_APPROVAL).count(),
                "my_pending_count": Event.objects.filter(
                    management_responsible=self.request.user,
                    status=Event.Status.PENDING_APPROVAL,
                ).count(),
                "event_types": EventType.objects.filter(is_active=True),
                "venues": Venue.objects.filter(is_active=True, display_enabled=True),
                "priorities": Event.Priority.choices,
                "statuses": Event.Status.choices,
                "search_query": self.request.GET.get("q", ""),
                "status_filter": self.request.GET.get(
                    "status", Event.Status.PENDING_APPROVAL
                ),
            }
        )
        return context


class EventApproveView(LoginRequiredMixin, CapabilityRequiredMixin, View):
    required_capability = Capability.APPROVE_EVENTS

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        notes = request.POST.get("notes", "")
        try:
            from apps.events.services.workflow import approve_event

            approve_event(event, request.user, notes=notes)
            messages.success(
                request,
                _("Event “%(title)s” approved successfully.") % {"title": event.title},
            )
        except ValidationError as exc:
            messages.error(request, exc.message)

        return redirect(reverse("events:detail", kwargs={"pk": event.pk}))


class EventRejectView(LoginRequiredMixin, CapabilityRequiredMixin, FormView):
    required_capability = Capability.APPROVE_EVENTS
    template_name = "events/event_confirm_reject.html"

    def dispatch(self, request, *args, **kwargs):
        from apps.events.forms import EventRejectForm

        self.form_class = EventRejectForm
        self.event = get_object_or_404(Event, pk=kwargs["pk"])
        if self.event.status != Event.Status.PENDING_APPROVAL:
            messages.warning(request, _("Event is not pending approval."))
            return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.event
        context["page_title"] = _("Reject Event — %(title)s") % {"title": self.event.title}
        return context

    def form_valid(self, form):
        from apps.events.services.workflow import reject_event

        reason = form.cleaned_data["reason"]
        try:
            reject_event(self.event, self.request.user, reason=reason)
            messages.success(
                self.request,
                _("Event “%(title)s” rejected.") % {"title": self.event.title},
            )
        except ValidationError as exc:
            messages.error(self.request, exc.message)

        return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))


class EventResubmitView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_owner = request.user == event.responsible_employee or request.user == event.created_by
        is_admin = user_has_capability(request.user, Capability.MANAGE_EVENTS)
        if not (is_owner or is_admin):
            raise PermissionDenied(_("Only the responsible employee or admin can resubmit."))

        try:
            from apps.events.services.workflow import resubmit_event

            resubmit_event(event, request.user)
            messages.success(
                request,
                _("Event “%(title)s” resubmitted for approval.") % {"title": event.title},
            )
        except ValidationError as exc:
            messages.error(request, exc.message)

        return redirect(reverse("events:detail", kwargs={"pk": event.pk}))


class EventEmergencyOverrideView(LoginRequiredMixin, CapabilityRequiredMixin, FormView):
    required_capability = Capability.MANAGE_EVENTS
    template_name = "events/event_confirm_override.html"

    def dispatch(self, request, *args, **kwargs):
        from apps.events.forms import EventEmergencyOverrideForm

        self.form_class = EventEmergencyOverrideForm
        self.event = get_object_or_404(Event, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.events.services.conflicts import find_conflicting_events

        conflicts = find_conflicting_events(
            venue=self.event.venue,
            planned_date=self.event.planned_date,
            start_time=self.event.start_time,
            end_time=self.event.end_time,
            exclude_event_id=str(self.event.pk),
        )
        context["event"] = self.event
        context["conflicting_events"] = conflicts
        context["page_title"] = _("Emergency Override — %(title)s") % {"title": self.event.title}
        return context

    def form_valid(self, form):
        from apps.events.services.emergency import execute_emergency_override

        justification = form.cleaned_data["justification"]
        try:
            ev, displaced = execute_emergency_override(
                self.event, self.request.user, justification=justification
            )
            messages.success(
                self.request,
                _("Emergency override executed! %(count)d event(s) displaced.")
                % {"count": len(displaced)},
            )
        except ValidationError as exc:
            messages.error(self.request, exc.message)

        return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))


class DisplacedEventsListView(LoginRequiredMixin, CapabilityRequiredMixin, ListView):
    required_capability = Capability.VIEW_MASTER_DATA
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 15

    def get_queryset(self):
        return Event.objects.filter(status=Event.Status.DISPLACED).select_related(
            "venue", "event_type", "responsible_employee", "displaced_by_event"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "nav_key": "displaced",
                "page_title": _("Displaced Events"),
            }
        )
        return context


class EventPostponeView(LoginRequiredMixin, FormView):
    template_name = "events/event_confirm_postpone.html"

    def dispatch(self, request, *args, **kwargs):
        from apps.events.forms import EventPostponeForm

        self.form_class = EventPostponeForm
        self.event = get_object_or_404(Event, pk=kwargs["pk"])
        is_owner = (
            request.user == self.event.responsible_employee or request.user == self.event.created_by
        )
        is_admin = (
            user_has_capability(request.user, Capability.MANAGE_EVENTS) or request.user.is_superuser
        )
        if not (is_owner or is_admin):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.event
        context["page_title"] = _("Postpone Event — %(title)s") % {"title": self.event.title}
        return context

    def form_valid(self, form):
        from apps.events.services.workflow import postpone_event

        reason = form.cleaned_data.get("reason", "")
        try:
            postpone_event(self.event, self.request.user, reason=reason)
            messages.success(
                self.request,
                _("Event “%(title)s” has been postponed.") % {"title": self.event.title},
            )
        except ValidationError as exc:
            messages.error(self.request, exc.message)

        return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))


class EventRescheduleView(LoginRequiredMixin, FormView):
    template_name = "events/event_reschedule.html"

    def dispatch(self, request, *args, **kwargs):
        from apps.events.forms import EventRescheduleForm

        self.form_class = EventRescheduleForm
        self.event = get_object_or_404(Event, pk=kwargs["pk"])
        is_owner = (
            request.user == self.event.responsible_employee or request.user == self.event.created_by
        )
        is_admin = (
            user_has_capability(request.user, Capability.MANAGE_EVENTS) or request.user.is_superuser
        )
        if not (is_owner or is_admin):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "planned_date": self.event.planned_date,
            "start_time": self.event.start_time,
            "end_time": self.event.end_time,
            "venue": self.event.venue,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.event
        context["page_title"] = _("Reschedule Event — %(title)s") % {"title": self.event.title}
        return context

    def form_valid(self, form):
        from apps.events.services.workflow import reschedule_event

        planned_date = form.cleaned_data["planned_date"]
        start_time = form.cleaned_data["start_time"]
        end_time = form.cleaned_data["end_time"]
        venue = form.cleaned_data.get("venue") or self.event.venue

        try:
            reschedule_event(
                self.event,
                self.request.user,
                planned_date=planned_date,
                start_time=start_time,
                end_time=end_time,
                venue=venue,
            )
            messages.success(
                self.request,
                _("Event “%(title)s” successfully rescheduled.") % {"title": self.event.title},
            )
            return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return self.form_invalid(form)


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


# --- Phase 4 Program & Public Page Views ---

class PublicKioskView(TemplateView):
    template_name = "events/public_kiosk.html"

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        
        events_today = Event.objects.filter(
            is_public_enabled=True,
            planned_date=today,
            status=Event.Status.APPROVED
        ).order_by('start_time').select_related("event_type", "venue")
        
        # We can also filter out events that are not publicly accessible if there are other conditions (like checkin_status)
        # But for now, is_public_enabled=True and status=APPROVED is sufficient for the kiosk.
        
        context["events_today"] = events_today
        context["now"] = now
        return context

class PublicEventPageView(DetailView):
    model = Event
    template_name = "events/public_event_detail.html"
    context_object_name = "event"
    slug_field = "public_token"
    slug_url_kwarg = "public_token"

    def dispatch(self, request, *args, **kwargs):
        from config.rate_limit import is_rate_limited
        from config.views import rate_limited_response

        token = kwargs.get("public_token", "")
        if is_rate_limited(request, "public-event", 600, 60, token):
            return rate_limited_response(request)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        token = self.kwargs.get("public_token")
        event = get_object_or_404(
            Event.objects.select_related("event_type", "venue").prefetch_related(
                "organizing_organizations", "sponsors", "program_items__speaker"
            ),
            public_token=token,
        )
        if not event.is_publicly_accessible:
            raise Http404(_("This event page is not currently published or unavailable."))
        return event

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if not self.request.COOKIES.get(CHECKIN_COOKIE_NAME):
            token, _ = get_or_create_browser_checkin_token(self.request)
            response.set_cookie(
                CHECKIN_COOKIE_NAME,
                token,
                max_age=365 * 24 * 3600,
                samesite="Lax",
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
            )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        context["countdown_info"] = event.public_countdown_info
        context["program_source"] = event.program_source

        if event.program_source == Event.ProgramSource.PDF and event.program_pdf:
            context["has_pdf"] = True
            context["pdf_url"] = event.program_pdf.url
        else:
            context["has_pdf"] = False

        agenda_items = list(event.program_items.all())
        context["agenda_items"] = agenda_items

        speakers = []
        seen_speaker_ids = set()
        for item in agenda_items:
            sp = item.speaker
            if sp and sp.public_profile_enabled and sp.pk not in seen_speaker_ids:
                seen_speaker_ids.add(sp.pk)
                speakers.append(sp)
        context["speakers"] = speakers

        scheme = self.request.scheme
        host = self.request.get_host()
        context["public_url"] = f"{scheme}://{host}/event/{event.public_token}/"

        # Phase 5 Attendance context
        status_info = event.checkin_status()
        checked_in, _ = is_already_checked_in(event, self.request)
        context["checkin_status"] = status_info
        context["attendance_count"] = event.attendances.count()
        context["user_checked_in"] = checked_in
        context["scanned"] = self.request.GET.get("scan") == "true"
        return context


class EventProgramEditView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/event_program_edit.html"
    context_object_name = "event"

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_object()
        is_owner = (
            request.user == self.event.responsible_employee or request.user == self.event.created_by
        )
        is_admin = (
            user_has_capability(request.user, Capability.MANAGE_EVENTS) or request.user.is_superuser
        )
        if not (is_owner or is_admin):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "nav_key": "events",
                "page_title": _("Manage Program & Public Page"),
                "mode_form": EventProgramModeForm(instance=self.event),
                "pdf_form": EventProgramPdfForm(),
                "banner_form": EventBannerImageForm(),
                "item_form": EventProgramItemForm(),
                "program_items": self.event.program_items.select_related("speaker").all(),
                "speakers": Speaker.objects.filter(public_profile_enabled=True),
                "public_url": f"{self.request.scheme}://{self.request.get_host()}/event/{self.event.public_token}/",
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        from apps.events.services.program import (
            add_program_item,
            remove_banner_image,
            remove_program_item,
            remove_program_pdf,
            rotate_public_token,
            set_public_enabled,
            update_program_source,
            upload_banner_image,
            upload_program_pdf,
        )

        action = request.POST.get("action")

        if action == "set_source":
            form = EventProgramModeForm(request.POST, instance=self.event)
            if form.is_valid():
                form.save()
                update_program_source(self.event, request.user, form.cleaned_data["program_source"])
                messages.success(request, _("Program details updated successfully."))
            else:
                messages.error(request, _("Error updating program details."))

        elif action == "upload_pdf":
            pdf_form = EventProgramPdfForm(request.POST, request.FILES)
            if pdf_form.is_valid():
                try:
                    upload_program_pdf(
                        self.event, request.user, pdf_form.cleaned_data["program_pdf"]
                    )
                    messages.success(request, _("Program PDF uploaded successfully."))
                except ValidationError as exc:
                    messages.error(request, exc.message)
            else:
                messages.error(
                    request,
                    _("Invalid file. Only PDF documents up to 10 MB are allowed."),
                )

        elif action == "remove_pdf":
            remove_program_pdf(self.event, request.user)
            messages.success(request, _("Program PDF document removed."))

        elif action == "upload_banner":
            banner_form = EventBannerImageForm(request.POST, request.FILES)
            if banner_form.is_valid():
                upload_banner_image(
                    self.event, request.user, banner_form.cleaned_data["banner_image"]
                )
                messages.success(request, _("Event banner image uploaded successfully."))
            else:
                messages.error(request, _("Invalid image file."))

        elif action == "remove_banner":
            remove_banner_image(self.event, request.user)
            messages.success(request, _("Event banner image removed."))

        elif action == "add_item":
            item_form = EventProgramItemForm(request.POST)
            if item_form.is_valid():
                add_program_item(
                    self.event,
                    request.user,
                    title=item_form.cleaned_data["title"],
                    start_time=item_form.cleaned_data["start_time"],
                    end_time=item_form.cleaned_data["end_time"],
                    description=item_form.cleaned_data.get("description", ""),
                    speaker=item_form.cleaned_data.get("speaker"),
                    speaker_name_override=item_form.cleaned_data.get("speaker_name_override", ""),
                    sort_order=item_form.cleaned_data.get("sort_order", 0),
                )
                messages.success(request, _("Agenda item added successfully."))
            else:
                messages.error(request, _("Error adding agenda item."))

        elif action == "delete_item":
            item_id = request.POST.get("item_id")
            if item_id:
                item = get_object_or_404(EventProgramItem, pk=item_id, event=self.event)
                remove_program_item(item, request.user)
                messages.success(request, _("Agenda item removed."))

        elif action == "rotate_token":
            rotate_public_token(self.event, request.user)
            messages.success(request, _("Public token rotated successfully."))

        elif action == "toggle_public":
            is_enabled = request.POST.get("is_public_enabled") == "true"
            set_public_enabled(self.event, request.user, is_enabled)
            status_text = _("enabled") if is_enabled else _("disabled")
            messages.success(request, _("Public page %(status)s.") % {"status": status_text})

        return redirect(reverse("events:program", kwargs={"pk": self.event.pk}))


class EventQrCodePngView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        public_url = f"{request.scheme}://{request.get_host()}/event/{event.public_token}/?scan=true"
        from apps.events.services.qr import generate_qr_code_png

        log_audit_event(
            "event.qr_generated",
            actor=request.user,
            target=event,
            payload={"format": "png"},
        )
        png_bytes = generate_qr_code_png(public_url)
        return HttpResponse(png_bytes, content_type="image/png")


class EventQrCodeSvgView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        public_url = f"{request.scheme}://{request.get_host()}/event/{event.public_token}/?scan=true"
        from apps.events.services.qr import generate_qr_code_svg

        log_audit_event(
            "event.qr_generated",
            actor=request.user,
            target=event,
            payload={"format": "svg"},
        )
        svg_xml = generate_qr_code_svg(public_url)
        return HttpResponse(svg_xml, content_type="image/svg+xml")


class EventPrintQrView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/event_print_qr.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        log_audit_event("event.qr_printed", actor=self.request.user, target=event)
        context["public_url"] = (
            f"{self.request.scheme}://{self.request.get_host()}/event/{event.public_token}/"
        )
        return context


class SpeakerListView(LoginRequiredMixin, ListView):
    model = Speaker
    template_name = "events/speaker_list.html"
    context_object_name = "speakers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_key"] = "events"
        context["page_title"] = _("Speakers Directory")
        return context


class SpeakerCreateView(LoginRequiredMixin, CreateView):
    model = Speaker
    form_class = SpeakerForm
    template_name = "events/speaker_form.html"
    success_url = reverse_lazy("events:speaker-list")

    def form_valid(self, form):
        messages.success(self.request, _("Speaker added successfully."))
        return super().form_valid(form)


class EventOverrideView(LoginRequiredMixin, CapabilityRequiredMixin, FormView):
    required_capability = Capability.OVERRIDE_EVENTS
    template_name = "events/event_confirm_override.html"

    def dispatch(self, request, *args, **kwargs):
        from apps.events.forms import EventRejectForm  # Reusing reject form for reason

        self.form_class = EventRejectForm
        self.event = get_object_or_404(Event, pk=kwargs["pk"])
        if self.event.status != Event.Status.PENDING_APPROVAL:
            messages.warning(request, _("Event is not pending approval."))
            return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        from apps.events.services.conflicts import find_conflicting_events

        context = super().get_context_data(**kwargs)
        context["event"] = self.event
        context["page_title"] = _('Override Conflict for "%(title)s"') % {"title": self.event.title}
        context["conflicting_events"] = find_conflicting_events(
            venue=self.event.venue,
            planned_date=self.event.planned_date,
            start_time=self.event.start_time,
            end_time=self.event.end_time,
            exclude_event_id=str(self.event.pk),
        )
        return context

    def form_valid(self, form):
        from apps.events.services.workflow import override_event

        reason = form.cleaned_data["reason"]
        try:
            override_event(self.event, self.request.user, reason=reason)
            messages.success(
                self.request,
                _("Event '%(title)s' approved via priority override.")
                % {"title": self.event.title},
            )
        except ValidationError as exc:
            messages.error(self.request, exc.message)
            return self.form_invalid(form)

        return redirect(reverse("events:detail", kwargs={"pk": self.event.pk}))


class SpeakerUpdateView(LoginRequiredMixin, UpdateView):
    model = Speaker
    form_class = SpeakerForm
    template_name = "events/speaker_form.html"
    success_url = reverse_lazy("events:speaker-list")

    def form_valid(self, form):
        messages.success(self.request, _("Speaker updated successfully."))
        return super().form_valid(form)
