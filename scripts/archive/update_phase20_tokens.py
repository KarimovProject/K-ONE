import os

# 1. Update static/css/tokens.css with consolidated K-ONE tokens
TOKENS_CSS = """/* ==========================================================================
   K-ONE DESIGN TOKENS (Phase 20)
   Global variables across all applications.
   ========================================================================== */

:root {
  /* --------------------------------------------------------------------------
     1. COLOR SYSTEM (K-ONE Brand & Operational Surfaces)
     -------------------------------------------------------------------------- */

  /* Core Surfaces */
  --color-surface-base: #F5F8FC;       /* Main bright background */
  --color-surface-panel: #F0F4F9;      /* Slightly deeper panel */
  --color-surface-elevated: #FFFFFF;   /* Standard elevated card/module */
  --color-surface-glass: rgba(255, 255, 255, 0.85); /* Frosted */

  --color-surface-tint-blue: #EEF5FF;  /* For tinted live/active modules */
  --color-surface-tint-cyan: #EAF8FB;  /* For tinted alternative modules */

  /* Navigation / Dark Accent */
  --color-nav-base: #071A33;           /* Deep ink / K-ONE Navy */
  --color-nav-hover: #0A2244;
  --color-nav-active: #082B57;
  --color-nav-text: #EAF8FB;

  /* Brand Palette */
  --color-brand-navy: #071A33;
  --color-brand-navy-light: #082B57;
  --color-brand-cobalt: #1769FF;       /* Primary Blue */
  --color-brand-cobalt-light: #287BFF;
  --color-brand-cobalt-subtle: rgba(23, 105, 255, 0.12);
  --color-brand-cyan: #00AEEF;         /* Cyan */
  --color-brand-turquoise: #13C8B0;
  --color-brand-violet: #7659FF;
  --color-brand-coral: #EF5B67;        /* Danger / Coral */

  /* Status */
  --color-status-free: #16C784;        /* Emerald */
  --color-status-free-bg: rgba(22, 199, 132, 0.1);
  --color-status-active: #1769FF;
  --color-status-active-bg: rgba(23, 105, 255, 0.1);
  --color-status-upcoming: #F5A623;    /* Amber */
  --color-status-upcoming-bg: rgba(245, 166, 35, 0.1);
  --color-status-special: #7659FF;
  --color-status-special-bg: rgba(118, 89, 255, 0.1);
  --color-status-critical: #EF5B67;
  --color-status-critical-bg: rgba(239, 91, 103, 0.1);

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #082B57, #1769FF);
  --gradient-secondary: linear-gradient(135deg, #1769FF, #00AEEF);
  --gradient-accent: linear-gradient(135deg, #7659FF, #1769FF);

  /* Typography Colors */
  --color-text-title: #071A33;         /* Deep navy */
  --color-text-main: #0A1F3A;          /* Ink */
  --color-text-secondary: #47566B;     /* Slate medium */
  --color-text-muted: #718096;         /* Slate light */
  --color-text-inverse: #FFFFFF;

  /* Borders & Dividers */
  --color-border-subtle: #E2E8F0;
  --color-border-default: #CBD5E1;
  --color-border-focus: #1769FF;
  --color-grid-line: rgba(7, 26, 51, 0.04);

  /* --------------------------------------------------------------------------
     2. TYPOGRAPHY SYSTEM
     -------------------------------------------------------------------------- */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;

  /* Strong Hierarchy */
  --text-title-xl: 32px;               /* Page title */
  --text-title: 22px;                  /* Section heading */
  --text-heading: 20px;
  --text-operational: 28px;            /* Operational number */
  --text-body-lg: 16px;
  --text-body: 14px;                   /* Standard body */
  --text-label: 13px;                  /* Form label */
  --text-table: 13.5px;                /* Table text */
  --text-meta: 12px;                   /* Meta / Subtext */
  --text-micro: 11px;                  /* 11px Small tags / uppercase */

  --weight-normal: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;
  --weight-black: 800;

  /* --------------------------------------------------------------------------
     3. ELEVATION & SHADOWS
     -------------------------------------------------------------------------- */
  --shadow-sm: 0 1px 3px rgba(7, 26, 51, 0.04), 0 1px 2px rgba(7, 26, 51, 0.02);
  --shadow-md: 0 4px 8px -1px rgba(7, 26, 51, 0.06), 0 2px 4px -1px rgba(7, 26, 51, 0.03);
  --shadow-lg: 0 12px 24px -4px rgba(7, 26, 51, 0.08), 0 4px 6px -2px rgba(7, 26, 51, 0.03);
  --shadow-glow-cobalt: 0 0 12px rgba(23, 105, 255, 0.25);
  --shadow-glow-cyan: 0 0 12px rgba(0, 174, 239, 0.25);

  /* --------------------------------------------------------------------------
     4. GEOMETRY & SPACING
     -------------------------------------------------------------------------- */
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-pill: 9999px;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* --------------------------------------------------------------------------
     5. TRANSITIONS & TIMING
     -------------------------------------------------------------------------- */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --duration-micro: 160ms;
  --duration-fast: 200ms;
  --duration-component: 240ms;

  --z-base: 1;
  --z-dropdown: 50;
  --z-sticky: 100;
  --z-drawer: 200;
  --z-modal: 300;
  --z-toast: 400;
}
"""

with open('static/css/tokens.css', 'w', encoding='utf-8') as f:
    f.write(TOKENS_CSS)

print("Updated tokens.css with Phase 20 K-ONE tokens.")
