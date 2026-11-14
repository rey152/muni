# Muni

Muni explains City of Waterloo council matters in plain language. Every sentence links to the exact record passage it comes from.

It's a build pipeline plus a static site. Nothing runs on a server, and your address, ward and comment drafts stay in your browser.

## Run it

Python 3.12+ and Node 22.23.4+ (what Astro 7.4.7 requires).

```
pip install -r requirements.txt
python3 pipeline/build.py          # validates review/, runs the checks, writes web/public/data/muni.json
python3 -m pytest -q tests

cd web
npm install
npm run build                      # static site in web/dist
node scripts/check-site.mjs        # checks the built site in Chrome (needs Google Chrome installed)
npm run preview                    # or: npm run dev
```

The build stops with an error, and names the item and the rule, if a reviewed record breaks a hard rule (see `docs/data-contract.md`). It also writes `site/data/muni.json` for the old prototype in `site/`, `pipeline/muni.sqlite`, `schema/*.json` and `docs/uml.md`.

### Staff report

```
python3 pipeline/staff_report.py   # writes staff/drift.csv and staff/drift.json
```

A separate step. It runs the build checks in memory, writes only `staff/` (gitignored) and never touches the site data. One row per Drift Sentinel finding: both passages with their source links, a word diff and a suggested fix. It doesn't say which source is right.

`python3 pipeline/easyread.py` prints the reading grade and qualifier results for every Easy Read line.

### NLI check (optional)

```
pip install -r requirements-nli.txt
python3 -c "import sys; sys.path.insert(0, 'pipeline'); from checks import nli; print(nli.load_model())"
```

The second line downloads `cross-encoder/nli-deberta-v3-base` once. The build itself never downloads it: with the model on disk it checks each exported claim against its passages and puts the results in `nli_checks` for staff. Without it, the build says the check was skipped and carries on. Either way it never holds anything back.

### AI drafts (optional)

```
ollama serve                       # in another terminal, with qwen2.5:7b pulled
python3 pipeline/ai.py draft <matter-id>
```

Drafts paraphrases and Easy Read lines into `review/suggestions/<matter-id>.yaml` with status `pending`, after the Qualifier Keeper, a number/date/status-word check and the NLI check. A person copies a draft into `review/matters/` after checking it. Outputs are cached in `pipeline/ai_cache.json` (tracked, so reruns give the same text) and logged to `review/ai-log.jsonl`.

### Fetching sources

```
python3 pipeline/fetch.py <url> P###          # one source
python3 pipeline/fetch.py --retry             # re-fetch only urls whose last try hit a network error
python3 pipeline/fetch.py --inbox P###        # ingest files saved by hand in manual_inbox/
python3 pipeline/link_snapshots.py            # copy fetch results into review/snapshots.yaml
```

## What's in it

| Feature | Where |
|---|---|
| Item Passport: find a matter by report, by-law or address number, including renumbered ones (2025-086 → 2025-087) | Home search |
| Decision Facts: seven fixed headings, each sentence with its source passage | Matter page |
| Windows Wall: deadlines only as quoted; open or closed is worked out in your browser | Matter page |
| Life of a Decision: one card per record in order | Matter page |
| Easy Read, with a reading grade per line (a guide, not a gate) | Matter page |
| Glass Box: provenance label on every sentence, plus a "Show without AI" switch | Matter page, How this works |
| Ward Match: pick a ward on the map, by location or from a list. Runs on your device. | Near me |
| Exposure Preview: highlights personal details in a draft comment, offline | Have your say |
| Qualifier Keeper: holds back any claim, or any claim's Easy Read lines, that drops a condition from its source | `pipeline/build.py` |
| Drift Sentinel: flags guide wording that differs from the rule it paraphrases, and claims whose source changed after review | `pipeline/build.py`, `pipeline/staff_report.py`, Staff page |

## Data and limits

- The reviewed records are in `review/`: one YAML file per matter in `review/matters/`, plus snapshots, passages, topics, authorities, rule pairs and channels. They cover four demo matters from the 2026-11-13 research pass in the Waterloo classification guide. Matter text is curated by hand, not parsed automatically. Passages marked "research note" are researcher summaries of a record, not verbatim text.
- Items migrated from the first prototype say `by: not recorded`, because the old file didn't record who approved them or when.
- `pipeline/fetch.py` fetches sources with Playwright and system Chrome and stores immutable snapshots (SHA-256, SQLite metadata) under `snapshots/`. Large binaries (PDFs and similar) are gitignored; their hashes stay in `snapshots/snapshots.sqlite` and `snapshots/fetch-report.json`. The latest run covered 294 urls: 275 ok, 4 blocked, 1 sign-in, 1 dead, 1 DNS error, and 12 not tried because their host had already refused us.
- We don't work around blocks. The City meeting portal (events.waterloo.ca) answered HTTP 403, so the December 8, 2025 packet, revised agenda and minutes have no fetched copy and no hash, and the claims that rely on them can't be watched for source changes. The Region's eScribe portal (Cloudflare browser check), bids&tenders, one ArcGIS item (sign-in) and one Cambridge Today page were blocked too. To add them, download the files by hand into `manual_inbox/` and run `python3 pipeline/fetch.py --inbox P###`.
- One engagewr.ca page snapshot is kept out of git (it embeds the site's own public map token, which GitHub push protection rejects). Its hash is still recorded.
- `checked_against` hashes on claims were filled in from the linked snapshots on 2026-11-14, as a baseline for source drift, not recorded by a reviewer at review time. See "Known gaps" in `docs/data-contract.md`.
- Ward polygons come from the City's ArcGIS `Wards_2026` FeatureServer (P224). `pipeline/wards.py` assigns a ward to a point with Shapely. The two heritage addresses were geocoded once at build time from OpenStreetMap Nominatim; both fall in Ward 7. Residents' own locations never leave the browser.
- `pipeline/parse_staff_report.py` reads staff-report headers from a PDF. It hasn't been run on a real packet yet, because the portal blocked the download.
- The Qualifier Keeper catches dropped wording, not every possible omission. Reading grades only count syllables and sentence length. The NLI check flags many research-note claims, since the notes are short; a flag means "a person should look", and a clean result doesn't prove a claim right.
- AI paraphrases are drafts that a person reviewed. AI never decides status, writes numbers or computes deadlines.

## Versions and licences

Python packages are pinned in `requirements.txt` (and `requirements-nli.txt` for the optional NLI check): Pydantic 2.13.2 (MIT), PyYAML 6.0.3 (MIT), textstat 0.7.13 (MIT), RapidFuzz 3.14.6 (MIT), Beautiful Soup 4.15.0 (MIT), lxml 6.1.3 (BSD), PyMuPDF 1.27.2.2 (AGPL-3.0 or Artifex commercial), Playwright 1.65.2 (Apache-2.0), pdfplumber 0.11.10 (MIT), Shapely 2.2.0 (BSD), transformers 5.23.0 (Apache-2.0), torch 2.15.0 (BSD-3-Clause and others). Web packages are pinned in `web/package.json`. Fonts: Fredoka and Source Serif 4 (OFL) from Google Fonts.
