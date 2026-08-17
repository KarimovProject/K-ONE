/**
 * IEMS Public Calendar - Phase 18.1 Restored API Engine
 */
(() => {
    'use strict';
  
    const root = document.querySelector("[data-calendar]");
    if (!root) return;
  
    const stage = root.querySelector("[data-calendar-stage]");
    const title = root.querySelector("[data-calendar-title]");
    const chips = root.querySelector("[data-filter-chips]");
    const drawer = document.querySelector("[data-event-dialog]");
    let previousFocus = null;
  
    let events = [];
    let cursor = new Date();
    let view = new URLSearchParams(location.search).get("view") || "month";
    let direction = "forward";
  
    const text = {
      uz: {
        months: ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"],
        days: ["Dush","Sesh","Chor","Pay","Jum","Shan","Yak"],
        today: "Bugun", tomorrow: "Erta", now: "Hozir",
        empty: "Tadbirlar topilmadi", more: "yana", retry: "Xatolik yuz berdi", again: "Qayta urinish"
      }
    }[document.documentElement.lang] || {
        months: ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"],
        days: ["Dush","Sesh","Chor","Pay","Jum","Shan","Yak"],
        today: "Bugun", tomorrow: "Erta", now: "Hozir",
        empty: "Tadbirlar topilmadi", more: "yana", retry: "Xatolik yuz berdi", again: "Qayta urinish"
    };
  
    const iso = d => {
        const _d = new Date(d);
        _d.setMinutes(_d.getMinutes() - _d.getTimezoneOffset());
        return _d.toISOString().split("T")[0];
    };
    
    // Live Clock Logic
    const locale = { uz: 'uz-UZ', ru: 'ru-RU', en: 'en-GB' }[document.documentElement.lang] || 'uz-UZ';
    const clockEl = document.querySelector('[data-clock]');
    const clockWeekdayEl = document.querySelector('[data-clock-weekday]');
    const tickClock = () => {
      const now = new Date();
      if (clockEl) clockEl.textContent = new Intl.DateTimeFormat(locale, { timeZone: 'Asia/Tashkent', hour: '2-digit', minute: '2-digit', hour12: false }).format(now);
      if (clockWeekdayEl) clockWeekdayEl.textContent = `${now.getDate()} ${text.months[now.getMonth()]} · ${text.days[now.getDay()]}`;
    };
    tickClock();
    setInterval(tickClock, 1000);
    
    const add = (d, n) => {
        const _d = new Date(d);
        _d.setDate(_d.getDate() + n);
        return _d;
    };
    
    const label = d => `${d.getDate()}-${text.months[d.getMonth()]}, ${d.getFullYear()}`;
    const esc = str => String(str).replace(/[&<>"']/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));
  
    const range = () => {
      let start, end;
      if (view === "month") {
        const first = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
        const last = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0);
        // adjust to Monday start
        start = add(first, -((first.getDay() + 6) % 7));
        end = add(last, (7 - last.getDay()) % 7);
      } else if (view === "week") {
        start = add(cursor, -((cursor.getDay() + 6) % 7));
        end = add(start, 6);
      } else {
        start = new Date(cursor);
        end = new Date(cursor);
      }
      return { start, end };
    };
  
    // Phase 18 Event Capsule
    const eventCard = (e, compact, index) => {
        let colorClass = 'cobalt';
        if(e.status === 'in_progress') colorClass = 'emerald';
        if(e.status === 'upcoming') colorClass = 'amber';
        
        return `<div class="cal-capsule cal-capsule--${colorClass}" data-event-index="${index}">
            <span class="cal-capsule__time">${esc(e.start_time.substring(0,5))}</span>
            <span style="overflow:hidden; text-overflow:ellipsis;">${esc(e.title)}</span>
        </div>`;
    };
  
    // Phase 18 Month Grid
    const renderMonth = (start, end) => {
      const days = [];
      for (let d = new Date(start); d <= end; d = add(d, 1)) days.push(d);
      
      const weekdaysHtml = text.days.map((x, i) => {
        const color = (i >= 5) ? 'color:var(--color-brand-cobalt);' : '';
        return `<div class="calendar-month__weekday" style="${color}">${x}</div>`;
      }).join("");
  
      const gridHtml = days.map(d => {
        const rows = events.filter(e => e.date === iso(d));
        let classes = ['calendar-day'];
        if (iso(d) === iso(new Date())) classes.push('calendar-day--today');
        if (d.getMonth() !== cursor.getMonth()) classes.push('calendar-day--outside');
        if (d.getDay() === 0 || d.getDay() === 6) classes.push('calendar-day--weekend');
        
        const header = `<div class="calendar-day__header"><span class="calendar-day__number">${d.getDate()}</span></div>`;
        const evHtml = `<div class="calendar-events">
            ${rows.slice(0,3).map(e => eventCard(e, true, events.indexOf(e))).join("")}
            ${rows.length > 3 ? `<div class="cal-more" style="text-align:left;">+${rows.length-3} ${text.more}</div>` : ""}
        </div>`;
  
        return `<div class="${classes.join(' ')}">${header}${evHtml}</div>`;
      }).join("");
  
      return `<div class="calendar-month__header">${weekdaysHtml}</div><div class="calendar-month__grid">${gridHtml}</div>`;
    };
  
    // Basic Week/Day fallback for now, using Phase 18 styles conceptually
    const renderWeek = (start) => {
        // Fallback to month visually if week isn't strictly styled yet, but we'll adapt.
        const days = Array.from({length: 7}, (_, i) => add(start, i));
        let html = `<div class="calendar-month__header">${days.map(d => `<div class="calendar-month__weekday">${text.days[(d.getDay()+6)%7]} ${d.getDate()}</div>`).join("")}</div>`;
        html += `<div class="calendar-month__grid" style="grid-template-columns: repeat(7, 1fr); min-height: 400px;">`;
        html += days.map(d => {
            const rows = events.filter(e => e.date === iso(d));
            return `<div class="calendar-day ${iso(d)===iso(new Date())?'calendar-day--today':''}"><div class="calendar-events">${rows.map(e => eventCard(e, false, events.indexOf(e))).join("")}</div></div>`;
        }).join("");
        html += `</div>`;
        return html;
    };
  
    const renderDay = () => renderWeek(cursor); // Alias for now to prevent broken views
  
    const renderList = () => {
        if (!events.length) return `<div style="padding:var(--space-6); text-align:center; color:var(--color-text-muted);">${text.empty}</div>`;
        
        return `<div style="padding:var(--space-4); display:flex; flex-direction:column; gap:var(--space-3);">
            ${events.map((e, index) => `
                <div class="cal-capsule cal-capsule--cobalt" data-event-index="${index}" style="padding:var(--space-3); font-size:var(--text-body);">
                    <span class="cal-capsule__time" style="font-size:var(--text-meta); width: 80px;">${esc(e.date)} ${esc(e.start_time.substring(0,5))}</span>
                    <span>${esc(e.title)} (${esc(e.venue)})</span>
                </div>
            `).join("")}
        </div>`;
    };
  
    const updateNow = () => {}; // Used for timeline line in original, omitting for simplicity in grid
  
    const render = () => {
      const {start, end} = range();
      
      if (view === "month") title.textContent = `${text.months[cursor.getMonth()]} ${cursor.getFullYear()}`;
      else if (view === "week") title.textContent = `${label(start)} – ${label(end)}`;
      else title.textContent = label(cursor);
  
      stage.innerHTML = view === "month" ? renderMonth(start, end) : view === "week" ? renderWeek(start) : view === "day" ? renderDay() : renderList();
      
      root.querySelectorAll(".segmented-control__btn").forEach(b => {
          b.classList.toggle('is-active', b.dataset.view === view);
      });
      
      history.replaceState(null, "", `${location.pathname}?date=${iso(cursor)}&view=${view}`);
    };
  
    const load = async () => {
      const {start, end} = range();
      const query = new URLSearchParams({start: iso(start), end: iso(end)});
      root.querySelectorAll("[data-filter]").forEach(c => { if (c.value) query.set(c.dataset.filter, c.value); });
      
      stage.innerHTML = `<div class="calendar-loading"><span></span><span></span><span></span><p>${text.today}...</p></div>`;
      
      try {
        const response = await fetch(`${root.dataset.endpoint}?${query}`);
        if (!response.ok) throw Error();
        events = (await response.json()).events || [];
        render();
      } catch {
        stage.innerHTML = `<div style="padding:var(--space-6); text-align:center; color:var(--color-status-critical);">${text.retry}</div>`;
      }
    };
  
    const move = n => {
      if (view === "month") cursor = new Date(cursor.getFullYear(), cursor.getMonth() + n, 1);
      else cursor = add(cursor, n * (view === "week" ? 7 : 1));
      load();
    };
  
    root.addEventListener("click", e => {
      const viewBtn = e.target.closest("[data-view]");
      if (viewBtn) { view = viewBtn.dataset.view; load(); return; }
      if (e.target.closest("[data-prev]")) move(-1);
      if (e.target.closest("[data-next]")) move(1);
      if (e.target.closest("[data-today]")) { cursor = new Date(); load(); }
      
      const card = e.target.closest("[data-event-index]");
      if (card) openDrawer(events[Number(card.dataset.eventIndex)]);
      
      if (e.target.closest("[data-clear-filters]")) {
          root.querySelectorAll("[data-filter]").forEach(c => c.value = "");
          load();
      }
    });
  
    let timer;
    root.querySelectorAll("[data-filter]").forEach(c => {
        c.addEventListener(c.type === "search" ? "input" : "change", () => {
            clearTimeout(timer);
            timer = setTimeout(load, 300);
        });
    });
  
    const openDrawer = e => {
      previousFocus = document.activeElement;
      if (!drawer) return;
      drawer.querySelector("[data-dialog-title]").textContent = e.title;
      
      const statusEl = drawer.querySelector("[data-dialog-status]");
      statusEl.textContent = e.status_label || e.status;
      statusEl.className = 'chip ' + (e.status === 'in_progress' ? 'chip--active' : 'chip--upcoming');
      
      drawer.querySelector("[data-dialog-time]").textContent = `${e.date} · ${e.start_time.substring(0,5)}–${e.end_time.substring(0,5)}`;
      drawer.querySelector("[data-dialog-venue]").textContent = e.venue;
      drawer.querySelector("[data-dialog-type]").textContent = e.event_type || "";
      drawer.querySelector("[data-dialog-responsible]").textContent = e.responsible || "";
      drawer.querySelector("[data-dialog-description]").textContent = e.description || "";
      
      drawer.classList.add('is-open');
    };
  
    const close = () => {
        drawer.classList.remove('is-open');
        if (previousFocus) previousFocus.focus();
    };
    
    drawer.querySelector("[data-dialog-close]")?.addEventListener("click", close);
  
    // INIT
    if (new URLSearchParams(location.search).get("date")) {
        cursor = new Date(new URLSearchParams(location.search).get("date"));
    }
    load();
  
  })();
