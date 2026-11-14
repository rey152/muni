// Rechecks dated participation windows against today's date on this device, because the
// static page may be days old. Only windows whose date was read from a quote carry
// data-deadline; rule-based, unpublished and unchecked windows are left alone.
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

function localToday(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}

function longDate(isoDate: string): string {
  const [year, month, day] = isoDate.split('-');
  return `${MONTHS[Number(month) - 1]} ${Number(day)}, ${year}`;
}

const today = localToday();

for (const card of document.querySelectorAll<HTMLElement>('[data-deadline]')) {
  const deadline = card.dataset.deadline!;
  // The quoted day itself still counts as open, matching the build's rule.
  const open = deadline >= today;
  const tag = card.querySelector('[data-window-tag]');
  const text = card.querySelector('[data-window-text]');
  const when = card.querySelector('[data-window-when]');
  if (tag) {
    tag.textContent = open ? 'Open' : 'Closed';
    tag.className = open ? 'tag tag--open' : 'tag tag--closed';
  }
  if (text) {
    text.textContent = open ? 'The quoted date has not passed yet.' : 'The quoted date has passed.';
  }
  if (when) {
    when.textContent = `Open or closed was worked out with today's date on this device (${longDate(today)}).`;
  }
}
