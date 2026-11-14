// What the staff page and its CSV list. Kept in one place so both say the same thing.
import { data } from './data';
import type { Snapshot } from './data';

// A source needs attention when its curated availability isn't "ok", or when the
// latest real fetch of its address didn't get through. The two can disagree on purpose.
export function sourcesWithProblems(): Snapshot[] {
  return data.snapshots.filter((s) => s.availability !== 'ok' || (s.latest_fetch && s.latest_fetch.availability !== 'ok'));
}

export function claimsNeedingRecheck() {
  return data.discrepancies.filter((d) => d.kind === 'source_drift');
}

export function claimsWithoutCheckedHash(): number {
  return data.matters.reduce((count, m) => count + m.claims.filter((c) => Object.keys(c.checked_against ?? {}).length === 0).length, 0);
}
