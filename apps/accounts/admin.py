from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import User


@admin.register(User)
class IEMSUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("IEMS access", {"fields": ("role", "preferred_language")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("IEMS access", {"fields": ("role", "preferred_language")}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = UserAdmin.list_filter + ("role", "preferred_language")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)


admin.site.site_header = "IEMS Boshqaruv markazi"
admin.site.site_title = "IEMS Admin"
admin.site.index_title = "Tizim boshqaruvi"
