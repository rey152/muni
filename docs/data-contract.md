# Muni data contract

`python3 pipeline/build.py` writes one file that the website reads:

- `web/public/data/muni.json` (new site)
- `site/data/muni.json` (old prototype, the same bytes, until it's retired)

It also copies `site/data/wards.geojson` to `web/public/data/wards.geojson`. Both `muni.json` files are build output and are gitignored, so run the build before starting either site.

The record models are in `pipeline/models.py`. Their JSON Schemas are in `schema/<Model>.json` and the class diagram is `docs/uml.md`. The build regenerates all three, and a test fails if they're out of date. This page describes the exported file, which adds a few computed fields to those models.

Types: `str`, `int`, `float`, `bool`, `null`, `[T]` is a list, `{K: V}` is an object. `str?` means the value can be `null`. Dates are `YYYY-MM-DD` text unless noted.

## What the build guarantees

The build stops with an error, and writes nothing, if any of these fails:

- Every claim cites at least one passage that exists and has a `provenance`.
- Every window with a `deadline_date` has a `deadline_quote` and a `passage_id`. The quote is found word for word in the passage, and the date is written in the quote (`Nov 8, 2026` → `2026-11-08`). Dates are never worked out from a meeting date.
- Every event's `outcome_text` is found word for word in its passage. So are condition texts and channel statements.
- No claim, event, window, condition, identifier, Easy Read line or channel is exported unless its `review.status` is `approved`. Anything with no review block counts as `pending`.
- Correspondence passages are never exported, and the build fails if anything cites one. A passage counts as correspondence when it has role `C2`, or when its snapshot belongs to a DF11.1 or DF11.2 particular (bound consultation appendices and comment-response tables).
- Ids are unique, and every reference points at a record that exists: passages, snapshots, topics, authorities, inventory particulars.
- No two matters share a normalized identifier.
- The inventory has all 267 particulars P001–P267 exactly once. Every relationship endpoint is a role code, a particular id, or a listed description (`inventory.described_endpoints`).

These don't stop the build. They hold items back instead:

- Claims that fail the Qualifier Keeper go to `blocked_claims`, not `matters`.
- Easy Read lines are checked together per claim, since one claim is often split over two lines. If the lines for a claim drop a qualifier the claim's passages carry (and the claim hasn't waived it), all of that claim's lines go to `blocked_easy_read`, not `matters[].easy_read`. The claim itself can still be exported.
- Claims whose source changed since review (source drift) get `review.status: "needs_recheck"` in memory and are left out until someone reviews them again. The review files on disk aren't changed. A claim only drifts when the newest ok fetch of a snapshot in its `checked_against` has a different sha256 and its cited passage isn't still there word for word. Research-note passages can't be looked up, so any hash change flags those claims.

The NLI check never holds anything back. Its results are in `nli_checks` for staff.

## Top level

