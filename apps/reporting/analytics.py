from collections import Counter
from datetime import datetime, time, timedelta
from statistics import median

from django.db.models import Count, Q, Sum
from django.db.models.functions import ExtractHour, TruncDay, TruncMonth, TruncWeek
from django.utils import timezone
from django.utils.translation import get_language

from apps.attendance.models import EventAttendance
from apps.audit.models import AuditEventLog
from apps.events.models import Event
from apps.notifications.models import TelegramConnection, TelegramDelivery
from apps.organizations.models import Organization, Sponsor
from apps.publications.models import Publication
from apps.venues.models import Venue

BOOKED_STATUSES = (
    Event.Status.APPROVED,
    Event.Status.PLANNED,
    Event.Status.SCHEDULED,
    Event.Status.ONGOING,
    Event.Status.COMPLETED,
    Event.Status.EMERGENCY,
)


def _rate(value, total):
    return round(value / total * 100, 1) if total else None


def _duration(event):
    start = datetime.combine(event.planned_date, event.start_time)
    end = datetime.combine(event.planned_date, event.end_time)
    return max(0, int((end - start).total_seconds() / 60))


def previous_range(start, end):
    days = (end - start).days + 1
    return start - timedelta(days=days), start - timedelta(days=1)


def executive_summary(events, start, end, previous_events=None):
    event_ids = events.values_list("pk", flat=True)
    expected = events.aggregate(total=Sum("expected_attendees"))["total"] or 0
    checked = EventAttendance.objects.filter(event_id__in=event_ids).count()
    publications = Publication.objects.filter(event_id__in=event_ids)
    deliveries = TelegramDelivery.objects.filter(
        event_id__in=event_ids, notification_type__startswith="reminder_"
    )
    previous_total = previous_events.count() if previous_events is not None else 0
    return {
        "total_events": events.count(),
        "approved_events": events.filter(status=Event.Status.APPROVED).count(),
        "completed_events": events.filter(status=Event.Status.COMPLETED).count(),
        "cancelled_events": events.filter(status=Event.Status.CANCELLED).count(),
        "emergency_events": events.filter(priority=Event.Priority.EMERGENCY).count(),
        "expected_attendees": expected,
        "checked_in": checked,
        "attendance_rate": _rate(checked, expected),
        "publications_published": publications.filter(status=Publication.Status.PUBLISHED).count(),
        "publications_failed": publications.filter(status=Publication.Status.FAILED).count(),
        "reminder_success_rate": _rate(
            deliveries.filter(status=TelegramDelivery.Status.SENT).count(), deliveries.count()
        ),
        "previous_total": previous_total,
        "event_change": events.count() - previous_total,
    }


def event_analytics(events):
    daily = list(
        events.annotate(bucket=TruncDay("planned_date"))
        .values("bucket")
        .annotate(total=Count("id"))
        .order_by("bucket")
    )
    weekly = list(
        events.annotate(bucket=TruncWeek("planned_date"))
        .values("bucket")
        .annotate(total=Count("id"))
        .order_by("bucket")
    )
    monthly = list(
        events.annotate(bucket=TruncMonth("planned_date"))
        .values("bucket")
        .annotate(total=Count("id"))
        .order_by("bucket")
    )
    by_status = list(events.values("status").annotate(total=Count("id")).order_by("status"))
    status_labels = dict(Event.Status.choices)
    for row in by_status:
        row["label"] = str(status_labels.get(row["status"], row["status"]))
    language = (get_language() or "uz").split("-")[0]
    type_field = (
        f"event_type__name_{language}" if language in {"uz", "ru", "en"} else "event_type__name_uz"
    )
    by_type_values = list(
        events.values(type_field).annotate(total=Count("id")).order_by(type_field)
    )
    by_type = [{"label": row[type_field], "total": row["total"]} for row in by_type_values]
    by_priority = list(events.values("priority").annotate(total=Count("id")).order_by("priority"))
    priority_labels = dict(Event.Priority.choices)
    for row in by_priority:
        row["label"] = str(priority_labels.get(row["priority"], row["priority"]))
    by_venue = list(
        events.values("venue__code", "venue__name_en")
        .annotate(total=Count("id"))
        .order_by("venue__code")
    )
    by_organization = list(
        events.values("organizing_organizations__name")
        .annotate(total=Count("id", distinct=True))
        .order_by("organizing_organizations__name")
    )
    by_responsible = list(
        events.values("responsible_employee__username")
        .annotate(total=Count("id"))
        .order_by("responsible_employee__username")
    )
    by_hour = list(
        events.annotate(hour=ExtractHour("start_time"))
        .values("hour")
        .annotate(total=Count("id"))
        .order_by("hour")
    )
    weekdays = Counter(value.weekday() for value in events.values_list("planned_date", flat=True))
    return {
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
        "by_status": by_status,
        "by_type": by_type,
        "by_priority": by_priority,
        "by_venue": by_venue,
        "by_organization": by_organization,
        "by_responsible": by_responsible,
        "by_hour": by_hour,
        "by_weekday": [{"weekday": key, "total": weekdays.get(key, 0)} for key in range(7)],
    }


