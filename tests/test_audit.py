import pytest
from django.contrib.auth import get_user_model

from apps.audit.models import AuditEventLog
from apps.audit.services import log_audit_event


@pytest.mark.django_db
def test_log_audit_event():
    user = get_user_model().objects.create_user(username="auditor", password="password")

    entry = log_audit_event(
        action=AuditEventLog.Action.EVENT_CREATED,
        actor=user,
        target=user,
        payload={"note": "test"},
    )

    assert entry.action == "event.created"
    assert entry.actor == user
    assert entry.target_id == str(user.pk)
    assert entry.payload == {"note": "test"}
    assert "auditor" in str(entry)
