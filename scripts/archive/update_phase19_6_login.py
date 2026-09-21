import os

# 1. Update templates/registration/login.html
LOGIN_TEMPLATE = """{% extends "base.html" %}
{% load i18n static %}

{% block title %}K-ONE — Kirish{% endblock %}

{% block unauthenticated_content %}
<section class="auth-brand-panel" aria-hidden="true">
  <div class="auth-brand-copy">
    <div class="logo-container">
      <img src="{% static 'img/k-one/k-one-official-transparent.png' %}" alt="K-ONE Logo" class="brand-logo-large">
    </div>
    <h1>Barcha tadbirlar yagona tizimda</h1>
    <p>Xalqaro tadbirlar, zallar faolligi va boshqaruv jarayonlarini bitta professional makonda birlashtiruvchi platforma.</p>
  </div>
</section>

<section class="auth-form-panel">
  <form class="login-card" method="post" novalidate>
    {% csrf_token %}
    <div class="login-heading">
      <div class="logo-container-mobile">
        <img src="{% static 'img/k-one/k-one-official-transparent.png' %}" alt="K-ONE Logo" class="brand-logo-mobile">
      </div>
      <h2>Xush kelibsiz</h2>
      <p>K-ONE boshqaruv tizimiga kiring</p>
    </div>

    {% if form.non_field_errors %}
      <div class="form-alert" role="alert">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <span>{% trans "Login yoki parol noto‘g‘ri. Qayta tekshirib kiriting." %}</span>
      </div>
    {% endif %}

    <div class="form-group">
      <label for="{{ form.username.id_for_label }}">Foydalanuvchi nomi</label>
      <div class="input-wrapper">
        <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        <input type="text" name="username" id="{{ form.username.id_for_label }}" class="premium-input" placeholder="Foydalanuvchi nomi" required {% if form.username.value and form.username.value != 'acceptance_admin' %}value="{{ form.username.value }}"{% endif %}>
      </div>
      {% if form.username.errors %}
        <div class="field-error" id="username-error">{{ form.username.errors }}</div>
      {% endif %}
    </div>

    <div class="form-group">
      <label for="{{ form.password.id_for_label }}">Parol</label>
      <div class="input-wrapper">
        <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
        <input type="password" name="password" id="{{ form.password.id_for_label }}" class="premium-input" placeholder="Parol" required>
      </div>
      {% if form.password.errors %}
        <div class="field-error" id="password-error">{{ form.password.errors }}</div>
      {% endif %}
    </div>

    {% if next %}<input type="hidden" name="next" value="{{ next }}">{% endif %}

    <button class="primary-button premium-btn" type="submit">Kirish</button>

    <p class="security-note"><span aria-hidden="true">●</span> Tizimga kirish faqat ruxsat etilgan xodimlar uchun.</p>
  </form>
</section>
{% endblock %}
"""

with open('templates/registration/login.html', 'w', encoding='utf-8') as f:
    f.write(LOGIN_TEMPLATE)

