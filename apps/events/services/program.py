import os
from datetime import time
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _

from apps.audit.models import AuditEventLog
from apps.events.models import Event, EventProgramItem, Speaker, generate_public_token

User = get_user_model()

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


def log_audit_event(action: str, actor: Any, target: Any, payload: dict | None = None):
    AuditEventLog.objects.create(
        actor=actor if (actor and actor.is_authenticated) else None,
        action=action,
        target_id=str(getattr(target, "pk", "")),
        target_repr=str(target)[:255],
        payload=payload or {},
    )


def update_program_source(event: Event, actor: User, source: str) -> Event:
    """Switch program mode between 'pdf' and 'manual'."""
    if source not in (Event.ProgramSource.PDF, Event.ProgramSource.MANUAL):
        raise ValidationError(_("Invalid program source mode."))

    old_source = event.program_source
    if old_source != source:
        event.program_source = source
        event.updated_by = actor
        event.save(update_fields=["program_source", "updated_by", "updated_at"])
        log_audit_event(
            "event.program_source_changed",
            actor=actor,
            target=event,
            payload={"old_source": old_source, "new_source": source},
        )
    return event


def validate_pdf_file(pdf_file) -> None:
    """Validate PDF file size, extension, and header bytes."""
    if not pdf_file:
        raise ValidationError(_("No file was uploaded."))

    if pdf_file.size > MAX_PDF_SIZE:
        raise ValidationError(_("File size exceeds maximum allowed limit of 10 MB."))

    ext = os.path.splitext(pdf_file.name)[1].lower()
    if ext != ".pdf":
        raise ValidationError(_("Only PDF files (.pdf) are allowed."))

    # Check magic header bytes (%PDF-)
    pdf_file.seek(0)
    header = pdf_file.read(5)
    pdf_file.seek(0)
    if header != b"%PDF-":
        raise ValidationError(_("Uploaded file is not a valid PDF document."))


def upload_program_pdf(event: Event, actor: User, pdf_file) -> Event:
    """Upload or replace program PDF for an event."""
    validate_pdf_file(pdf_file)

    is_replacement = bool(event.program_pdf)

    # Clean up old file if present
    if event.program_pdf and default_storage.exists(event.program_pdf.name):
        try:
            default_storage.delete(event.program_pdf.name)
        except Exception:
            pass

    event.program_pdf = pdf_file
    event.program_source = Event.ProgramSource.PDF
    event.updated_by = actor
    event.save(update_fields=["program_pdf", "program_source", "updated_by", "updated_at"])

    action = "event.program_pdf_replaced" if is_replacement else "event.program_pdf_uploaded"
    log_audit_event(
        action,
        actor=actor,
        target=event,
        payload={"filename": os.path.basename(pdf_file.name), "size": pdf_file.size},
    )
    return event


def remove_program_pdf(event: Event, actor: User) -> Event:
    """Remove program PDF from event."""
    if event.program_pdf:
        filename = event.program_pdf.name
        if default_storage.exists(filename):
            try:
                default_storage.delete(filename)
            except Exception:
                pass
        event.program_pdf = None
        event.updated_by = actor
        event.save(update_fields=["program_pdf", "updated_by", "updated_at"])
        log_audit_event(
            "event.program_pdf_removed",
            actor=actor,
            target=event,
            payload={"removed_filename": os.path.basename(filename)},
        )
    return event


def add_program_item(
    event: Event,
    actor: User,
    title: str,
    start_time: time,
    end_time: time,
    description: str = "",
    speaker: Speaker | None = None,
    speaker_name_override: str = "",
    sort_order: int = 0,
) -> EventProgramItem:
    """Add a structured agenda entry to the event program."""
    clean_title = (title or "").strip()
    if not clean_title:
        raise ValidationError(_("Program item title cannot be empty."))

    item = EventProgramItem.objects.create(
        event=event,
        title=clean_title,
        start_time=start_time,
        end_time=end_time,
        description=(description or "").strip(),
        speaker=speaker,
        speaker_name_override=(speaker_name_override or "").strip(),
        sort_order=sort_order,
    )
    log_audit_event(
        "event.program_item_added",
        actor=actor,
        target=event,
        payload={"item_id": item.pk, "title": clean_title},
    )
    return item


def update_program_item(
    item: EventProgramItem,
    actor: User,
    title: str | None = None,
    start_time: time | None = None,
    end_time: time | None = None,
    description: str | None = None,
    speaker: Speaker | None = None,
    speaker_name_override: str | None = None,
    sort_order: int | None = None,
) -> EventProgramItem:
    """Update an existing program agenda item."""
    update_fields = []
    if title is not None:
        item.title = title.strip()
        update_fields.append("title")
    if start_time is not None:
        item.start_time = start_time
        update_fields.append("start_time")
    if end_time is not None:
        item.end_time = end_time
        update_fields.append("end_time")
    if description is not None:
        item.description = description.strip()
        update_fields.append("description")
    if speaker is not None:
        item.speaker = speaker
        update_fields.append("speaker")
    if speaker_name_override is not None:
        item.speaker_name_override = speaker_name_override.strip()
        update_fields.append("speaker_name_override")
    if sort_order is not None:
        item.sort_order = sort_order
        update_fields.append("sort_order")

    if update_fields:
        update_fields.append("updated_at")
        item.save(update_fields=update_fields)

    log_audit_event(
        "event.program_item_updated",
        actor=actor,
        target=item.event,
        payload={"item_id": item.pk, "title": item.title},
    )
    return item


def remove_program_item(item: EventProgramItem, actor: User) -> None:
    """Remove a program agenda item."""
    event = item.event
    item_id = item.pk
    title = item.title
    item.delete()
    log_audit_event(
        "event.program_item_removed",
        actor=actor,
        target=event,
        payload={"item_id": item_id, "title": title},
    )


def rotate_public_token(event: Event, actor: User) -> Event:
    """Regenerate event public token for security/rotation."""
    old_token = event.public_token
    new_token = generate_public_token()
    event.public_token = new_token
    event.updated_by = actor
    event.save(update_fields=["public_token", "updated_by", "updated_at"])
    log_audit_event(
        "event.public_token_rotated",
        actor=actor,
        target=event,
        payload={"old_token": old_token[:8] + "...", "new_token": new_token[:8] + "..."},
    )
    return event


def set_public_enabled(event: Event, actor: User, is_enabled: bool) -> Event:
    """Enable or disable public page visibility for event."""
    if event.is_public_enabled != is_enabled:
        event.is_public_enabled = is_enabled
        event.updated_by = actor
        event.save(update_fields=["is_public_enabled", "updated_by", "updated_at"])
        log_audit_event(
            "event.public_page_enabled",
            actor=actor,
            target=event,
            payload={"is_public_enabled": is_enabled},
        )
    return event
