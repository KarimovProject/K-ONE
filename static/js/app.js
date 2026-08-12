(() => {
  const shell = document.querySelector("[data-shell]");
  if (!shell) return;

  const openButton = shell.querySelector("[data-sidebar-open]");
  const closeButton = shell.querySelector("[data-sidebar-close]");

  const closeSidebar = () => {
    shell.classList.remove("sidebar-open");
    openButton?.setAttribute("aria-expanded", "false");
  };

  openButton?.addEventListener("click", () => {
    const willOpen = !shell.classList.contains("sidebar-open");
    shell.classList.toggle("sidebar-open", willOpen);
    openButton.setAttribute("aria-expanded", String(willOpen));
  });
  closeButton?.addEventListener("click", closeSidebar);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeSidebar();
  });
})();