# 2. Update static/css/app.css with refined 50/50 login layout, autofill override, and compact alert
with open('static/css/app.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

# Replace the login section in app.css
old_auth_section = """/* --------------------------------------------------------------------------
   3. AUTHENTICATION / LOGIN LAYOUT (Phase 19.5)
   -------------------------------------------------------------------------- */"""

# Let's write the complete, clean app.css
APP_CSS_CLEAN = """/* ==========================================================================
   K-ONE APP SHELL (Authenticated Workspace & Auth)
   Phase 19.6 - Professional Institutional Polish
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
  height: 42px;
  width: auto;
  max-width: 130px;
  object-fit: contain;
  display: block;
  transform: scale(1.3);
  transform-origin: left center;
  margin-left: 4px;
  margin-bottom: 2px;
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

.sr-only {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
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
    display: flex;
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

@media (max-width: 640px) {
  .topbar {
    padding: 0 16px;
    height: 56px;
  }
  .topbar-context {
    display: none;
  }
  .user-block,
  .admin-link,
  .public-view-link {
    display: none;
  }
  .menu-button {
    font-size: 24px;
    color: var(--color-text-title);
    padding: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* --------------------------------------------------------------------------
   3. AUTHENTICATION / LOGIN LAYOUT (Phase 19.6)
   -------------------------------------------------------------------------- */
.auth-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: #F7F9FC;
}

.auth-brand-panel {
  flex: 0 0 50%;
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
  box-sizing: border-box;
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
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.logo-container {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
  margin: 0 0 16px 0;
  display: inline-block;
  position: relative;
}

.brand-logo-large {
  width: 100%;
  max-width: 350px;
  max-height: 300px;
  height: auto;
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 8px 24px rgba(0, 174, 239, 0.12));
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
  font-size: 1.85rem;
  line-height: 1.25;
  margin: 16px 0 10px 0;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #FFFFFF;
}

.auth-brand-copy p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  margin: 0;
}

.auth-form-panel {
  flex: 0 0 50%;
  background: #F7F9FC;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 32px;
  box-sizing: border-box;
}

.login-card {
  width: 100%;
  max-width: 430px;
  background: #FFFFFF;
  padding: 36px 32px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(8, 43, 87, 0.06);
  display: flex;
  flex-direction: column;
  gap: 16px;
  border: 1px solid var(--color-border-subtle);
  box-sizing: border-box;
}

.login-heading {
  text-align: center;
  margin-bottom: 4px;
}

.login-heading h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-text-title);
  margin: 0 0 4px 0;
  letter-spacing: -0.01em;
}

.login-heading p {
  color: var(--color-text-muted);
  font-size: 13px;
  margin: 0;
}

.form-alert {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #FFF5F5;
  border: 1px solid #FEB2B2;
  color: #C53030;
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.3;
}

.form-alert svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: #E53E3E;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
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

/* Base input styling */
.auth-form-panel input[type="text"],
.auth-form-panel input[type="password"],
.premium-input {
  width: 100%;
  height: 50px;
  background: #FFFFFF;
  border: 1px solid var(--color-border-default);
  padding: 0 16px 0 42px;
  border-radius: 11px;
  font-size: 14px;
  color: #071A33;
  font-family: var(--font-sans);
  transition: border-color 0.2s var(--ease-out), box-shadow 0.2s var(--ease-out);
  box-sizing: border-box;
}

.auth-form-panel input:focus,
.premium-input:focus {
  outline: none;
  border-color: #16BCEB;
  background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(22, 188, 235, 0.15);
}

/* Chrome/Edge Autofill Override to prevent pale yellow */
.auth-form-panel input:-webkit-autofill,
.auth-form-panel input:-webkit-autofill:hover,
.auth-form-panel input:-webkit-autofill:focus,
.auth-form-panel input:-webkit-autofill:active,
.premium-input:-webkit-autofill,
.premium-input:-webkit-autofill:hover,
.premium-input:-webkit-autofill:focus,
.premium-input:-webkit-autofill:active {
  -webkit-text-fill-color: #071A33 !important;
  -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset !important;
  box-shadow: 0 0 0 1000px #FFFFFF inset !important;
  transition: background-color 9999s ease-out 0s;
}

.auth-form-panel .primary-button.premium-btn {
  width: 100%;
  height: 50px;
  background: #082B57;
  color: #FFFFFF;
  border: 1px solid rgba(22, 188, 235, 0.3);
  padding: 0;
  border-radius: 11px;
  font-size: 14px;
  font-weight: 700;
  margin-top: 4px;
  cursor: pointer;
  transition: all 0.2s var(--ease-out);
  box-shadow: 0 2px 6px rgba(8, 43, 87, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-form-panel .primary-button.premium-btn:hover {
  background: #0A356C;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(8, 43, 87, 0.22);
}

.field-error {
  color: #E53E3E;
  font-size: 11px;
  font-weight: 600;
  margin-top: 2px;
}

.security-note {
  font-size: 12px;
  color: var(--color-text-muted);
  text-align: center;
  margin: 4px 0 0 0;
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
    margin-bottom: 12px;
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
    f.write(APP_CSS_CLEAN)

print("Updated login template and app.css with Phase 19.6 specifications.")
