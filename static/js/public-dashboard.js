(() => {
  const dashboard = document.querySelector("[data-dashboard]");
  const venueGrid = document.querySelector("[data-venue-grid]");
  const clock = document.querySelector("[data-clock]");
  const date = document.querySelector("[data-date]");
  const locale =
    { uz: "uz-UZ", ru: "ru-RU", en: "en-GB" }[document.documentElement.lang] || "uz-UZ";
  const language = document.documentElement.lang || "uz";
  const calendarNames = {
    uz: {months: ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"], weekdays: ["yakshanba", "dushanba", "seshanba", "chorshanba", "payshanba", "juma", "shanba"]},
    ru: {months: ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"], weekdays: ["воскресенье", "понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]},
    en: {months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], weekdays: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]},
  }[language];
  const tick = () => {
    const now = new Date();
    if (clock) clock.textContent = new Intl.DateTimeFormat(locale, {timeZone: "Asia/Tashkent", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false}).format(now);
    if (date) {
      const parts = Object.fromEntries(new Intl.DateTimeFormat("en-US", {timeZone: "Asia/Tashkent", weekday: "short", day: "numeric", month: "numeric"}).formatToParts(now).map((part) => [part.type, part.value]));
      const weekdayIndex = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(parts.weekday);
      date.textContent = `${calendarNames.weekdays[weekdayIndex]}, ${parts.day} ${calendarNames.months[Number(parts.month) - 1]}`;
    }
  };
  tick();
  window.setInterval(tick, 1000);
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"})[char]);
  const setMetric = (target, value) => {
    const start = Number(target.textContent) || 0;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || start === value) {
      target.textContent = value;
      return;
    }
    const started = performance.now();
    const frame = (now) => {
      const progress = Math.min(1, (now - started) / 420);
      target.textContent = Math.round(start + (value - start) * progress);
      if (progress < 1) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  };
  const venueCard = (venue) => `<article class="live-venue-card status-${escapeHtml(String(venue.status).toLowerCase())}"><header><span class="venue-monogram">${escapeHtml(venue.code)}</span><span class="live-status"><i></i>${escapeHtml(venue.status_label)}</span></header><h3>${escapeHtml(venue.name)}</h3><p class="venue-current">${escapeHtml(venue.current_title || venue.next_title || "Available for scheduling")}</p>${venue.minutes_remaining ? `<strong class="venue-countdown">${escapeHtml(venue.minutes_remaining)} min</strong><div class="venue-progress"><i style="width:68%"></i></div>` : venue.minutes_until_start ? `<strong class="venue-countdown">${escapeHtml(venue.minutes_until_start)} min</strong>` : ""}${venue.next_title ? `<div class="venue-next"><span>Next · ${escapeHtml(venue.next_start)}</span><strong>${escapeHtml(venue.next_title)}</strong></div>` : ""}<footer><span>${escapeHtml(venue.ends_at || venue.next_start || "Open")}</span><small>${escapeHtml(venue.today_count)}</small></footer></article>`;
  const eventRow = (event) => `<article class="timeline-event"><time><strong>${escapeHtml(event.start_time)}</strong><span>${escapeHtml(event.date)}</span></time><i style="--event-color:${escapeHtml(event.color || "#06b6d4")}"></i><div><h3>${escapeHtml(event.title)}</h3><p>${escapeHtml(event.venue)}${event.event_type ? ` · ${escapeHtml(event.event_type)}` : ""}</p></div><span class="event-status status-${escapeHtml(event.status)}">${escapeHtml(event.status_label || event.status)}</span></article>`;
  const refresh = async () => {
    const endpoint = dashboard?.dataset.endpoint || venueGrid?.dataset.endpoint;
    if (!endpoint) return;
    const state = document.querySelector("[data-refresh-state]");
    try {
      const response = await fetch(endpoint, {headers: {Accept: "application/json"}});
      if (!response.ok) throw new Error("refresh failed");
      const data = await response.json();
      if (data.metrics) Object.entries(data.metrics).forEach(([key, value]) => {
        const target = document.querySelector(`[data-metric="${key}"]`);
        if (target) setMetric(target, value);
      });
      if (venueGrid && data.venues) venueGrid.innerHTML = data.venues.map(venueCard).join("");
      const today = document.querySelector("[data-today-events]");
      const upcoming = document.querySelector("[data-upcoming-events]");
      if (today && data.today_events?.length) today.innerHTML = data.today_events.map(eventRow).join("");
      if (upcoming && data.upcoming_events?.length) upcoming.innerHTML = data.upcoming_events.map(eventRow).join("");
      if (state) { state.dataset.state = "ok"; const message = state.querySelector("[data-refresh-message]"); if (message) message.textContent = message.dataset.ok; state.querySelector("[data-refresh-retry]")?.setAttribute("hidden", ""); }
    } catch {
      if (state) { state.dataset.state = "error"; const message = state.querySelector("[data-refresh-message]"); if (message) message.textContent = message.dataset.error; state.querySelector("[data-refresh-retry]")?.removeAttribute("hidden"); }
    }
  };
  document.querySelector("[data-refresh-retry]")?.addEventListener("click", refresh);
  refresh();
  window.setInterval(refresh, 20000);
})();
