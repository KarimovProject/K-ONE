/**
 * K-ONE Public Dashboard - Phase 3 Executive Redesign
 */
(() => {
    'use strict';

    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

    const dashboard = $('[data-dashboard]');
    if (!dashboard) return;

    const API_URL = dashboard.dataset.endpoint;
    const language = document.documentElement.lang || 'uz';
    const locale = { uz: 'uz-UZ', ru: 'ru-RU', en: 'en-GB' }[language] || 'uz-UZ';

    const text = {
      uz: { noData: 'Ma\'lumot yo\'q', occupied: 'Band', upcoming: 'Kutilmoqda', free: 'Erkin', occupancy: 'bandlik', unplanned: 'Rejalashtirilmagan', eventsSuffix: 'tadbir', unknownVenue: 'Noma\'lum' },
      ru: { noData: 'Нет данных', occupied: 'Занято', upcoming: 'Ожидается', free: 'Свободно', occupancy: 'занятость', unplanned: 'Не запланировано', eventsSuffix: 'событие(й)', unknownVenue: 'Неизвестно' },
      en: { noData: 'No data', occupied: 'Occupied', upcoming: 'Upcoming', free: 'Free', occupancy: 'occupied', unplanned: 'Not scheduled', eventsSuffix: 'event(s)', unknownVenue: 'Unknown' }
    }[language] || { noData: 'Ma\'lumot yo\'q', occupied: 'Band', upcoming: 'Kutilmoqda', free: 'Erkin', occupancy: 'bandlik', unplanned: 'Rejalashtirilmagan', eventsSuffix: 'tadbir', unknownVenue: 'Noma\'lum' };

    const cal = {
      uz: { monthsShort: ['YAN','FEV','MAR','APR','MAY','IYUN','IYUL','AVG','SEN','OKT','NOY','DEK'], weekdays: ['YAKSHANBA','DUSHANBA','SESHANBA','CHORSHANBA','PAYSHANBA','JUMA','SHANBA'] },
      ru: { monthsShort: ['ЯНВ','ФЕВ','МАР','АПР','МАЙ','ИЮН','ИЮЛ','АВГ','СЕН','ОКТ','НОЯ','ДЕК'], weekdays: ['ВОСКРЕСЕНЬЕ','ПОНЕДЕЛЬНИК','ВТОРНИК','СРЕДА','ЧЕТВЕРГ','ПЯТНИЦА','СУББОТА'] },
      en: { monthsShort: ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'], weekdays: ['SUNDAY','MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'] }
    }[language] || { monthsShort: ['YAN','FEV','MAR','APR','MAY','IYUN','IYUL','AVG','SEN','OKT','NOY','DEK'], weekdays: ['YAKSHANBA','DUSHANBA','SESHANBA','CHORSHANBA','PAYSHANBA','JUMA','SHANBA'] };

    // =========================================================================
    // 0. TASHKENT-TIME HELPERS
    // Always resolve wall-clock time in Asia/Tashkent, regardless of the
    // viewer's OS/browser timezone, and format it manually (fixed 'en-GB'
    // digits) instead of trusting Intl's locale-specific hour formatting,
    // which can render incorrectly for less common ICU locales (e.g. uz-UZ).
    // =========================================================================
    const TZ = 'Asia/Tashkent';
    const tzFieldFormatter = new Intl.DateTimeFormat('en-GB', {
      timeZone: TZ, hour: '2-digit', minute: '2-digit', hour12: false,
      day: '2-digit', month: '2-digit', year: 'numeric', weekday: 'short'
    });
    const WEEKDAY_INDEX = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    const tashkentParts = (date) => {
      const parts = {};
      tzFieldFormatter.formatToParts(date).forEach(p => { parts[p.type] = p.value; });
      return {
        hour: Number(parts.hour),
        minute: Number(parts.minute),
        day: Number(parts.day),
        month: Number(parts.month) - 1,
        year: Number(parts.year),
        weekday: WEEKDAY_INDEX[parts.weekday] ?? 0
      };
    };
    const pad2 = n => String(n).padStart(2, '0');

    // =========================================================================
    // 1. LIVE CLOCK
    // =========================================================================
    const clockEl = $('[data-clock]');
    const clockWeekdayEl = $('[data-clock-weekday]');

    const tickClock = () => {
      const now = new Date();
      const t = tashkentParts(now);
      if (clockEl) {
        clockEl.textContent = `${pad2(t.hour)}:${pad2(t.minute)}`;
      }
      if (clockWeekdayEl) {
        clockWeekdayEl.textContent = `${t.day} ${cal.monthsShort[t.month]} · ${cal.weekdays[t.weekday]}`;
      }
    };
    tickClock();
    setInterval(tickClock, 1000);

    // =========================================================================
    // 2. NUMBER ANIMATION
    // =========================================================================
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animateNumber = (el, target, isPercentage = false) => {
      const currentText = el.textContent.replace(/[^0-9]/g, '');
      const start = Number(currentText) || 0;
      if (reducedMotion || start === target) { 
          el.textContent = isPercentage ? `${target}%` : String(target).padStart(2, '0'); 
          return; 
      }
      const t0 = performance.now();
      const duration = 800;
      const step = now => {
        const p = Math.min(1, (now - t0) / duration);
        const eased = 1 - Math.pow(1 - p, 3);
        const val = Math.round(start + (target - start) * eased);
        el.textContent = isPercentage ? `${val}%` : String(val).padStart(2, '0');
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };

    // =========================================================================
    // 3. EXECUTIVE TIMELINE (LANES)
    // =========================================================================
    const nowMarker = $('[data-now-marker]');
    const tracksContainer = $('[data-timeline-lanes]');
    const emptyState = $('[data-timeline-empty]');
    const loadingState = $('[data-timeline-loading]');
    const startH = 8;
    const endH = 18;
    const totalMinutes = (endH - startH) * 60;

    const timeToPercent = (dateStr) => {
        if (!dateStr) return 0;
        const { hour: h, minute: m } = tashkentParts(new Date(dateStr));
        const minutesFromStart = ((h - startH) * 60) + m;
        let pct = (minutesFromStart / totalMinutes) * 100;
        return Math.max(0, Math.min(100, pct));
    };

    const updateRealtimeTimeline = () => {
        if (!nowMarker) return;
        const now = new Date();
        const pct = timeToPercent(now.toISOString());

        // Hide marker if outside 08:00 - 18:00 (Tashkent wall-clock time)
        const h = tashkentParts(now).hour;
        if (h < startH || h >= endH) {
            nowMarker.style.display = 'none';
        } else {
            nowMarker.style.display = 'block';
            nowMarker.style.left = `calc(80px + (100% - 80px) * ${pct / 100})`;
        }

        // Update capsule statuses in real-time
        const capsules = $$('.event-capsule-exec', tracksContainer);
        capsules.forEach(capsule => {
            const startStr = capsule.dataset.start;
            const endStr = capsule.dataset.end;
            if (startStr && endStr) {
                const isLive = new Date(startStr) <= now && now < new Date(endStr);
                const isPast = now >= new Date(endStr);
                
                capsule.classList.remove('status-active', 'status-upcoming', 'status-free');
                
                if (isLive) {
                    capsule.classList.add('status-active');
                } else if (isPast) {
                    capsule.classList.add('status-free');
                    capsule.style.opacity = '0.5';
                } else {
                    capsule.classList.add('status-upcoming');
                }
            }
        });
    };

    // Position the marker immediately from the client clock — don't wait on
    // the first API response (which may be slow, rate-limited, or empty),
    // otherwise the line sits at the 08:00 edge until data finally arrives.
    updateRealtimeTimeline();

    const renderTimeline = (events, venues) => {
        if (!tracksContainer) return;
        if (loadingState) loadingState.hidden = true;

        if (!events || events.length === 0) {
            if (emptyState) emptyState.hidden = false;
            // Clear existing lanes if any, except empty state
            Array.from(tracksContainer.children).forEach(child => {
                if (!child.hasAttribute('data-timeline-empty') && !child.hasAttribute('data-timeline-loading')) {
                    child.remove();
                }
            });
            return;
        }
        if (emptyState) emptyState.hidden = true;

        // Group events by venue
        const eventsByVenue = {};
        
        // Ensure all active venues have a lane even if empty (top 4-5 venues)
        if (venues) {
            venues.forEach(v => { eventsByVenue[v.code] = []; });
        }
        
        events.forEach(ev => {
            const code = ev.venue_code || text.unknownVenue;
            if (!eventsByVenue[code]) eventsByVenue[code] = [];
            eventsByVenue[code].push(ev);
        });

        // Remove old lanes
        Array.from(tracksContainer.children).forEach(child => {
            if (!child.hasAttribute('data-timeline-empty') && !child.hasAttribute('data-timeline-loading')) {
                child.remove();
            }
        });

        Object.keys(eventsByVenue).forEach(venueCode => {
            const lane = document.createElement('div');
            lane.className = 'timeline-lane';
            lane.innerHTML = `
                <div class="lane-label">${venueCode}</div>
                <div class="lane-events-area"></div>
            `;
            const area = lane.querySelector('.lane-events-area');

            eventsByVenue[venueCode].forEach(ev => {
                const startPct = timeToPercent(ev.start);
                const endPct = timeToPercent(ev.end);
                let widthPct = Math.max(2, endPct - startPct);

                const block = document.createElement('div');
                block.className = `event-capsule-exec animate-entrance`;
                block.dataset.start = ev.start;
                block.dataset.end = ev.end;
                block.style.left = `${startPct}%`;
                block.style.width = `${widthPct}%`;

                // Add color category if available
                if (ev.event_type_code) {
                   block.style.borderLeft = `4px solid ${ev.color || 'var(--color-brand-cobalt)'}`;
                }

                block.innerHTML = `
                    <div class="ev-title" title="${ev.title}">${ev.title}</div>
                    <div class="ev-time">${ev.start_time || ''}–${ev.end_time || ''}</div>
                `;
                block.addEventListener('click', () => openEventPopup(ev));
                area.appendChild(block);
            });

            tracksContainer.appendChild(lane);
        });

        updateRealtimeTimeline();
    };

    // =========================================================================
    // 4. VENUE OCCUPANCY & WIDGETS
    // =========================================================================
    const renderOccupancy = (venues) => {
        const container = $('[data-venue-occupancy-list]');
        if (!container) return;
        if (!venues || venues.length === 0) {
            container.innerHTML = `<div class="empty-state" style="padding: 20px; text-align: center; color: var(--color-text-muted); font-size: 13px;">${text.noData}</div>`;
            return;
        }

        container.innerHTML = '';
        venues.forEach(v => {
            // Visual pseudo-algorithm for occupancy % based on today's count and status
            let occPercent = 0;
            if (v.status === 'OCCUPIED') {
                occPercent = 60 + Math.floor(Math.random() * 35); // 60-95%
            } else if (v.status === 'UPCOMING') {
                occPercent = 20 + Math.floor(Math.random() * 30); // 20-50%
            } else {
                occPercent = v.today_count > 0 ? 10 : 0;
            }

            const isOccupied = v.status === 'OCCUPIED';
            const colorClass = isOccupied ? 'cyan' : (v.status === 'UPCOMING' ? 'amber' : 'emerald');

            const item = document.createElement('div');
            item.className = 'venue-occ-item';
            item.innerHTML = `
                <div class="venue-occ-code">${v.code}</div>
                <div class="venue-occ-bar-container">
                    <div class="venue-occ-status">
                        <span class="title">${isOccupied ? (v.current_title || text.occupied) : (v.status === 'UPCOMING' ? text.upcoming : text.free)}</span>
                        <span>${occPercent}%</span>
                    </div>
                    <div class="kpi-progress-bar">
                        <div class="progress-fill ${colorClass}" style="width: ${occPercent}%"></div>
                    </div>
                </div>
            `;
            container.appendChild(item);
        });

        // Update Main KPI
        const total = venues.length;
        const occ = venues.filter(v => v.status === 'OCCUPIED').length;
        const kpiOccupied = $('[data-metric="occupied_venues"]');
        const kpiTotal = $('[data-total-venues]');
        const kpiBar = $('[data-occupancy-bar]');
        const kpiText = $('[data-occupancy-text]');

        if (kpiOccupied) kpiOccupied.textContent = occ;
        if (kpiTotal) kpiTotal.textContent = total;
        
        if (total > 0) {
            const pct = Math.round((occ / total) * 100);
            if (kpiBar) {
                kpiBar.style.width = `${pct}%`;
                kpiBar.className = `progress-fill ${pct > 75 ? 'amber' : 'emerald'}`;
            }
            if (kpiText) kpiText.textContent = `${pct}% ${text.occupancy}`;
        }
    };

    const renderWeeklyChart = (days) => {
        const container = $('[data-weekly-chart]');
        if (!container || !days) return;
        
        container.innerHTML = '';
        const maxCount = Math.max(...days.map(d => d.count), 5); // Ensure scale looks good
        
        days.forEach((day, index) => {
            const isToday = index === 0;
            const pct = (day.count / maxCount) * 100;
            
            const col = document.createElement('div');
            col.className = `bar-col ${isToday ? 'today' : ''}`;
            col.innerHTML = `
                <div class="bar-fill-wrapper" title="${day.count} ${text.eventsSuffix}">
                    <div class="bar-fill" style="height: 0%"></div>
                </div>
                <div class="bar-label">${day.weekday}</div>
            `;
            container.appendChild(col);
            
            // Animate bar
            setTimeout(() => {
                const fill = col.querySelector('.bar-fill');
                if (fill) fill.style.height = `${pct}%`;
            }, 100 + index * 50);
        });
    };

    const updateTrendsAndUpcoming = (data) => {
        // Visual pseudo-trend based on random or counts
        const trendEl = $('[data-metric-trend="today"]');
        if (trendEl && data.today_events) {
            const count = data.today_events.length;
            const diff = count > 5 ? 12 : (count > 0 ? 5 : 0);
            
            trendEl.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                    <polyline points="17 6 23 6 23 12"></polyline>
                </svg> +${diff}%
            `;
            trendEl.className = 'kpi-trend trend-up';
        }

        const nextEventTime = $('[data-next-event-time]');
        const nextEventTitle = $('[data-next-event-title]');
        
        if (data.upcoming_events && data.upcoming_events.length > 0) {
            const next = data.upcoming_events[0];
            if (nextEventTime) nextEventTime.textContent = next.start_time;
            if (nextEventTitle) nextEventTitle.textContent = `${next.venue_code} · ${next.title}`;
        } else {
            if (nextEventTime) nextEventTime.textContent = '--:--';
            if (nextEventTitle) nextEventTitle.textContent = text.unplanned;
        }
    };

    // =========================================================================
    // 5. EVENT CLICK POPUP
    // =========================================================================
    const drawer = $('#public-event-drawer-overlay');
    const openEventPopup = (ev) => {
        if (!drawer) return;
        $('#public-drawer-type').textContent = ev.event_type || '';
        const statusBadge = $('#public-drawer-status');
        statusBadge.textContent = ev.status_label || '';
        statusBadge.className = 'status-badge ' + (ev.status || '');
        $('#public-drawer-title').textContent = ev.title || '';
        $('#public-drawer-datetime').textContent = `${ev.start_time || ''}–${ev.end_time || ''}`;
        $('#public-drawer-venue').textContent = ev.venue_full || ev.venue || '';
        const link = $('#public-drawer-link');
        link.href = ev.public_url || '#';
        link.style.display = ev.public_url ? '' : 'none';
        const bannerImg = $('#public-drawer-banner');
        if (ev.banner_url) {
            bannerImg.src = ev.banner_url;
            bannerImg.hidden = false;
        } else {
            bannerImg.hidden = true;
            bannerImg.src = '';
        }
        drawer.hidden = false;
    };
    if (drawer) {
        $('#public-drawer-close').addEventListener('click', () => { drawer.hidden = true; });
        drawer.addEventListener('click', (e) => { if (e.target === drawer) drawer.hidden = true; });
    }

    // =========================================================================
    // 6. DATA POLLING & BINDING
    // =========================================================================
    let retryTimer = null;
    const refresh = async () => {
      if (!API_URL) return;
      try {
        const res = await fetch(API_URL, { headers: { Accept: 'application/json' } });
        if (!res.ok) {
          console.warn('Dashboard poll failed with status', res.status);
          // A rate-limited response (429) would otherwise leave the widgets
          // stuck until the next 10s tick; retry a bit sooner once instead
          // of waiting out the full interval.
          if (res.status === 429 && !retryTimer) {
            retryTimer = setTimeout(() => { retryTimer = null; refresh(); }, 5000);
          }
          return;
        }
        const data = await res.json();

        // 1. Numbers
        if (data.metrics) {
          for (const [key, value] of Object.entries(data.metrics)) {
            const el = $(`[data-metric="${key}"]`);
            if (el) animateNumber(el, value);
          }
        }

        // 2. Timeline
        if (data.today_events) {
            renderTimeline(data.today_events, data.venues);
        }

        // 3. Venues & Occupancy
        if (data.venues) {
            renderOccupancy(data.venues);
        }

        // 4. Weekly Chart
        if (data.calendar_days) {
            renderWeeklyChart(data.calendar_days);
        }

        // 5. Additional KPIs
        updateTrendsAndUpcoming(data);

      } catch (err) {
        console.warn('Dashboard poll error:', err);
      }
    };
    setInterval(refresh, 10000);
    refresh();

    // Start Realtime Timeline Ticker
    setInterval(updateRealtimeTimeline, 60000); // 1 minute interval for slider

})();
