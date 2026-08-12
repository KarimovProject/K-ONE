# Environment variables

Copy `.env.example` to `.env`. `.env` is ignored by Git and must never contain committed
credentials.

| Variable | Native Windows purpose |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.local` for local development |
| `DJANGO_SECRET_KEY` | Unique local signing secret |
| `DJANGO_DEBUG` | Local debug behavior |
| `DJANGO_ALLOWED_HOSTS` | Local host allowlist |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Trusted local HTTP origins |
| `DJANGO_LANGUAGE_CODE` | Default locale (`uz`, `ru`, or `en`) |
| `DJANGO_TIME_ZONE` | Application timezone; default `Asia/Tashkent` |
| `DJANGO_STATIC_ROOT` | Absolute static collection path |
| `DJANGO_MEDIA_ROOT` | Absolute uploaded-media path |
| `DB_NAME` | Native PostgreSQL database; default `iems` |
| `DB_USER` | Native PostgreSQL role; expected local value `postgres` |
| `DB_PASSWORD` | Existing local PostgreSQL password |
| `DB_HOST` | `127.0.0.1` for native Windows PostgreSQL |
| `DB_PORT` | Native PostgreSQL port, normally `5432` |
| `REDIS_HOST` | `127.0.0.1` for native Windows Redis |
| `REDIS_PORT` | Native Redis port, normally `6379` |
| `REDIS_URL` | Django cache and Redis health URL (database 0) |
| `CELERY_BROKER_URL` | Celery broker URL (database 1) |
| `CELERY_RESULT_BACKEND` | Celery result URL (database 2) |
| `APP_VERSION` | Version exposed by application health |
| `LOG_LEVEL` | Root logging threshold |
| `SECURE_SSL_REDIRECT` | HTTPS redirect; false only for local HTTP |

Native defaults never use Docker DNS names such as `db` or `redis`. Optional Compose services
override `DB_HOST` and Redis URLs inside their isolated deployment network.

The native Windows service on the verified workstation is Redis 3.0.504. `redis-py 5.2.1`
is intentionally pinned because it uses the compatible RESP2 connection path. Redis-py 8
attempts the unsupported `HELLO` command against this server.
