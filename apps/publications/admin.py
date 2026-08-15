from django.contrib import admin

from apps.publications.models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("headline", "event", "platform", "language", "status", "scheduled_for")
    list_filter = ("platform", "language", "status")
    search_fields = ("headline", "event__title")
    readonly_fields = (
        "id",
        "external_post_id",
        "external_container_id",
        "published_at",
        "error_code",
        "error_message",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("event", "created_by", "approved_by")
    date_hierarchy = "scheduled_for"

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def has_delete_permission(self, request, obj=None):
        safe = {
            Publication.Status.DRAFT,
            Publication.Status.READY,
            Publication.Status.FAILED,
            Publication.Status.CANCELLED,
        }
        return bool(obj and obj.status in safe and super().has_delete_permission(request, obj))
