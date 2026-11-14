// Theme button: Paper (light) or Dusk (dark). Without a saved choice the
// system setting decides, through the prefers-color-scheme rules in global.css.
const button = document.getElementById('theme-btn');

function systemPrefersDark(): boolean {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function isDark(): boolean {
  const chosen = document.documentElement.getAttribute('data-theme');
  if (chosen) return chosen === 'dark';
  return systemPrefersDark();
}

function showState() {
  button?.setAttribute('aria-pressed', isDark() ? 'true' : 'false');
}

button?.addEventListener('click', () => {
  const next = isDark() ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try {
    localStorage.setItem('muni-theme', next);
  } catch {
    // Storage can be blocked (private mode); the theme still applies to this page.
  }
  showState();
});

showState();
