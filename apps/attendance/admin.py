from django.contrib import admin

from apps.attendance.models import EventAttendance


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "attendee_name",
        "attendee_organization",
        "checkin_method",
        "checked_in_at",
    )
    list_filter = ("checkin_method", "checked_in_at")
    search_fields = ("event__title", "attendee_name", "attendee_organization")
    date_hierarchy = "checked_in_at"
    readonly_fields = tuple(field.name for field in EventAttendance._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
