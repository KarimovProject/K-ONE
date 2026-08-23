import os

# 1. Update templates/registration/login.html
LOGIN_TEMPLATE = """{% extends "base.html" %}
{% load i18n static %}

{% block title %}K-ONE — Kirish{% endblock %}

{% block unauthenticated_content %}
<section class="auth-brand-panel" aria-hidden="true">
  <div class="auth-brand-art-wrapper">
    <img src="{% static 'img/k-one/k-one-login-hero-art.png' %}" alt="K-ONE Brand Hero" class="auth-hero-art-img">
  </div>
  <div class="sr-only">
    <h1>K-ONE — Barcha tadbirlar yagona tizimda</h1>
    <p>Xalqaro tadbirlar, zallar faoliyati va boshqaruv jarayonlarini bitta professional makonda birlashtiruvchi platforma.</p>
  </div>
</section>

<section class="auth-form-panel">
  <form class="login-card" method="post" novalidate>
    {% csrf_token %}
    <div class="login-heading">
      <div class="logo-container-mobile">
        <img src="{% static 'img/k-one/k-one-login-illuminated.png' %}" alt="K-ONE Logo" class="brand-logo-mobile">
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

# 2. Update static/css/app.css
with open('static/css/app.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

# Replace auth-brand-panel and add auth-hero-art-img
app_css = app_css.replace(""".auth-brand-panel {
  flex: 0 0 50%;
  background-color: #020F26;
  background-image: radial-gradient(circle at 40% 45%, #082859 0%, #020E24 85%);
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
  max-width: 400px;
  max-height: 380px;
  height: auto;
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 12px 32px rgba(0, 174, 239, 0.18));
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
}""", """.auth-brand-panel {
  flex: 0 0 50%;
  background: #01112D;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  color: #FFFFFF;
  overflow: hidden;
  box-sizing: border-box;
}

.auth-brand-art-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #01112D;
}

.auth-hero-art-img {
  width: 100%;
  height: 100%;
  max-width: 680px;
  max-height: 1000px;
  object-fit: contain;
  display: block;
  animation: fadeInScale 0.4s var(--ease-out);
}

@keyframes fadeInScale {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}

.logo-container-mobile {
  display: none;
}""")

with open('static/css/app.css', 'w', encoding='utf-8') as f:
    f.write(app_css)

print("Configured auth brand panel with full authentic user-uploaded artwork.")