def venue_analytics(events, start, end):
    day_count = (end - start).days + 1
    rows = []
    booked = events.filter(status__in=BOOKED_STATUSES)
    for venue in Venue.objects.filter(is_active=True).order_by("sort_order", "code"):
        working = (
            max(
                0,
                int(
                    (
                        datetime.combine(start, venue.working_end)
                        - datetime.combine(start, venue.working_start)
                    ).total_seconds()
                    / 60
                ),
            )
            * day_count
        )
        venue_events = list(booked.filter(venue=venue))
        minutes = sum(_duration(event) for event in venue_events)
        by_day = Counter(event.planned_date for event in venue_events)
        by_period = Counter(
            "morning"
            if event.start_time < time(12)
            else "afternoon"
            if event.start_time < time(17)
            else "evening"
            for event in venue_events
        )
        rows.append(
            {
                "id": venue.pk,
                "code": venue.code,
                "name": venue.localized_name,
                "available_minutes": working,
                "booked_minutes": minutes,
                "utilization": _rate(minutes, working) or 0.0,
                "event_count": len(venue_events),
                "average_duration": round(minutes / len(venue_events), 1) if venue_events else 0,
                "busiest_day": str(by_day.most_common(1)[0][0]) if by_day else "",
                "peak_period": by_period.most_common(1)[0][0] if by_period else "",
            }
        )
    return rows


def attendance_analytics(events):
    ids = events.values_list("pk", flat=True)
    records = EventAttendance.objects.filter(event_id__in=ids)
    expected = events.aggregate(total=Sum("expected_attendees"))["total"] or 0
    checked = records.count()
    by_method = dict(records.values_list("checkin_method").annotate(total=Count("id")))
    highest = list(
        events.annotate(checked=Count("attendances"))
        .values("id", "title", "expected_attendees", "checked")
        .order_by("-checked")[:10]
    )
    return {
        "expected": expected,
        "checked": checked,
        "rate": _rate(checked, expected),
        "anonymous": records.filter(attendee_name="").count(),
        "identified": records.exclude(attendee_name="").count(),
        "public_qr": by_method.get(EventAttendance.Method.PUBLIC_QR, 0),
        "staff_manual": by_method.get(EventAttendance.Method.STAFF_MANUAL, 0),
        "highest": highest,
    }


def approval_analytics(events):
    ids = [str(pk) for pk in events.values_list("pk", flat=True)]
    logs = AuditEventLog.objects.filter(target_id__in=ids, action__startswith="event.")
    durations = []
    for submitted_at, reviewed_at in (
        events.exclude(submitted_at=None)
        .exclude(reviewed_at=None)
        .values_list("submitted_at", "reviewed_at")
    ):
        durations.append((reviewed_at - submitted_at).total_seconds() / 3600)
    now = timezone.now()
    buckets = {"under_4h": 0, "4_12h": 0, "12_24h": 0, "1_3d": 0, "over_3d": 0}
    for event in events.filter(status=Event.Status.PENDING_APPROVAL).exclude(submitted_at=None):
        age = (now - event.submitted_at).total_seconds() / 3600
        key = (
            "under_4h"
            if age < 4
            else "4_12h"
            if age < 12
            else "12_24h"
            if age < 24
            else "1_3d"
            if age < 72
            else "over_3d"
        )
        buckets[key] += 1
    return {
        "submitted": logs.filter(action="event.submitted").count(),
        "approved": logs.filter(action="event.approved").count(),
        "rejected": logs.filter(action="event.rejected").count(),
        "resubmitted": logs.filter(action="event.resubmitted").count(),
        "pending": events.filter(status=Event.Status.PENDING_APPROVAL).count(),
        "average_hours": round(sum(durations) / len(durations), 1) if durations else None,
        "median_hours": round(median(durations), 1) if durations else None,
        "buckets": buckets,
    }


def emergency_analytics(events):
    ids = [str(pk) for pk in events.values_list("pk", flat=True)]
    logs = AuditEventLog.objects.filter(target_id__in=ids)
    return {
        "emergency_events": events.filter(priority=Event.Priority.EMERGENCY).count(),
        "overrides": logs.filter(action="event.emergency_overridden").count(),
        "displaced": logs.filter(action="event.displaced").count(),
        "rescheduled_displaced": events.filter(
            displaced_by_event__isnull=False, status=Event.Status.PLANNED
        ).count(),
        "unresolved_displaced": events.filter(status=Event.Status.DISPLACED).count(),
    }


