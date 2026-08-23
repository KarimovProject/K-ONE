import os

# 1. Update templates/public/base.html with transparent logo & v=19.5
with open('templates/public/base.html', 'r', encoding='utf-8') as f:
    pub_base = f.read()

pub_base = pub_base.replace('?v=19.4', '?v=19.5')
pub_base = pub_base.replace(
    'src="{% static \'img/k-one/k-one-official.png\' %}"',
    'src="{% static \'img/k-one/k-one-official-transparent.png\' %}"'
)

with open('templates/public/base.html', 'w', encoding='utf-8') as f:
    f.write(pub_base)

# 2. Update templates/base.html with v=19.5
with open('templates/base.html', 'r', encoding='utf-8') as f:
    base_html = f.read()

base_html = base_html.replace('?v=19.2', '?v=19.5')
base_html = base_html.replace('?v=19.4', '?v=19.5')

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(base_html)

# 3. Update public.css for header logo sizing (110-140px on desktop, 95-110px on 1366, 70-82px on mobile)
with open('static/css/public.css', 'r', encoding='utf-8') as f:
    pub_css = f.read()

pub_css = pub_css.replace("""/* --- Logo --- */
.brand-logo-public {
  height: 68px;
  width: auto;
  max-width: 120px;
  object-fit: contain;
  display: block;
  transition: transform var(--duration-micro) var(--ease-out);
}""", """/* --- Logo --- */
.brand-logo-public {
  height: 60px;
  width: auto;
  min-width: 110px;
  max-width: 140px;
  object-fit: contain;
  display: block;
  transition: transform var(--duration-micro) var(--ease-out);
}""")

pub_css = pub_css.replace("""@media (max-width: 1400px) {
  .public-header {
    padding: 0 var(--space-6);
  }
}""", """@media (max-width: 1400px) {
  .public-header {
    padding: 0 var(--space-6);
  }
  .brand-logo-public {
    min-width: 95px;
    max-width: 110px;
    height: 52px;
  }
}""")

pub_css = pub_css.replace("""@media (max-width: 640px) {
  .public-header {
    height: 72px;
    padding: 0 16px;
  }""", """@media (max-width: 640px) {
  .public-header {
    height: 72px;
    padding: 0 16px;
  }
  .brand-logo-public {
    min-width: 70px;
    max-width: 82px;
    height: 42px;
  }""")

with open('static/css/public.css', 'w', encoding='utf-8') as f:
    f.write(pub_css)

