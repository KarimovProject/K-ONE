from dataclasses import asdict, dataclass

import redis
from django.conf import settings
from django.db import connections
from django.db.utils import DatabaseError


@dataclass(frozen=True)
class HealthResult:
    service: str
    status: str
    detail: str

    @property
    def is_healthy(self) -> bool:
        return self.status == "ok"

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def check_application() -> HealthResult:
    return HealthResult("application", "ok", f"IEMS {settings.APP_VERSION}")


def check_database() -> HealthResult:
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return HealthResult("database", "error", "Database connection unavailable")
    return HealthResult("database", "ok", "Database connection available")


def check_redis() -> HealthResult:
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
    except redis.RedisError:
        return HealthResult("redis", "error", "Redis connection unavailable")
    return HealthResult("redis", "ok", "Redis connection available")
