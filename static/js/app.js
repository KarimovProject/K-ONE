
document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.createElement('button');
  toggleBtn.className = 'sidebar-toggle-btn';
  toggleBtn.innerHTML = '<svg width=\'20\' height=\'20\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'><polyline points=\'15 18 9 12 15 6\'></polyline></svg>';
  
  if(sidebar) {
    sidebar.appendChild(toggleBtn);
    
    // Check local storage for state
    if(localStorage.getItem('sidebar-collapsed') === 'true') {
      document.body.classList.add('sidebar-collapsed');
    }

    toggleBtn.addEventListener('click', () => {
      document.body.classList.toggle('sidebar-collapsed');
      const isCollapsed = document.body.classList.contains('sidebar-collapsed');
      localStorage.setItem('sidebar-collapsed', isCollapsed);
    });
  }

  // Mobile navigation drawer: the topbar's hamburger button only carries
  // data-sidebar-open/aria attributes in the markup — nothing was ever
  // wired up to actually toggle it, so it did nothing on phones/tablets.
  const shell = document.querySelector('[data-shell]');
  const openBtn = document.querySelector('[data-sidebar-open]');
  const closeBtn = document.querySelector('[data-sidebar-close]');
  if (shell && openBtn) {
    const setOpen = (isOpen) => {
      shell.classList.toggle('sidebar-open', isOpen);
      openBtn.setAttribute('aria-expanded', String(isOpen));
    };
    openBtn.addEventListener('click', () => setOpen(true));
    closeBtn?.addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') setOpen(false);
    });
  }

  // Restrict phone inputs to digits and the common phone punctuation
  // (+, -, (, ), space) so users can't type letters into a phone field.
  document.querySelectorAll('input[type="tel"]').forEach((input) => {
    input.addEventListener('input', () => {
      const cleaned = input.value.replace(/[^0-9+\-() ]/g, '');
      if (cleaned !== input.value) {
        input.value = cleaned;
      }
    });
  });
});

