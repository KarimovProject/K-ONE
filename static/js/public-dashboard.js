/**
 * IEMS Public Dashboard - Phase 18
 */
(() => {
    'use strict';
  
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
  
    const dashboard = $('[data-dashboard]');
    if (!dashboard) return;
  
    const API_URL = dashboard.dataset.endpoint;
    const locale = { uz: 'uz-UZ', ru: 'ru-RU', en: 'en-GB' }[document.documentElement.lang] || 'uz-UZ';
    const language = document.documentElement.lang || 'uz';
  
    const cal = {
      uz: { monthsShort: ['YAN','FEV','MAR','APR','MAY','IYUN','IYUL','AVG','SEN','OKT','NOY','DEK'], weekdays: ['YAKSHANBA','DUSHANBA','SESHANBA','CHORSHANBA','PAYSHANBA','JUMA','SHANBA'] },
      ru: { monthsShort: ['ЯНВ','ФЕВ','МАР','АПР','МАЙ','ИЮН','ИЮЛ','АВГ','СЕН','ОКТ','НОЯ','ДЕК'], weekdays: ['ВОСКРЕСЕНЬЕ','ПОНЕДЕЛЬНИК','ВТОРНИК','СРЕДА','ЧЕТВЕРГ','ПЯТНИЦА','СУББОТА'] },
      en: { monthsShort: ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'], weekdays: ['SUNDAY','MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY'] }
    }[language] || { monthsShort: ['YAN','FEV','MAR','APR','MAY','IYUN','IYUL','AVG','SEN','OKT','NOY','DEK'], weekdays: ['YAKSHANBA','DUSHANBA','SESHANBA','CHORSHANBA','PAYSHANBA','JUMA','SHANBA'] };
  
    // =========================================================================
    // 1. LIVE CLOCK
    // =========================================================================
    const clockEl = $('[data-clock]');
    const clockWeekdayEl = $('[data-clock-weekday]');
  
    const tickClock = () => {
      const now = new Date();
      if (clockEl) {
        clockEl.textContent = new Intl.DateTimeFormat(locale, {
          timeZone: 'Asia/Tashkent', hour: '2-digit', minute: '2-digit', hour12: false
        }).format(now);
      }
      if (clockWeekdayEl) {
        const d = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Tashkent' }));
        clockWeekdayEl.textContent = `${d.getDate()} ${cal.monthsShort[d.getMonth()]} · ${cal.weekdays[d.getDay()]}`;
      }
    };
    tickClock();
    setInterval(tickClock, 1000);
  
    // =========================================================================
    // 2. NEXT EVENT COUNTDOWN
    // =========================================================================
    const countdownEl = $('[data-countdown]');
    const updateCountdown = () => {
      if (!countdownEl) return;
      const target = countdownEl.dataset.nextStart;
      if (!target) return;
      const targetDate = new Date(target);
      const now = new Date();
      const diff = Math.max(0, targetDate - now);
      
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      
      const hEl = $('[data-countdown-h]', countdownEl);
      const mEl = $('[data-countdown-m]', countdownEl);
      const sEl = $('[data-countdown-s]', countdownEl);
      
      if (hEl) hEl.textContent = String(h).padStart(2, '0');
      if (mEl) mEl.textContent = String(m).padStart(2, '0');
      if (sEl) sEl.textContent = String(s).padStart(2, '0');
    };
    updateCountdown();
    setInterval(updateCountdown, 1000);
  
    // =========================================================================
    // 3. KPI COUNT-UP ANIMATION
    // =========================================================================
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animateNumber = (el, target) => {
      const start = Number(el.textContent) || 0;
      if (reducedMotion || start === target) { el.textContent = String(target).padStart(2, '0'); return; }
      const t0 = performance.now();
      const duration = 800;
      const step = now => {
        const p = Math.min(1, (now - t0) / duration);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = String(Math.round(start + (target - start) * eased)).padStart(2, '0');
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
  
    // =========================================================================
    // 4. TIMELINE RENDERING
    // =========================================================================
    const nowMarker = $('[data-now-marker]');
    const tracksContainer = $('[data-timeline-tracks]');
    const startH = 8;
    const endH = 18;
    const totalMinutes = (endH - startH) * 60;
  
    const timeToPercent = (dateStr) => {
        if (!dateStr) return 0;
        const d = new Date(dateStr);
        const h = d.getHours();
        const m = d.getMinutes();
        const minutesFromStart = ((h - startH) * 60) + m;
        let pct = (minutesFromStart / totalMinutes) * 100;
        return Math.max(0, Math.min(100, pct));
    };
  
    const updateTimelineMarker = () => {
        if (!nowMarker) return;
        const now = new Date();
        const pct = timeToPercent(now.toISOString());
        nowMarker.style.left = `${pct}%`;
    };
    
    const renderTimeline = (events) => {
        if (!tracksContainer) return;
        tracksContainer.innerHTML = '';
        
        let stagger = 1;
        events.forEach((ev, index) => {
            const startPct = timeToPercent(ev.start);
            const endPct = timeToPercent(ev.end);
            let widthPct = Math.max(5, endPct - startPct);
            
            const isLive = ev.status === 'in_progress';
            const laneIndex = index % 5;
            const topOffset = laneIndex * 60;
            
            const block = document.createElement('div');
            block.className = `timeline-event animate-stagger-${stagger} animate-entrance ${isLive ? 'timeline-event--active' : 'timeline-event--upcoming'}`;
            block.style.left = `${startPct}%`;
            block.style.width = `${widthPct}%`;
            block.style.top = `${topOffset}px`;
            
            block.innerHTML = `
                <div class="timeline-event__meta">${ev.venue_code}</div>
                <div class="timeline-event__title">${ev.title}</div>
            `;
            
            tracksContainer.appendChild(block);
            if (stagger < 5) stagger++;
        });
        
        const maxLanes = Math.min(events.length, 5);
        tracksContainer.style.minHeight = `${maxLanes * 60 + 20}px`;
    };
  
    updateTimelineMarker();
    setInterval(updateTimelineMarker, 60000);
  
    // =========================================================================
    // 5. DATA POLLING & BINDING
    // =========================================================================
    const refresh = async () => {
      if (!API_URL) return;
      try {
        const res = await fetch(API_URL, { headers: { Accept: 'application/json' } });
        if (!res.ok) return;
        const data = await res.json();
  
        if (data.metrics) {
          for (const [key, value] of Object.entries(data.metrics)) {
            const el = $(`[data-metric="${key}"]`);
            if (el) animateNumber(el, value);
          }
        }
  
        if (data.today_events) {
            renderTimeline(data.today_events);
        }
        
      } catch (err) {
        console.warn('Dashboard poll error:', err);
      }
    };
    setInterval(refresh, 30000);
    refresh();
  
  })();
