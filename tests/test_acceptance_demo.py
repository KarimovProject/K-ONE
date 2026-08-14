import secrets

import pytest
from django.core.management import call_command

from apps.accounts.models import User
from apps.events.models import Event, EventType
from apps.organizations.models import Organization, Sponsor
from apps.venues.models import Venue


@pytest.mark.django_db
def test_acceptance_demo_is_idempotent_and_cleanup_is_scoped(monkeypatch):
    password = f"Acceptance-{secrets.token_urlsafe(24)}!"
    monkeypatch.setenv("IEMS_ACCEPTANCE_PASSWORD", password)
    real_venue = Venue.objects.create(
        code="REAL",
        name_uz="Real",
        name_ru="Real",
        name_en="Real",
        capacity=10,
        working_start="08:00",
        working_end="18:00",
    )

    call_command("prepare_acceptance_demo", with_events=True)
    call_command("prepare_acceptance_demo", with_events=True)

    assert User.objects.filter(username__startswith="acceptance_").count() == 8
    assert Venue.objects.filter(code__startswith="ACCD").count() == 4
    assert EventType.objects.filter(code="acceptance_demo").count() == 1
    assert Organization.objects.filter(name__startswith="[ACCEPTANCE_DEMO]").count() == 1
    assert Sponsor.objects.filter(name__startswith="[ACCEPTANCE_DEMO]").count() == 1
    assert Event.objects.filter(title__startswith="[ACCEPTANCE_DEMO]").count() == 3
    assert User.objects.get(username="acceptance_super_admin").check_password(password)
    acceptance_admin = User.objects.get(username="acceptance_admin")
    assert acceptance_admin.role == User.Role.SUPER_ADMIN
    assert acceptance_admin.is_active
    assert acceptance_admin.is_staff
    assert acceptance_admin.is_superuser
    assert acceptance_admin.check_password(password)

    call_command("cleanup_acceptance_demo")

    assert User.objects.filter(username__startswith="acceptance_").count() == 0
    assert Venue.objects.filter(code__startswith="ACCD").count() == 0
    assert EventType.objects.filter(code="acceptance_demo").count() == 0
    assert Event.objects.filter(title__startswith="[ACCEPTANCE_DEMO]").count() == 0
    assert Venue.objects.filter(pk=real_venue.pk).exists()


@pytest.mark.django_db
def test_acceptance_demo_does_not_echo_password(monkeypatch, capsys):
    password = f"Acceptance-{secrets.token_urlsafe(24)}!"
    monkeypatch.setenv("IEMS_ACCEPTANCE_PASSWORD", password)
    call_command("prepare_acceptance_demo")
    assert password not in capsys.readouterr().out
