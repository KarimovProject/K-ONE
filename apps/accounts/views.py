from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View

from apps.accounts.forms import (
    MAX_UNAVAILABILITY_SLOTS_PER_YEAR,
    DoctorRegistrationForm,
    ProfileForm,
    StaffUnavailabilityForm,
)
from apps.accounts.models import StaffUnavailability, User
from apps.accounts.rbac import Capability, CapabilityRequiredMixin
from apps.accounts.selectors import is_admin_privileged, manageable_users
from apps.events.models import Event
from config.rate_limit import clear_rate_limit, is_rate_limited


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Profile updated successfully."))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "nav_key": "profile",
                "assigned_count": user.responsible_events.count(),
                "management_count": user.management_events.count(),
                "telegram_connected": bool(
                    getattr(user, "telegram_connection", None)
                    and user.telegram_connection.is_active
                ),
                "upcoming_assigned_events": (
                    Event.objects.filter(
                        Q(responsible_employee=user)
                        | Q(management_responsible=user)
                        | Q(attending_doctors=user)
                    )
                    .filter(planned_date__gte=timezone.localdate())
                    .distinct()
                    .select_related("venue", "event_type")
                    .order_by("planned_date", "start_time")
                ),
            }
        )
        if user.role == User.Role.DOCTOR:
            context["speaker_events_count"] = user.attending_events.count()
        return context


class DoctorRegisterView(CreateView):
    model = User
    form_class = DoctorRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("register-submitted")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if is_rate_limited(request, "register", 5, 300):
            return render(
                request,
                "errors/429.html",
                {"message": _("Too many registration attempts. Please try again later.")},
                status=429,
            )
        response = super().post(request, *args, **kwargs)
        clear_rate_limit(request, "register")
        return response

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["just_registered_username"] = self.object.username
        return response


class RegistrationSubmittedView(TemplateView):
    """A dedicated, unmissable confirmation screen shown right after
    self-registration. Messages set via the `messages` framework never
    render on unauthenticated pages (base.html only shows them inside
    the authenticated shell), so a plain redirect to `login` silently
    dropped the "your account is pending approval" notice — new doctors
    had no idea their application had actually gone through."""

    template_name = "registration/register_submitted.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.request.session.pop("just_registered_username", None)
        return context


