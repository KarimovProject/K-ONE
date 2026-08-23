import os
import sys
import django

sys.path.insert(0, r"C:\IEMS")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
U = get_user_model()
u, _ = U.objects.get_or_create(username="acceptance_admin")
u.set_password("K-ONE-admin-2026!")
u.is_active = True
if hasattr(u, "is_staff"):
    u.is_staff = True
if hasattr(u, "is_superuser"):
    u.is_superuser = True
u.save()
print("User updated!")
