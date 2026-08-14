import http.cookiejar
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import time as dt_time
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DB_CONN_MAX_AGE"] = "0"
sys.path.insert(0, os.getcwd())

import django

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.contrib.sessions.backends.db import SessionStore  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.attendance.models import EventAttendance  # noqa: E402
from apps.events.models import Event, EventType  # noqa: E402
from apps.notifications.telegram.tasks import dispatch_due_reminders  # noqa: E402
from apps.publications.models import Publication  # noqa: E402
from apps.publications.tasks import dispatch_scheduled_publications  # noqa: E402
from apps.venues.models import DisplayToken, Venue  # noqa: E402

PORT = 8564
BASE_URL = f"http://127.0.0.1:{PORT}"
PASSWORD = "Phase10-Load-Test!"
User = get_user_model()


def cleanup():
    Event.objects.filter(title__startswith="[P10 LOAD]").delete()
    DisplayToken.objects.filter(name="P10 load display").delete()
    EventType.objects.filter(code="p10-load").delete()
    Venue.objects.filter(code="P10-LOAD").delete()
    User.objects.filter(username__startswith="p10_load_").delete()


def prepare():
    cleanup()
    leader = User.objects.create_user(
        "p10_load_leader", password=PASSWORD, role=User.Role.LEADERSHIP_VIEWER
    )
    responsible = User.objects.create_user(
        "p10_load_responsible", password=PASSWORD, role=User.Role.RESPONSIBLE_EMPLOYEE
    )
    venue = Venue.objects.create(
        code="P10-LOAD",
        name_uz="Load Hall",
        name_ru="Load Hall",
        name_en="Load Hall",
        capacity=500,
        working_start=dt_time(8),
        working_end=dt_time(20),
    )
    event_type = EventType.objects.create(
        code="p10-load", name_uz="Load", name_ru="Load", name_en="Load"
    )
    event = Event.objects.create(
        title="[P10 LOAD] Public event",
        event_type=event_type,
        venue=venue,
        planned_date=timezone.localdate(),
        start_time=dt_time(0),
        end_time=dt_time(23, 59),
        responsible_employee=responsible,
        management_responsible=leader,
        created_by=responsible,
        status=Event.Status.APPROVED,
        expected_attendees=500,
        checkin_enabled=True,
        checkin_opens_at=timezone.now() - timedelta(hours=1),
        checkin_closes_at=timezone.now() + timedelta(hours=1),
    )
    now = timezone.localtime().replace(microsecond=0)
    for index in range(25):
        Event.objects.create(
            title=f"[P10 LOAD] Background {index}",
            event_type=event_type,
            venue=venue,
            planned_date=(now + timedelta(days=1)).date(),
            start_time=now.time(),
            end_time=(now + timedelta(hours=1)).time(),
            responsible_employee=responsible,
            management_responsible=leader,
            created_by=responsible,
            status=Event.Status.APPROVED,
            expected_attendees=10,
            reminder_7d=False,
            reminder_3d=False,
            reminder_1d=True,
            reminder_3h=False,
            reminder_30m=False,
        )
    for index in range(25):
        Publication.objects.create(
            event=event,
            platform=Publication.Platform.TELEGRAM_CHANNEL,
            language="uz",
            status=Publication.Status.SCHEDULED,
            headline=f"[P10 LOAD] Publication {index}",
            scheduled_for=timezone.now(),
            created_by=responsible,
        )
    display = DisplayToken.objects.create(name="P10 load display")
    session = SessionStore()
    session["_auth_user_id"] = str(leader.pk)
    session["_auth_user_backend"] = "django.contrib.auth.backends.ModelBackend"
    session["_auth_user_hash"] = leader.get_session_auth_hash()
    session.save()
    return event, display, session.session_key


def wait_for_server():
    for _ in range(50):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health/", timeout=2):
                return
        except Exception:
            time.sleep(0.2)
    raise RuntimeError("Django load-test server did not start")


def request(url, headers=None, data=None):
    started = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers=headers or {}, data=data)
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = response.read()
            return response.status, (time.perf_counter() - started) * 1000, len(payload)
    except Exception:
        return 0, (time.perf_counter() - started) * 1000, 0


