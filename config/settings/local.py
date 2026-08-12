from config.settings.base import *  # noqa: F403
from config.settings.base import env

DEBUG = env("DJANGO_DEBUG", default=True)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
