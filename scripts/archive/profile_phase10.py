import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
sys.path.insert(0, os.getcwd())

import django

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.db import connection  # noqa: E402
from django.test import Client  # noqa: E402
from django.test.utils import CaptureQueriesContext, setup_test_environment  # noqa: E402


def main():
    setup_test_environment()
    users = get_user_model()
    user, created = users.objects.get_or_create(
        username="p10_profile_admin",
        defaults={"role": users.Role.SUPER_ADMIN, "is_staff": True},
    )
    client = Client()
    client.force_login(user)
    routes = {
        "dashboard": "/",
        "calendar": "/calendar/",
        "leadership": "/leadership/",
        "tv_api": "/api/v1/leadership/venues/",
        "publication_list": "/publications/",
        "reports": "/reports/",
    }
    results = {}
    try:
        for name, route in routes.items():
            started = time.perf_counter()
            with CaptureQueriesContext(connection) as captured:
                response = client.get(route)
            results[name] = {
                "status": response.status_code,
                "queries": len(captured),
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                "payload_bytes": len(response.content),
            }
    finally:
        if created:
            user.delete()
    output = Path("test-results/phase10-profile.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    if any(value["status"] != 200 for value in results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
