import pytest
from django.core.management import call_command
from django.utils import translation

from apps.events.models import EventType
from apps.venues.models import Venue


@pytest.mark.django_db
def test_master_data_seed_is_idempotent_and_localized():
    call_command("seed_master_data")
    call_command("seed_master_data")

    assert Venue.objects.count() == 4
    assert EventType.objects.count() == 10
    venue = Venue.objects.get(code="ICH")
    with translation.override("ru"):
        assert venue.localized_name == "Международный конференц-зал"
    with translation.override("uz"):
        assert venue.localized_name == "Xalqaro konferensiyalar zali"
