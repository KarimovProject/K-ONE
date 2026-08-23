import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.test import Client

c = Client()
res = c.get("/accounts/login/")
print(f"Login GET: {res.status_code}")

c.login(username="acceptance_admin", password="K-ONE-admin-2026!")
routes = [
    "/workspace/",
    "/events/",
    "/dashboard/calendar/",
    "/venues/",
    "/master-data/event-types/",
    "/master-data/organizations/",
    "/master-data/sponsors/",
    "/master-data/speakers/",
    "/publications/",
    "/leadership/",
    "/reporting/"
]

for r in routes:
    r_res = c.get(r)
    print(f"GET {r}: {r_res.status_code}")
