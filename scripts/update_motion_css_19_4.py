import os

# 1. Update static/css/motion.css
MOTION_CSS = """/* ==========================================================================
   IEMS MOTION SYSTEM - Phase 19.4
   Animation primitives only. No phase prefixes.
   ========================================================================== */

:root {
  /* Premium Durations */
  --duration-micro: 160ms;       /* Hover, focus, small states */
  --duration-fast: 220ms;        /* Month transitions */
  --duration-component: 280ms;   /* Card expands, standard transitions */
  --duration-modal: 450ms;       /* Drawers, modals, page entrance */

  /* Premium Easing Curves */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);       /* Smooth Apple-like decelerate */
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);   /* Smooth accelerate & decelerate */
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Subtle pop/bounce */
  --ease-linear: linear;
}

/* --------------------------------------------------------------------------
   1. GLOBAL REDUCED MOTION
   -------------------------------------------------------------------------- */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* --------------------------------------------------------------------------
   2. KEYFRAMES
   -------------------------------------------------------------------------- */

@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Status Breathing Animations */
@keyframes status-breathe {
  0%, 100% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 0 rgba(22, 199, 132, 0.4); }
  50% { transform: scale(0.92); opacity: 0.7; box-shadow: 0 0 0 5px rgba(22, 199, 132, 0); }
}

@keyframes status-pulse-cobalt {
  0%, 100% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 0 rgba(20, 92, 255, 0.4); }
  50% { transform: scale(0.92); opacity: 0.7; box-shadow: 0 0 0 5px rgba(20, 92, 255, 0); }
}

@keyframes status-pulse-amber {
  0%, 100% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 0 rgba(255, 176, 32, 0.4); }
  50% { transform: scale(0.92); opacity: 0.7; box-shadow: 0 0 0 5px rgba(255, 176, 32, 0); }
}

/* NOW Pulse */
@keyframes now-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
}

/* --------------------------------------------------------------------------
   3. UTILITY CLASSES
   -------------------------------------------------------------------------- */

.animate-entrance {
  animation: fade-in-up var(--duration-modal) var(--ease-out) both;
}

.animate-stagger-1 { animation-delay: 40ms; }
.animate-stagger-2 { animation-delay: 80ms; }
.animate-stagger-3 { animation-delay: 120ms; }
.animate-stagger-4 { animation-delay: 160ms; }
.animate-stagger-5 { animation-delay: 200ms; }

.status-breathe-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.status-breathe-dot.bg-free {
  background: var(--color-status-free, #16C784);
  animation: status-breathe 2.4s infinite ease-in-out;
}
.status-breathe-dot.bg-active {
  background: var(--color-brand-cobalt, #145CFF);
  animation: status-pulse-cobalt 2s infinite ease-in-out;
}
.status-breathe-dot.bg-upcoming {
  background: var(--color-status-upcoming, #FFB020);
  animation: status-pulse-amber 2.2s infinite ease-in-out;
}

.marker-pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #FFFFFF;
  display: inline-block;
  animation: now-pulse 1.6s infinite ease-in-out;
}
"""

with open('static/css/motion.css', 'w', encoding='utf-8') as f:
    f.write(MOTION_CSS)
print("Updated motion.css")
