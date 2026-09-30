from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from apps.accounts.rbac import Capability, CapabilityRequiredMixin, user_has_capability
from apps.audit.services import log_audit_event
from apps.events.forms import (
    EventCancelForm,
    EventUpdateForm,
)
from apps.events.models import Event
from apps.events.selectors import active_event_types, base_event_queryset
from apps.events.services.conflicts import validate_and_lock_event_reservation
from apps.events.services.doctors import (
    busy_attending_doctor_errors,
    notify_assigned_doctors,
)
from apps.notifications.telegram.services import schedule_responsible_assignment
from apps.venues.selectors import active_venues
from config.master_data import (
    MasterDataDeleteMixin,
)

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
        event = self.object
        user = self.request.user

        is_owner = user == event.responsible_employee or user == event.created_by
        is_mgmt = user == event.management_responsible or user_has_capability(
            user, Capability.APPROVE_EVENTS
        )
        is_admin = user_has_capability(user, Capability.MANAGE_EVENTS)
        is_override_authorized = user_has_capability(user, Capability.OVERRIDE_EVENTS)

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
                    and event.status
                    in (Event.Status.DRAFT, Event.Status.REJECTED, Event.Status.PLANNED)
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
        ):
            raise PermissionDenied
        # form.save(commit=False) mutates this same instance in place during
        # is_valid(), so the pre-edit value must be captured here, before
        # the form ever touches it, to detect a reassignment in form_valid().
        self._previous_responsible_id = event.responsible_employee_id
        return event

    def form_valid(self, form):
        event = form.save(commit=False)
        event.updated_by = self.request.user
        previously_attending_doctor_ids = set(event.attending_doctors.values_list("pk", flat=True))

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

        # A doctor already marked busy for this time cannot be assigned —
        # checked against the form's selection before anything is saved.
        attending_doctors = form.cleaned_data.get("attending_doctors")
        if attending_doctors:
            for error in busy_attending_doctor_errors(
                attending_doctors,
                event.planned_date,
                event.start_time,
                event.end_time,
                exclude_event_id=event.pk,
            ):
                form.add_error(None, error)
            if form.errors:
                return self.form_invalid(form)

        event.save()
        form.save_m2m()

        newly_assigned_doctors = event.attending_doctors.exclude(
            pk__in=previously_attending_doctor_ids
        )
        if newly_assigned_doctors.exists():
            notify_assigned_doctors(event, newly_assigned_doctors)

        if event.responsible_employee_id != self._previous_responsible_id:
            schedule_responsible_assignment(event)

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


class EventDeleteView(
    LoginRequiredMixin, CapabilityRequiredMixin, MasterDataDeleteMixin, DeleteView
):
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
