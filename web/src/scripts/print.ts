// Printed pages should show every source, so open the closed source boxes while
// printing and close them again afterwards.
let openedForPrint: HTMLDetailsElement[] = [];

window.addEventListener('beforeprint', () => {
  openedForPrint = [...document.querySelectorAll<HTMLDetailsElement>('details:not([open])')];
  for (const details of openedForPrint) details.open = true;
});

window.addEventListener('afterprint', () => {
  for (const details of openedForPrint) details.open = false;
  openedForPrint = [];
});

document.getElementById('print-btn')?.addEventListener('click', () => window.print());
