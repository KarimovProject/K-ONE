from datetime import date, datetime, time
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.accounts.models import User
from apps.accounts.rbac import Capability, CapabilityRequiredMixin
from apps.audit.services import log_audit_event
from apps.events.forms import (
    EventStep1Form,
    EventStep2Form,
    EventStep3Form,
    EventStep4Form,
    EventStep5Form,
)
from apps.events.models import Event, EventType
from apps.events.services.conflicts import (
    check_venue_availability,
    validate_and_lock_event_reservation,
)
from apps.events.views import busy_attending_doctor_errors, notify_assigned_doctors
from apps.organizations.models import Organization, Sponsor
from apps.venues.models import Venue

SESSION_KEY = "event_wizard_data"


class EventWizardView(LoginRequiredMixin, CapabilityRequiredMixin, View):
    required_capability = Capability.CREATE_OWN_EVENTS

    def get_step_forms(self, data=None):
        return {
            1: EventStep1Form(data=data, prefix="step1"),
            2: EventStep2Form(data=data, prefix="step2"),
            3: EventStep3Form(data=data, prefix="step3"),
            4: EventStep4Form(data=data, prefix="step4"),
            5: EventStep5Form(data=data, prefix="step5"),
        }

    def get_session_data(self, request) -> dict[str, Any]:
        return request.session.get(SESSION_KEY, {})

    def save_session_data(self, request, data: dict[str, Any]) -> None:
        request.session[SESSION_KEY] = data
        request.session.modified = True

    def clear_session_data(self, request) -> None:
        if SESSION_KEY in request.session:
            del request.session[SESSION_KEY]
            request.session.modified = True

    def get(self, request):
        current_step = int(request.GET.get("step", 1))
        current_step = max(1, min(5, current_step))

        wizard_data = self.get_session_data(request)

        # Pre-fill forms from session if available
        initial_data = {}
        for step in range(1, 6):
            step_key = f"step{step}"
            if step_key in wizard_data:
                for k, v in wizard_data[step_key].items():
                    initial_data[f"{step_key}-{k}"] = v

        form = self.get_step_forms(initial_data if initial_data else None)[current_step]

        context = self.build_context(request, current_step, form, wizard_data)
        return render(request, f"events/wizard/step_{current_step}.html", context)

    def post(self, request):
        current_step = int(request.POST.get("current_step", 1))
        action = request.POST.get("action", "next")

        wizard_data = self.get_session_data(request)

        if action == "back":
            prev_step = max(1, current_step - 1)
            return redirect(f"{reverse('events:wizard')}?step={prev_step}")

        if action == "reset":
            self.clear_session_data(request)
            return redirect(reverse("events:wizard"))

        # Process step submission
        form = self.get_step_forms(request.POST)[current_step]

        if not form.is_valid():
            context = self.build_context(request, current_step, form, wizard_data)
            return render(request, f"events/wizard/step_{current_step}.html", context)

        # Update session with cleaned data
        cleaned = form.cleaned_data.copy()
        step_dict = {}
        for k, v in cleaned.items():
            if isinstance(v, datetime | date):
                step_dict[k] = v.isoformat()
            elif isinstance(v, time):
                step_dict[k] = v.strftime("%H:%M")
            elif isinstance(v, Venue | EventType | User):
                step_dict[k] = v.pk
            elif hasattr(v, "values_list"):  # QuerySet of ManyToMany
                step_dict[k] = list(v.values_list("pk", flat=True))
            else:
                step_dict[k] = v

        wizard_data[f"step{current_step}"] = step_dict
        self.save_session_data(request, wizard_data)

        # Handle final submission from step 5 or save draft anytime
        if action in ("save_draft", "save_planned") or current_step == 5:
            return self.finalize_event(request, action, wizard_data)

        next_step = min(5, current_step + 1)
        return redirect(f"{reverse('events:wizard')}?step={next_step}")

    def finalize_event(self, request, action: str, wizard_data: dict[str, Any]):
        # Extract fields from all wizard steps
        step1 = wizard_data.get("step1", {})
        step2 = wizard_data.get("step2", {})
        step3 = wizard_data.get("step3", {})
        step4 = wizard_data.get("step4", {})
        step5 = wizard_data.get("step5", {})

        title = step1.get("title", "")
        event_type_id = step1.get("event_type")
        description = step1.get("description", "")
        expected_attendees = int(step1.get("expected_attendees", 1))
        priority = step1.get("priority", Event.Priority.NORMAL)

        planned_date_str = step2.get("planned_date")
        start_time_str = step2.get("start_time")
        end_time_str = step2.get("end_time")
        venue_id = step2.get("venue")

        resp_emp_id = step3.get("responsible_employee")
        mgmt_resp_id = step3.get("management_responsible")

        attending_doctor_ids = step3.get("attending_doctors", [])
        org_ids = step4.get("organizing_organizations", [])
        sponsor_ids = step4.get("sponsors", [])

        zoom_url = step5.get("zoom_url", "")
        registration_url = step5.get("registration_url", "")
        notes = step5.get("notes", "")

        has_required = (
            title
            and event_type_id
            and planned_date_str
            and start_time_str
            and end_time_str
            and venue_id
        )
        if not has_required:
            messages.error(request, _("Please complete all required fields before saving."))
            return redirect(f"{reverse('events:wizard')}?step=1")

        planned_date = datetime.strptime(planned_date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        venue = Venue.objects.get(pk=venue_id)
        event_type = EventType.objects.get(pk=event_type_id)
        resp_emp = User.objects.get(pk=resp_emp_id) if resp_emp_id else request.user
        mgmt_resp = User.objects.get(pk=mgmt_resp_id) if mgmt_resp_id else request.user

        target_status = Event.Status.PLANNED if action == "save_planned" else Event.Status.DRAFT

        try:
            validate_and_lock_event_reservation(
                venue=venue,
                planned_date=planned_date,
                start_time=start_time,
                end_time=end_time,
                status=target_status,
                expected_attendees=expected_attendees,
            )
        except ValidationError as exc:
            messages.error(request, exc.message)
            return redirect(f"{reverse('events:wizard')}?step=2")

        if attending_doctor_ids:
            candidate_doctors = User.objects.filter(pk__in=attending_doctor_ids)
            doctor_errors = busy_attending_doctor_errors(
                candidate_doctors, planned_date, start_time, end_time
            )
            if doctor_errors:
                for error in doctor_errors:
                    messages.error(request, error)
                return redirect(f"{reverse('events:wizard')}?step=3")

        # Create Event record
        event = Event.objects.create(
            title=title,
            event_type=event_type,
            description=description,
            venue=venue,
            planned_date=planned_date,
            start_time=start_time,
            end_time=end_time,
            responsible_employee=resp_emp,
            management_responsible=mgmt_resp,
            zoom_url=zoom_url,
            registration_url=registration_url,
            status=target_status,
            priority=priority,
            expected_attendees=expected_attendees,
            notes=notes,
            created_by=request.user,
            updated_by=request.user,
        )

        if org_ids:
            event.organizing_organizations.set(Organization.objects.filter(pk__in=org_ids))
        if sponsor_ids:
            event.sponsors.set(Sponsor.objects.filter(pk__in=sponsor_ids))
        if attending_doctor_ids:
            event.attending_doctors.set(candidate_doctors)
            notify_assigned_doctors(event, candidate_doctors)

        # Audit logs
        log_audit_event(
            "event.created",
            actor=request.user,
            target=event,
            payload={"status": target_status},
        )
        if target_status == Event.Status.PLANNED:
            log_audit_event("event.planned", actor=request.user, target=event)

        self.clear_session_data(request)
        messages.success(
            request,
            _("Event “%(title)s” saved successfully as %(status)s.")
            % {"title": event.title, "status": event.get_status_display()},
        )
        return redirect(reverse("events:detail", kwargs={"pk": event.pk}))

    def build_context(
        self,
        request,
        current_step: int,
        form,
        wizard_data: dict[str, Any],
    ) -> dict[str, Any]:
        availability_result = None

        # Calculate live availability if Step 2 data is available
        step2 = wizard_data.get("step2", {})
        has_step2_timing = (
            step2.get("venue")
            and step2.get("planned_date")
            and step2.get("start_time")
            and step2.get("end_time")
        )
        if has_step2_timing:
            try:
                venue = Venue.objects.get(pk=step2["venue"])
                p_date = datetime.strptime(step2["planned_date"], "%Y-%m-%d").date()
                s_time = datetime.strptime(step2["start_time"], "%H:%M").time()
                e_time = datetime.strptime(step2["end_time"], "%H:%M").time()
                attendees = int(wizard_data.get("step1", {}).get("expected_attendees", 1))

                availability_result = check_venue_availability(
                    venue=venue,
                    planned_date=p_date,
                    start_time=s_time,
                    end_time=e_time,
                    expected_attendees=attendees,
                )
            except Exception:
                pass

        summary_data = {}
        if current_step == 5:
            summary_data = self.build_summary(wizard_data)

        return {
            "current_step": current_step,
            "form": form,
            "wizard_data": wizard_data,
            "availability_result": availability_result,
            "summary_data": summary_data,
            "page_title": _("Event Planning Wizard — Step %(step)d of 5") % {"step": current_step},
        }

    def build_summary(self, wizard_data: dict[str, Any]) -> dict[str, Any]:
        s1 = wizard_data.get("step1", {})
        s2 = wizard_data.get("step2", {})
        s3 = wizard_data.get("step3", {})
        s4 = wizard_data.get("step4", {})

        event_type = EventType.objects.filter(pk=s1.get("event_type")).first()
        venue = Venue.objects.filter(pk=s2.get("venue")).first()
        resp_emp = User.objects.filter(pk=s3.get("responsible_employee")).first()
        mgmt_resp = User.objects.filter(pk=s3.get("management_responsible")).first()
        attending_doctors = User.objects.filter(pk__in=s3.get("attending_doctors", []))
        orgs = Organization.objects.filter(pk__in=s4.get("organizing_organizations", []))
        sponsors = Sponsor.objects.filter(pk__in=s4.get("sponsors", []))

        return {
            "title": s1.get("title"),
            "event_type": event_type,
            "expected_attendees": s1.get("expected_attendees"),
            "priority": s1.get("priority"),
            "planned_date": s2.get("planned_date"),
            "start_time": s2.get("start_time"),
            "end_time": s2.get("end_time"),
            "venue": venue,
            "responsible_employee": resp_emp,
            "management_responsible": mgmt_resp,
            "attending_doctors": attending_doctors,
            "organizing_organizations": orgs,
            "sponsors": sponsors,
        }
