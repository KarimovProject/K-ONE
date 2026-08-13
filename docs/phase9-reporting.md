# Phase 9: reporting and analytics

All reporting queries require a bounded date range in `Asia/Tashkent`. The default is the current month and custom ranges are limited to two years. Filters are applied once by the read-side selector and reused by the dashboard, authenticated APIs and exports.

## Venue utilization policy

Booked minutes count only `approved`, `planned`, `scheduled`, `ongoing`, `completed` and `emergency` events. Draft, pending approval, rejected, cancelled and displaced events do not consume utilization. Available minutes equal each active venue's daily working minutes multiplied by every calendar day in the selected inclusive range.

## Privacy and scope

Leadership views expose aggregate attendance only. Exports omit attendee hashes, raw browser tokens, Telegram identifiers, chat IDs, approval notes, platform credentials and emergency justification. Phase 9 reads Phase 7 and Phase 8 ledgers but does not call Telegram, Instagram or external analytics APIs.

Server-side report policy gives administrators, leadership, management and responsible employees the appropriate aggregate views (responsible employees remain restricted to their own events). Reception operators can access only attendance reporting and its CSV export; content managers can access only publication reporting and its CSV export. API and export endpoints enforce the same policy as the UI.

## Visualization

The dashboard uses dependency-free semantic HTML progress/bar charts with visible labels, values and text/table equivalents. This keeps the existing server-rendered architecture, works without a CDN and does not rely on color alone.

## Performance

The reporting boundary uses database annotations, bounded querysets, `select_related`, `prefetch_related` and grouped values queries. Existing indexes cover event date/status, attendance timestamps, audit action/timestamp, publication status/schedule and Telegram delivery status/schedule, so no speculative Phase 9 index was added.
