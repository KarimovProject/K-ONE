import pytest
from django.core.management import call_command

from apps.events.models import EventType
from apps.venues.models import Venue


@pytest.mark.django_db
def test_seed_master_data_command_is_idempotent():
    call_command("seed_master_data")
    assert Venue.objects.count() == 4
    assert EventType.objects.count() == 10

    # Verify initial venue codes
    codes = set(Venue.objects.values_list("code", flat=True))
    assert codes == {"ICH", "SSH", "INR", "EMR"}

    # Run a second time to verify idempotency
    call_command("seed_master_data")
    assert Venue.objects.count() == 4
    assert EventType.objects.count() == 10
