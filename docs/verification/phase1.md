# Phase 1 verification

Checked on 2026-11-14 by an independent verifier, from a clean state, against `Muni-implementation-plan.md` §5, the inventory in `data/inventory/`, `docs/data-contract.md` and the `muni-design-system` skill. Nothing in this pass changed code or data. Only this file was written.

| Item | Result |
|---|---|
| Clean run (tests, build, staff report, web build, site checker) | PASS |
| (a) §5 hard rules, read from the export | FAIL (3 rules pass; 2 have problems, see below) |
| (b) 267 particulars and 21 relationships in the export | PASS |
| (c) Curated snapshots: no placeholder url, availability matches the latest fetch | FAIL (S-region-escribe; S-dec8-packet notes) |
| (d) Git status and ignore rules | PASS for ignore rules; the committed tree doesn't run |
| (e) 5 screenshots at 390 and 5 at 1280 against the design system | PASS with 2 small issues |
| (f) Network requests that could carry a resident's location or draft text | FAIL (search query in the url) |

## Clean run

Commands, run in this order from `/Users/rediateabaineh/Downloads/muni` after `rm -rf web/dist pipeline/muni.sqlite`:

- `python3 -m pytest -q tests`: `61 passed in 4.52s`
- `python3 pipeline/build.py` (exit 0):
  - `Exported 4 matters, 20 claims, 1 blocked, 1 discrepancies -> web/public/data/muni.json, site/data/muni.json`
  - `BLOCKED C-planted: missing ['not a', 'not yet']`
  - `NLI (staff only, not a gate): 20 claims checked, 14 flagged [...]`
- `python3 pipeline/staff_report.py`: `Wrote 1 discrepancy rows to staff/drift.csv, staff/drift.json`, `D-RP-p253-lobbyist: Guide says 10 days; the rule says 10 business days.`
- `cd web && npm ci`: `found 0 vulnerabilities`
- `npm run build`: `26 page(s) built`, `Complete!`
- `node scripts/check-site.mjs`: `All checks passed.` Notes included `OpenFreeMap requests after locating and tapping (should be none, the map isn't moved): 0` and the offline map message.

`web/public/data/muni.json` and `site/data/muni.json` are byte-identical (`cmp`).

## (a) §5 hard rules: FAIL

I read `web/public/data/muni.json` with my own script, not the pipeline's checks. The export has 4 matters, 20 claims, 10 events, 4 windows and 17 passages.

| Rule | Result | Evidence |
|---|---|---|
| Every Claim has at least one passage_id and a provenance | PASS | 20 of 20 claims have passage_ids that resolve to exported passages, and provenance is one of quote / extraction / ai_paraphrase / human. |
| A window with a deadline_date has a deadline_quote and a passage_id; the date is never derived | PASS as written, but see W-k1 | Two dated windows: W-h1 (2026-11-06) and W-k1 (2026-11-08). Both have a quote and a passage, and the date is written in the quote. **W-k1's "quote" is a research note** (`PA-p210-appeal`, kind `research_note`): "Appeal to the Ontario Land Tribunal (OLT) ending Nov 8, 2026." The data contract says `deadline_quote` is verbatim. The source PDF S-p210 is now fetched (sha256 11ecf4a2…), and its text reads "The last day for filling an appeal i s November 8, 2026", so a verbatim passage is available. |
| Every Event's outcome_text is verbatim from its passage | FAIL in substance | All 10 outcome_texts appear word for word in their cited passage. But 7 of 10 cite `research_note` passages (EV-f1, EV-f2, EV-f3, EV-f5, EV-d1, EV-k1, EV-k2), so the text is a researcher's summary and not the source's words. The contract allows this through `outcome_kind`, and the site labels each one "Muni's research note (not its exact words)". The three Dec 8 sources are blocked, so the fees and debt events can't be fixed yet. EV-k1 and EV-k2 cite S-p210, which is now fetched, so they can. The same applies to conditions CO-f1, CO-d1, CO-d2 and CO-k1. |
| No Claim with review.status != approved is exported | PASS | All 20 exported claims, plus every event, window, condition, identifier, Easy Read line and channel, are `approved`. C-planted is held back (`blocked_claims`). Every review says `by: "not recorded"`, carried over from `review/matters.json`. |
| Correspondence passages excluded; no personal details exported | PASS | No exported passage has role C2. `build.py` has a correspondence gate (`check_correspondence`). A regex scan of the whole export found no email address, phone number or postal code. |

