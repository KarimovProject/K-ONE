/**
 * IEMS Public Calendar - Phase 19.4 Unified Engine
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

    // Live clock badge (date/time, real-time, Asia/Tashkent).
    (() => {
        const clockEl = document.querySelector("[data-clock]");
        const weekdayEl = document.querySelector("[data-clock-weekday]");
        if (!clockEl && !weekdayEl) return;
        const locale = { uz: "uz-UZ", ru: "ru-RU", en: "en-GB", tr: "tr-TR" }[document.documentElement.lang] || "uz-UZ";
        const tick = () => {
            const now = new Date();
            if (clockEl) {
                clockEl.textContent = new Intl.DateTimeFormat(locale, {
                    timeZone: "Asia/Tashkent", hour: "2-digit", minute: "2-digit", hour12: false,
                }).format(now);
            }
            if (weekdayEl) {
                weekdayEl.textContent = new Intl.DateTimeFormat(locale, {
                    timeZone: "Asia/Tashkent", day: "numeric", month: "short", weekday: "long",
                }).format(now);
            }
        };
        tick();
        setInterval(tick, 1000);
    })();

    const text = {
      uz: {
        months: ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"],
        days: ["Dush","Sesh","Chor","Pay","Jum","Shan","Yak"],
        today: "Bugun", tomorrow: "Erta", now: "Hozir",
        empty: "Tadbirlar topilmadi", more: "yana", retry: "Xatolik yuz berdi", again: "Qayta urinish"
      },
      ru: {
        months: ["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"],
        days: ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"],
        today: "Сегодня", tomorrow: "Завтра", now: "Сейчас",
        empty: "Мероприятия не найдены", more: "ещё", retry: "Произошла ошибка", again: "Повторить"
      },
      en: {
        months: ["January","February","March","April","May","June","July","August","September","October","November","December"],
        days: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        today: "Today", tomorrow: "Tomorrow", now: "Now",
        empty: "No events found", more: "more", retry: "Something went wrong", again: "Retry"
      },
      tr: {
        months: ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"],
        days: ["Pzt","Sal","Çar","Per","Cum","Cmt","Paz"],
        today: "Bugün", tomorrow: "Yarın", now: "Şimdi",
        empty: "Etkinlik bulunamadı", more: "daha fazla", retry: "Bir hata oluştu", again: "Tekrar dene"
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

    const add = (d, n) => {
        const _d = new Date(d);
        _d.setDate(_d.getDate() + n);
        return _d;
    };

    const label = d => `${d.getDate()}-${text.months[d.getMonth()]}, ${d.getFullYear()}`;
    const esc = str => String(str || '').replace(/[&<>"']/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));

    const range = () => {
      let start, end;
      if (view === "month") {
        const first = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
        const last = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0);
        start = add(first, -((first.getDay() + 6) % 7));
        end = add(last, (7 - last.getDay()) % 7);
      } else if (view === "week") {
        start = add(cursor, -((cursor.getDay() + 6) % 7));
        end = add(start, 6);
      } else {
        start = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
        end = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0);
      }
      return { start, end };
    };

    // Phase 19.4 Event Capsule with Event Types and Room code
    const eventCard = (e, compact, index) => {
        let colorClass = 'cobalt';
        const typeCode = (e.event_type_code || '').toLowerCase();
        if (typeCode.includes('conf') || typeCode.includes('konf') || typeCode.includes('forum')) colorClass = 'cobalt';
        else if (typeCode.includes('meet') || typeCode.includes('majlis')) colorClass = 'cyan';
        else if (typeCode.includes('sem') || typeCode.includes('train')) colorClass = 'emerald';
        else if (typeCode.includes('spec') || typeCode.includes('rasmiy')) colorClass = 'violet';

        if (e.status === 'in_progress' || e.status === 'ONGOING') colorClass = 'emerald';
        else if (e.status === 'upcoming' || e.status === 'SCHEDULED') colorClass = 'cobalt';

        const venueCode = e.venue_code || (e.venue ? e.venue.substring(0, 4) : 'AUD');
        const timeStr = e.start_time ? e.start_time.substring(0, 5) : '';

        return `<div class="cal-capsule cal-capsule--${colorClass}" data-event-index="${index}" title="${esc(e.title)} (${venueCode})">
            <div class="cal-capsule__meta">
                <span class="cal-capsule__time">${esc(timeStr)}</span>
                <span class="cal-capsule__room">${esc(venueCode)}</span>
            </div>
            <div class="cal-capsule__title">${esc(e.title)}</div>
        </div>`;
    };

    // Phase 19.4 Month Grid
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
        if (rows.length > 0) classes.push('calendar-day--has-events');

        const header = `<div class="calendar-day__header">
            <span class="calendar-day__number">${d.getDate()}</span>
            ${rows.length > 0 ? `<span class="calendar-day__count">${rows.length}</span>` : ''}
        </div>`;
        const evHtml = `<div class="calendar-events">
            ${rows.slice(0, 2).map(e => eventCard(e, true, events.indexOf(e))).join("")}
            ${rows.length > 2 ? `<div class="cal-more">+${rows.length - 2} ${text.more}</div>` : ""}
        </div>`;

        return `<div class="${classes.join(' ')}" data-date="${iso(d)}">${header}${evHtml}</div>`;
      }).join("");

      return `<div class="calendar-month__header">${weekdaysHtml}</div><div class="calendar-month__grid">${gridHtml}</div>`;
    };

    const renderWeek = (start) => {
        const days = Array.from({length: 7}, (_, i) => add(start, i));
        let html = `<div class="calendar-month__header">${days.map(d => `<div class="calendar-month__weekday">${text.days[(d.getDay()+6)%7]} ${d.getDate()}</div>`).join("")}</div>`;
        html += `<div class="calendar-month__grid" style="grid-template-columns: repeat(7, 1fr); min-height: 440px;">`;
        html += days.map(d => {
            const rows = events.filter(e => e.date === iso(d));
            return `<div class="calendar-day ${iso(d)===iso(new Date())?'calendar-day--today':''}"><div class="calendar-day__header"><span class="calendar-day__number">${d.getDate()}</span></div><div class="calendar-events">${rows.map(e => eventCard(e, false, events.indexOf(e))).join("")}</div></div>`;
        }).join("");
        html += `</div>`;
        return html;
    };

    const renderDay = () => renderWeek(cursor);

    const renderList = () => {
        if (!events.length) return `<div style="padding:var(--space-8); text-align:center; color:var(--color-text-muted);">${text.empty}</div>`;

        return `<div style="padding:var(--space-4); display:flex; flex-direction:column; gap:var(--space-3);">
            ${events.map((e, index) => `
                <div class="cal-capsule cal-capsule--cobalt" data-event-index="${index}" style="padding:var(--space-3); font-size:var(--text-body); cursor:pointer;">
                    <span class="cal-capsule__time" style="font-size:var(--text-meta); width: 120px; font-weight:700;">${esc(e.date)} · ${esc((e.start_time||'').substring(0,5))}</span>
                    <span style="font-weight:700; color:var(--color-text-title);">${esc(e.title)}</span>
                    <span style="margin-left:auto; font-size:var(--text-micro); color:var(--color-text-muted); background:var(--color-surface-panel); padding:2px 8px; border-radius:4px;">${esc(e.venue)}</span>
                </div>
            `).join("")}
        </div>`;
    };

    // Phase 27.1 Mobile Calendar Architecture
    const renderMobile = () => {
        const start = add(cursor, -((cursor.getDay() + 6) % 7));
        const days = Array.from({length: 7}, (_, i) => add(start, i));

        let stripHtml = `<div class="mobile-cal-strip">`;
        days.forEach(d => {
            const isSelected = iso(d) === iso(cursor);
            const isToday = iso(d) === iso(new Date());
            const hasEvents = events.some(e => e.date === iso(d));
            let classes = ['mobile-cal-day'];
            if (isSelected) classes.push('is-selected');
            if (isToday) classes.push('is-today');

            stripHtml += `<div class="${classes.join(' ')}" data-select-date="${iso(d)}">
                <span class="mobile-cal-day-name">${text.days[(d.getDay()+6)%7].substring(0, 2)}</span>
                <span class="mobile-cal-day-num">${d.getDate()}</span>
                ${hasEvents ? '<span class="mobile-cal-dot"></span>' : ''}
            </div>`;
        });
        stripHtml += `</div>`;

        const dayEvents = events.filter(e => e.date === iso(cursor));
        let agendaHtml = `<div class="mobile-cal-agenda">`;

        const dateString = `${cursor.getDate()} ${text.months[cursor.getMonth()]}, ${text.days[(cursor.getDay()+6)%7]}`;
        agendaHtml += `<div class="mobile-cal-agenda-header">
            <h3>${dateString}</h3>
            <span>${dayEvents.length} ta tadbir</span>
        </div>`;

        if (dayEvents.length === 0) {
            agendaHtml += `<div class="mobile-cal-empty">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                <p>Bu kunda tadbirlar yo'q</p>
            </div>`;
        } else {
            agendaHtml += `<div class="mobile-cal-events">`;
            dayEvents.forEach((e, index) => {
                let colorClass = 'cobalt';
                const typeCode = (e.event_type_code || '').toLowerCase();
                if (typeCode.includes('conf') || typeCode.includes('konf') || typeCode.includes('forum')) colorClass = 'cobalt';
                else if (typeCode.includes('meet') || typeCode.includes('majlis')) colorClass = 'cyan';
                else if (typeCode.includes('sem') || typeCode.includes('train')) colorClass = 'emerald';
                else if (typeCode.includes('spec') || typeCode.includes('rasmiy')) colorClass = 'violet';

                if (e.status === 'in_progress' || e.status === 'ONGOING') colorClass = 'emerald';
                else if (e.status === 'upcoming' || e.status === 'SCHEDULED') colorClass = 'cobalt';

                const venueCode = e.venue_code || (e.venue ? e.venue.substring(0, 4) : 'AUD');
                const timeStr = e.start_time ? e.start_time.substring(0, 5) : '';
                const endTimeStr = e.end_time ? e.end_time.substring(0, 5) : '';

                agendaHtml += `
                <div class="mobile-event-card border-${colorClass}" data-event-index="${events.indexOf(e)}">
                    <div class="mobile-event-time">
                        <strong>${timeStr}</strong>
                        ${endTimeStr ? `<span>${endTimeStr}</span>` : ''}
                    </div>
                    <div class="mobile-event-body">
                        <div class="mobile-event-room"><span class="dot bg-${colorClass}"></span> ${venueCode}</div>
                        <h4 class="mobile-event-title">${esc(e.title)}</h4>
                        <div class="mobile-event-meta">${esc(e.event_type || '')}</div>
                    </div>
                </div>`;
            });
            agendaHtml += `</div>`;
        }
        agendaHtml += `</div>`;

        return `<div class="mobile-calendar-wrapper fade-in-up">${stripHtml}${agendaHtml}</div>`;
    };

    const render = () => {
      const {start, end} = range();

      if (view === "month") title.textContent = `${text.months[cursor.getMonth()]} ${cursor.getFullYear()}`;
      else if (view === "week") title.textContent = `${label(start)} – ${label(end)}`;
      else title.textContent = label(cursor);

      if (window.innerWidth <= 767) {
          stage.innerHTML = renderMobile();
      } else {
          stage.innerHTML = view === "month" ? renderMonth(start, end) : view === "week" ? renderWeek(start) : view === "day" ? renderDay() : renderList();
      }

      root.querySelectorAll("[data-view]").forEach(b => {
          b.classList.toggle('active', b.dataset.view === view);
          if (b.hasAttribute('aria-selected') || b.dataset.view === view) {
              b.setAttribute('aria-selected', b.dataset.view === view);
          }
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

      const dayBtn = e.target.closest("[data-select-date]");
      if (dayBtn) {
          cursor = new Date(dayBtn.dataset.selectDate);
          render();
          return;
      }

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

      const now = new Date();
      const isLive = e.start && e.end && new Date(e.start) <= now && now < new Date(e.end);
      const statusEl = drawer.querySelector("[data-dialog-status]");
      statusEl.textContent = e.status_label || e.status;
      statusEl.className = 'chip ' + (isLive ? 'chip--active' : 'chip--upcoming');

      const startTime = (e.start_time || '').substring(0,5);
      const endTime = (e.end_time || '').substring(0,5);
      drawer.querySelector("[data-dialog-time]").textContent = `${e.date} · ${startTime}${endTime ? '–' + endTime : ''}`;
      drawer.querySelector("[data-dialog-venue]").textContent = e.venue_full || e.venue;
      drawer.querySelector("[data-dialog-type]").textContent = e.event_type || "";
      drawer.querySelector("[data-dialog-responsible]").textContent = e.responsible || "";
      drawer.querySelector("[data-dialog-description]").textContent = e.description || "";

      const bannerImg = drawer.querySelector("[data-dialog-banner]");
      if (e.banner_url) {
          bannerImg.src = e.banner_url;
          bannerImg.hidden = false;
      } else {
          bannerImg.hidden = true;
          bannerImg.src = '';
      }

      const programLink = drawer.querySelector("[data-dialog-program]");
      const mainLink = drawer.querySelector("[data-dialog-link]");
      if (e.public_url) {
          programLink.href = e.public_url;
          programLink.hidden = false;
          mainLink.href = e.public_url;
          mainLink.hidden = false;
      } else {
          programLink.hidden = true;
          mainLink.hidden = true;
      }

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
