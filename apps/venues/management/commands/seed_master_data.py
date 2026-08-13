from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.events.models import EventType
from apps.venues.models import Venue

VENUES = (
    {
        "code": "ICH",
        "name_uz": "Xalqaro konferensiyalar zali",
        "name_ru": "Международный конференц-зал",
        "name_en": "International Conference Hall",
        "capacity": 300,
        "sort_order": 10,
    },
    {
        "code": "SSH",
        "name_uz": "Ilmiy seminarlar zali",
        "name_ru": "Зал научных семинаров",
        "name_en": "Scientific Seminar Hall",
        "capacity": 120,
        "sort_order": 20,
    },
    {
        "code": "INR",
        "name_uz": "Xalqaro muzokaralar xonasi",
        "name_ru": "Комната международных переговоров",
        "name_en": "International Negotiation Room",
        "capacity": 40,
        "sort_order": 30,
    },
    {
        "code": "EMR",
        "name_uz": "Rahbariyat majlislar xonasi",
        "name_ru": "Зал заседаний руководства",
        "name_en": "Executive Meeting Room",
        "capacity": 24,
        "sort_order": 40,
    },
)

EVENT_TYPES = (
    ("conference", "Konferensiya", "Конференция", "Conference", "#2563EB", False, False),
    ("symposium", "Simpozium", "Симпозиум", "Symposium", "#8B5CF6", True, False),
    ("seminar", "Seminar", "Семинар", "Seminar", "#06B6D4", False, False),
    ("round_table", "Davra suhbati", "Круглый стол", "Round Table", "#0D9488", False, False),
    (
        "delegation_visit",
        "Xorijiy delegatsiya tashrifi",
        "Визит иностранной делегации",
        "Foreign Delegation Visit",
        "#10B981",
        True,
        False,
    ),
    (
        "guest_meeting",
        "Xorijiy mehmonlar bilan uchrashuv",
        "Встреча с иностранными гостями",
        "Foreign Guest Meeting",
        "#14B8A6",
        False,
        False,
    ),
    ("negotiation", "Muzokara", "Переговоры", "Negotiation", "#F59E0B", True, False),
    (
        "working_meeting",
        "Ishchi uchrashuv",
        "Рабочая встреча",
        "Working Meeting",
        "#64748B",
        False,
        False,
    ),
    (
        "management_meeting",
        "Rahbariyat uchrashuvi",
        "Встреча руководства",
        "Management Meeting",
        "#7C3AED",
        True,
        False,
    ),
    (
        "emergency",
        "Favqulodda tadbir",
        "Экстренное мероприятие",
        "Emergency Event",
        "#F97360",
        True,
        True,
    ),
)


class Command(BaseCommand):
    help = "Idempotently seed Phase 1 venues and event types."

    @transaction.atomic
    def handle(self, *args, **options):
        venue_count = 0
        for values in VENUES:
            defaults = {
                **values,
                "working_start": time(8, 0),
                "working_end": time(20, 0),
                "is_active": True,
                "display_enabled": True,
            }
            code = defaults.pop("code")
            Venue.objects.update_or_create(code=code, defaults=defaults)
            venue_count += 1

        event_type_count = 0
        for sort_order, values in enumerate(EVENT_TYPES, start=1):
            code, name_uz, name_ru, name_en, color, approval, emergency = values
            EventType.objects.update_or_create(
                code=code,
                defaults={
                    "name_uz": name_uz,
                    "name_ru": name_ru,
                    "name_en": name_en,
                    "color": color,
                    "icon": code.replace("_", "-"),
                    "is_active": True,
                    "requires_management_approval": approval,
                    "allows_emergency_override": emergency,
                    "sort_order": sort_order * 10,
                },
            )
            event_type_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Master data ready: {venue_count} venues, {event_type_count} event types."
            )
        )
