// Item Passport search. A query that matches a known identifier opens its matter.
// A query shaped like an identifier that we don't know gets an honest "no match".
// Anything else goes to MiniSearch over titles, places, topics and checked sentences.
import MiniSearch from 'minisearch';
import { looksLikeIdentifier, normalizeIdentifier } from '../lib/identifiers';

interface SearchDoc {
  id: string;
  title: string;
  topics: string[];
  location: string;
  identifiers: string[];
  text: string;
}

interface SearchFile {
  checked_on: string;
  alias: Record<string, string>;
  docs: SearchDoc[];
}

const input = document.getElementById('q') as HTMLInputElement;
const results = document.getElementById('results')!;
const query = new URLSearchParams(window.location.search).get('q')?.trim() ?? '';
input.value = query;

function showMessage(title: string, text: string) {
  results.replaceChildren();
  const box = document.createElement('div');
  box.className = 'mu-alert mu-alert--info';
  const dot = document.createElement('span');
  dot.className = 'mu-alert__dot';
  dot.setAttribute('aria-hidden', 'true');
  const body = document.createElement('div');
  const heading = document.createElement('p');
  heading.className = 'mu-alert__title';
  heading.textContent = title;
  const detail = document.createElement('p');
  detail.className = 'mu-alert__text';
  detail.textContent = text;
  body.append(heading, detail);
  box.append(dot, body);
  results.append(box);
}

// The rows are prebuilt on the page (template#result-rows), one per matter.
const rowTemplate = document.getElementById('result-rows') as HTMLTemplateElement;

function resultRow(matterId: string): Node | null {
  const row = rowTemplate.content.querySelector(`li[data-matter="${CSS.escape(matterId)}"]`);
  return row ? row.cloneNode(true) : null;
}

function showResults(matterIds: string[]) {
  results.replaceChildren();
  const list = document.createElement('ul');
  list.className = 'ledger';
  for (const id of matterIds) {
    const row = resultRow(id);
    if (row) list.append(row);
  }
  const count = document.createElement('p');
  const shown = list.children.length;
  count.textContent = `${shown} ${shown === 1 ? 'match' : 'matches'} for “${query}”.`;
  results.append(count, list);
}

async function run() {
  if (!query) {
    results.replaceChildren();
    return;
  }
  const response = await fetch('/data/search.json');
  if (!response.ok) throw new Error(`search.json returned ${response.status}`);
  const file: SearchFile = await response.json();

  const matterId = file.alias[normalizeIdentifier(query)];
  if (matterId) {
    showMessage('Opening the matter', `“${query}” is a number Muni knows.`);
    window.location.replace(`/matter/${matterId}/`);
    return;
  }

  if (looksLikeIdentifier(query)) {
    showMessage('No match', `No matter in the records Muni has checked uses the number “${query}”. Muni doesn't guess. Check the number, or look at the list below.`);
    return;
  }

  const search = new MiniSearch<SearchDoc>({
    fields: ['title', 'identifiers', 'location', 'topics', 'text'],
    storeFields: ['id'],
    extractField: (doc, field) => {
      const value = doc[field as keyof SearchDoc];
      return Array.isArray(value) ? value.join(' ') : value;
    },
    searchOptions: { boost: { title: 3, identifiers: 3, location: 2 }, prefix: true, fuzzy: 0.2, combineWith: 'AND' },
  });
  search.addAll(file.docs);
  const found = search.search(query);
  if (found.length === 0) {
    showMessage('No match', `Nothing in the matters Muni has checked matches “${query}”. Try fewer words, a street name, or browse by topic.`);
    return;
  }
  showResults(found.map((hit) => String(hit.id)));
}

run().catch((error) => {
  showMessage("Search didn't load", `Please try again. (${error.message})`);
});
