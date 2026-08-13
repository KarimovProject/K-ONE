from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.accounts.rbac import Capability, CapabilityRequiredMixin


class MasterDataContextMixin:
    nav_key = ""
    page_title = ""
    page_description = ""
    resource_name = ""
    resource_name_plural = ""
    list_url_name = ""
    create_url_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "nav_key": self.nav_key,
                "page_title": self.page_title,
                "page_description": self.page_description,
                "resource_name": self.resource_name,
                "resource_name_plural": self.resource_name_plural,
                "list_url_name": self.list_url_name,
                "create_url_name": self.create_url_name,
                "can_manage": self.request.user.has_capability(Capability.MANAGE_MASTER_DATA),
            }
        )
        return context


class MasterDataReadMixin(LoginRequiredMixin, CapabilityRequiredMixin):
    required_capability = Capability.VIEW_MASTER_DATA


class MasterDataManageMixin(LoginRequiredMixin, CapabilityRequiredMixin):
    required_capability = Capability.MANAGE_MASTER_DATA


class MasterDataListMixin:
    paginate_by = 20
    search_fields: tuple[str, ...] = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "all")
        if query and self.search_fields:
            predicate = Q()
            for field in self.search_fields:
                predicate |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(predicate)
        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["status_filter"] = self.request.GET.get("status", "all")
        context["total_count"] = self.get_queryset().count()
        return context


class MasterDataFormMixin:
    template_name = "master_data/form.html"

    def get_success_url(self):
        return reverse_lazy(self.list_url_name)

    def form_valid(self, form):
        action = _("updated") if form.instance.pk else _("created")
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("%(resource)s was %(action)s successfully.")
            % {"resource": self.resource_name, "action": action},
        )
        return response


class MasterDataDeleteMixin:
    template_name = "master_data/confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy(self.list_url_name)

    def form_valid(self, form):
        messages.success(
            self.request,
            _("%(resource)s was deleted.") % {"resource": self.resource_name},
        )
        return super().form_valid(form)
