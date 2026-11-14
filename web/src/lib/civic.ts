// Labels and small derivations shared by the pages. Everything here works from
// reviewed records only: a stage counts as recorded only when an event says so.
import { data, findParticular, getPassage, getSnapshot } from './data';
import type { Claim, Matter, MatterEvent, ParticipationWindow, Snapshot } from './data';

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

// Dates in muni.json can be YYYY, YYYY-MM, YYYY-MM-DD or a full ISO timestamp.
// We only reformat what is written; nothing is filled in or guessed.
export function formatDate(value: string | null | undefined): string {
  if (!value) return 'not recorded';
  const match = /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/.exec(value);
  if (!match) return value;
  const [, year, month, day] = match;
  if (!month) return year;
  const monthName = MONTHS[Number(month) - 1];
  if (!day) return `${monthName} ${year}`;
  return `${monthName} ${Number(day)}, ${year}`;
}

export const asOf = formatDate(data.checked_on);
export const builtOn = formatDate(data.generated_on);

export function notEstablished(): string {
  return `Not established in the records checked (as of ${asOf}).`;
}

export const SECTIONS = [
  { key: 'applies_to', title: 'Applies to' },
  { key: 'what_and_why', title: 'What it would do and why' },
  { key: 'who_decides', title: 'Who decides' },
  { key: 'conditions', title: 'Conditions' },
  { key: 'not_decided', title: 'Not decided yet' },
  { key: 'have_a_say', title: 'How to have a say' },
  { key: 'records', title: 'Records' },
];

export const EVENT_LABELS: Record<string, string> = {
  proposed: 'Proposed',
  staff_recommendation: 'Staff recommendation',
  committee_action: 'Committee action',
  council_decision: 'Council decision',
  mayoral_instrument: 'Mayoral decision',
  provincial_decision: 'Provincial decision',
  appeal_window: 'Appeal or objection period',
  in_force: 'In force',
  repealed: 'Repealed',
  amended: 'Amended',
  implemented: 'Implemented',
};

export function eventLabel(kind: string): string {
  return EVENT_LABELS[kind] ?? kind;
}

// "2026" sorts before "2026-01-05" as text, which matches how the pipeline picks the latest event.
export function eventsInDateOrder(matter: Matter): MatterEvent[] {
  return [...matter.events].sort((a, b) => a.date.localeCompare(b.date));
}

export function latestEvent(matter: Matter): MatterEvent | undefined {
  if (!matter.status_summary) return undefined;
  return matter.events.find((e) => e.id === matter.status_summary!.latest_event_id);
}

const DECISION_KINDS = ['council_decision', 'mayoral_instrument', 'provincial_decision'];

export function hasDecisionRecord(matter: Matter): boolean {
  return matter.events.some((e) => DECISION_KINDS.includes(e.kind) || e.kind === 'in_force' || e.kind === 'repealed');
}

// Stages a resident would expect next that have no record. Only two are checked,
// because no single municipal process fits every matter.
export function missingStages(matter: Matter): string[] {
  const kinds = matter.events.map((e) => e.kind);
  const decided = kinds.some((k) => DECISION_KINDS.includes(k));
  if (!decided && !kinds.includes('in_force')) return ['Decision'];
  if (!kinds.includes('in_force') && !kinds.includes('repealed')) return ['In force'];
  return [];
}

export interface EasyReadStep {
  name: string;
  events: MatterEvent[];
}

// The five Easy Read steps. A step is filled only by an event of a matching kind.
export function easyReadSteps(matter: Matter): EasyReadStep[] {
  const steps = [
    { name: 'Proposed', kinds: ['proposed'] },
    { name: 'Staff recommendation', kinds: ['staff_recommendation'] },
    { name: 'Decided', kinds: DECISION_KINDS },
    { name: 'In force', kinds: ['in_force'] },
    { name: 'Done', kinds: ['implemented'] },
  ];
  return steps.map((step) => ({
    name: step.name,
    events: eventsInDateOrder(matter).filter((e) => step.kinds.includes(e.kind)),
  }));
}

export function eventsOutsideSteps(matter: Matter): MatterEvent[] {
  const stepKinds = ['proposed', 'staff_recommendation', ...DECISION_KINDS, 'in_force', 'implemented'];
  return eventsInDateOrder(matter).filter((e) => !stepKinds.includes(e.kind));
}

function citesVerbatim(passageIds: string[]): boolean {
  return passageIds.some((id) => getPassage(id).kind === 'verbatim');
}

export function provenanceLabel(claim: Claim): string {
  if (claim.provenance === 'quote') {
    return citesVerbatim(claim.passage_ids) ? 'Quote' : 'Quote from a research note';
  }
  if (claim.provenance === 'extraction') return 'Extracted';
  if (claim.provenance === 'ai_paraphrase') return 'AI paraphrase';
  return 'Written by a person';
}

