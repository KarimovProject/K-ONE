import os

# 1. Update templates/partials/sidebar.html
SIDEBAR_HTML = """{% load i18n static %}
<aside class="sidebar" id="primary-navigation" aria-label="{% trans 'Primary navigation' %}">
  <div class="sidebar-header">
    <a class="sidebar-brand" href="{% url 'dashboard' %}">
      <img src="{% static 'img/k-one/k-one-official-transparent.png' %}" alt="K-ONE" class="sidebar-logo">
      <span class="sidebar-slogan">{% trans "Barcha tadbirlar yagona tizimda" %}</span>
    </a>
  </div>

  <nav class="nav-list sidebar-nav">
    <span class="nav-section">{% trans "Ish maydoni" %}</span>
    <a class="nav-item sidebar-nav-item{% if nav_key == 'workspace' %} is-active active{% endif %}" href="{% url 'dashboard' %}">
      <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="dashboard" %}</span>
      <span>{% trans "Bosh sahifa" %}</span>
    </a>
    <a class="nav-item sidebar-nav-item{% if nav_key == 'events' %} is-active active{% endif %}" href="{% url 'events:list' %}">
      <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="event" %}</span>
      <span>{% trans "Tadbirlar" %}</span>
    </a>
    <a class="nav-item sidebar-nav-item{% if nav_key == 'calendar' %} is-active active{% endif %}" href="{% url 'calendar' %}">
      <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="calendar" %}</span>
      <span>{% trans "Taqvim" %}</span>
    </a>

    {% if user.is_superuser or user.role == 'super_admin' or user.role == 'management_responsible' or user.role == 'international_admin' %}
      <span class="nav-section">{% trans "Operatsiya" %}</span>
      {% if user.is_superuser or user.role == 'super_admin' or user.role == 'management_responsible' %}
        <a class="nav-item sidebar-nav-item{% if nav_key == 'approvals' %} is-active active{% endif %}" href="{% url 'events:approval-list' %}">
          <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="check" %}</span>
          <span>{% trans "Tasdiqlash" %}</span>
        </a>
      {% endif %}
      <a class="nav-item sidebar-nav-item{% if nav_key == 'displaced' %} is-active active{% endif %}" href="{% url 'events:displaced-list' %}">
        <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="move" %}</span>
        <span>{% trans "Ko'chirilganlar" %}</span>
      </a>
    {% endif %}

    {% if user.is_superuser or user.role == 'super_admin' or user.role == 'international_admin' %}
      <span class="nav-section">{% trans "Asosiy ma'lumotlar" %}</span>
      <a class="nav-item sidebar-nav-item{% if nav_key == 'venues' %} is-active active{% endif %}" href="{% url 'venues:list' %}">
        <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="venue" %}</span>
        <span>{% trans "Zallar" %}</span>
      </a>
      <a class="nav-item sidebar-nav-item{% if nav_key == 'event_types' %} is-active active{% endif %}" href="{% url 'event-types:list' %}">
        <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="tag" %}</span>
        <span>{% trans "Tadbir turlari" %}</span>
      </a>
      <a class="nav-item sidebar-nav-item{% if nav_key == 'organizations' %} is-active active{% endif %}" href="{% url 'organizations:list' %}">
        <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="organization" %}</span>
        <span>{% trans "Tashkilotlar" %}</span>
      </a>
      <a class="nav-item sidebar-nav-item{% if nav_key == 'sponsors' %} is-active active{% endif %}" href="{% url 'sponsors:list' %}">
        <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="organization" %}</span>
        <span>{% trans "Homiylar" %}</span>
      </a>
      <a class="nav-item sidebar-nav-item{% if nav_key == 'speakers' %} is-active active{% endif %}" href="{% url 'events:speaker-list' %}">
        <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="speaker" %}</span>
        <span>{% trans "Ma'ruzachilar" %}</span>
      </a>
    {% endif %}

    {% if user.is_superuser or user.role == 'super_admin' or user.role == 'content_manager' %}
      <span class="nav-section">{% trans "Aloqa" %}</span>
      <a class="nav-item sidebar-nav-item{% if nav_key == 'publications' %} is-active active{% endif %}" href="{% url 'publications:list' %}">
        <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="publication" %}</span>
        <span>{% trans "Nashrlar" %}</span>
      </a>
    {% endif %}

    <span class="nav-section">{% trans "Tahlil" %}</span>
    {% if user.is_superuser or user.role == 'super_admin' or user.role == 'international_admin' or user.role == 'leadership_viewer' or user.role == 'management_responsible' %}
      <a class="nav-item sidebar-nav-item{% if nav_key == 'leadership' %} is-active active{% endif %}" href="{% url 'leadership-dashboard' %}">
        <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="report" %}</span>
        <span>{% trans "Rahbariyat paneli" %}</span>
      </a>
    {% endif %}
    <a class="nav-item sidebar-nav-item{% if nav_key == 'reports' %} is-active active{% endif %}" href="{% url 'reporting:dashboard' %}">
      <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="report" %}</span>
      <span>{% trans "Hisobotlar" %}</span>
    </a>

    <span class="nav-section">{% trans "Personal" %}</span>
    <a class="nav-item sidebar-nav-item{% if nav_key == 'telegram' %} is-active active{% endif %}" href="{% url 'notifications:telegram-settings' %}">
      <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="send" %}</span>
      <span>Telegram</span>
    </a>
    <a class="nav-item sidebar-nav-item{% if nav_key == 'profile' %} is-active active{% endif %}" href="{% url 'profile' %}">
      <span class="nav-icon">{% include "admin/includes/iems_icon.html" with name="user" %}</span>
      <span>{% trans "Profil" %}</span>
    </a>
  </nav>

  <div class="sidebar-status sidebar-footer">
    <span class="status-dot status-breathe-dot bg-free"></span>
    <div class="sidebar-status-copy">
      <strong>{% trans "Tizim faol" %}</strong>
      <small>{% trans "Operatsion holatda" %}</small>
    </div>
  </div>
</aside>
"""