Other problems found while checking:
- **C-d4 says it is a quote but isn't one.** It has `provenance: "quote"` and the text "The final provincial limit is not yet received." Its only passage, PA-debt-calc (a research note), reads "…final provincial limit not yet received." The site shows quote-provenance claims as exact source words.
- **Easy Read relink:** ER-d4 now points to C-d2, as the WIRE report says.

## (b) Particulars and relationships: PASS

- `particulars`: 267 in the export. No ids are missing or extra compared with `data/inventory/Waterloo-particulars-classified.json` (identical to the copy in `Context/`) or `Claude-Waterloo-context.json`. Every field the source has is exported unchanged (0 field differences).
- `relationships`: 21 (L01–L21). None are missing or extra compared with `Claude-Waterloo-context.json`, and there are 0 field differences. `relationship_families` 8 and `document_components` 2 also match the source counts.

## (c) Curated snapshots: FAIL

I compared `review/snapshots.yaml` with `snapshots/snapshots.sqlite` (`snapshots` and `fetch_log`) and with each export snapshot's `latest_fetch`.

| Id | url | Availability | Latest fetch | Verdict |
|---|---|---|---|---|
| S-bylaw-2026-047 | `…/zeqjquvr/fees-and-charges-bylaw.pdf` | ok | 200 ok, 15:43:34Z, bb5ba2ad… | match |
| S-p209 | `…/jtzfarez/notice-of-intention-to-designate-131-william-st-w.pdf` | ok | 200 ok, edea81c3… | match |
| S-p210 | `…/kj2cb4ri/15-king-street-north-notice-of-passing.pdf` | ok | 200 ok 18:56:52Z, 11ecf4a2… (an ENOTFOUND at 16:01 sits between two ok fetches) | match |
| S-p202 | register-to-speak page | ok | 200 ok, b3fe8cc4… | match |
| S-p253-page / S-p253-bylaw | Region pages | ok | 200 ok, hashes match | match |
| S-dec8-packet | `…/949c2f40-…` | blocked | `snapshots` row 14:33:53Z, HTTP 403 for this exact url; `fetch_log` 15:39:49Z not_tried | availability matches; reason wrong (see below) |
| S-dec8-revised / S-dec8-minutes | `…/1cdc7d1e-…`, `…/40f19d1e-…` | blocked | fetch_log `not_tried` (host refused at `/meetings/`, 403 at 15:36:48Z) | consistent with policy |
| **S-region-escribe** | `https://pub-regionofwaterloo.escribemeetings.com/` (site root) | blocked | **no fetch of this url** | **FAIL** |

Problems:
1. **S-region-escribe has a placeholder url.** It is the site root, which no one ever fetched, with `fetched_at: '2026-11-13'` and availability `blocked`. Its `particular` is **P147**, but P147 is the floodplain staff report on the City CDN, which was fetched **ok** (`…/x4dg5hdc/floodplain-staff-report.pdf`). The eScribe particulars are P019 (`filestream.ashx?DocumentId=13783`, HTTP 403 blocked at 15:36:54Z) and P211 (`DocumentId=13240`, not_tried). No passage cites S-region-escribe, but it is exported and shown on /sources/.
2. **S-dec8-packet's reason says "not requested", but it was requested.** sqlite has a 403 for that exact url at 14:33:53Z, and the body is hashed (f7f4841a…). The curated `fetched_at` (15:36:48Z) is the time of the `/meetings/` 403, a different url.
3. **S-dec8-packet's title doesn't match its url** (already reported by FETCH, still open). The guide (line 663) and dossier N21 identify `949c2f40-…` as the 9-page agenda, and `197061bb-…` as the 313-page packet (guide line 1404, ref `[df04-dec8]`). The site shows "City Council packet, December 8, 2025 (313 pages)" as the source of every fees and debt claim.
4. The export's `latest_fetch` is read only from the `snapshots` table, so S-dec8-revised and S-dec8-minutes show `latest_fetch: null` even though `fetch_log` has a `not_tried` row for each. This is minor.

