from django.core.management.base import BaseCommand

from apps.notifications.telegram.tasks import dispatch_due_reminders
from apps.publications.tasks import dispatch_scheduled_publications


class Command(BaseCommand):
    help = (
        "Run the periodic jobs that Celery Beat normally schedules (Telegram reminders, "
        "scheduled publications). Intended for hosts without Redis/Celery, e.g. a cron entry."
    )

    def handle(self, *args, **options):
        reminders = dispatch_due_reminders()
        publications = dispatch_scheduled_publications()
        self.stdout.write(f"reminders={reminders} publications={publications}")
