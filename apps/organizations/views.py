from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.organizations.forms import OrganizationForm, SponsorForm
from apps.organizations.models import Organization, Sponsor
from config.master_data import (
    MasterDataContextMixin,
    MasterDataDeleteMixin,
    MasterDataFormMixin,
    MasterDataListMixin,
    MasterDataManageMixin,
    MasterDataReadMixin,
)


class OrganizationContextMixin(MasterDataContextMixin):
    model = Organization
    nav_key = "organizations"
    page_title = _("Organizations")
    page_description = _("Maintain local, foreign, and partner organization records.")
    resource_name = _("Organization")
    resource_name_plural = _("organizations")
    list_url_name = "organizations:list"
    create_url_name = "organizations:create"


class OrganizationListView(
    MasterDataReadMixin,
    MasterDataListMixin,
    OrganizationContextMixin,
    ListView,
):
    template_name = "organizations/organization_list.html"
    context_object_name = "organizations"
    search_fields = ("name", "short_name", "country", "city", "contact_person")

    def get_queryset(self):
        queryset = super().get_queryset()
        organization_type = self.request.GET.get("type", "all")
        if organization_type in Organization.Type.values:
            queryset = queryset.filter(organization_type=organization_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type_filter"] = self.request.GET.get("type", "all")
        context["organization_types"] = Organization.Type.choices
        return context


class OrganizationDetailView(MasterDataReadMixin, OrganizationContextMixin, DetailView):
    template_name = "organizations/organization_detail.html"
    context_object_name = "organization"


class OrganizationCreateView(
    MasterDataManageMixin,
    MasterDataFormMixin,
    OrganizationContextMixin,
    CreateView,
):
    form_class = OrganizationForm
    page_title = _("Create organization")


class OrganizationUpdateView(
    MasterDataManageMixin,
    MasterDataFormMixin,
    OrganizationContextMixin,
    UpdateView,
):
    form_class = OrganizationForm
    page_title = _("Edit organization")


class OrganizationDeleteView(
    MasterDataManageMixin,
    MasterDataDeleteMixin,
    OrganizationContextMixin,
    DeleteView,
):
    page_title = _("Delete organization")


class SponsorContextMixin(MasterDataContextMixin):
    model = Sponsor
    nav_key = "sponsors"
    page_title = _("Sponsors")
    page_description = _("Maintain sponsor identity and contact records for later event use.")
    resource_name = _("Sponsor")
    resource_name_plural = _("sponsors")
    list_url_name = "sponsors:list"
    create_url_name = "sponsors:create"


class SponsorListView(MasterDataReadMixin, MasterDataListMixin, SponsorContextMixin, ListView):
    template_name = "organizations/sponsor_list.html"
    context_object_name = "sponsors"
    search_fields = ("name", "contact_person", "email", "phone")


class SponsorDetailView(MasterDataReadMixin, SponsorContextMixin, DetailView):
    template_name = "organizations/sponsor_detail.html"
    context_object_name = "sponsor"


class SponsorCreateView(
    MasterDataManageMixin,
    MasterDataFormMixin,
    SponsorContextMixin,
    CreateView,
):
    form_class = SponsorForm
    page_title = _("Create sponsor")


class SponsorUpdateView(
    MasterDataManageMixin,
    MasterDataFormMixin,
    SponsorContextMixin,
    UpdateView,
):
    form_class = SponsorForm
    page_title = _("Edit sponsor")


class SponsorDeleteView(
    MasterDataManageMixin,
    MasterDataDeleteMixin,
    SponsorContextMixin,
    DeleteView,
):
    page_title = _("Delete sponsor")