def organization_analytics(events):
    rows = list(
        Organization.objects.filter(events__in=events)
        .annotate(
            total_events=Count("events", distinct=True),
            upcoming=Count(
                "events",
                filter=Q(events__planned_date__gte=timezone.localdate()),
                distinct=True,
            ),
            completed=Count(
                "events", filter=Q(events__status=Event.Status.COMPLETED), distinct=True
            ),
            expected=Sum("events__expected_attendees"),
            checked=Count("events__attendances", distinct=True),
        )
        .values(
            "id",
            "name",
            "organization_type",
            "total_events",
            "upcoming",
            "completed",
            "expected",
            "checked",
        )
        .order_by("-total_events", "name")
    )
    type_labels = dict(Organization.Type.choices)
    for row in rows:
        row["organization_type_label"] = str(
            type_labels.get(row["organization_type"], row["organization_type"])
        )
    return rows


def sponsor_analytics(events):
    sponsors = list(
        Sponsor.objects.filter(events__in=events)
        .annotate(total_events=Count("events", distinct=True))
        .values("id", "name", "total_events")
        .order_by("-total_events", "name")
    )
    associations = events.values(
        "sponsors__id", "id", "title", "planned_date", "event_type__name_en"
    ).order_by("planned_date", "title")
    by_sponsor = {}
    for row in associations:
        sponsor_id = row.pop("sponsors__id")
        if sponsor_id:
            by_sponsor.setdefault(sponsor_id, []).append(row)
    for sponsor in sponsors:
        associated = by_sponsor.get(sponsor["id"], [])
        sponsor["event_types"] = sorted(
            {row["event_type__name_en"] for row in associated if row["event_type__name_en"]}
        )
        sponsor["associated_events"] = associated
        sponsor["date_start"] = associated[0]["planned_date"] if associated else None
        sponsor["date_end"] = associated[-1]["planned_date"] if associated else None
    return sponsors


def workload_analytics(events):
    today = timezone.localdate()
    return list(
        events.values("responsible_employee__id", "responsible_employee__username")
        .annotate(
            assigned=Count("id", distinct=True),
            upcoming=Count("id", filter=Q(planned_date__gte=today), distinct=True),
            completed=Count("id", filter=Q(status=Event.Status.COMPLETED), distinct=True),
            pending=Count("id", filter=Q(status=Event.Status.PENDING_APPROVAL), distinct=True),
            emergencies=Count("id", filter=Q(priority=Event.Priority.EMERGENCY), distinct=True),
            checkins=Count("attendances", distinct=True),
        )
        .order_by("responsible_employee__username")
    )


def publication_analytics(events, platform=""):
    publications = Publication.objects.filter(event__in=events)
    if platform:
        publications = publications.filter(platform=platform)
    status_counts = dict(publications.values_list("status").annotate(total=Count("id")))
    total = publications.count()
    published = status_counts.get(Publication.Status.PUBLISHED, 0)
    return {
        "total": total,
        "telegram": publications.filter(platform=Publication.Platform.TELEGRAM_CHANNEL).count(),
        "instagram": publications.filter(platform=Publication.Platform.INSTAGRAM).count(),
        "statuses": status_counts,
        "status_rows": [
            {"status": status, "label": str(label), "total": status_counts.get(status, 0)}
            for status, label in Publication.Status.choices
            if status_counts.get(status, 0)
        ],
        "retries": publications.aggregate(total=Sum("retry_count"))["total"] or 0,
        "success_rate": _rate(
            published, published + status_counts.get(Publication.Status.FAILED, 0)
        ),
    }


def telegram_analytics(events):
    deliveries = TelegramDelivery.objects.filter(
        event__in=events, notification_type__startswith="reminder_"
    )
    total = deliveries.count()
    sent = deliveries.filter(status=TelegramDelivery.Status.SENT).count()
    recipient_ids = list(events.order_by().values_list("responsible_employee_id", flat=True))
    recipient_ids.extend(events.order_by().values_list("management_responsible_id", flat=True))
    recipient_ids = list(set(recipient_ids))
    connected = TelegramConnection.objects.filter(user_id__in=recipient_ids, is_active=True).count()
    return {
        "scheduled": total,
        "sent": sent,
        "failed": deliveries.filter(status=TelegramDelivery.Status.FAILED).count(),
        "retried": deliveries.filter(retry_count__gt=0).count(),
        "success_rate": _rate(sent, total),
        "connected_recipients": connected,
        "unconnected_recipients": max(0, len(set(recipient_ids)) - connected),
    }


def build_report(events, start, end, filters, previous_events=None):
    venues = venue_analytics(events, start, end)
    available = sum(row["available_minutes"] for row in venues)
    booked = sum(row["booked_minutes"] for row in venues)
    summary = executive_summary(events, start, end, previous_events)
    summary["venue_utilization"] = _rate(booked, available)
    return {
        "start": start,
        "end": end,
        "summary": summary,
        "events": event_analytics(events),
        "venues": venues,
        "attendance": attendance_analytics(events),
        "approvals": approval_analytics(events),
        "emergency": emergency_analytics(events),
        "organizations": organization_analytics(events),
        "sponsors": sponsor_analytics(events),
        "workload": workload_analytics(events),
        "publications": publication_analytics(events, filters.get("publication_platform", "")),
        "telegram": telegram_analytics(events),
    }
