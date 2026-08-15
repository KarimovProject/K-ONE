from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.events.models import Event, EventProgramItem, EventType, Speaker


class NoBulkDeleteAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions


@admin.register(EventType)
class EventTypeAdmin(NoBulkDeleteAdmin):
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
    readonly_fields = ("referenced_events",)

    @admin.display(description="Referenced events")
    def referenced_events(self, obj):
        return obj.events.count() if obj else 0


class EventProgramInline(admin.TabularInline):
    model = EventProgramItem
    extra = 0
    autocomplete_fields = ("speaker",)


@admin.register(Event)
class EventAdmin(NoBulkDeleteAdmin):
    list_display = (
        "event_title",
        "event_schedule",
        "event_venue",
        "event_kind",
        "event_responsible",
        "event_status",
        "event_priority",
    )
    list_filter = (
        "status",
        "priority",
        "planned_date",
        "venue",
        "event_type",
        "display_visibility",
    )
    search_fields = ("title", "venue__code", "venue__name_en", "responsible_employee__username")
    ordering = ("-planned_date", "start_time")
    date_hierarchy = "planned_date"
    autocomplete_fields = (
        "event_type",
        "venue",
        "responsible_employee",
        "management_responsible",
        "created_by",
        "updated_by",
        "reviewed_by",
    )
    filter_horizontal = ("organizing_organizations", "sponsors")
    readonly_fields = (
        "id",
        "public_token",
        "submitted_at",
        "reviewed_at",
        "created_at",
        "updated_at",
    )
    inlines = (EventProgramInline,)
    fieldsets = (
        (
            _("Basic information"),
            {"fields": ("title", "event_type", "description", "status", "priority")},
        ),
        (
            _("Schedule and venue"),
            {
                "fields": (
                    "planned_date",
                    "start_time",
                    "end_time",
                    "venue",
                    "expected_attendees",
                )
            },
        ),
        (
            _("Responsible persons and partners"),
            {
                "fields": (
                    "responsible_employee",
                    "management_responsible",
                    "organizing_organizations",
                    "sponsors",
                )
            },
        ),
        (
            _("Public information and attendance"),
            {
                "fields": (
                    "display_visibility",
                    "is_public_enabled",
                    "public_token",
                    "zoom_url",
                    "registration_url",
                    "program_source",
                    "program_pdf",
                    "program_intro",
                    "program_notes",
                    "checkin_enabled",
                    "checkin_opens_at",
                    "checkin_closes_at",
                )
            },
        ),
        (
            _("Workflow"),
            {
                "fields": (
                    "submitted_at",
                    "reviewed_at",
                    "reviewed_by",
                    "rejection_reason",
                    "emergency_justification",
                    "displaced_by_event",
                )
            },
        ),
        (
            _("Reminder policy"),
            {
                "fields": (
                    "reminders_enabled",
                    "reminder_7d",
                    "reminder_3d",
                    "reminder_1d",
                    "reminder_3h",
                    "reminder_30m",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("System metadata"),
            {
                "fields": ("created_by", "updated_by", "created_at", "updated_at", "notes"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Event"), ordering="title")
    def event_title(self, obj):
        return obj.title

    @admin.display(description=_("Date / time"), ordering="planned_date")
    def event_schedule(self, obj):
        return f"{obj.planned_date:%d.%m.%Y} · {obj.start_time:%H:%M}"

    @admin.display(description=_("Venue"), ordering="venue__name_uz")
    def event_venue(self, obj):
        return obj.venue

    @admin.display(description=_("Type"), ordering="event_type__name_uz")
    def event_kind(self, obj):
        return obj.event_type

    @admin.display(description=_("Responsible"), ordering="responsible_employee__username")
    def event_responsible(self, obj):
        return obj.responsible_employee

    @admin.display(description=_("Status"), ordering="status")
    def event_status(self, obj):
        return _(obj.get_status_display())

    @admin.display(description=_("Priority"), ordering="priority")
    def event_priority(self, obj):
        return _(obj.get_priority_display())

    def has_delete_permission(self, request, obj=None):
        allowed = {Event.Status.DRAFT, Event.Status.REJECTED, Event.Status.CANCELLED}
        return bool(obj and super().has_delete_permission(request, obj) and obj.status in allowed)


@admin.register(Speaker)
class SpeakerAdmin(NoBulkDeleteAdmin):
    list_display = ("full_name", "title", "organization", "country", "public_profile_enabled")
    list_filter = ("public_profile_enabled", "country")
    search_fields = ("full_name", "title", "organization", "country")
    readonly_fields = ("created_at", "updated_at")

    def has_delete_permission(self, request, obj=None):
        return bool(
            obj and not obj.program_items.exists() and super().has_delete_permission(request, obj)
        )


@admin.register(EventProgramItem)
class EventProgramItemAdmin(NoBulkDeleteAdmin):
    list_display = ("title", "event", "start_time", "end_time", "speaker", "sort_order")
    list_filter = ("event__planned_date",)
    search_fields = ("title", "event__title", "speaker__full_name")
    autocomplete_fields = ("event", "speaker")
    readonly_fields = ("created_at", "updated_at")
