from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import DoctorProfile, StaffUnavailability, User


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    extra = 0


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

    def get_inlines(self, request, obj):
        if obj is not None and obj.role == User.Role.DOCTOR:
            return (DoctorProfileInline,)
        return ()


@admin.register(StaffUnavailability)
class StaffUnavailabilityAdmin(admin.ModelAdmin):
    list_display = ("user", "start_date", "start_time", "end_date", "end_time", "reason")
    list_filter = ("start_date", "end_date")
    search_fields = ("user__username", "user__first_name", "user__last_name", "reason")
    ordering = ("-start_date", "-start_time")


admin.site.site_header = "IEMS Boshqaruv markazi"
admin.site.site_title = "IEMS Admin"
admin.site.index_title = "Tizim boshqaruvi"
