from django.contrib import admin

from apps.audit.models import AuditEventLog


@admin.register(AuditEventLog)
class AuditEventLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "action", "actor", "target_repr", "target_id")
    list_filter = ("action", "timestamp")
    search_fields = ("actor__username", "target_repr", "target_id")
    date_hierarchy = "timestamp"
    readonly_fields = tuple(field.name for field in AuditEventLog._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
