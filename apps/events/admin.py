from django.contrib import admin

from apps.events.models import EventType


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name_en",
        "color",
        "is_active",
        "requires_management_approval",
        "sort_order",
    )
    list_filter = ("is_active", "requires_management_approval", "allows_emergency_override")
    search_fields = ("code", "name_uz", "name_ru", "name_en")
    ordering = ("sort_order", "code")
