# IEMS Visual Redesign Audit

**Date:** August 15, 2026  
**Auditor:** Senior Product Design & UX Engineering Team  
**Scope:** Complete visual experience review of IEMS (Phase 11 Information Architecture) across 5 viewports:
- 1920×1080 (Desktop Large)
- 1440×900 (Laptop Standard)
- 1366×768 (Notebook)
- 768×1024 (Tablet Portrait)
- 390×844 (Mobile)

---

## Executive Summary

While the Phase 0–11 core business logic, API capabilities, RBAC, conflict resolution, and data models are rock solid (285 passing unit tests), **the current user-facing visual design is rated 0/10 by the project owner**. It resembles a developer dashboard or basic Django template with generic cards, plain white/grey tables, harsh borders, static layouts, and lack of visual prestige.

This document details the audit findings for all 17 primary screens (A through Q) and sets the exact target specifications for the complete visual rebuild.

---

## Detailed Audit by Screen

### A. Public Dashboard (`/dashboard/`)
* **Visual Hierarchy:** Lacks institutional gravitas. Hero section is static and flat. KPI cards look like generic Bootstrap boxes.
* **Whitespace & Layout:** Cards are cramped on small viewports and stretched awkwardly on 1920px displays.
* **Typography:** Browser-default font rendering, insufficient weight contrast between numbers and labels.
* **Color:** Plain dark blue headers mixed with standard slate cards; missing scientific cyan and medical teal accents.
* **CTA Clarity:** "Tadbirlar taqvimi" and "Zallar holati" buttons lack hover depth or clear primary focus.
* **Animation Opportunity:** Background node/grid light fields, live status dot pulses, counter number rollups.
* **Responsive Weakness:** On 390px mobile, KPI grid breaks into stacked full-width boxes without comfortable padding.
* **Consistency & Accessibility:** Low contrast on subtle text badges; focus rings missing.