with open('templates/partials/sidebar.html', 'w', encoding='utf-8') as f:
    f.write(SIDEBAR_HTML)

# 2. Update templates/partials/topbar.html
TOPBAR_HTML = """{% load i18n account_ui %}
<header class="topbar">
  <div class="topbar-left">
    <button class="icon-button menu-button" type="button" data-sidebar-open aria-controls="primary-navigation" aria-expanded="false">
      <span aria-hidden="true">☰</span>
      <span class="sr-only">{% trans "Open navigation" %}</span>
    </button>
    <div class="topbar-context">
      <span class="eyebrow">{% trans "Xalqaro bo'lim" %}</span>
      <strong>{% trans "Boshqaruv markazi" %}</strong>
    </div>
  </div>

  <div class="topbar-actions">
    <form class="language-switch" action="{% url 'set_language' %}" method="post" aria-label="{% trans 'Language' %}">
      {% csrf_token %}
      <input name="next" type="hidden" value="{{ request.get_full_path }}">
      {% get_current_language as CURRENT_LANGUAGE %}
      {% for code, name in LANGUAGES %}
        <button name="language" value="{{ code }}" type="submit"{% if code == CURRENT_LANGUAGE %} class="is-current" aria-current="true"{% endif %}>{{ code|upper }}</button>
      {% endfor %}
    </form>

    <a class="icon-button notification-button" href="{% url 'notifications:list' %}" aria-label="{% trans 'Notifications' %}">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
    </a>

    <div class="user-block">
      <span class="avatar">{{ user.get_username|slice:':1'|upper }}</span>
      <a class="user-copy" href="{% url 'profile' %}">
        <strong>{{ user.get_full_name|default:user.get_username }}</strong>
        <small>{{ user|localized_role }}</small>
      </a>
      <form action="{% url 'logout' %}" method="post">
        {% csrf_token %}
        <button class="text-button" type="submit">{% trans "Chiqish" %}</button>
      </form>
    </div>

    {% if user.is_staff or user.is_superuser %}
      <a class="admin-link" href="{% url 'admin:index' %}">{% trans "Admin" %}</a>
    {% endif %}
    <a class="public-view-link" href="{% url 'public-dashboard' %}" target="_blank">{% trans "Ochiq tizim" %} ↗</a>
  </div>
</header>
"""

