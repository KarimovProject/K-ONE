from celery import shared_task
from django.utils import timezone

from apps.publications.adapters import PublicationAdapterError
from apps.publications.models import Publication
from apps.publications.services import mark_publication_failed, publish_publication


@shared_task(name="apps.publications.tasks.dispatch_scheduled_publications")
def dispatch_scheduled_publications() -> int:
    ids = list(
        Publication.objects.filter(
            status=Publication.Status.SCHEDULED, scheduled_for__lte=timezone.now()
        ).values_list("pk", flat=True)
    )
    for publication_id in ids:
        publish_publication_task.delay(str(publication_id))
    return len(ids)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def publish_publication_task(self, publication_id: str) -> str:
    try:
        publication = publish_publication(publication_id)
        return publication.status
    except PublicationAdapterError as exc:
        publication = Publication.objects.get(pk=publication_id)
        mark_publication_failed(publication, exc)
        if exc.transient and publication.retry_count < 3:
            raise self.retry(exc=exc) from exc
        return publication.status
