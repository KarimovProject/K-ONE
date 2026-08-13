from typing import Any

from apps.audit.models import AuditEventLog


def log_audit_event(
    action: str,
    actor=None,
    target=None,
    payload: dict[str, Any] | None = None,
) -> AuditEventLog:
    target_id = ""
    target_repr = ""
    if target is not None:
        target_id = str(getattr(target, "pk", getattr(target, "id", "")))
        target_repr = str(target)[:255]

    return AuditEventLog.objects.create(
        actor=actor if actor and getattr(actor, "is_authenticated", False) else None,
        action=action,
        target_id=target_id,
        target_repr=target_repr,
        payload=payload or {},
    )
