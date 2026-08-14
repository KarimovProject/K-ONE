import getpass
import os
from datetime import time, timedelta

from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.events.models import Event, EventType
from apps.organizations.models import Organization, Sponsor
from apps.venues.models import Venue

DEMO_TAG = "[ACCEPTANCE_DEMO]"
DEMO_PASSWORD_ENV = "IEMS_ACCEPTANCE_PASSWORD"

DEMO_USERS = (
    ("acceptance_super_admin", User.Role.SUPER_ADMIN, "Super Admin"),
    ("acceptance_international_admin", User.Role.INTERNATIONAL_ADMIN, "International Admin"),
    ("acceptance_responsible", User.Role.RESPONSIBLE_EMPLOYEE, "Responsible Employee"),
    ("acceptance_management", User.Role.MANAGEMENT_RESPONSIBLE, "Management Responsible"),
    ("acceptance_leadership", User.Role.LEADERSHIP_VIEWER, "Leadership Viewer"),
    ("acceptance_content", User.Role.CONTENT_MANAGER, "Content Manager"),
    ("acceptance_reception", User.Role.RECEPTION_OPERATOR, "Reception Operator"),
)

DEMO_VENUES = (
    ("ACCD1", "DEMO Konferensiya zali", "DEMO Конференц-зал", "DEMO Conference Hall", 120),
    ("ACCD2", "DEMO Seminar zali", "DEMO Зал семинаров", "DEMO Seminar Hall", 60),
    ("ACCD3", "DEMO Muzokara xonasi", "DEMO Переговорная", "DEMO Meeting Room", 24),
    ("ACCD4", "DEMO Kichik zal", "DEMO Малый зал", "DEMO Small Hall", 12),
)


def _acceptance_password() -> str:
    password = os.environ.get(DEMO_PASSWORD_ENV, "")
    if not password:
        if not os.isatty(0):
            raise CommandError(
                f"Set {DEMO_PASSWORD_ENV} for non-interactive use. The value is never stored."
            )
        password = getpass.getpass("Acceptance users password (input hidden): ")
        confirmation = getpass.getpass("Repeat password: ")
        if password != confirmation:
            raise CommandError("Passwords do not match.")
    validate_password(password)
    return password


class Command(BaseCommand):
    help = "Create or update a small, clearly tagged local human-acceptance dataset."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-events",
            action="store_true",
            help="Also create three clearly tagged DEMO events for dashboards and reports.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        password = _acceptance_password()

        users = {}
        for username, role, display_name in DEMO_USERS:
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.invalid",
                    "first_name": "TEST",
                    "last_name": display_name,
                    "role": role,
                    "preferred_language": User.Language.UZBEK,
                    "is_active": True,
                    "is_staff": role == User.Role.SUPER_ADMIN,
                    "is_superuser": role == User.Role.SUPER_ADMIN,
                },
            )
            user.set_password(password)
            user.save(update_fields=["password"])
            users[role] = user

        venues = []
        for sort_order, values in enumerate(DEMO_VENUES, start=1):
            code, name_uz, name_ru, name_en, capacity = values
            venue, _ = Venue.objects.update_or_create(
                code=code,
                defaults={
                    "name_uz": f"{DEMO_TAG} {name_uz}",
                    "name_ru": f"{DEMO_TAG} {name_ru}",
                    "name_en": f"{DEMO_TAG} {name_en}",
                    "description": f"{DEMO_TAG} Local acceptance only",
                    "location": "TEST floor",
                    "capacity": capacity,
                    "working_start": time(8, 0),
                    "working_end": time(20, 0),
                    "is_active": True,
                    "display_enabled": True,
                    "sort_order": 900 + sort_order,
                },
            )
            venues.append(venue)

        event_type, _ = EventType.objects.update_or_create(
            code="acceptance_demo",
            defaults={
                "name_uz": f"{DEMO_TAG} Sinov tadbiri",
                "name_ru": f"{DEMO_TAG} Тестовое мероприятие",
                "name_en": f"{DEMO_TAG} Test event",
                "description": f"{DEMO_TAG} Local acceptance only",
                "color": "#2563EB",
                "icon": "test",
                "is_active": True,
                "requires_management_approval": True,
                "allows_emergency_override": True,
                "sort_order": 900,
            },
        )
        organization, _ = Organization.objects.update_or_create(
            name=f"{DEMO_TAG} International Test Organization",
            defaults={
                "short_name": "DEMO ITO",
                "organization_type": Organization.Type.PARTNER,
                "country": "Test country",
                "city": "Tashkent",
                "notes": f"{DEMO_TAG} Local acceptance only",
                "is_active": True,
            },
        )
        sponsor, _ = Sponsor.objects.update_or_create(
            name=f"{DEMO_TAG} Test Sponsor",
            defaults={
                "description": "Local acceptance only",
                "notes": f"{DEMO_TAG} Local acceptance only",
                "is_active": True,
            },
        )

        event_count = 0
        if options["with_events"]:
            today = timezone.localdate()
            event_specs = (
                ("Draft event", Event.Status.DRAFT, 1, venues[0], time(9), time(10, 30)),
                ("Approved event", Event.Status.APPROVED, 2, venues[1], time(11), time(12)),
                ("Planned event", Event.Status.PLANNED, 4, venues[2], time(14), time(15)),
            )
            for label, status, day_offset, venue, start, end in event_specs:
                title = f"{DEMO_TAG} {label}"
                defaults = {
                    "event_type": event_type,
                    "description": f"{DEMO_TAG} Safe local acceptance event",
                    "venue": venue,
                    "planned_date": today + timedelta(days=day_offset),
                    "start_time": start,
                    "end_time": end,
                    "responsible_employee": users[User.Role.RESPONSIBLE_EMPLOYEE],
                    "management_responsible": users[User.Role.MANAGEMENT_RESPONSIBLE],
                    "status": status,
                    "expected_attendees": min(venue.capacity, 20),
                    "notes": f"{DEMO_TAG} May be removed by cleanup_acceptance_demo",
                    "created_by": users[User.Role.INTERNATIONAL_ADMIN],
                    "updated_by": users[User.Role.INTERNATIONAL_ADMIN],
                }
                event = Event.objects.filter(title=title).order_by("created_at").first()
                if event is None:
                    event = Event.objects.create(title=title, **defaults)
                else:
                    for field, value in defaults.items():
                        setattr(event, field, value)
                    event.save()
                event.organizing_organizations.set([organization])
                event.sponsors.set([sponsor])
                event_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Acceptance demo ready: "
                f"{len(DEMO_USERS)} users, {len(venues)} venues, 1 event type, "
                f"1 organization, 1 sponsor, {event_count} events."
            )
        )
        self.stdout.write("Usernames start with 'acceptance_'. The password was not stored.")
        if not options["with_events"]:
            self.stdout.write("Add --with-events only if dashboard/report sample data is needed.")
