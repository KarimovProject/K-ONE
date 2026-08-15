from django.contrib import admin

from apps.notifications.models import (
    Notification,
    TelegramConnection,
    TelegramDelivery,
    TelegramLinkToken,
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "title", "severity", "is_read", "created_at")
    list_filter = ("severity", "is_read")
    search_fields = ("recipient__username", "title", "message")
    readonly_fields = ("created_at",)


@admin.register(TelegramConnection)
class TelegramConnectionAdmin(admin.ModelAdmin):
    list_display = ("user", "telegram_username", "is_active", "connected_at")
    exclude = ("chat_id",)
    readonly_fields = ("telegram_user_id", "connected_at", "last_verified_at")


@admin.register(TelegramDelivery)
class TelegramDeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "recipient_user",
        "notification_type",
        "status",
        "scheduled_for",
    )
    list_filter = ("status", "notification_type")
    readonly_fields = tuple(field.name for field in TelegramDelivery._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TelegramLinkToken)
class TelegramLinkTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "expires_at", "used_at", "created_at")
    readonly_fields = ("token_hash", "created_at")
