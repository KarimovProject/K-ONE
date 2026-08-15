(() => {
  const shell = document.querySelector("[data-admin-shell]");
  document.querySelector("[data-sidebar-open]")?.addEventListener("click", () => shell?.classList.add("sidebar-open"));
  document.querySelector("[data-sidebar-close]")?.addEventListener("click", () => shell?.classList.remove("sidebar-open"));
  document.querySelector("[data-sidebar-collapse]")?.addEventListener("click", () => shell?.classList.toggle("is-collapsed"));
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") shell?.classList.remove("sidebar-open"); });
  document.querySelectorAll(".messagelist li").forEach((toast) => {
    toast.querySelector("button")?.addEventListener("click", () => toast.remove());
    if (!toast.classList.contains("error")) window.setTimeout(() => toast.remove(), 5000);
  });
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduced) document.querySelectorAll("[data-admin-counter]").forEach((node) => {
    const target = Number(node.textContent) || 0;
    const started = performance.now();
    const step = (now) => { const progress = Math.min(1, (now - started) / 500); node.textContent = Math.round(target * progress); if (progress < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  });
})();
