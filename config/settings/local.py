from config.settings.base import *  # noqa: F403
from config.settings.base import env

DEBUG = env("DJANGO_DEBUG", default=True)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Keep local HTTP acceptance sessions isolated from other Django projects on the same host.
# Browser cookies are scoped by host, not port, so the framework defaults can collide on LAN PCs.
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME", default="iems_local_sessionid")
CSRF_COOKIE_NAME = env("CSRF_COOKIE_NAME", default="iems_local_csrftoken")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