| Field | Type | Meaning |
|---|---|---|
| `checked_on` | str | Date the curated records were checked (`review/index.yaml`). |
| `generated_on` | str | Date the build ran. Window states were computed against this date. |
| `snapshots` | [Snapshot] | Every record Muni cites. |
| `passages` | [Passage] | Every passage, minus correspondence. |
| `matters` | [Matter] | Approved content only, in `review/index.yaml` order. |
| `channels` | [Channel] | What each comment channel says about publication (Exposure Preview). |
| `alias` | {str: str} | Normalized identifier → matter id (Item Passport). |
| `blocked_claims` | [BlockedClaim] | Claims the Qualifier Keeper stopped. For the staff page only. |
| `blocked_easy_read` | [BlockedEasyRead] | Easy Read lines held back because their set for a claim dropped a qualifier. For the staff page only. |
| `easy_read_checks` | [EasyReadCheck] | Reading grade and Qualifier Keeper results for each matter's Easy Read set, before anything was held back. For the staff page only. |
| `nli_checks` | [NliCheck] | One NLI result per exported claim. Flags for a person to look at, never a gate. For the staff page only. |
| `discrepancies` | [Discrepancy] | Drift Sentinel findings. For the staff page only. |
| `topics` | [Topic] | The six public topics. |
| `authorities` | [Authority] | Bodies matters name in `authority_ids`. |
| `search_docs` | [SearchDoc] | One document per matter, for MiniSearch. |
| `particulars` | [Particular] | All 267 inventory particulars. |
| `relationships` | [Relationship] | The 21 typed graph edges (L01–L21). |
| `relationship_families` | [RelationshipFamily] | R1–R8. |
| `document_components` | [DocumentComponent] | Components inside one particular (P071-ASSESSMENT, P071-REVIEW). |
| `families` | {str: Family} | Document families DF01–DF20: `{name: str, subfamilies: {code: {name: str, members: [str]}}}`. |
| `roles` | {str: Role} | Information roles A1–G3: `{code, name, description, category, category_name, category_description}`, all str. |
| `inventory` | object | `generated: str`, `source_check_date: str`, `described_endpoints: {str: str}` (free-text graph endpoints and why they're allowed). |
| `coverage` | Coverage | Counts over the inventory. |

## Snapshot

| Field | Type | Meaning |
|---|---|---|
| `id` | str | e.g. `S-p209`. |
| `url` | str | Source URL. `S-region-escribe` only records the eScribe site root; see "Known gaps". |
| `final_url` | str? | URL after redirects, if recorded. |
| `fetched_at` | str | When the curated record was obtained (date or ISO timestamp). |
| `checked_on` | str | The snapshot's own check date, or top-level `checked_on`. |
| `sha256` | str? | Hash of the newest ok fetch of `url`, copied in by `pipeline/link_snapshots.py`. `null` when there's no ok fetch (blocked hosts). |
| `content_type` | str? | |
| `status` | int? | HTTP status recorded with the curated snapshot. |
| `obtained_by` | `"chromium"` \| `"manual"` | |
| `availability` | `"ok"` \| `"blocked"` \| `"sign_in"` \| `"dead"` \| `"request_only"` | As curated. Anything other than `ok` has a `reason`. |
| `reason` | str | Why it's unavailable; `""` if available. |
| `particular` | str | Inventory ids as written, e.g. `"P011-P014,P196,P197"`. |
| `particular_ids` | [str] | The same, expanded. |
| `publisher` | str | |
| `title` | str | |
| `path` | str? | Local file, if any. |
| `fetch_count` | int | Rows in `snapshots/snapshots.sqlite` whose URL matches. Site-root URLs are never matched. |
| `latest_fetch` | FetchInfo? | Most recent real fetch of this URL, or `null`. |

**FetchInfo** (one row `pipeline/fetch.py` wrote): `fetched_at: str` (UTC ISO), `url: str`, `final_url: str?`, `status: int?`, `availability: str?`, `sha256: str`, `content_type: str?`, `obtained_by: str`, `path: str`. `availability` comes from the HTTP status: 2xx → `ok`, 401 → `sign_in`, 403 → `blocked`, 404/410 → `dead`, a manual file → `ok`, anything else → `null`. A 200 can still be a bot-check page; the status alone can't tell.

## Passage

| Field | Type | Meaning |
|---|---|---|
| `id` | str | e.g. `PA-p209-objection`. |
| `snapshot_id` | str | |
| `locator` | str | Human-readable place (the locator's label, or `p.N`, or the element path). The old site prints this string. |
| `locator_detail` | object | `{page: int?, char_start: int?, char_end: int?, element_path: str?, label: str}`. |
| `kind` | `"verbatim"` \| `"research_note"` | A research note is a researcher's summary, not source text. Label it that way on screen. |
| `text` | str | |
| `roles` | [{code: str, method: `"rule"`\|`"llm"`\|`"human"`}] | Information roles. `llm` tags are hints, never evidence. |
| `note` | str | Reviewer note. |

## Matter

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Slug, also the review file name. |
| `title` | str | |
| `topics` | [str] | Topic names (as in `topics[].name`). |
| `topic_slugs` | [str] | The same topics as slugs. |
| `authority` | str | Display text for who decides. |
| `authority_ids` | [str] | Ids in `authorities`. |
| `location` | str | Address, place, or `"citywide"`. |
| `wards` | [int] | 1–7. Empty for citywide. |
| `identifiers` | [Identifier] | |
| `events` | [Event] | In record order. Sort by `date` to show them in time. |
| `conditions` | [Condition] | |
| `windows` | [Window] | |
| `claims` | [Claim] | Approved claims that passed every check. |
| `easy_read` | [EasyReadLine] | Lines whose parent claim was exported. |
| `status_summary` | object? | `{latest_event_id, latest_event_kind, latest_event_date}` (str), the event with the latest `date`. `null` if no events. Partial dates sort as text, so `"2026"` sorts before `"2026-01-05"`. |
| `particular_ids` | [str] | Inventory particulars behind the snapshots this matter cites. Snapshot-level: citing one page of the Dec 8 packet links all six packet particulars. |
| `snapshot_ids` | [str] | Snapshots this matter cites. |

Every item below also carries `matter_id: str` and `review: Review`.

**Review**: `by: str`, `on: str?`, `status: "approved" | "edit" | "reject" | "needs_recheck" | "pending"`, `note: str`. Items migrated from the prototype say `by: "not recorded"` and `on: null`, because the old file didn't record who approved them or when.

**Identifier**: `value: str`, `normalized: str`, `kind: "report no." | "file no." | "by-law no." | "OPA no." | "MD no." | "address"`, `passage_id: str`, `valid_from: str`, `valid_to: str` (`""` when unknown), `note: str`.

**Event**: `id: str`, `kind`: one of `proposed`, `staff_recommendation`, `committee_action`, `council_decision`, `mayoral_instrument`, `provincial_decision`, `appeal_window`, `in_force`, `repealed`, `amended`, `implemented`. `date: str` (`YYYY`, `YYYY-MM` or `YYYY-MM-DD`), `actor: str`, `outcome_text: str` (word for word from the passage), `outcome_kind: "verbatim" | "research_note"` (the cited passage's kind), `passage_id: str`, `establishes: str`, `not_establishes: str`.

**Condition**: `id: str`, `text: str` (word for word from the passage), `applies_to: str`, `imposed_by: "decision" | "report" | "study_mitigation"`, `passage_id: str`.

**Window**:

| Field | Type | Meaning |
|---|---|---|
| `id` | str | |
| `action` | str | What a resident can do. |
| `channel` | str | How, as the source says. |
| `state` | `"dated"` \| `"rule_based"` \| `"not_published"` \| `"not_checked"` \| `"source_unavailable"` | The stored input. The old site reads this and works out open or closed itself. |
| `computed_state` | `"open"` \| `"closed"` \| `"rule_based"` \| `"not_published"` \| `"not_checked"` \| `"source_unavailable"` | `dated` becomes `open` if `deadline_date >= generated_on`, else `closed`. Recompute in the browser against today, since the file can be days old. |
| `deadline_quote` | str | Verbatim from the passage. Never show a date without it. |
| `deadline_date` | str? | Only for `dated`, and only as written in the quote. |
| `passage_id` | str | |
| `checked_on` | str | Window's own check date, or top-level `checked_on`. |
| `note` | str | Required for `source_unavailable` (why). |

`not_published` means the source was checked and states no deadline. `not_checked` means it wasn't checked. Keep them apart on screen.

**Claim**:

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Unique across all matters. |
| `section` | str | `applies_to`, `what_and_why`, `who_decides`, `conditions`, `not_decided`, `have_a_say` or `records`. |
| `text` | str | |
| `provenance` | `"quote"` \| `"extraction"` \| `"ai_paraphrase"` \| `"human"` | How the text was made, not whether it's true. |
| `passage_ids` | [str] | At least one. |
| `fallback` | str | Source wording shown when "Show without AI" hides an `ai_paraphrase`. Required for those. |
| `checked_against` | {str: str} | Snapshot id → sha256 the claim was checked against. Source drift compares it with the newest fetch. Empty when every cited passage comes from a snapshot with no ok fetch (the Dec 8 packet and minutes). See "Known gaps" for how the current values were filled. |
| `qualifiers_required` | [str] | Qualifier markers found in the cited passages. |
| `qualifiers_waived` | {str: str} | Marker → reviewer's reason it isn't needed in this sentence. |
| `review_summary` | str | e.g. `"Approved. Reviewer: not recorded. Date: not recorded."` |

**EasyReadLine**: `id: str`, `text: str`, `claim_id: str`, `grade_level: float?`. The build fills `grade_level` on every exported line: Flesch-Kincaid grade from textstat, rounded to one decimal, never below 0. The target is about grade 5–6, as a guide, not a gate. A formula like this only counts syllables and sentence length, so a low grade doesn't prove a line is easy to understand.

## Other lists

**Channel**: `id`, `channel`, `statement` (word for word from the passage), `passage_id`, `review`.

**BlockedClaim**: `id: str`, `matter_id: str`, `text: str`, `missing: [str]` (markers the claim dropped).

**BlockedEasyRead**: `id: str`, `matter_id: str`, `claim_id: str`, `text: str`, `missing: [str]` (markers the claim's set of lines dropped, read together).

**EasyReadCheck**: `matter_id: str`, `target: str` (`"About grade 5-6. A guide, not a gate."`), `set_grade_level: float?` (all lines read as one text; `null` with no lines), `set_above_target: bool`, `line_count: int`, `lines: [{id, claim_id, text: str, grade_level: float, above_target: bool, qualifiers_required: [str], qualifiers_missing: [str]}]`, `claims_missing_qualifiers: {claim_id: [str]}`. It covers the approved lines of exported claims, before anything was held back, so a held-back line still shows here with what it missed.

**NliCheck**: `claim_id: str`, `matter_id: str`, `available: bool`, `model: str` (`cross-encoder/nli-deberta-v3-base`), `flag: bool`, `reason: str`; when `available`, also `scores: {contradiction, entailment, neutral: float}` and `label: str` (the highest score). The premise is the claim's cited passages joined with newlines; the hypothesis is the claim text. `flag` is true for `contradiction`, or entailment below 0.5. Research notes are short summaries, so many of their claims are flagged; a flag means "a person should look", and a clean result doesn't mean the claim is right. The build only uses a model already on disk (it never downloads one). Without transformers and torch, or without the model, every result is `available: false` with the reason, and nothing else changes.

**Discrepancy**: `id: str`, `kind: "rule_drift" | "source_drift"`, `topic: str`, `guide: {passage_id, text}?` and `rule: {passage_id, text}?` (rule drift's two sides), `claim_id: str?`, `snapshot_id: str?`, `checked_sha256: str?`, `latest_sha256: str?` (source drift), `difference: str`, `suggested_fix: str`, `found_on: str`, `status: "open" | "resolved"`. A difference doesn't say which source is right.

**Topic**: `slug`, `name`, `description` (str).

**Authority**: `id: str`, `name: str`, `tier: "City" | "Region" | "Province" | "tribunal"`.

**SearchDoc**: `id: str` (matter id), `title: str`, `topics: [str]`, `location: str`, `identifiers: [str]` (as written), `text: str` (exported claims and Easy Read lines joined).

**Alias normalization**: lowercase, then `by-law`/`bylaw` → `bylaw`, then remove spaces, `-`, `_` and `.`. So `By-law 2025-086`, `bylaw 2025 086` and `BYLAW2025086` all become `bylaw2025086`. `models.normalize_identifier` and `norm()` in `site/app.js` must stay identical. Check the alias map first; if nothing matches, use MiniSearch, and say "no match" rather than guess.

## Inventory

**Particular** (both inventory files merged by id):

| Field | Type | Source |
|---|---|---|
| `id`, `title`, `level`, `summary` | str | classified |
| `family`, `family_name`, `subfamily`, `subfamily_name` | str | classified |
| `components` | [str] | classified: document-family codes of components inside it |
| `group`, `authority`, `url`, `access`, `access_note`, `pull_confirmed`, `publication_structure`, `transferability`, `extraction` | str | supplied baseline (same in both files) |
| `retrieval_urls` | [str] | supplied baseline |
| `original_response_status` | int? | graph |
| `original_response_kind` | str? | graph |
| `primary_role`, `primary_reason` | str | this research pass |
| `secondary_roles` | [{code: str, reason: str}] | this research pass |
| `role_note`, `supplied_roles` | str | classified |
| `supplied_primary` | str | graph's primary role. Differs from `primary_role` for 31 particulars. |
| `categories` | [str] | graph role codes |
| `classification_reason` | str | graph |
| `parsing_note`, `evidence`, `evidence_detail`, `authority_status` | str | classified |
| `evidence_references` | [str] | graph: local research-evidence paths, not included here |
| `cross_refs` | [str] | particular ids |
| `linked_snapshot_ids` | [str] | curated snapshots naming this particular |
| `linked_matter_ids` | [str] | matters citing those snapshots |
| `latest_fetch` | FetchInfo? | latest real fetch matched by particular id, its URLs, or its snapshots' URLs |

**Relationship**: `id: str`, `categories: str` (the edge as written, e.g. `"C1 → C2 → C3"`), `from: [Endpoint]` (first node), `to: [Endpoint]` (last node), `chain: [[Endpoint]]` (every node in order, so middle steps aren't lost), `arrows: ["→" | "↔"]` (between consecutive nodes), `families: [str]` (R1–R8), `meaning`, `condition`, `evidence`, `url`, `limitation`, `connection_basis`, `dependency`, `retrieval_dependency`, `access_context`, `evidence_url_current_test` (str), `evidence_particular_ids: [str]` (particulars whose URL is the evidence URL). **Endpoint**: `{kind: "particular" | "role" | "description", value: str}`. All 21 current edges join role codes; L21 ends in the description "linked A/B/etc. resources".

**RelationshipFamily**: `code`, `name`, `verbs`, `meaning` (str).

**DocumentComponent**: `id`, `label`, `element_type`, `description`, `source_particular`, `url` (str), `subcategory_codes: [str]`.

**Coverage**: `particulars: int`; count objects `{value: int}` named `by_access`, `by_response_status`, `by_evidence`, `by_fetch_availability` (`not_fetched` when no real fetch, `unknown` when the status says nothing), `by_snapshot_availability` (curated snapshots), `by_family`, `by_level`, `by_authority`, `by_primary_role`, `by_any_role` (primary plus secondary, once per particular), `by_relationship_family`; `linked_to_matters: int`, `linked_to_snapshots: int`, `relationships: int`, `historical_retrieval: {yes, no, total, percent}`, `retrieval_audit_checked: str`, `limits: [str]`. Fetch counts are per particular, so one 403 on the Dec 8 packet counts once for each of its six particulars. None of these counts measure extraction or answer accuracy; show `limits` next to them.

## Known gaps

- `S-dec8-packet`, `S-dec8-revised` and `S-dec8-minutes` are `blocked`: events.waterloo.ca answered HTTP 403, so the host was left alone. They have no sha256, and the claims that cite only them (C-f2, C-f3, C-d1–C-d4) have an empty `checked_against`, so source drift can't watch them. They need a manual download into `manual_inbox/`.
- Dossier N21 says `S-dec8-packet`'s URL is the 9-page agenda and the 313-page packet has a different URL. That hasn't been checked, because the host is blocked.
- `S-region-escribe` records only the eScribe site root (a Cloudflare browser check blocked it), so it's never matched to a fetch.
- The current `checked_against` values were filled in on 2026-11-14 from `review/snapshots.yaml`, not recorded by a reviewer at review time (the migrated reviews don't say what was checked or when). They are the newest ok fetch of each snapshot. For S-p209, the verbatim passages were found word for word in that file. The other cited passages are research notes, which can't be matched word for word; their numbers and dates were spot-checked against the file's text (some differ only in spacing, like `2026 -080`). They are a baseline for drift, not proof that a person re-read that exact file.
- `ER-d4` was relinked from `C-d4` to `C-d2` on 2026-11-14 (text unchanged). It repeats C-d2's second sentence, and without it C-d2's Easy Read lines dropped "not yet".

## How to add a matter

1. Make sure each record you'll cite is in `review/snapshots.yaml` with its `particular` id(s) from the inventory. Fetch it with `python3 pipeline/fetch.py <url> P###`. If the site blocks automated access, download it by hand into `manual_inbox/` and run `python3 pipeline/fetch.py --inbox P###`. Don't work around a block.
2. Add each passage you'll cite to `review/passages.yaml`: the exact text, a locator, its roles, and `kind: verbatim` only if the text is copied from the snapshot. Otherwise use `research_note`.
3. Create `review/matters/<matter-id>.yaml`. The file name must equal `id`. Fill in `title`, `topics` (names from `review/topics.yaml`), `authority`, `authority_ids`, `location`, `wards`, then `identifiers`, `events`, `conditions`, `windows`, `claims` and `easy_read`. Copy an existing matter file for the shape.
4. Give every item a `review:` block with `by`, `on` (`YYYY-MM-DD`) and `status`. Only `approved` items are published.
5. Add the matter id to `matters:` in `review/index.yaml`, in the order the site should list it.
6. Run `python3 pipeline/build.py` and `python3 -m pytest -q tests`. Fix whatever the build reports. It names the item and the rule.
