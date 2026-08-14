import logging

from django.core.cache import cache

logger = logging.getLogger("iems.security")


def client_ip(request) -> str:
    """Use the direct peer address; trusted-proxy handling belongs at the edge."""
    return request.META.get("REMOTE_ADDR", "unknown")


def _key(request, scope: str, identity: str = "") -> str:
    return f"rate:{scope}:{client_ip(request)}:{identity}"[:240]


def clear_rate_limit(request, scope: str, identity: str = "") -> None:
    cache.delete(_key(request, scope, identity))


def is_rate_limited(request, scope: str, limit: int, window: int, identity: str = "") -> bool:
    key = _key(request, scope, identity)
    try:
        if cache.add(key, 1, timeout=window):
            return False
        return cache.incr(key) > limit
    except Exception:
        logger.warning("rate_limit_backend_unavailable", extra={"scope": scope})
        return False
