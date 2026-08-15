from django.contrib import admin

from apps.venues.models import DisplayToken, Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("code", "name_en", "capacity", "is_active", "display_enabled", "sort_order")
    list_filter = ("is_active", "display_enabled")
    search_fields = ("code", "name_uz", "name_ru", "name_en", "location")
    ordering = ("sort_order", "code")

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions


@admin.register(DisplayToken)
class DisplayTokenAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at", "last_used_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("token", "created_at", "last_used_at")
    actions = ("rotate_tokens", "enable_displays", "disable_displays")

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Rotate selected display tokens")
    def rotate_tokens(self, request, queryset):
        for token in queryset:
            token.rotate(request.user)

    @admin.action(description="Enable selected displays")
    def enable_displays(self, request, queryset):
        for token in queryset:
            token.set_enabled(True, request.user)

    @admin.action(description="Disable selected displays")
    def disable_displays(self, request, queryset):
        for token in queryset:
            token.set_enabled(False, request.user)
