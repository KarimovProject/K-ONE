import os
from pathlib import Path

import environ
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parents[1]
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

django_application = get_wsgi_application()

if settings.DEBUG:
    application = StaticFilesHandler(django_application)
else:
    application = django_application
