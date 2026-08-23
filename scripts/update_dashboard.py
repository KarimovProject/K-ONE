import os

DASHBOARD_HTML = """{% extends "public/base.html" %}
{% load i18n static %}

{% block title %}K-ONE — Operatsion Markaz{% endblock %}

{% block content %}
<div class="dashboard-shell">
  <!-- TOP KPI COMMAND RAIL -->
  <section class="kpi-rail">
    <div class="kpi-card premium-card">
      <div class="kpi-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
      </div>
      <div class="kpi-content">
        <span class="kpi-label">BUGUN</span>
        <span class="kpi-value">{{ today_total|default:"0" }} <span class="kpi-unit">Tadbir</span></span>
      </div>
    </div>

    <div class="kpi-card premium-card kpi-live">
      <div class="kpi-icon icon-active">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
      </div>
      <div class="kpi-content">
        <span class="kpi-label">JONLI HOZIR</span>
        <div class="kpi-value-group">
          <span class="pulse-dot"></span>
          <span class="kpi-value">{{ live_count|default:"0" }} <span class="kpi-unit">Davom etmoqda</span></span>
        </div>
      </div>
    </div>

    <div class="kpi-card premium-card kpi-free">
      <div class="kpi-icon icon-free">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
      </div>
      <div class="kpi-content">
        <span class="kpi-label">ERKIN ZALLAR</span>
        <span class="kpi-value">{{ free_venues|default:"4" }} <span class="kpi-unit">Jami zallardan</span></span>
      </div>
    </div>

    <div class="kpi-card premium-card">
      <div class="kpi-icon icon-upcoming">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
      </div>
      <div class="kpi-content">
        <span class="kpi-label">KEYINGI TADBIR</span>
        <span class="kpi-value kpi-time">
          {% if next_event %}
            {{ next_event.start_time|date:"H:i" }} <span class="kpi-unit">{{ next_event.venue.code|default:"AUD" }}</span>
          {% else %}
            --:-- <span class="kpi-unit">Yo'q</span>
          {% endif %}
        </span>
      </div>
    </div>
  </section>

  <!-- MAIN CANVAS -->
  <div class="dashboard-canvas">
    <!-- LEFT: TIMELINE -->
    <section class="timeline-panel premium-panel">
      <header class="panel-header">
        <h2>XRONOLOGIK OQIM</h2>
        <span class="subtitle">08:00 — 18:00</span>
      </header>
      <div class="timeline-container">
        <!-- Time grid background -->
        <div class="timeline-scale">
          <div class="timeline-hour"><span>08:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>09:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>10:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>11:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>12:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>13:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>14:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>15:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>16:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>17:00</span><div class="grid-line"></div></div>
          <div class="timeline-hour"><span>18:00</span><div class="grid-line"></div></div>
        </div>

        <!-- Current time marker -->
        <div class="current-time-marker" style="left: 45%;">
          <div class="marker-line"></div>
          <span class="marker-badge">NOW</span>
        </div>

        <!-- Event tracks -->
        <div class="timeline-tracks">
          <!-- Placeholder event capsule 1 -->
          <div class="event-capsule status-active" style="left: 20%; width: 25%; top: 10px;">
            <div class="event-capsule-content">
              <span class="event-title">Xalqaro Simpozium</span>
              <span class="event-meta">10:00-12:30 • AUD1</span>
            </div>
          </div>
          <!-- Placeholder event capsule 2 -->
          <div class="event-capsule status-upcoming" style="left: 55%; width: 15%; top: 60px;">
            <div class="event-capsule-content">
              <span class="event-title">Vazirlik uchrashuvi</span>
              <span class="event-meta">13:30-15:00 • AUD3</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- RIGHT: VENUE ACTIVITY -->
    <section class="venues-panel premium-panel">
      <header class="panel-header">
        <h2>ZALLAR FAOLLIGI</h2>
      </header>
      <div class="venue-activity-list">
        {% for v in venues %}
          <div class="venue-activity-item">
            <div class="venue-status-dot {% if v.status == 'OCCUPIED' %}pulse-dot bg-active{% elif v.status == 'UPCOMING' %}bg-upcoming{% else %}bg-free{% endif %}"></div>
            <div class="venue-info">
              <div class="venue-code-row">
                <span class="venue-code">{{ v.code }}</span>
                {% if v.status == 'OCCUPIED' %}
                  <span class="badge badge-active">FAOL</span>
                {% elif v.status == 'UPCOMING' %}
                  <span class="badge badge-upcoming">KUTILMOQDA</span>
                {% else %}
                  <span class="badge badge-free">ERKIN</span>
                {% endif %}
              </div>
              <div class="venue-name">{{ v.localized_name|default:"Xalqaro konferensiyalar zali" }}</div>
              {% if v.status == 'OCCUPIED' %}
                <div class="venue-next-event">14:00-16:00 • Plenar sessiya</div>
              {% endif %}
            </div>
          </div>
        {% empty %}
          <!-- Static Placeholders for QA / Design phase -->
          <div class="venue-activity-item">
            <div class="venue-status-dot bg-free"></div>
            <div class="venue-info">
              <div class="venue-code-row">
                <span class="venue-code">AUD1</span>
                <span class="badge badge-free">ERKIN</span>
              </div>
              <div class="venue-name">Xalqaro konferensiyalar zali</div>
            </div>
          </div>

          <div class="venue-activity-item">
            <div class="venue-status-dot pulse-dot bg-active"></div>
            <div class="venue-info">
              <div class="venue-code-row">
                <span class="venue-code">AUD2</span>
                <span class="badge badge-active">FAOL</span>
              </div>
              <div class="venue-name">Kichik majlislar zali</div>
              <div class="venue-next-event">09:00-11:00 • Investitsiya forumi</div>
            </div>
          </div>
        {% endfor %}
      </div>
    </section>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/public-dashboard.js' %}"></script>
{% endblock %}
"""

with open('templates/public/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(DASHBOARD_HTML)
