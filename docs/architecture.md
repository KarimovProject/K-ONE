# Architecture overview

IEMS is a modular Django monolith. Each domain has a dedicated app boundary, while shared
runtime configuration lives in `config`. Phase 0 intentionally creates only the custom
account model; other domain apps are empty seams for later approved phases.

## Boundaries

- `accounts`: authentication, custom user, role vocabulary, and capability mapping.
- `events`, `venues`, `organizations`: core master and event domains, not implemented yet.
- `approvals`, `attendance`: workflow domains, not implemented yet.
- `notifications`, `publications`: delivery and external integrations, disabled for now.
- `reporting`: dashboard presentation selector and shell view only.
- `audit`: future immutable audit trail boundary.
- `config`: settings, URL routing, Celery bootstrap, and operational health checks.

Views coordinate HTTP behavior. Queries belong in selectors when non-trivial read models
arrive; state transitions belong in services. Templates render supplied presentation data
and do not own business rules. Repositories are not introduced until an external or complex
persistence boundary genuinely requires them.

Settings are split into base, local, test, and production modules. Tests use an isolated
in-memory SQLite database so the baseline can run without external services; local and
production settings use PostgreSQL. Native Windows development connects to PostgreSQL and
Redis on `127.0.0.1`; Compose hostnames exist only in the optional deployment reference.
Redis backs Django's default cache, Celery broker, and result backend on separate logical
databases. Redis health is tested with a mocked network call while the actual endpoint performs
a real ping at runtime.