# 4. Update static/css/app.css for sidebar width (228px), topbar (64px), content (max-width 1480px), and login
APP_CSS = """/* ==========================================================================
   K-ONE APP SHELL (Authenticated Workspace)
   Phase 19.5 - Compact Enterprise Control Panel
   ========================================================================== */

:root {
  --workspace-sidebar-width: 228px;
}

body {
  margin: 0;
  padding: 0;
  font-family: var(--font-sans);
  background: #F7F9FC;
  color: var(--color-text-main);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-shell {
  display: grid;
  grid-template-columns: var(--workspace-sidebar-width) minmax(0, 1fr);
  height: 100vh;
  overflow: hidden;
  background: #F7F9FC;
}

/* --------------------------------------------------------------------------
   1. SIDEBAR (Compact Deep Navy #071A33)
   -------------------------------------------------------------------------- */
.sidebar {
  background: #071A33;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
  height: 100vh;
  z-index: var(--z-sticky);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  box-sizing: border-box;
  overflow: hidden;
}

.sidebar-header {
  height: 68px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-decoration: none;
}

.sidebar-logo {
  height: 38px;
  width: auto;
  max-width: 130px;
  object-fit: contain;
  display: block;
}

.sidebar-slogan {
  font-size: 9px;
  font-weight: 700;
  color: #16BCEB;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav,
.nav-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-section {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.4);
  padding: 10px 16px 4px;
}

.sidebar-nav-item,
.nav-item {
  height: 40px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  border-left: 3px solid transparent;
  transition: all 0.2s var(--ease-out);
}

.sidebar-nav-item:hover,
.nav-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #FFFFFF;
}

.sidebar-nav-item.active,
.sidebar-nav-item.is-active,
.nav-item.is-active {
  background: #082B57;
  color: #FFFFFF;
  border-left-color: #16BCEB;
  box-shadow: inset 16px 0 16px -16px rgba(22, 188, 235, 0.4);
}

.sidebar-nav-item svg,
.nav-item svg,
.nav-icon svg {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  opacity: 0.75;
}

.sidebar-nav-item.active svg,
.nav-item.is-active svg {
  opacity: 1;
  stroke: #16BCEB;
}

.sidebar-footer,
.sidebar-status {
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-status-copy {
  display: flex;
  flex-direction: column;
}

.sidebar-status-copy strong {
  font-size: 11px;
  font-weight: 700;
  color: #FFFFFF;
}

.sidebar-status-copy small {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

/* --------------------------------------------------------------------------
   2. MAIN CONTENT AREA & TOPBAR
   -------------------------------------------------------------------------- */
.shell-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #F7F9FC;
  position: relative;
  height: 100vh;
  overflow: hidden;
}

.topbar {
  height: 64px;
  background: #FFFFFF;
  border-bottom: 1px solid var(--color-border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: var(--z-sticky);
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar-context {
  display: flex;
  flex-direction: column;
}

.topbar-context .eyebrow {
  font-size: 10px;
  font-weight: 800;
  color: #16BCEB;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.topbar-context strong {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-title);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.language-switch {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #F0F4F8;
  padding: 2px 4px;
  border-radius: 8px;
}

.language-switch button {
  background: transparent;
  border: none;
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-muted);
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.language-switch button.is-current {
  background: #FFFFFF;
  color: #082B57;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.notification-button {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F0F4F8;
  border-radius: 50%;
  color: var(--color-text-main);
  text-decoration: none;
  transition: all 0.2s ease;
}

.notification-button:hover {
  background: #E2E8F0;
  color: var(--color-brand-cobalt);
}

.user-block {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 8px;
  border-left: 1px solid var(--color-border-subtle);
}

.user-block .avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #082B57;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 12px;
}

.user-copy {
  display: flex;
  flex-direction: column;
  text-decoration: none;
}

.user-copy strong {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-title);
}

.user-copy small {
  font-size: 10px;
  color: var(--color-text-muted);
}

.user-block .text-button {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 6px;
}

.user-block .text-button:hover {
  color: var(--color-brand-coral);
}

.admin-link {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-muted);
  text-decoration: none;
  padding: 4px 8px;
}

.public-view-link {
  font-size: 12px;
  font-weight: 700;
  color: #082B57;
  background: rgba(22, 188, 235, 0.12);
  border: 1px solid rgba(22, 188, 235, 0.3);
  padding: 5px 12px;
  border-radius: var(--radius-pill);
  text-decoration: none;
  transition: all 0.2s ease;
}

.public-view-link:hover {
  background: rgba(22, 188, 235, 0.2);
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  box-sizing: border-box;
}

.menu-button {
  display: none;
  background: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

/* Mobile responsive */
@media (max-width: 1024px) {
  .app-shell {
    grid-template-columns: 100%;
  }
  .sidebar {
    position: fixed;
    width: var(--workspace-sidebar-width);
    top: 0; left: 0; bottom: 0;
    transform: translateX(-100%);
    transition: transform 0.3s var(--ease-out);
  }
  .sidebar.is-open {
    transform: translateX(0);
  }
  .menu-button {
    display: block;
  }
  .sidebar-backdrop.is-open {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(7, 26, 51, 0.6);
    backdrop-filter: blur(4px);
    z-index: 90;
    border: none;
  }
}

/* --------------------------------------------------------------------------
   3. AUTHENTICATION / LOGIN LAYOUT (Phase 19.5)
   -------------------------------------------------------------------------- */
.auth-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: #F7F9FC;
}

.auth-brand-panel {
  flex: 0 0 54%;
  background-color: #071A33;
  background-image: url('../img/k-one/k-one-login-network.svg');
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: #FFFFFF;
  overflow: hidden;
}

.auth-brand-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 70%, rgba(22, 188, 235, 0.08) 0%, rgba(20, 92, 255, 0.04) 50%, transparent 75%);
  animation: pulse-glow 8s infinite alternate;
}

@keyframes pulse-glow {
  0% { opacity: 0.6; }
  100% { opacity: 1; }
}

.auth-brand-copy {
  position: relative;
  z-index: 2;
  max-width: 480px;
}

.logo-container {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
  margin-bottom: 24px;
  display: inline-block;
  position: relative;
}

.logo-container::before {
  content: '';
  position: absolute;
  inset: -40px;
  background: radial-gradient(circle, rgba(22, 188, 235, 0.08) 0%, rgba(20, 92, 255, 0.04) 45%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}

.brand-logo-large {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 360px;
  height: auto;
  object-fit: contain;
  display: block;
  animation: fadeInScale 0.4s var(--ease-out);
}

@keyframes fadeInScale {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.logo-container-mobile {
  display: none;
}

.auth-brand-copy h1 {
  font-size: 2rem;
  line-height: 1.2;
  margin-bottom: 12px;
  font-weight: 900;
  letter-spacing: -0.02em;
  color: #FFFFFF;
}

.auth-brand-copy p {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.75);
  line-height: 1.5;
  margin: 0;
}

.auth-form-panel {
  flex: 0 0 46%;
  background: #F7F9FC;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 32px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  background: #FFFFFF;
  padding: 40px;
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(8, 43, 87, 0.06);
  display: flex;
  flex-direction: column;
  gap: 16px;
  border: 1px solid var(--color-border-subtle);
  box-sizing: border-box;
}

.login-heading {
  text-align: center;
  margin-bottom: 8px;
}

.login-heading h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text-title);
  margin-bottom: 4px;
}

.login-heading p {
  color: var(--color-text-muted);
  font-size: 13px;
  margin: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-main);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.auth-form-panel input[type="text"],
.auth-form-panel input[type="password"],
.premium-input {
  width: 100%;
  height: 50px;
  background: #FAFBFD;
  border: 1px solid var(--color-border-subtle);
  padding: 0 16px 0 42px;
  border-radius: 12px;
  font-size: 14px;
  color: var(--color-text-main);
  font-family: var(--font-sans);
  transition: all 0.2s var(--ease-out);
  box-sizing: border-box;
}

.auth-form-panel input:focus,
.premium-input:focus {
  outline: none;
  border-color: #16BCEB;
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(22, 188, 235, 0.15);
}

.auth-form-panel .primary-button.premium-btn {
  width: 100%;
  height: 50px;
  background: #082B57;
  color: #FFFFFF;
  border: 1px solid rgba(22, 188, 235, 0.3);
  padding: 0;
  border-radius: var(--radius-pill);
  font-size: 14px;
  font-weight: 700;
  margin-top: 8px;
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
  box-shadow: 0 4px 12px rgba(8, 43, 87, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-form-panel .primary-button.premium-btn:hover {
  background: #0A356C;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(8, 43, 87, 0.22);
}

.form-alert {
  background: #FFF5F5;
  border: 1px solid #FFD1D1;
  color: #E53E3E;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

.field-error {
  color: #E53E3E;
  font-size: 11px;
  font-weight: 600;
  margin-top: 2px;
}

.security-note {
  font-size: 11px;
  color: var(--color-text-muted);
  text-align: center;
  margin: 8px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.security-note span {
  color: var(--color-status-free);
  font-size: 8px;
}

@media (max-width: 900px) {
  .auth-layout {
    flex-direction: column;
  }
  .auth-brand-panel {
    display: none;
  }
  .auth-form-panel {
    flex: 1;
    width: 100%;
    padding: 24px 16px;
  }
  .login-card {
    padding: 28px 20px;
  }
  .logo-container-mobile {
    display: flex;
    justify-content: center;
    margin-bottom: 16px;
  }
  .brand-logo-mobile {
    height: 60px;
    width: auto;
    max-width: 140px;
    object-fit: contain;
  }
}
"""