with open('templates/partials/topbar.html', 'w', encoding='utf-8') as f:
    f.write(TOPBAR_HTML)

# 3. Update templates/registration/login.html
LOGIN_HTML = """{% extends "base.html" %}
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

    {% if form.non_field_errors %}<div class="form-alert" role="alert">{{ form.non_field_errors }}</div>{% endif %}

    <div class="form-group">
      <label for="{{ form.username.id_for_label }}">Foydalanuvchi nomi</label>
      <div class="input-wrapper">
        <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        <input type="text" name="username" id="{{ form.username.id_for_label }}" class="premium-input" placeholder="Foydalanuvchi nomi" required {% if form.username.value and form.username.value != 'acceptance_admin' %}value="{{ form.username.value }}"{% endif %}>
      </div>
      {% if form.username.errors %}<div class="field-error" id="username-error">{{ form.username.errors }}</div>{% endif %}
    </div>

    <div class="form-group">
      <label for="{{ form.password.id_for_label }}">Parol</label>
      <div class="input-wrapper">
        <svg class="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
        <input type="password" name="password" id="{{ form.password.id_for_label }}" class="premium-input" placeholder="Parol" required>
      </div>
      {% if form.password.errors %}<div class="field-error" id="password-error">{{ form.password.errors }}</div>{% endif %}
    </div>

    {% if next %}<input type="hidden" name="next" value="{{ next }}">{% endif %}

    <button class="primary-button premium-btn" type="submit">Kirish</button>

    <p class="security-note"><span aria-hidden="true">●</span> Tizimga kirish faqat ruxsat etilgan xodimlar uchun.</p>
  </form>
</section>
{% endblock %}
"""

with open('templates/registration/login.html', 'w', encoding='utf-8') as f:
    f.write(LOGIN_HTML)

