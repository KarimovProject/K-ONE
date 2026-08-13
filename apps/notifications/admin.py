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
    readonly_fields = ("message_text",)


@admin.register(TelegramLinkToken)
class TelegramLinkTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "expires_at", "used_at", "created_at")
    readonly_fields = ("token_hash", "created_at")
