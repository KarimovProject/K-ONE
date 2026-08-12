from collections.abc import Callable

from django.http import HttpRequest, JsonResponse

from config.health_checks import HealthResult, check_application, check_database, check_redis


def _health_response(check: Callable[[], HealthResult]) -> JsonResponse:
    result = check()
    return JsonResponse(result.as_dict(), status=200 if result.is_healthy else 503)


def application_health(request: HttpRequest) -> JsonResponse:
    return _health_response(check_application)


def database_health(request: HttpRequest) -> JsonResponse:
    return _health_response(check_database)


def redis_health(request: HttpRequest) -> JsonResponse:
    return _health_response(check_redis)

