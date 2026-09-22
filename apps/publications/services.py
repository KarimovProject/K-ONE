from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.audit.services import log_audit_event
from apps.publications.adapters import (
    InstagramAdapter,
    PublicationAdapterError,
    PublicationPermanentError,
    TelegramChannelAdapter,
)
from apps.publications.banner import save_banner
from apps.publications.models import Publication
from apps.publications.policies import ensure_event_publishable
from apps.publications.rendering import render_caption


def prepare_publication(publication: Publication, actor, regenerate_banner: bool = True):
    ensure_event_publishable(publication.event)
    publication.rendered_caption = render_caption(publication)
    publication.status = Publication.Status.READY
    publication.save(update_fields=("rendered_caption", "status", "updated_at"))
    if regenerate_banner:
        save_banner(publication)
        log_audit_event("banner.generated", actor=actor, target=publication)
    log_audit_event("publication.updated", actor=actor, target=publication)
    return publication


def approve_publication(publication: Publication, actor):
    if publication.status != Publication.Status.READY:
        raise ValidationError("Only ready publications can be approved.")
    ensure_event_publishable(publication.event)
    publication.status = Publication.Status.APPROVED
    publication.approved_by = actor
    publication.save(update_fields=("status", "approved_by", "updated_at"))
    log_audit_event("publication.approved", actor=actor, target=publication)
    return publication


def schedule_publication(publication: Publication, actor, scheduled_for):
    if (
        publication.status != Publication.Status.APPROVED
        or not scheduled_for
        or scheduled_for <= timezone.now()
    ):
        raise ValidationError("An approved publication requires a future schedule time.")
    publication.status = Publication.Status.SCHEDULED
    publication.scheduled_for = scheduled_for
    publication.save(update_fields=("status", "scheduled_for", "updated_at"))
    log_audit_event("publication.scheduled", actor=actor, target=publication)
    return publication


def cancel_publication(publication: Publication, actor):
    if publication.status in (Publication.Status.PUBLISHED, Publication.Status.PUBLISHING):
        raise ValidationError("Published or publishing posts cannot be cancelled.")
    publication.status = Publication.Status.CANCELLED
    publication.save(update_fields=("status", "updated_at"))
    log_audit_event("publication.cancelled", actor=actor, target=publication)


def mark_publication_failed(publication: Publication, error) -> Publication:
    publication.status = Publication.Status.FAILED
    publication.retry_count += 1
    publication.error_code = getattr(error, "code", "publication_error")
    publication.error_message = str(error)[:255]
    publication.save(
        update_fields=(
            "status",
            "retry_count",
            "error_code",
            "error_message",
            "updated_at",
        )
    )
    log_audit_event("publication.failed", target=publication)
    return publication


def _banner_url(publication: Publication) -> str:
    if not publication.banner:
        raise ValidationError("Generate a banner before publishing.")
    if not settings.IEMS_BASE_URL:
        raise ValidationError("IEMS_BASE_URL is required for platform image access.")
    return f"{settings.IEMS_BASE_URL.rstrip('/')}{publication.banner.url}"


def publish_publication(publication_id, adapter=None):
    with transaction.atomic():
        publication = (
            Publication.objects.select_for_update()
            .select_related("event")
            .get(pk=publication_id)
        )
        if publication.status == Publication.Status.PUBLISHED:
            return publication
        if publication.status not in (
            Publication.Status.APPROVED,
            Publication.Status.SCHEDULED,
            Publication.Status.FAILED,
        ):
            raise ValidationError("Publication is not approved for publishing.")
        ensure_event_publishable(publication.event)
        publication.status = Publication.Status.PUBLISHING
        publication.error_code = ""
        publication.error_message = ""
        publication.save(update_fields=("status", "error_code", "error_message", "updated_at"))

    # Deliberately committed and released outside the lock above, before the
    # external network call: a crash here leaves the publication stuck in
    # PUBLISHING (needs manual/periodic recovery) instead of rolling back to
    # a retryable status that would cause a duplicate live post on retry.
    try:
        adapter = adapter or (
            TelegramChannelAdapter()
            if publication.platform == Publication.Platform.TELEGRAM_CHANNEL
            else InstagramAdapter()
        )
        result = adapter.publish(_banner_url(publication), publication.rendered_caption)
    except PublicationAdapterError:
        raise
    except Exception as exc:
        # Anything other than the adapter's own error type (e.g. a missing
        # banner/IEMS_BASE_URL from _banner_url) used to leave the
        # publication perpetually retryable with no failure recorded.
        # Wrapping it lets publish_publication_task's existing
        # PublicationAdapterError handling mark it FAILED uniformly.
        raise PublicationPermanentError(str(exc)) from exc

    publication.status = Publication.Status.PUBLISHED
    publication.published_at = timezone.now()
    publication.external_post_id = result.post_id
    publication.external_container_id = result.container_id
    publication.external_url = result.external_url
    publication.save(
        update_fields=(
            "status",
            "published_at",
            "external_post_id",
            "external_container_id",
            "external_url",
            "updated_at",
        )
    )
    log_audit_event("publication.published", target=publication)
    return publication