with open('static/css/app.css', 'w', encoding='utf-8') as f:
    f.write(APP_CSS)

# 5. Update static/css/workspace.css with Phase 19.5 styles
WORKSPACE_CSS = """/* ==========================================================================
   K-ONE WORKSPACE DASHBOARD (Phase 19.5)
   Compact Enterprise Control Panel
   ========================================================================== */

.workspace-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1440px;
  margin: 0 auto;
  width: 100%;
}

.animate-entrance {
  animation: pageEntrance 0.35s var(--ease-out);
}

@keyframes pageEntrance {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --------------------------------------------------------------------------
   1. COMPACT HERO SECTION
   -------------------------------------------------------------------------- */
.workspace-hero {
  background: #FFFFFF;
  border: 1px solid var(--color-border-subtle);
  border-radius: 16px;
  padding: 18px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.workspace-hero__copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.workspace-hero__badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}

.role-badge {
  background: rgba(20, 92, 255, 0.08);
  color: var(--color-brand-cobalt);
  font-size: 11px;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: var(--radius-pill);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.workspace-date-pill {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

.workspace-hero h1 {
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--color-text-title);
  margin: 0;
  letter-spacing: -0.02em;
}

.workspace-hero p {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}

.compact-hero-btn {
  height: 42px;
  padding: 0 20px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 700;
  background: #082B57;
  color: #FFFFFF;
  border: 1px solid rgba(22, 188, 235, 0.3);
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  box-shadow: 0 2px 6px rgba(8, 43, 87, 0.15);
  transition: all 0.2s var(--ease-out);
}

.compact-hero-btn:hover {
  background: #0A356C;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 43, 87, 0.22);
}

/* --------------------------------------------------------------------------
   2. 4 COMPACT KPI TILES
   -------------------------------------------------------------------------- */
.workspace-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.metric-tile {
  background: #FFFFFF;
  border: 1px solid var(--color-border-subtle);
  border-radius: 14px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  transition: transform 0.2s var(--ease-out), box-shadow 0.2s var(--ease-out), border-color 0.2s var(--ease-out);
}

.metric-tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(8, 43, 87, 0.06);
  border-color: rgba(22, 188, 235, 0.4);
}

.metric-tile__icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.metric-tile--cobalt .metric-tile__icon {
  background: rgba(20, 92, 255, 0.08);
  color: var(--color-brand-cobalt);
}

.metric-tile--coral .metric-tile__icon {
  background: rgba(255, 106, 106, 0.1);
  color: var(--color-brand-coral);
}

.metric-tile--amber .metric-tile__icon {
  background: rgba(255, 176, 32, 0.1);
  color: var(--color-status-upcoming);
}

.metric-tile--cyan .metric-tile__icon {
  background: rgba(22, 188, 235, 0.1);
  color: var(--color-brand-cyan);
}

.metric-tile__content {
  display: flex;
  flex-direction: column;
}

.metric-tile__label {
  font-size: 11px;
  font-weight: 800;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-tile__value {
  font-size: 1.6rem;
  font-weight: 900;
  color: var(--color-text-title);
  line-height: 1.1;
  margin-top: 2px;
}

.text-critical {
  color: var(--color-brand-coral) !important;
}

.text-warning {
  color: var(--color-status-upcoming) !important;
}

/* --------------------------------------------------------------------------
   3. TWO-COLUMN WORKSPACE GRID
   -------------------------------------------------------------------------- */
.workspace-grid {
  display: grid;
  grid-template-columns: 62% 1fr;
  gap: 20px;
  align-items: start;
}

.workspace-panel {
  background: #FFFFFF;
  border: 1px solid var(--color-border-subtle);
  border-radius: 16px;
  padding: 20px 22px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border-subtle);
}

.panel-eyebrow {
  font-size: 10px;
  font-weight: 800;
  color: #16BCEB;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  display: block;
}

.panel-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--color-text-title);
  margin: 2px 0 0;
}

.panel-action-link {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-brand-cobalt);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 4px;
}

.panel-action-link:hover {
  text-decoration: underline;
}

/* Agenda list */
.workspace-event-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.workspace-event-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  background: #FAFBFD;
  border-radius: 10px;
  border: 1px solid var(--color-border-subtle);
  text-decoration: none;
  transition: all 0.2s var(--ease-out);
}

.workspace-event-row:hover {
  background: #FFFFFF;
  transform: translateX(2px);
  border-color: rgba(22, 188, 235, 0.35);
  box-shadow: 0 2px 8px rgba(8, 43, 87, 0.05);
}

.event-row-time {
  display: flex;
  flex-direction: column;
  min-width: 60px;
  font-family: var(--font-mono);
}

.event-row-time .date {
  font-size: 11px;
  font-weight: 800;
  color: var(--color-text-title);
}

.event-row-time .time {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-muted);
}

.event-row-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.event-row-info .title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-title);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-row-info .meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--color-text-muted);
}

.event-row-arrow {
  color: var(--color-text-muted);
  font-size: 13px;
  transition: transform 0.2s ease;
}

.workspace-event-row:hover .event-row-arrow {
  transform: translateX(2px);
  color: var(--color-brand-cobalt);
}

.empty-state-card {
  padding: 32px 16px;
  text-align: center;
}

.empty-state-card h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-title);
  margin: 0 0 4px;
}

.empty-state-card p {
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 0;
}

/* Quick actions */
.workspace-quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-action-item {
  height: 48px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 14px;
  background: #FAFBFD;
  border-radius: 10px;
  border: 1px solid var(--color-border-subtle);
  text-decoration: none;
  transition: all 0.2s var(--ease-out);
}

.quick-action-item:hover {
  background: #FFFFFF;
  transform: translateX(2px);
  border-color: rgba(22, 188, 235, 0.35);
  box-shadow: 0 2px 8px rgba(8, 43, 87, 0.05);
}

.quick-action-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-action-icon.cobalt { background: rgba(20, 92, 255, 0.08); color: var(--color-brand-cobalt); }
.quick-action-icon.cyan { background: rgba(22, 188, 235, 0.1); color: var(--color-brand-cyan); }
.quick-action-icon.emerald { background: rgba(22, 199, 132, 0.1); color: var(--color-status-free); }
.quick-action-icon.violet { background: rgba(121, 87, 255, 0.1); color: var(--color-brand-violet); }

.quick-action-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.quick-action-text strong {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-title);
}

.quick-action-text small {
  font-size: 10px;
  color: var(--color-text-muted);
}

.quick-action-item .arrow {
  color: var(--color-text-muted);
  font-size: 13px;
  transition: transform 0.2s ease;
}

.quick-action-item:hover .arrow {
  transform: translateX(2px);
  color: var(--color-brand-cobalt);
}

/* Responsive */
@media (max-width: 1024px) {
  .workspace-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
  .workspace-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .workspace-hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .compact-hero-btn {
    width: 100%;
    justify-content: center;
  }
  .workspace-metrics {
    grid-template-columns: 1fr;
  }
}
"""

with open('static/css/workspace.css', 'w', encoding='utf-8') as f:
    f.write(WORKSPACE_CSS)

print("Updated public.css, app.css, and workspace.css.")