`snapshots/fetch-report.json`: 294 urls, `{'ok': 275, 'blocked': 4, 'not_tried': 12, 'sign_in': 1, 'error': 1, 'dead': 1}`. This matches the FETCH and WIRE reports.

## (d) Git status: PASS for ignore rules, but the committed tree can't run

`git status --short --ignored` shows these ignored: `.pytest_cache/`, `manual_inbox/`, `__pycache__/` (pipeline, checks, tests), `pipeline/muni.sqlite`, `pipeline/nli_cache.json`, `site/data/muni.json`, `snapshots/.chrome-profile/`, every snapshot `.pdf/.zip/.png/.bin`, the engagewr.ca token HTML, `staff/`, `web/.astro/`, `web/dist/`, `web/node_modules/`, `web/public/data/muni.json` and `web/test-screens/`. No tracked file matches an ignore rule (`git ls-files -ci --exclude-standard` is empty), and no tracked file is over 1 MB. `snapshots/snapshots.sqlite` (364 KB) is tracked on purpose: plan §3 keeps hashes in the database. `pipeline/ai_cache.json` is tracked on purpose. Tracked `*.requests.json` files have `access_token=REDACTED`.

`git add -A --dry-run` would stage exactly these 63 paths:

```
remove review/matters.json
add data/inventory/Claude-Waterloo-context.json
add data/inventory/Muni-new-ideas-catalogue.md
add data/inventory/Waterloo-particulars-classified.json
add docs/research/ideas/{N109,N113,N123,N124,N20,N21,N31,N37,N43,N58}.md
add docs/uml.md
add pipeline/{ai.py,ai_cache.json,diffs.py,easyread.py,inventory.py,models.py,review_io.py,staff_report.py,store.py}
add pipeline/checks/{drift.py,nli.py,qualifier.py}
add review/{ai-log.jsonl,authorities.yaml,channels.yaml,index.yaml,passages.yaml,planted.yaml,rule_pairs.yaml,topics.yaml}
add review/suggestions/debt-limit-2026.yaml
add schema/{Authority,Channel,Claim,Condition,Discrepancy,DocumentComponent,EasyReadLine,Endpoint,Event,FetchInfo,Identifier,Locator,Matter,ParticipationWindow,Particular,Passage,PassageRef,PlantedClaim,Relationship,RelationshipFamily,Review,Role,RulePair,SecondaryRole,Snapshot,Topic}.json
add tests/test_checks.py
```

None of these should be ignored. The largest is `data/inventory/Waterloo-particulars-classified.json` at 673 KB. This file (`docs/verification/phase1.md`) is new and is committed separately.

**The pushed HEAD doesn't run.** I ran `git archive HEAD` into a scratch folder, then `python3 pipeline/build.py` gave `ModuleNotFoundError: No module named 'easyread'`, and `pytest` gave `1 error during collection`. The modules and review files listed above are still untracked. `manual_inbox/README.md` can't be committed while all of `manual_inbox/` is ignored.

## (e) Screenshots: PASS with 2 small issues

I looked at home-390-light, matter-fees-390-light, near-me-390-dark, q-have-a-say-390-light and easy-read-390-dark, and at home-1280-light, matter-debt-1280-dark, search-1280-light, topic-1280-light and staff-1280-light. I cropped the tall pages into readable sections.

What matches the design system:
- Paper and Dusk grounds, Fredoka throughout, and a civic-navy header and rail.
- Topic tiles: 4 columns at 1280 and 2 at 390, each with its topic glyph.
- Pill status chips; the alert uses a dot, not a coloured box; dashed "not the official notice" boxes.
- Ledger rows with date stamps and chevrons; sentence case; one primary button per screen.
- Research notes are labelled "not the source's exact words".
- The off-palette hex values in `global.css` (`#000`, `#999`, `#fff`) are only in the print block. The built CSS uses font sizes 12–40px, and nothing is under 12px.

Issues:
1. The matter header reads "From **1 official records**" on the debt page (`web/src/pages/matter/[id]/index.astro:91` has no singular form).
2. On Dusk, the near-me basemap stays a light OpenFreeMap style, so the map is a bright block on the evening ground. This is cosmetic. The fixed bottom tab bar appears mid-page in full-page screenshots. That is how Playwright captures fixed elements, not a layout bug.

