from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.audit.services import log_audit_event
from apps.events.models import Event
from apps.publications.adapters import PublicationAdapterError
from apps.publications.forms import PublicationForm
from apps.publications.models import Publication
from apps.publications.policies import ELIGIBLE_STATUSES, can_approve, can_prepare, can_publish
from apps.publications.services import (
    approve_publication,
    cancel_publication,
    mark_publication_failed,
    prepare_publication,
    publish_publication,
    schedule_publication,
)


class PublicationListView(LoginRequiredMixin, ListView):
    model = Publication
    template_name = "publications/list.html"
    context_object_name = "publications"
    paginate_by = 25

    def get_queryset(self):
        queryset = Publication.objects.select_related("event", "created_by")
        query = self.request.GET.get("q", "").strip()
        for field in ("platform", "language", "status"):
            value = self.request.GET.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        if query:
            queryset = queryset.filter(
                Q(headline__icontains=query) | Q(event__title__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        counts = dict(Publication.objects.values_list("status").annotate(total=Count("id")))
        context.update(
            {
                "nav_key": "publications",
                "counts": counts,
                "statuses": Publication.Status.choices,
                "platforms": Publication.Platform.choices,
                "languages": (("uz", "UZ"), ("ru", "RU"), ("en", "EN")),
                "can_create": can_prepare(self.request.user),
            }
        )
        return context


class PublicationCreateView(LoginRequiredMixin, CreateView):
    model = Publication
    form_class = PublicationForm
    template_name = "publications/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs["event_pk"], status__in=ELIGIBLE_STATUSES)
        if not can_prepare(request.user, self.event):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "headline": self.event.title,
            "short_description": self.event.description,
            "language": self.request.user.preferred_language,
        }

    def form_valid(self, form):
        form.instance.event = self.event
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_audit_event("publication.created", actor=self.request.user, target=self.object)
        return response

    def get_success_url(self):
        return reverse("publications:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"event": self.event, "nav_key": "publications", "is_create": True})
        return context


class PublicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Publication
    form_class = PublicationForm
    template_name = "publications/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not can_prepare(request.user, self.object.event) or self.object.status not in (
            Publication.Status.DRAFT,
            Publication.Status.READY,
            Publication.Status.FAILED,
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("publications:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"event": self.object.event, "nav_key": "publications"})
        return context


class PublicationDetailView(LoginRequiredMixin, DetailView):
    model = Publication
    template_name = "publications/detail.html"
    context_object_name = "publication"

    def get_queryset(self):
        return Publication.objects.select_related("event", "created_by", "approved_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "nav_key": "publications",
                "can_edit": can_prepare(self.request.user, self.object.event),
                "can_approve": can_approve(self.request.user),
                "can_publish": can_publish(self.request.user),
            }
        )
        return context


class PublicationActionView(LoginRequiredMixin, View):
    action = ""

    def post(self, request, pk):
        publication = get_object_or_404(Publication, pk=pk)
        try:
            if self.action == "prepare":
                if not can_prepare(request.user, publication.event):
                    raise PermissionDenied
                prepare_publication(publication, request.user)
            elif self.action == "approve":
                if not can_approve(request.user):
                    raise PermissionDenied
                approve_publication(publication, request.user)
            elif self.action == "schedule":
                if not can_publish(request.user):
                    raise PermissionDenied
                schedule_publication(publication, request.user, publication.scheduled_for)
            elif self.action in ("publish", "retry"):
                if not can_publish(request.user):
                    raise PermissionDenied
                if not cache.add(f"publication-action:{publication.pk}", "1", 10):
                    messages.warning(request, "Publication action is already in progress.")
                    return redirect("publications:detail", pk=pk)
                if self.action == "retry":
                    log_audit_event("publication.retried", actor=request.user, target=publication)
                publish_publication(publication.pk)
            elif self.action == "cancel":
                if not can_publish(request.user):
                    raise PermissionDenied
                cancel_publication(publication, request.user)
        except PublicationAdapterError as exc:
            publication.refresh_from_db()
            mark_publication_failed(publication, exc)
            messages.error(request, "Platform publication failed. Review integration settings.")
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(request, "Publication updated.")
        return redirect("publications:detail", pk=pk)
