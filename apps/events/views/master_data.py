
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.events.forms import (
    EventTypeForm,
)
from apps.events.models import EventType
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
