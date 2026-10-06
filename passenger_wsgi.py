"""Entry point for Passenger (CloudLinux "Setup Python App") shared hosting.

Passenger imports this module; the Docker/Waitress deployments use
config.wsgi directly and do not need this file.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from config.wsgi import application  # noqa: E402
