// Loads public/data/muni.json at build time. pipeline/build.py writes that file;
// docs/data-contract.md describes every field. Only the fields the site uses are typed here.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

export interface Review {
  by: string;
  on: string | null;
  status: string;
  note: string;
}

export interface FetchInfo {
  fetched_at: string;
  url: string;
  final_url: string | null;
  status: number | null;
  availability: string | null;
  sha256: string;
  content_type: string | null;
  obtained_by: string;
  path: string;
}

export interface Snapshot {
  id: string;
  url: string;
  final_url: string | null;
  fetched_at: string;
  checked_on: string;
  sha256: string | null;
  status: number | null;
  obtained_by: string;
  availability: string;
  reason: string;
  particular_ids: string[];
  publisher: string;
  title: string;
  fetch_count: number;
  latest_fetch: FetchInfo | null;
}

export interface Passage {
  id: string;
  snapshot_id: string;
  locator: string;
  kind: 'verbatim' | 'research_note';
  text: string;
  roles: { code: string; method: string }[];
  note: string;
}

export interface Identifier {
  value: string;
  normalized: string;
  kind: string;
  passage_id: string;
  valid_from: string;
  valid_to: string;
  note: string;
}

export interface MatterEvent {
  id: string;
  kind: string;
  date: string;
  actor: string;
  outcome_text: string;
  outcome_kind: 'verbatim' | 'research_note';
  passage_id: string;
  establishes: string;
  not_establishes: string;
}

export interface Condition {
  id: string;
  text: string;
  applies_to: string;
  imposed_by: string;
  passage_id: string;
}

export interface ParticipationWindow {
  id: string;
  action: string;
  channel: string;
  state: string;
  computed_state: string;
  deadline_quote: string;
  deadline_date: string | null;
  passage_id: string;
  checked_on: string;
  note: string;
}

export interface Claim {
  id: string;
  section: string;
  text: string;
  provenance: 'quote' | 'extraction' | 'ai_paraphrase' | 'human';
  passage_ids: string[];
  fallback: string;
  checked_against: Record<string, string>;
  qualifiers_required: string[];
  qualifiers_waived: Record<string, string>;
  review_summary: string;
}

export interface EasyReadLine {
  id: string;
  text: string;
  claim_id: string;
}

export interface Matter {
  id: string;
  title: string;
  topics: string[];
  topic_slugs: string[];
  authority: string;
  authority_ids: string[];
  location: string;
  wards: number[];
  identifiers: Identifier[];
  events: MatterEvent[];
  conditions: Condition[];
  windows: ParticipationWindow[];
  claims: Claim[];
  easy_read: EasyReadLine[];
  status_summary: { latest_event_id: string; latest_event_kind: string; latest_event_date: string } | null;
  particular_ids: string[];
  snapshot_ids: string[];
}

export interface Channel {
  id: string;
  channel: string;
  statement: string;
  passage_id: string;
}

export interface BlockedClaim {
  id: string;
  matter_id: string;
  text: string;
  missing: string[];
}

export interface Discrepancy {
  id: string;
  kind: string;
  topic: string;
  guide: { passage_id: string; text: string } | null;
  rule: { passage_id: string; text: string } | null;
  claim_id: string | null;
  snapshot_id: string | null;
  checked_sha256: string | null;
  latest_sha256: string | null;
  difference: string;
  suggested_fix: string;
  found_on: string;
  status: string;
}

export interface Topic {
  slug: string;
  name: string;
  description: string;
}

export interface Authority {
  id: string;
  name: string;
  tier: string;
}

export interface SearchDoc {
  id: string;
  title: string;
  topics: string[];
  location: string;
  identifiers: string[];
  text: string;
}

