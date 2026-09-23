import html

from django.urls import reverse

from apps.events.models import Event

LABELS = {
    "uz": {"heading": "🔔 Eslatma", "event": "Tadbir", "starts": "Boshlanishiga"},
    "ru": {"heading": "🔔 Напоминание", "event": "Событие", "starts": "До начала"},
    "en": {"heading": "🔔 Reminder", "event": "Event", "starts": "Starts in"},
}
OFFSETS = {
    "reminder_7d": {"uz": "7 kun qoldi", "ru": "7 дней", "en": "7 days"},
    "reminder_3d": {"uz": "3 kun qoldi", "ru": "3 дня", "en": "3 days"},
    "reminder_1d": {"uz": "1 kun qoldi", "ru": "1 день", "en": "1 day"},
    "reminder_3h": {"uz": "3 soat qoldi", "ru": "3 часа", "en": "3 hours"},
    "reminder_30m": {"uz": "30 daqiqa qoldi", "ru": "30 минут", "en": "30 minutes"},
}
EVENT_ACTIONS = {
    "assigned_responsible": {
        "uz": "Siz mas'ul etib tayinlandingiz",
        "ru": "Вы назначены ответственным",
        "en": "You've been assigned as responsible",
    },
}


def normalize_language(language: str) -> str:
    return language if language in LABELS else "uz"


def _event_lines(event: Event, language: str, base_url: str = "") -> list[str]:
    weekday = event.weekday_name_for(language)
    organizers = ", ".join(event.organizing_organizations.values_list("name", flat=True)) or "—"
    responsible_name = (
        event.responsible_employee.get_full_name() or event.responsible_employee.username
    )
    lines = [
        f"📌 <b>{html.escape(event.title)}</b>",
        f"📅 {event.planned_date:%d.%m.%Y}, {weekday}",
        f"🕒 {event.start_time:%H:%M}–{event.end_time:%H:%M}",
        f"📍 {html.escape(event.venue.localized_name)}",
        f"👤 {html.escape(responsible_name)}",
        f"🏢 {html.escape(organizers)}",
    ]
    if event.zoom_url:
        lines.append(f"Zoom: {html.escape(event.zoom_url)}")
    if event.registration_url:
        lines.append(f"Registration: {html.escape(event.registration_url)}")
    if base_url:
        route = (
            reverse("public-event-page", kwargs={"public_token": event.public_token})
            if event.is_publicly_accessible
            else reverse("events:detail", kwargs={"pk": event.pk})
        )
        lines.append(f"🔗 {base_url.rstrip('/')}{route}")
    return lines


def format_reminder(event: Event, reminder_type: str, language: str, base_url: str = "") -> str:
    language = normalize_language(language)
    labels = LABELS[language]
    offset = OFFSETS[reminder_type][language]
    return "\n".join(
        [
            labels["heading"],
            "",
            *_event_lines(event, language, base_url),
            "",
            f"{labels['starts']} {offset}.",
        ]
    )


def format_event_notification(event: Event, action: str, language: str, base_url: str = "") -> str:
    language = normalize_language(language)
    heading = EVENT_ACTIONS[action][language]
    return "\n".join([f"<b>{heading}</b>", "", *_event_lines(event, language, base_url)])
