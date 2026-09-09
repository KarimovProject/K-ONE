import os
import django
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.events.models import EventType, Event
from apps.venues.models import Venue
from apps.organizations.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()

print("Creating EventTypes...")
type_meeting, _ = EventType.objects.get_or_create(
    code="MEETING",
    defaults={
        "name_uz": "Uchrashuv",
        "name_ru": "Встреча",
        "name_en": "Meeting",
        "color": "#3b82f6",
        "is_active": True,
    }
)

type_conf, _ = EventType.objects.get_or_create(
    code="CONF",
    defaults={
        "name_uz": "Konferensiya",
        "name_ru": "Конференция",
        "name_en": "Conference",
        "color": "#10b981",
        "is_active": True,
    }
)

print("Creating Venues...")
venue_main, _ = Venue.objects.get_or_create(
    code="MAIN",
    defaults={
        "name_uz": "Katta Majlislar Zali",
        "name_ru": "Главный зал",
        "name_en": "Main Hall",
        "capacity": 200,
        "working_start": datetime.time(9, 0),
        "working_end": datetime.time(18, 0),
        "is_active": True,
    }
)

venue_small, _ = Venue.objects.get_or_create(
    code="ROOM1",
    defaults={
        "name_uz": "Xona 1",
        "name_ru": "Комната 1",
        "name_en": "Room 1",
        "capacity": 20,
        "working_start": datetime.time(9, 0),
        "working_end": datetime.time(18, 0),
        "is_active": True,
    }
)

print("Creating Organizations...")
org, _ = Organization.objects.get_or_create(
    name="K ONE Korporatsiyasi",
    defaults={
        "short_name": "KONE",
        "organization_type": Organization.Type.LOCAL,
        "is_active": True,
    }
)

print("Creating Events...")
# Create an event that is currently ongoing for testing QR code
now = timezone.now()
today = now.date()

user_admin = User.objects.filter(is_superuser=True).first()
if not user_admin:
    print("Warning: No superuser found to assign as created_by.")
    user_admin = User.objects.first()

event_ongoing, _ = Event.objects.get_or_create(
    title="Hozirgi muhim uchrashuv",
    defaults={
        "description": "Ushbu uchrashuv QR kod test qilish uchun hozirgi vaqtga to'g'irlangan.",
        "event_type": type_meeting,
        "venue": venue_small,
        "planned_date": today,
        "start_time": (now - datetime.timedelta(hours=1)).time(),
        "end_time": (now + datetime.timedelta(hours=2)).time(),
        "status": Event.Status.APPROVED,
        "created_by": user_admin,
        "responsible_employee": user_admin,
        "management_responsible": user_admin,
        "is_public_enabled": True,
        "checkin_enabled": True,
    }
)

event_future, _ = Event.objects.get_or_create(
    title="Ertangi Konferensiya",
    defaults={
        "description": "Bu ertangi konferensiya. QR orqali kelish sinab ko'riladi.",
        "event_type": type_conf,
        "venue": venue_main,
        "planned_date": today + datetime.timedelta(days=1),
        "start_time": datetime.time(10, 0),
        "end_time": datetime.time(12, 0),
        "status": Event.Status.APPROVED,
        "created_by": user_admin,
        "responsible_employee": user_admin,
        "management_responsible": user_admin,
        "is_public_enabled": True,
        "checkin_enabled": True,
    }
)

print("Data successfully created!")
