from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.deletion import ProtectedError

from apps.accounts.models import User
from apps.events.models import Event, EventType
from apps.organizations.models import Organization, Sponsor
from apps.venues.models import Venue

from .prepare_acceptance_demo import DEMO_TAG


class Command(BaseCommand):
    help = "Delete only records carrying the IEMS local acceptance marker."

    @transaction.atomic
    def handle(self, *args, **options):
        counts = {}
        events = Event.objects.filter(title__startswith=DEMO_TAG)
        counts["events"] = events.count()
        events.delete()

        for label, queryset in (
            ("sponsors", Sponsor.objects.filter(name__startswith=DEMO_TAG)),
            ("organizations", Organization.objects.filter(name__startswith=DEMO_TAG)),
            ("event types", EventType.objects.filter(code="acceptance_demo")),
            ("venues", Venue.objects.filter(code__startswith="ACCD")),
            ("users", User.objects.filter(username__startswith="acceptance_")),
        ):
            count = queryset.count()
            try:
                with transaction.atomic():
                    queryset.delete()
            except ProtectedError:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped protected {label}: a non-DEMO record still references them."
                    )
                )
                count = 0
            counts[label] = count

        summary = ", ".join(f"{label}={count}" for label, count in counts.items())
        self.stdout.write(self.style.SUCCESS(f"Acceptance cleanup complete: {summary}."))
