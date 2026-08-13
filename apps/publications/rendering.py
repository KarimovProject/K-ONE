from django.conf import settings
from django.urls import reverse

from apps.publications.models import Publication


def public_event_url(publication: Publication) -> str:
    path = reverse("public-event-page", kwargs={"public_token": publication.event.public_token})
    return f"{settings.IEMS_BASE_URL.rstrip('/')}{path}" if settings.IEMS_BASE_URL else path


def render_caption(publication: Publication) -> str:
    event = publication.event
    base = [
        publication.caption.strip() or publication.short_description.strip(),
        "",
        f"📅 {event.planned_date:%d.%m.%Y}, {event.weekday_name_for(publication.language)}",
        f"🕒 {event.start_time:%H:%M}–{event.end_time:%H:%M}",
        f"📍 {getattr(event.venue, f'name_{publication.language}', event.venue.name_uz)}",
    ]
    if publication.platform == Publication.Platform.TELEGRAM_CHANNEL:
        if event.zoom_url:
            base.append(f"Zoom: {event.zoom_url}")
        if event.registration_url:
            base.append(f"Registration: {event.registration_url}")
        base.append(f"Program: {public_event_url(publication)}")
    else:
        labels = {
            "uz": "Dastur va havolalar uchun bannerdagi QR kodni skanerlang.",
            "ru": "Сканируйте QR-код на баннере для программы и ссылок.",
            "en": "Scan the QR code on the banner for the program and links.",
        }
        base.append(labels.get(publication.language, labels["uz"]))
    return "\n".join(part for part in base if part is not None).strip()