def prepare_checkin(token, index):
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    page = opener.open(f"{BASE_URL}/event/{token}/", timeout=20).read().decode()
    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page)
    if not match:
        raise RuntimeError("CSRF token not found")
    data = urllib.parse.urlencode(
        {"csrfmiddlewaretoken": match.group(1), "attendee_name": f"Load Guest {index}"}
    ).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/event/{token}/checkin/",
        data=data,
        headers={"Referer": f"{BASE_URL}/event/{token}/"},
    )

    def submit(_):
        started = time.perf_counter()
        try:
            with opener.open(req, timeout=20) as response:
                payload = response.read()
                return response.status, (time.perf_counter() - started) * 1000, len(payload)
        except Exception:
            return 0, (time.perf_counter() - started) * 1000, 0

    return submit


def run_group(name, count, worker):
    with ThreadPoolExecutor(max_workers=count) as pool:
        futures = [pool.submit(worker, index) for index in range(count)]
        results = [future.result() for future in as_completed(futures)]
    latencies = sorted(item[1] for item in results)
    success = sum(item[0] == 200 for item in results)

    def percentile(value):
        return latencies[min(len(latencies) - 1, int(len(latencies) * value))]

    return {
        "scenario": name,
        "requests": count,
        "success": success,
        "error_rate": round((count - success) / count * 100, 2),
        "latency_ms": {
            "p50": round(statistics.median(latencies), 2),
            "p95": round(percentile(0.95), 2),
            "p99": round(percentile(0.99), 2),
        },
        "average_payload_bytes": round(sum(item[2] for item in results) / count),
    }


def main():
    event, display, session_key = prepare()
    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_server()
        results = [
            run_group(
                "100 public event users",
                100,
                lambda _: request(f"{BASE_URL}/event/{event.public_token}/"),
            )
        ]
        checkin_workers = [prepare_checkin(event.public_token, index) for index in range(100)]
        results.extend(
            [
                run_group("100 unique QR check-ins", 100, lambda i: checkin_workers[i](i)),
                run_group(
                    "50 display polling clients",
                    50,
                    lambda _: request(f"{BASE_URL}/api/v1/display/{display.token}/venues/"),
                ),
                run_group(
                    "25 report dashboard users",
                    25,
                    lambda _: request(
                        f"{BASE_URL}/reports/", {"Cookie": f"sessionid={session_key}"}
                    ),
                ),
            ]
        )
        double_click = prepare_checkin(event.public_token, 101)
        before_double_click = EventAttendance.objects.filter(event=event).count()
        with ThreadPoolExecutor(max_workers=2) as pool:
            double_results = list(pool.map(double_click, range(2)))
        after_double_click = EventAttendance.objects.filter(event=event).count()
        background_started = time.perf_counter()
        reminder_scheduled = dispatch_due_reminders()
        with patch("apps.publications.tasks.publish_publication_task.delay") as enqueue:
            publication_scheduled = dispatch_scheduled_publications()
        background_elapsed = round((time.perf_counter() - background_started) * 1000, 2)
        checked = EventAttendance.objects.filter(event=event).count()
        result = {
            "scenarios": results,
            "unique_checkins": checked,
            "expected_checkins": 101,
            "double_click_http_successes": sum(item[0] == 200 for item in double_results),
            "double_click_rows_created": after_double_click - before_double_click,
            "background_workload": {
                "reminder_deliveries_created": reminder_scheduled,
                "publications_enqueued": publication_scheduled,
                "publication_queue_calls": enqueue.call_count,
                "elapsed_ms": background_elapsed,
            },
        }
        output = Path("test-results/phase10-load.json")
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        if (
            any(item["error_rate"] for item in results)
            or checked != 101
            or after_double_click - before_double_click != 1
            or reminder_scheduled != 50
            or publication_scheduled != 25
            or enqueue.call_count != 25
        ):
            raise SystemExit(1)
    finally:
        server.terminate()
        server.wait(timeout=10)
        cleanup()


if __name__ == "__main__":
    main()