// What "Show without AI" puts in place of an AI paraphrase, and how to label it honestly.
export function claimFallback(claim: Claim): { text: string; label: string } {
  const passages = claim.passage_ids.map(getPassage);
  const text = claim.fallback || passages[0].text;
  const fromVerbatim = passages.some((p) => p.kind === 'verbatim' && p.text.includes(text));
  return { text, label: fromVerbatim ? 'Quote' : 'Research note wording' };
}

export interface WindowStateText {
  tag: string;
  text: string;
}

// `state` is a computed state: open, closed, rule_based, not_published, not_checked or source_unavailable.
export function windowStateText(window: ParticipationWindow, state: string): WindowStateText {
  if (state === 'open') {
    return { tag: 'Open', text: 'The quoted date has not passed yet.' };
  }
  if (state === 'closed') {
    return { tag: 'Closed', text: 'The quoted date has passed.' };
  }
  if (state === 'rule_based') {
    return { tag: 'General rule', text: 'This is a general rule, not a date set for this item. Confirm on the item page.' };
  }
  if (state === 'not_published') {
    return { tag: 'No deadline published', text: 'The source was checked and states no deadline.' };
  }
  if (state === 'source_unavailable') {
    return { tag: 'Source unavailable', text: `Muni couldn't read the source. ${window.note}`.trim() };
  }
  return { tag: 'Not checked', text: "Muni hasn't checked a source for this yet." };
}

export function statusClass(tag: string): string {
  if (tag === 'Open') return 'tag tag--open';
  if (tag === 'Closed') return 'tag tag--closed';
  return 'tag';
}

// Three curated snapshots record only a site's home page. A home page link would
// send people to the wrong place, so use the inventory particular's own address instead.
function isSiteRoot(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.pathname === '/' && parsed.search === '';
  } catch {
    return false;
  }
}

export interface LiveLink {
  href: string;
  label: string;
  note: string;
}

export function liveLinks(snapshot: Snapshot): LiveLink[] {
  if (!isSiteRoot(snapshot.url)) {
    return [{ href: snapshot.url, label: 'Open the live source', note: '' }];
  }
  const links: LiveLink[] = [];
  for (const id of snapshot.particular_ids) {
    const particular = findParticular(id);
    if (particular?.url && !isSiteRoot(particular.url)) {
      links.push({
        href: particular.url,
        label: `Open the live source (${id})`,
        note: `This record's saved entry lists only the site's home page, so this link is the address in Muni's research inventory for ${id}.`,
      });
    }
  }
  if (links.length === 0) {
    links.push({ href: snapshot.url, label: 'Open the publisher’s site', note: 'The saved entry lists only the site’s home page, not the document’s own address.' });
  }
  return links;
}

export function availabilityText(value: string | null): string {
  if (value === 'ok') return 'readable';
  if (value === 'blocked') return 'blocked (the site refused automated access)';
  if (value === 'sign_in') return 'needs sign-in';
  if (value === 'dead') return 'dead link';
  if (value === 'request_only') return 'available on request only';
  return 'not known';
}

// "Blocked (…). Not requested: …" — the availability, then the recorded reason as its own sentence.
export function availabilityWithReason(snapshot: Snapshot): string {
  const text = availabilityText(snapshot.availability);
  const status = text.charAt(0).toUpperCase() + text.slice(1);
  if (!snapshot.reason) return status;
  const reason = snapshot.reason.charAt(0).toUpperCase() + snapshot.reason.slice(1);
  return `${status}. ${reason}`;
}

export function fetchSummary(snapshot: Snapshot): string {
  const fetch = snapshot.latest_fetch;
  if (!fetch) return "Muni's fetcher has no saved copy of this address yet. The saved copy isn't published on this site.";
  const status = fetch.status ? `HTTP ${fetch.status}` : 'no HTTP status';
  return `Last fetched ${formatDate(fetch.fetched_at)}: ${status}, ${availabilityText(fetch.availability)}. The saved copy isn't published on this site.`;
}

export function snapshotsForMatter(matter: Matter): Snapshot[] {
  return matter.snapshot_ids.map(getSnapshot);
}

export function wardText(matter: Matter): string {
  if (matter.wards.length === 0) {
    return matter.location.toLowerCase() === 'citywide' ? 'Citywide' : 'Ward not recorded';
  }
  const label = matter.wards.length === 1 ? 'Ward' : 'Wards';
  return `${label} ${matter.wards.join(', ')}`;
}

export function placeText(matter: Matter): string {
  if (matter.location.toLowerCase() === 'citywide') return 'Citywide';
  return `${matter.location} · ${wardText(matter)}`;
}

export function pluralMatters(count: number): string {
  return count === 1 ? '1 matter' : `${count} matters`;
}
