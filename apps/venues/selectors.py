from django.db.models import QuerySet

from apps.venues.models import Venue


def active_venues() -> QuerySet[Venue]:
    return Venue.objects.filter(is_active=True)


def displayable_venues() -> QuerySet[Venue]:
    return active_venues().filter(display_enabled=True)


def get_venue_by_code(code: str) -> Venue | None:
    try:
        return Venue.objects.get(code__iexact=code.strip())
    except Venue.DoesNotExist:
        return None
