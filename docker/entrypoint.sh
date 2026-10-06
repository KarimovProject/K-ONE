#!/bin/sh
set -eu

# Only the web service runs schema/static setup; worker and beat start
# after it so they never race each other on migrations.
if [ "${IEMS_RUN_MIGRATIONS:-0}" = "1" ]; then
    python manage.py migrate --noinput
    python manage.py collectstatic --noinput
fi

exec "$@"
