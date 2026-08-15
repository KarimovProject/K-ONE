from django.contrib import admin

from apps.organizations.models import Organization, Sponsor


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "organization_type", "country", "is_active")
    list_filter = ("organization_type", "is_active", "country")
    search_fields = ("name", "short_name", "country", "city", "contact_person")

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def has_delete_permission(self, request, obj=None):
        return bool(obj and not obj.events.exists() and super().has_delete_permission(request, obj))


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_person", "email")

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def has_delete_permission(self, request, obj=None):
        return bool(obj and not obj.events.exists() and super().has_delete_permission(request, obj))
