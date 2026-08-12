from django.conf import settings
from django.core.cache import cache


def test_native_service_urls_do_not_use_docker_dns_names():
    assert "redis://redis:" not in settings.CELERY_BROKER_URL
    assert "redis://redis:" not in settings.CELERY_RESULT_BACKEND


def test_test_cache_is_isolated_from_native_redis():
    cache.set("phase-zero-native-baseline", "ok", timeout=10)

    assert cache.get("phase-zero-native-baseline") == "ok"
