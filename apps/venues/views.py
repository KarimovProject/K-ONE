from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.venues.forms import VenueForm
from apps.venues.models import Venue
from config.master_data import (
    MasterDataContextMixin,
    MasterDataDeleteMixin,
    MasterDataFormMixin,
    MasterDataListMixin,
    MasterDataManageMixin,
    MasterDataReadMixin,
)


class VenueContextMixin(MasterDataContextMixin):
    model = Venue
    nav_key = "venues"
    page_title = _("Venues")
    page_description = _("Maintain halls and rooms available to international events.")
    resource_name = _("Venue")
    resource_name_plural = _("venues")
    list_url_name = "venues:list"
    create_url_name = "venues:create"


class VenueListView(MasterDataReadMixin, MasterDataListMixin, VenueContextMixin, ListView):
    template_name = "venues/venue_list.html"
    context_object_name = "venues"
    search_fields = ("code", "name_uz", "name_ru", "name_en", "location")


class VenueDetailView(MasterDataReadMixin, VenueContextMixin, DetailView):
    template_name = "venues/venue_detail.html"
    context_object_name = "venue"


class VenueCreateView(MasterDataManageMixin, MasterDataFormMixin, VenueContextMixin, CreateView):
    form_class = VenueForm
    page_title = _("Create venue")


class VenueUpdateView(MasterDataManageMixin, MasterDataFormMixin, VenueContextMixin, UpdateView):
    form_class = VenueForm
    page_title = _("Edit venue")


class VenueDeleteView(MasterDataManageMixin, MasterDataDeleteMixin, VenueContextMixin, DeleteView):
    page_title = _("Delete venue")
    success_url = reverse_lazy("venues:list")
