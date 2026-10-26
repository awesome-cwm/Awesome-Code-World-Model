/* Apply the saved preference before paint; all pages share the same setting. */
(() => {
  'use strict';
  const key = 'cwm-theme';
  const choices = ['system', 'light', 'dark'];
  const labels = {system: 'System', light: 'Light', dark: 'Dark'};
  const icons = {system:'<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8m-4-4v4"/>',light:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1"/>',dark:'<path d="M20 15A9 9 0 0 1 9 4a9 9 0 1 0 11 11Z"/>'};
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = 'system';
  let button;
  try {
    const saved = localStorage.getItem(key);
    if (choices.includes(saved)) preference = saved;
  } catch (_) { /* Browsing still works when local storage is unavailable. */ }

  function apply() {
    const effective = preference === 'system' ? (system.matches ? 'dark' : 'light') : preference;
    root.dataset.theme = effective;
    root.dataset.themePreference = preference;
    if (button) {
      button.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">${icons[preference]}</svg>`;
      button.setAttribute('aria-label', `Theme: ${labels[preference]}. Switch to ${labels[choices[(choices.indexOf(preference) + 1) % choices.length]]} theme`);
      button.title = button.getAttribute('aria-label');
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = getComputedStyle(root).getPropertyValue('--paper').trim();
  }
  apply();
  system.addEventListener('change', () => { if (preference === 'system') apply(); });
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      preference = choices.includes(event.newValue) ? event.newValue : 'system';
      apply();
    }
  });
  document.addEventListener('DOMContentLoaded', () => {
    const target = document.querySelector('.header, .document nav');
    if (!target) return;
    button = document.createElement('button');
    button.type = 'button';
    button.className = 'theme-toggle';
    button.addEventListener('click', () => {
      preference = choices[(choices.indexOf(preference) + 1) % choices.length];
      try { localStorage.setItem(key, preference); } catch (_) { /* Keep the current-page choice. */ }
      if (!document.startViewTransition || matchMedia('(prefers-reduced-motion: reduce)').matches) return apply();
      button.disabled = true;
      const box = button.getBoundingClientRect();
      root.style.setProperty('--theme-x', `${box.x + box.width / 2}px`);
      root.style.setProperty('--theme-y', `${box.y + box.height / 2}px`);
      const transition = document.startViewTransition(() => { apply(); root.dataset.themeChanging = ''; });
      transition.finished.catch(() => {}).finally(() => { delete root.dataset.themeChanging; button.disabled = false; });
    });
    target.append(button);
    apply();
  });
})();
