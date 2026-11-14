// The Drift Sentinel fix list as CSV, built with the site so downloading needs no JavaScript.
import { data } from '../../lib/data';
import { availabilityText } from '../../lib/civic';
import { sourcesWithProblems } from '../../lib/staff';

function cell(value: string | null | undefined): string {
  const text = value ?? '';
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

export function GET() {
  const rows: (string | null | undefined)[][] = [
    ['type', 'id', 'topic_or_matter', 'guide_or_claim_text', 'guide_passage', 'rule_or_missing', 'rule_passage', 'difference_or_reason', 'suggested_fix', 'found_on', 'status'],
  ];
  for (const d of data.discrepancies) {
    rows.push([d.kind, d.id, d.topic, d.guide?.text, d.guide?.passage_id, d.rule?.text, d.rule?.passage_id, d.difference, d.suggested_fix, d.found_on, d.status]);
  }
  for (const b of data.blocked_claims) {
    rows.push(['held_back_claim', b.id, b.matter_id, b.text, '', b.missing.join('; '), '', 'Dropped a qualifier its source has', 'Put the missing qualifier back, or record why it is not needed', '', 'open']);
  }
  for (const s of sourcesWithProblems()) {
    const fetchText = s.latest_fetch ? `latest fetch HTTP ${s.latest_fetch.status ?? 'none'}: ${availabilityText(s.latest_fetch.availability)}` : '';
    rows.push(['source_problem', s.id, s.title, s.url, '', `curated: ${s.availability}`, '', [s.reason, fetchText].filter(Boolean).join('; '), 'Download it by hand into manual_inbox/ if the site blocks automated access', s.checked_on, 'open']);
  }
  const csv = rows.map((row) => row.map(cell).join(',')).join('\n') + '\n';
  return new Response(csv, { headers: { 'Content-Type': 'text/csv; charset=utf-8' } });
}
