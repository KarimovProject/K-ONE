# IEMS security audit, Phase 10

## Scope and outcome

The review covers authentication, role checks, public/display tokens, public event and check-in routes, attendance, Telegram linking, publication mutations, report exports, uploads, API permissions, cookies, CSRF, production settings, audit payloads and error handling. Automated regression tests complement manual route and code review.

## Findings fixed

1. Login had no shared brute-force throttle. A cache-backed IP plus normalized-username limit now returns HTTP 429 after ten failed attempts in five minutes and resets after successful authentication.
2. Public pages, check-in/count APIs, display polling, publication publish/retry and report exports had inconsistent abuse controls. Explicit scoped limits now protect these routes. Attendance identity remains browser-token based, never IP based.
3. A new browser could double-submit before receiving its identifier cookie. The public page now pre-seeds an HttpOnly, SameSite=Lax browser token; the database unique constraint remains the final race-safe guard.
4. Speaker and generated-banner model fields did not enforce the shared binary validator when files entered through admin/model paths. Image validators now verify extension, MIME when supplied, signature, Pillow decoding and size. Program PDFs now validate size, extension and `%PDF-` signature at model level.
5. Production settings lacked a complete explicit host/origin, SameSite, referrer, structured logging and static manifest policy. These are now production-specific and do not affect local HTTP development.
6. Generic production error pages and a detail-free aggregate readiness route were missing. Localized 400/403/404/429/500 pages and `/health/ready/` are present.
7. Telegram delivery lacked an outer short-lived dispatch lock. A cache lock now prevents parallel worker delivery for the same ledger row; database delivery status remains the durable idempotency record.
8. Database persistent-connection lifetime was fixed at 60 seconds. `DB_CONN_MAX_AGE` is now configurable; the load harness uses zero so threaded development testing cannot exhaust PostgreSQL connections.

## Verified controls

- Django CSRF middleware protects browser mutations; DRF uses authenticated session authentication by default.
- Sessions rotate on login; inactive users fail authentication and capability checks evaluate current database role state on every request.
- Public and display tokens use `secrets.token_urlsafe`, unique indexed columns and explicit rotation/disable paths.
- Rejected, cancelled, displaced and unpublished events are not publicly accessible.
- Telegram link tokens are stored as hashes, expire and are rate limited. Raw tokens and integration credentials are not audit logged.
- Publication services use transaction locks and persisted state to prevent duplicate external posts.
- Report UI, API and exports enforce the same role scope.
- Uploaded SVG is not accepted. Media directories are not listable by Django; production Nginx must disable directory indexes.

## Accepted/documented gaps

- Two-factor authentication is not implemented. Production policy should require IdP/SSO or a reviewed Django 2FA package before high-risk internet exposure.
- CSP permits inline scripts/styles because existing server-rendered FullCalendar and page scripts are inline. Phase 10 limits origins and object/frame capabilities; nonce migration is recommended later.
- FullCalendar and Google Fonts remain third-party browser origins. Self-hosting is recommended before restricted-network deployment.
- HSTS preload defaults off because it is an irreversible domain-wide commitment. Enable only after DNS/TLS and all subdomains are permanently ready.
- Real Telegram Channel and Instagram smoke tests remain NOT TESTED.

## RBAC matrix

| Area | Super admin | International admin | Responsible | Management | Leadership | Content | Reception |
|---|---|---|---|---|---|---|---|
| Master data view | Full | Full | Read | Read | Read | Read | Read |
| Master data mutate | Full | Full | No | No | No | No | No |
| Events | Full | Full | Own create/manage | Review context | Read | Publication context | Attendance context |
| Approval/emergency | Full | Full | Submit own | Approve/reject/override | Read | No | No |
| Program/QR | Full | Full | Own event | No | Read public | No | No |
| Attendance | Full | Full | Own event | Aggregate/read | Aggregate/read | No | Operate |
| Leadership/display management | Full | Full | No | Read | Read | No | Operational venue read |
| Telegram settings | Own + admin diagnostics | Own + admin diagnostics | Own | Own | Own | Own | Own |
| Publications | Full | Full | Request own | Approve | Preview | Prepare/publish policy | No |
| Reports | Full | Full | Own events | Aggregate | Aggregate | Publications only | Attendance only |

Server-side tests cover critical direct-route denials; hiding navigation is not treated as authorization.
