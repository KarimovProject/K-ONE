
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (
    FormView,
    ListView,
)

from apps.accounts.rbac import Capability, CapabilityRequiredMixin, user_has_capability
from apps.events.models import Event, EventType
from apps.events.selectors import can_manage_event

# --- Phase 3 Approval & Emergency Views ---


class EventSubmitApprovalView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not can_manage_event(request.user, event):
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
        from apps.events.services.conflicts import find_conflicting_events
        from apps.venues.models import Venue

        context = super().get_context_data(**kwargs)

        # Calculate conflicts for pending events
        events_with_conflicts = []
        for event in context["events"]:
            conflicts = []
            if event.status == Event.Status.PENDING_APPROVAL:
                conflicts = list(
                    find_conflicting_events(
                        venue=event.venue,
                        planned_date=event.planned_date,
                        start_time=event.start_time,
                        end_time=event.end_time,
                        exclude_event_id=str(event.pk),
                    )
                )

            event.conflicting_events = conflicts
            event.can_override = user_has_capability(self.request.user, Capability.OVERRIDE_EVENTS)
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
        if not can_manage_event(request.user, event):
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
        if not can_manage_event(request.user, self.event):
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
        if not can_manage_event(request.user, self.event):
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