export interface Particular {
  id: string;
  title: string;
  level: string;
  summary: string;
  family: string;
  family_name: string;
  subfamily: string;
  subfamily_name: string;
  group: string;
  authority: string;
  url: string;
  access: string;
  access_note: string;
  evidence: string;
  evidence_detail: string;
  authority_status: string;
  primary_role: string;
  primary_reason: string;
  secondary_roles: { code: string; reason: string }[];
  parsing_note: string;
  cross_refs: string[];
  linked_snapshot_ids: string[];
  linked_matter_ids: string[];
  latest_fetch: FetchInfo | null;
}

export interface Endpoint {
  kind: 'particular' | 'role' | 'description';
  value: string;
}

export interface Relationship {
  id: string;
  categories: string;
  chain: Endpoint[][];
  arrows: string[];
  families: string[];
  meaning: string;
  condition: string;
  evidence: string;
  url: string;
  limitation: string;
  connection_basis: string;
  evidence_particular_ids: string[];
}

export interface RelationshipFamily {
  code: string;
  name: string;
  verbs: string;
  meaning: string;
}

export interface DocumentComponent {
  id: string;
  label: string;
  element_type: string;
  description: string;
  source_particular: string;
  url: string;
  subcategory_codes: string[];
}

export interface Role {
  code: string;
  name: string;
  description: string;
  category: string;
  category_name: string;
}

export interface Family {
  name: string;
  subfamilies: Record<string, { name: string; members: string[] }>;
}

export interface Coverage {
  particulars: number;
  by_access: Record<string, number>;
  by_evidence: Record<string, number>;
  by_fetch_availability: Record<string, number>;
  by_snapshot_availability: Record<string, number>;
  by_family: Record<string, number>;
  linked_to_matters: number;
  linked_to_snapshots: number;
  relationships: number;
  historical_retrieval: { yes: number; no: number; total: number; percent: number };
  retrieval_audit_checked: string;
  limits: string[];
}

export interface MuniData {
  checked_on: string;
  generated_on: string;
  snapshots: Snapshot[];
  passages: Passage[];
  matters: Matter[];
  channels: Channel[];
  alias: Record<string, string>;
  blocked_claims: BlockedClaim[];
  discrepancies: Discrepancy[];
  topics: Topic[];
  authorities: Authority[];
  search_docs: SearchDoc[];
  particulars: Particular[];
  relationships: Relationship[];
  relationship_families: RelationshipFamily[];
  document_components: DocumentComponent[];
  families: Record<string, Family>;
  roles: Record<string, Role>;
  inventory: { generated: string; source_check_date: string; described_endpoints: Record<string, string> };
  coverage: Coverage;
}

// `npm run build` runs from web/, so the path is relative to that folder.
const dataPath = join(process.cwd(), 'public', 'data', 'muni.json');

function loadData(): MuniData {
  let text: string;
  try {
    text = readFileSync(dataPath, 'utf8');
  } catch {
    throw new Error(`Can't read ${dataPath}. Run "python3 pipeline/build.py" from the repo root first.`);
  }
  return JSON.parse(text) as MuniData;
}

export const data = loadData();

const passagesById = new Map(data.passages.map((p) => [p.id, p]));
const snapshotsById = new Map(data.snapshots.map((s) => [s.id, s]));
const particularsById = new Map(data.particulars.map((p) => [p.id, p]));
const mattersById = new Map(data.matters.map((m) => [m.id, m]));

// The build already checks every reference, so a missing id here is a real bug: fail loudly.
export function getPassage(id: string): Passage {
  const passage = passagesById.get(id);
  if (!passage) throw new Error(`muni.json has no passage ${id}`);
  return passage;
}

export function getSnapshot(id: string): Snapshot {
  const snapshot = snapshotsById.get(id);
  if (!snapshot) throw new Error(`muni.json has no snapshot ${id}`);
  return snapshot;
}

export function findParticular(id: string): Particular | undefined {
  return particularsById.get(id);
}

export function getMatter(id: string): Matter {
  const matter = mattersById.get(id);
  if (!matter) throw new Error(`muni.json has no matter ${id}`);
  return matter;
}

export function mattersInTopic(slug: string): Matter[] {
  return data.matters.filter((m) => m.topic_slugs.includes(slug));
}