# 4. Update templates/workspace/home.html
WORKSPACE_HOME_HTML = """{% extends "base.html" %}
{% load i18n %}

{% block title %}{% trans "Ish maydoni" %} · K-ONE{% endblock %}

{% block content %}
<div class="workspace-page animate-entrance">
  <!-- COMPACT HERO HEADER -->
  <section class="workspace-hero">
    <div class="workspace-hero__copy">
      <div class="workspace-hero__badge-row">
        <span class="role-badge">{{ user.get_role_display|default:_("Mas'ul xodim") }}</span>
        <span class="workspace-date-pill">{% now "d-F, Y" %}</span>
      </div>
      <h1>{% trans "Salom" %}, {{ user.first_name|default:user.username }}</h1>
      <p>{% trans "Bugungi xalqaro tadbirlar dasturi va tezkor boshqaruv amallari." %}</p>
    </div>
    <div class="workspace-hero__actions">
      <a class="primary-button compact-hero-btn" href="{% url 'events:wizard' %}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        <span>{% trans "+ Yangi tadbir" %}</span>
      </a>
    </div>
  </section>

  <!-- 4 COMPACT KPI TILES -->
  <section class="workspace-metrics" aria-label="{% trans 'Key indicators' %}">
    <article class="metric-tile metric-tile--cobalt">
      <div class="metric-tile__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
      </div>
      <div class="metric-tile__content">
        <span class="metric-tile__label">{% trans "Yaqin tadbirlar" %}</span>
        <strong class="metric-tile__value">{{ upcoming_count|default:"0" }}</strong>
      </div>
    </article>

    <article class="metric-tile metric-tile--coral">
      <div class="metric-tile__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      </div>
      <div class="metric-tile__content">
        <span class="metric-tile__label">{% trans "Harakat talab etiladi" %}</span>
        <strong class="metric-tile__value text-critical">{{ needs_action_count|default:"0" }}</strong>
      </div>
    </article>

    <article class="metric-tile metric-tile--amber">
      <div class="metric-tile__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
      </div>
      <div class="metric-tile__content">
        <span class="metric-tile__label">{% trans "Tasdiq kutilmoqda" %}</span>
        <strong class="metric-tile__value text-warning">{{ pending_approval_count|default:content_pending_count|default:checkin_today_count|default:"0" }}</strong>
      </div>
    </article>

    <article class="metric-tile metric-tile--cyan">
      <div class="metric-tile__icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
      </div>
      <div class="metric-tile__content">
        <span class="metric-tile__label">{% trans "Yangi xabarlar" %}</span>
        <strong class="metric-tile__value">{{ notification_count|default:"0" }}</strong>
      </div>
    </article>
  </section>

  <!-- TWO-COLUMN WORKSPACE GRID -->
  <div class="workspace-grid">
    <!-- LEFT: AGENDA / UPCOMING EVENTS -->
    <section class="workspace-panel workspace-panel--agenda">
      <header class="panel-header">
        <div>
          <span class="panel-eyebrow">{% trans "Operatsion oqim" %}</span>
          <h2 class="panel-title">{% trans "Yaqinlashayotgan tadbirlar" %}</h2>
        </div>
        <a class="panel-action-link" href="{% url 'events:list' %}">
          <span>{% trans "Barchasi" %}</span>
          <span>→</span>
        </a>
      </header>

      <div class="workspace-event-list">
        {% for event in upcoming %}
          <a class="workspace-event-row" href="{% url 'events:detail' event.pk %}">
            <div class="event-row-time">
              <span class="date">{{ event.planned_date|date:"d M" }}</span>
              <span class="time">{{ event.start_time|time:"H:i" }}</span>
            </div>
            <div class="event-row-info">
              <strong class="title">{{ event.title }}</strong>
              <div class="meta">
                <span class="venue">{{ event.venue.localized_name }}</span>
                <span class="status-badge status-{{ event.status|lower }}">{{ event.get_status_display }}</span>
              </div>
            </div>
            <span class="event-row-arrow">→</span>
          </a>
        {% empty %}
          <div class="empty-state-card">
            <h3>{% trans "Sizning jadvalingiz bo'sh" %}</h3>
            <p>{% trans "Sizga biriktirilgan va yaqinlashayotgan tadbirlar bu yerda avtomatik aks etadi." %}</p>
          </div>
        {% endfor %}
      </div>
    </section>

    <!-- RIGHT: QUICK ACTIONS -->
    <aside class="workspace-panel workspace-panel--actions">
      <header class="panel-header">
        <div>
          <span class="panel-eyebrow">{% trans "Boshqaruv" %}</span>
          <h2 class="panel-title">{% trans "Tezkor amallar" %}</h2>
        </div>
      </header>

      <div class="workspace-quick-actions">
        <a class="quick-action-item" href="{% url 'calendar' %}">
          <div class="quick-action-icon cobalt">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          </div>
          <div class="quick-action-text">
            <strong>{% trans "Ichki operatsion taqvim" %}</strong>
            <small>{% trans "Barcha rejalashtirilgan dasturlar" %}</small>
          </div>
          <span class="arrow">→</span>
        </a>

        <a class="quick-action-item" href="{% url 'notifications:telegram-settings' %}">
          <div class="quick-action-icon cyan">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </div>
          <div class="quick-action-text">
            <strong>{% trans "Telegram bildirishnomalari" %}</strong>
            <small>{% trans "Tezkor xabar va eslatmalar" %}</small>
          </div>
          <span class="arrow">→</span>
        </a>

        <a class="quick-action-item" href="{% url 'profile' %}">
          <div class="quick-action-icon emerald">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <div class="quick-action-text">
            <strong>{% trans "Profil va sozlamalar" %}</strong>
            <small>{% trans "Shaxsiy ma'lumotlar va til" %}</small>
          </div>
          <span class="arrow">→</span>
        </a>

        <a class="quick-action-item" href="{% url 'public-dashboard' %}" target="_blank">
          <div class="quick-action-icon violet">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
          </div>
          <div class="quick-action-text">
            <strong>{% trans "Ochiq jonli markaz" %}</strong>
            <small>{% trans "Tashqi monitoring ekrani" %}</small>
          </div>
          <span class="arrow">↗</span>
        </a>
      </div>
    </aside>
  </div>
</div>
{% endblock %}
"""

with open('templates/workspace/home.html', 'w', encoding='utf-8') as f:
    f.write(WORKSPACE_HOME_HTML)

print("Updated sidebar, topbar, login, and workspace home templates.")
