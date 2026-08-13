from django.contrib import admin

from apps.organizations.models import Organization, Sponsor


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "organization_type", "country", "is_active")
    list_filter = ("organization_type", "is_active", "country")
    search_fields = ("name", "short_name", "country", "city", "contact_person")


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_person", "email")