### B. Public Calendar (`/dashboard/calendar/`)
* **Visual Hierarchy:** Looks like raw FullCalendar embedded in a div. Header navigation buttons are unstyled.
* **Whitespace & Layout:** Month view cells have inconsistent padding; day grid text clashes with event chips.
* **Typography:** Small 12px text in event chips; event titles truncated abruptly.
* **Color:** Standard blue strips for events regardless of event category or status semantics.
* **CTA Clarity:** View switcher (Oy / Hafta / Kun / Ro'yxat) lacks segmented slider indicator.
* **Animation Opportunity:** Smooth view transition animations, drawer slide-in from right when clicking event chip.
* **Responsive Weakness:** Month view on mobile is unreadable; needs automatic switch to agenda/list mode.
* **Consistency & Accessibility:** Filter controls rely on native browser selects; keyboard focus is erratic.

### C. Live Venues (`/venues/live/`)
* **Visual Hierarchy:** Simple grid of boxes without room elevation or presence.
* **Whitespace & Layout:** Excessive padding inside venue cards; status indicators are tiny dots.
* **Typography:** Venue names lack distinct weights; time remaining text is muted gray.
* **Color:** Simple green/red tags instead of rich glowing cyan/deep blue occupied states and emerald available states.
* **CTA Clarity:** No direct action to view upcoming schedule or book venue.
* **Animation Opportunity:** Minute-based smooth progress bar animation for ongoing events, ambient status glow.
* **Responsive Weakness:** Card grid breaks awkwardly on tablet viewports (768px).
* **Consistency & Accessibility:** Status rely solely on color dots without descriptive icon badges.

### D. Login (`/accounts/login/`)
* **Visual Hierarchy:** Centered white card on grey background — classic developer login style.
* **Whitespace & Layout:** Huge unused empty space around card; fields feel disconnected.
* **Typography:** Standard system sans-serif without institutional brand character.
* **Color:** Dull blue button on white card.
* **CTA Clarity:** "Kirish" button lacks elevation and feedback state.
* **Animation Opportunity:** Premium split-screen layout with left-hand animated scientific network/nodes.
* **Responsive Weakness:** On mobile, split screen should stack cleanly with header branding.
* **Consistency & Accessibility:** Form input borders lack focus glow; screen reader error messages missing.

### E. User Workspace (`/workspace/`)
* **Visual Hierarchy:** Flat collection of statistics and lists. Doesn't feel like a personal command center.
* **Whitespace & Layout:** Uneven column gap between quick actions and event tables.
* **Typography:** Headers share same font size as card titles.
* **Color:** Monochrome tables with plain blue links.
* **CTA Clarity:** "+ Yangi tadbir yaratish" button is small and tucked into top right corner.
* **Animation Opportunity:** Staggered card entrance on load, hover elevation for actionable task cards.
* **Responsive Weakness:** Mobile view table horizontal scroll creates bad user experience.
* **Consistency & Accessibility:** Badges use inline style overrides instead of unified design tokens.

### F. Profile (`/profile/`)
* **Visual Hierarchy:** Simple form list without avatar/identity header.
* **Whitespace & Layout:** Tight field grouping, narrow text inputs on desktop displays.
* **Typography:** Labels and input values are identical font size.
* **Color:** Plain grey borders around inputs.
* **CTA Clarity:** Save button lacks clear success state feedback.
* **Animation Opportunity:** Tab transition indicator between Personal Info and Security settings.
* **Responsive Weakness:** Stretches across 1920px screen unnecessarily.

### G. Events List (`/events/`)
* **Visual Hierarchy:** Standard data table view. Lacks quick filters or priority visual tagging.
* **Whitespace & Layout:** Cramped table rows with text overflow.
* **Typography:** Identical font weight across title, venue, and date columns.
* **Color:** Unrefined status pills.
* **CTA Clarity:** Search bar looks unintegrated.
* **Animation Opportunity:** Hover highlight row transition, smooth filter drawer toggle.
* **Responsive Weakness:** Unusable on mobile viewports (requires horizontal scrolling).

### H. Event Create Wizard (`/events/create/`)
* **Visual Hierarchy:** Long scrolling form or multi-tab view without clear visual step progress.
* **Whitespace & Layout:** Field inputs placed arbitrarily without grid alignment.
* **Typography:** Instructions are small muted text; step titles lack weight.
* **Color:** Standard primary blue for active step.
* **CTA Clarity:** "Keyingisi" / "Oldingisi" buttons blend into background.
* **Animation Opportunity:** Step transition slide animations, interactive venue availability cards.
* **Responsive Weakness:** Multi-column inputs overflow on 390px viewports.

### I. Event Detail (`/events/<id>/`)
* **Visual Hierarchy:** Form-like view with tabs. Lacks visual hero overview of event.
* **Whitespace & Layout:** Uneven card spacing, long text fields stretch across full width.
* **Typography:** Main title is undersized compared to page header.
* **Color:** Neutral dark background missing; status badge is tiny.
* **CTA Clarity:** Action buttons (Edit, Approve, Cancel, Print QR) are grouped in flat bar.
* **Animation Opportunity:** Action button loading feedback, smooth tab panel fade.
* **Responsive Weakness:** Sidebar items wrap beneath main content awkwardly.

### J. Approvals (`/events/?status=pending`)
* **Visual Hierarchy:** Indistinguishable from general events list table.
* **Whitespace & Layout:** Table rows do not emphasize urgent pending items.
* **Typography:** Date and priority labels look plain.
* **Color:** Missing warm amber priority highlights and approval requirement tokens.
* **CTA Clarity:** Quick Approve / Reject action buttons are small text links.
* **Animation Opportunity:** Card removal animation upon decision, sticky action drawer.

### K. Attendance (`/events/<id>/attendance/`)
* **Visual Hierarchy:** Basic count box next to table of check-ins.
* **Whitespace & Layout:** Empty spaces around stats, poor alignment.
* **Typography:** Check-in count number is small (24px).
* **Color:** Plain green numbers without glowing live status indicator.
* **CTA Clarity:** Manual check-in button lacks prominence.
* **Animation Opportunity:** Live count-up animation as attendees scan QR.

### L. Leadership Dashboard (`/leadership/`)
* **Visual Hierarchy:** Detailed operational charts cluttering executive view.
* **Whitespace & Layout:** Cards lack generous padding and strategic hierarchy.
* **Typography:** Key metrics share space with minor table labels.
* **Color:** Standard chart colors; missing deep institutional navy and royal violet.
* **CTA Clarity:** Date filter controls lack clean executive styling.
* **Animation Opportunity:** Executive card entrance stagger, live update counter morphing.

### M. TV Wallboard (`/display/venues/`)
* **Visual Hierarchy:** Text size too small for 4K / large TV displays.
* **Whitespace & Layout:** Margins too large, content feels sparse in center.
* **Typography:** Standard body font scale used instead of 28px-72px TV typography.
* **Color:** Flat dark background without subtle light fields or high-contrast status glow.
* **CTA Clarity:** Real-time clock and room status indicators are hard to read from distance.
* **Animation Opportunity:** Continuous ambient status pulse, smooth event countdown update.

### N. Telegram Settings (`/notifications/telegram/`)
* **Visual Hierarchy:** Simple form list. Bot connection status is not visually highlighted.
* **Whitespace & Layout:** Text fields stretch full width on desktop.
* **Typography:** Token strings look like unformatted code.
* **Color:** Plain grey notice box.
* **CTA Clarity:** Connect / Disconnect button lacks verified green card state.
* **Animation Opportunity:** Verified checkmark animation upon connection test.

### O. Publication Composer (`/publications/`)
* **Visual Hierarchy:** Form fields on left, blank text box on right.
* **Whitespace & Layout:** Does not resemble a modern social media composer.
* **Typography:** Title input and post body use same font style.
* **Color:** Missing channel-specific brand color accents (Telegram cyan, Instagram gradient).
* **CTA Clarity:** "Chop etish" button lacks scheduled vs immediate state toggle.
* **Animation Opportunity:** Real-time live phone/card preview update.

### P. Reports (`/reports/`)
* **Visual Hierarchy:** Dense grid of unstyled tables and plain charts.
* **Whitespace & Layout:** Cramped chart containers with clipped legends.
* **Typography:** Axis labels are tiny grey text.
* **Color:** Multi-colored rainbow charts violating institutional theme.
* **CTA Clarity:** Export PDF / Excel buttons look like plain links.
* **Animation Opportunity:** Chart draw-in animation, export progress spinner.

### Q. Django Admin (`/admin/`)
* **Visual Hierarchy:** Standard Django green/blue header styling.
* **Whitespace & Layout:** Default table density without modern padding.
* **Typography:** Generic system fonts.
* **Color:** Unbranded Django header color (#417690).
* **CTA Clarity:** Action dropdown and search button blend together.
* **Animation Opportunity:** Smooth sidebar collapse, row selection highlights.

---

## Key Redesign Action Plan

1. **Design Tokens (`static/css/tokens.css`):** Rebuild complete token system featuring Midnight Navy (`#071427`), Deep Navy (`#0B1F38`), Institutional Blue (`#165DFF`), Scientific Cyan (`#16C7E8`), Medical Teal (`#00A99D`), Emerald (`#16B978`), Warm Amber (`#F5A524`), Coral (`#F05D5E`), Royal Violet (`#7559E8`).
2. **Typography Scale & Self-Hosted Fonts:** Self-host Inter/Plus Jakarta Sans with proper font weight tokens (400, 500, 600, 700, 800) and scale (13px to 72px).
3. **Motion Design System:** Standardize CSS variables for instant (120ms), fast (180ms), standard (280ms), slow (450ms), emphasis (650ms) using `cubic-bezier(.16,1,.3,1)` easing and full `prefers-reduced-motion` support.
4. **Public & Workspace Pages:** Implement luxury glassmorphic surfaces, animated ambient grid background for hero sections, custom FullCalendar theme wrapper, venue status live progression bar, split-screen login, intuitive event wizard, responsive tables, and executive TV wallboard.
5. **Django Admin Branding:** Inject custom IEMS institutional header, dark navy theme, rounded inputs, custom badges, and sticky table header formatting into Django Admin templates.
