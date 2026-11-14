// Exposure Preview: marks personal details in a draft. Everything stays in this page;
// the draft is saved to localStorage only when the person presses the save button.
const PATTERNS: { kind: string; regex: RegExp }[] = [
  { kind: 'email', regex: /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi },
  { kind: 'phone number', regex: /(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b/g },
  { kind: 'postal code', regex: /\b[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d\b/gi },
  {
    kind: 'street address',
    regex: /\b\d{1,5}\s+(?:[A-Z][\w'-]*\s+){1,4}(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Blvd|Boulevard|Cres|Crescent|Ct|Court|Pl|Place|Way|Lane|Ln|Line|Trail|Pkwy|Terr|Terrace)\b\.?(?:\s+[NSEW]\b)?/gi,
  },
  // The name itself has to start with capitals, so the pattern is case-sensitive apart from "my".
  { kind: 'name', regex: /\b[Mm]y name is\s+([A-Z][a-z'’-]+(?:\s+[A-Z][a-z'’-]+){0,2})/g },
];
const STORAGE_KEY = 'muni-comment-draft';

interface Found {
  start: number;
  end: number;
  kind: string;
}

const draft = document.getElementById('draft') as HTMLTextAreaElement;
const summary = document.getElementById('exposure-summary')!;
const preview = document.getElementById('exposure-preview')!;
const saveButton = document.getElementById('save-draft')!;
const forgetButton = document.getElementById('forget-draft')!;
const saveStatus = document.getElementById('save-status')!;

function findDetails(text: string): Found[] {
  const found: Found[] = [];
  for (const { kind, regex } of PATTERNS) {
    for (const match of text.matchAll(regex)) {
      let start = match.index;
      let value = match[0];
      if (kind === 'name') {
        value = match[1];
        start = match.index + match[0].lastIndexOf(value);
      }
      found.push({ start, end: start + value.length, kind });
    }
  }
  // Earliest first; when two overlap, keep the first one.
  found.sort((a, b) => a.start - b.start);
  const kept: Found[] = [];
  for (const item of found) {
    const last = kept[kept.length - 1];
    if (!last || item.start >= last.end) kept.push(item);
  }
  return kept;
}

function plural(kind: string, count: number): string {
  if (count === 1) return `1 ${kind}`;
  return kind === 'street address' ? `${count} street addresses` : `${count} ${kind}s`;
}

function update() {
  const text = draft.value;
  const found = findDetails(text);
  preview.replaceChildren();
  let position = 0;
  for (const item of found) {
    preview.append(text.slice(position, item.start));
    const mark = document.createElement('mark');
    mark.dataset.kind = item.kind;
    mark.textContent = text.slice(item.start, item.end);
    preview.append(mark);
    position = item.end;
  }
  preview.append(text.slice(position));

  if (found.length === 0) {
    summary.textContent = 'Nothing found yet.';
    return;
  }
  const counts = new Map<string, number>();
  for (const item of found) counts.set(item.kind, (counts.get(item.kind) ?? 0) + 1);
  const parts = [...counts].map(([kind, count]) => plural(kind, count));
  summary.textContent = `Found ${parts.join(', ')}. These are marked below. If you send this, they could become part of the public record.`;
}

function loadSaved() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      draft.value = saved;
      saveStatus.textContent = 'Loaded the draft you saved on this device.';
    }
  } catch {
    // Storage blocked: start with an empty draft.
  }
}

saveButton.addEventListener('click', () => {
  try {
    localStorage.setItem(STORAGE_KEY, draft.value);
    saveStatus.textContent = 'Saved on this device only.';
  } catch {
    saveStatus.textContent = "This browser won't let Muni save. Copy your draft somewhere safe.";
  }
});

forgetButton.addEventListener('click', () => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Nothing was stored.
  }
  saveStatus.textContent = 'No draft is saved on this device.';
});

draft.addEventListener('input', update);
loadSaved();
update();