class MyEventsListView(LoginRequiredMixin, ListView):
    """Shared base for the three "my events" pages linked from the profile
    KPI tiles. Splits the user's events into a past section (most recent
    first) and an upcoming section (soonest first) shown below it."""

    template_name = "accounts/event_relation_list.html"
    context_object_name = "events"
    relation_field = ""
    page_heading = ""
    page_description = ""
    empty_message = ""

    def get_queryset(self):
        return getattr(self.request.user, self.relation_field).select_related(
            "venue", "event_type"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        events = list(context[self.context_object_name])
        context["past_events"] = sorted(
            (event for event in events if event.planned_date < today),
            key=lambda event: (event.planned_date, event.start_time),
            reverse=True,
        )
        context["upcoming_events"] = sorted(
            (event for event in events if event.planned_date >= today),
            key=lambda event: (event.planned_date, event.start_time),
        )
        context.update(
            {
                "nav_key": "profile",
                "page_heading": self.page_heading,
                "page_description": self.page_description,
                "empty_message": self.empty_message,
            }
        )
        return context


class ResponsibleEventsListView(MyEventsListView):
    relation_field = "responsible_events"
    page_heading = _("Assigned events")
    page_description = _("All events where you are the responsible employee.")
    empty_message = _("You are not currently responsible for any events.")


class ManagementEventsListView(MyEventsListView):
    relation_field = "management_events"
    page_heading = _("Management events")
    page_description = _("All events where you are the management responsible.")
    empty_message = _("You are not currently the management responsible for any events.")


class DoctorAssignedEventsView(MyEventsListView):
    relation_field = "attending_events"
    page_heading = _("Speaker-assigned events")
    page_description = _("All events where you are assigned as a speaker doctor.")
    empty_message = _("You don't have any speaker-assigned events yet.")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role != User.Role.DOCTOR:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AvailabilityListView(LoginRequiredMixin, ListView):
    model = StaffUnavailability
    template_name = "accounts/availability.html"
    context_object_name = "slots"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role != User.Role.DOCTOR:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return StaffUnavailability.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_key"] = "availability"
        context.setdefault("form", StaffUnavailabilityForm(user=self.request.user))
        current_year = date.today().year
        context["slots_used_this_year"] = StaffUnavailability.objects.filter(
            user=self.request.user, start_date__year=current_year
        ).count()
        context["slots_limit_per_year"] = MAX_UNAVAILABILITY_SLOTS_PER_YEAR
        context["current_year"] = current_year
        return context

    def post(self, request, *args, **kwargs):
        form = StaffUnavailabilityForm(request.POST, user=request.user)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.user = request.user
            slot.save()
            messages.success(request, _("Busy time slot added."))
            return redirect("doctor-availability")
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class AdminDoctorAvailabilityView(LoginRequiredMixin, CapabilityRequiredMixin, ListView):
    """Admin-only management of a specific doctor's busy/unavailability
    slots. Doctors can still add their own slots (AvailabilityListView),
    but may no longer delete them — that self-service loophole let a
    doctor mark themselves busy and then un-mark it right before a
    conflict check, defeating the whole point of the record. Only staff
    with MANAGE_USERS can remove a slot here, or add one on the doctor's
    behalf without the yearly self-service cap applying."""

    required_capability = Capability.MANAGE_USERS
    model = StaffUnavailability
    template_name = "accounts/admin_doctor_availability.html"
    context_object_name = "slots"

    def get_doctor(self):
        return get_object_or_404(User, pk=self.kwargs["pk"], role=User.Role.DOCTOR)

    def get_queryset(self):
        return StaffUnavailability.objects.filter(user=self.get_doctor())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_key"] = "users"
        context["doctor"] = self.get_doctor()
        context.setdefault("form", StaffUnavailabilityForm())
        return context

    def post(self, request, *args, **kwargs):
        doctor = self.get_doctor()
        form = StaffUnavailabilityForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.user = doctor
            slot.save()
            messages.success(
                request,
                _("Busy time slot added for %(doctor)s.")
                % {"doctor": doctor.get_full_name() or doctor.username},
            )
            return redirect("admin-doctor-availability", pk=doctor.pk)
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class AdminAvailabilityDeleteView(LoginRequiredMixin, CapabilityRequiredMixin, View):
    required_capability = Capability.MANAGE_USERS

    def post(self, request, pk, *args, **kwargs):
        slot = get_object_or_404(StaffUnavailability, pk=pk)
        doctor_pk = slot.user_id
        slot.delete()
        messages.success(request, _("Busy time slot removed."))
        return redirect("admin-doctor-availability", pk=doctor_pk)


class UserManagementListView(LoginRequiredMixin, CapabilityRequiredMixin, ListView):
    """Sibling page to /profile/ for approving pending registrations (doctors)
    and managing account activity, without needing Django Admin access."""

    model = User
    required_capability = Capability.MANAGE_USERS
    template_name = "accounts/user_management.html"
    context_object_name = "users"

    def get_queryset(self):
        return (
            manageable_users()
            .select_related("doctor_profile")
            .order_by("is_active", "first_name", "last_name", "username")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_key"] = "users"
        context["pending_count"] = self.get_queryset().filter(is_active=False).count()
        return context


class UserToggleActiveView(LoginRequiredMixin, CapabilityRequiredMixin, View):
    required_capability = Capability.MANAGE_USERS

    def post(self, request, pk, *args, **kwargs):
        target = get_object_or_404(User, pk=pk)
        if target.pk == request.user.pk:
            messages.error(request, _("You cannot change your own active status here."))
            return redirect("user-management")
        if is_admin_privileged(target):
            raise PermissionDenied
        target.is_active = not target.is_active
        update_fields = ["is_active"]
        if target.is_active and target.approved_at is None:
            target.approved_at = timezone.now()
            update_fields.append("approved_at")
        target.save(update_fields=update_fields)
        if target.is_active:
            messages.success(
                request,
                _("%(user)s activated.") % {"user": target.get_full_name() or target.username},
            )
        else:
            messages.success(
                request,
                _("%(user)s deactivated.") % {"user": target.get_full_name() or target.username},
            )
        return redirect("user-management")
