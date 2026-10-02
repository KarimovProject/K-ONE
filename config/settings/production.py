import os

from config.settings.base import *  # noqa: F403
from config.settings.base import env

DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS")
# The Windows LAN Scheduled Task runs Waitress directly with no
# TLS-terminating reverse proxy in front of it (plain HTTP), so forcing
# HTTPS-only settings there would 301-redirect every request to a
# nonexistent https:// endpoint and drop Secure cookies entirely (breaking
# login with a CSRF failure). register-tasks.ps1 sets this one flag for
# that task only — it is never read from .env, so it can't silently weaken
# a real TLS-fronted deployment (Docker, etc.), which always defaults secure.
_PLAIN_HTTP_LAN = os.environ.get("IEMS_PLAIN_HTTP_LAN") == "True"
SESSION_COOKIE_SECURE = not _PLAIN_HTTP_LAN
CSRF_COOKIE_SECURE = not _PLAIN_HTTP_LAN
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_SSL_REDIRECT = not _PLAIN_HTTP_LAN
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=False)
# Preload is an irreversible domain-wide commitment. Enable only after operations approve it.
if not SECURE_HSTS_PRELOAD:
    SILENCED_SYSTEM_CHECKS = ["security.W021"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
# STATICFILES_STORAGE is ignored by Django 5.1+ (removed in favor of
# STORAGES) — without this, collectstatic silently fell back to the
# unhashed default storage and never wrote a manifest.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.dummy.EmailBackend")
# "file" is kept alongside "production_console" so logs still land somewhere
# when the process has no attached console/stdout (e.g. native Windows
# Scheduled Tasks launched via pythonw.exe) — under Docker/gunicorn,
# production_console (stdout) is what's normally collected.
LOGGING["root"] = {"handlers": ["production_console", "file"], "level": LOG_LEVEL}  # noqa: F405
LOGGING["loggers"]["django.request"]["handlers"] = ["production_console", "file"]  # noqa: F405