## (f) Network requests carrying location or draft text: FAIL

I grepped `web/dist/_astro/*.js` and every inline script in `web/dist/**/*.html` for `fetch(`, `XMLHttpRequest`, `sendBeacon`, `WebSocket`, `EventSource`, `geolocation`, storage APIs, forms and absolute hosts.

- **Near me: PASS.** `getCurrentPosition` coordinates go only to Turf (`booleanPointInPolygon`) and a map marker (`setLngLat`). The app's own `fetch` is `/data/wards.geojson`, and the map is never moved to the person. `history.replaceState` writes `#ward-N`, and a fragment is never sent to the server. localStorage stores the ward number only after the person ticks the box. External hosts in the bundle are `tiles.openfreemap.org` plus the usual MapLibre strings. The checker confirmed 0 tile requests after locating.
- **Draft check: PASS.** `src/scripts/comment.ts` makes no network call, and the draft goes to localStorage only on the save button. `<textarea id="draft" spellcheck="true">`: Chrome's opt-in "enhanced spell check" sends field text to Google. This is minor; `spellcheck="false"`, or a note, would close it.
- **Search: FAIL.** Both search forms (`index.astro` and `search.astro`) are `<form action="/search/" method="get">`, and `search.ts` reads `new URLSearchParams(window.location.search).get('q')`. The home page asks people to search "by … street". So a typed address such as `?q=123 King St N` goes to the static host in the request line and ends up in its access logs, and in browser history and any Referer. Plan §1 says the resident's address stays in the browser. Using the fragment (`#q=`), or handling submit in JS without navigating with a query, would keep it local.

## Bugs found

1. `review/snapshots.yaml` (S-region-escribe): the url is the site root, which was never fetched; `particular: P147` is wrong (P147 is the City floodplain report, fetched ok); `fetched_at: '2026-11-13'` has no matching fetch. To reproduce, run `sqlite3 snapshots/snapshots.sqlite "select * from fetch_log where url='https://pub-regionofwaterloo.escribemeetings.com/'"`, which returns nothing.
2. `review/snapshots.yaml` (S-dec8-packet): the reason says "not requested", but sqlite has a 403 for that exact url at 2026-11-14T14:33:53Z. The title says "packet (313 pages)", but the guide and N21 say `949c2f40-…` is the 9-page agenda. To reproduce, run `sqlite3 snapshots/snapshots.sqlite "select fetched_at,status from snapshots where url like '%949c2f40%'"`.
3. The C-d4 claim (in `review/matters/debt-limit-2026.yaml`) has `provenance: quote`, but its text isn't verbatim from PA-debt-calc. To reproduce, compare "The final provincial limit is not yet received." with the passage "…final provincial limit not yet received."
4. Window W-k1, events EV-k1/EV-k2 and condition CO-k1 (heritage-15-king): a dated deadline and the event outcomes rest on research-note passages, but S-p210 is now fetched and has the verbatim sentence. To reproduce, run `python3 -c "import fitz;print('November 8, 2026' in ' '.join(p.get_text() for p in fitz.open('snapshots/media-002-ca.cdn.govstack.com/11ecf4a2466b9f3c10360399a5e6255f673fc98642469adc7e8d13f581c1e388.pdf')))"`, which prints True, while `PA-p210-appeal` has kind `research_note`.
5. `web/src/pages/index.astro` and `web/src/pages/search.astro`, plus `web/src/scripts/search.ts`: the search text, which can be a street address, is sent to the host as `?q=`. To reproduce, type "123 King St N" on the home page and press Enter; the browser requests `/search/?q=123+King+St+N`.
6. `web/src/pages/matter/[id]/index.astro:91`: "From 1 official records". To reproduce, open `/matter/debt-limit-2026/`.
7. Committed HEAD (99558e1): `pipeline/build.py` and `tests/` import modules that aren't committed. To reproduce, run `git archive HEAD | tar -x -C /tmp/x && cd /tmp/x && python3 pipeline/build.py`, which gives `ModuleNotFoundError: No module named 'easyread'`.
