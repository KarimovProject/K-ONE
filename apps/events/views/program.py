
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.events.forms import (
    EventBannerImageForm,
    EventProgramItemForm,
    EventProgramModeForm,
    EventProgramPdfForm,
    SpeakerForm,
)
from apps.events.models import Event, EventProgramItem, Speaker
from apps.events.selectors import can_manage_event


class EventProgramEditView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/event_program_edit.html"
    context_object_name = "event"

    def dispatch(self, request, *args, **kwargs):
        self.event = self.get_object()
        if not can_manage_event(request.user, self.event):
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


class SpeakerListView(LoginRequiredMixin, ListView):
    model = Speaker
    template_name = "events/speaker_list.html"
    context_object_name = "speakers"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_key"] = "speakers"
        context["page_title"] = _("Speakers Directory")
        return context


class SpeakerCreateView(LoginRequiredMixin, CreateView):
    model = Speaker
    form_class = SpeakerForm
    template_name = "events/speaker_form.html"
    success_url = reverse_lazy("events:speaker-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_key"] = "speakers"
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Speaker added successfully."))
        return super().form_valid(form)


class SpeakerUpdateView(LoginRequiredMixin, UpdateView):
    model = Speaker
    form_class = SpeakerForm
    template_name = "events/speaker_form.html"
    success_url = reverse_lazy("events:speaker-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["nav_key"] = "speakers"
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Speaker updated successfully."))
        return super().form_valid(form)
