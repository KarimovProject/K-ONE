from django.contrib import admin

from apps.publications.models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("headline", "event", "platform", "language", "status", "scheduled_for")
    list_filter = ("platform", "language", "status")
    search_fields = ("headline", "event__title")
    readonly_fields = (
        "external_post_id",
        "external_container_id",
        "published_at",
        "error_code",
        "error_message",
    )
