# Muni

Muni explains City of Waterloo council matters in plain language. Every sentence links to the exact record passage it comes from.

It's a build pipeline plus a static site. Nothing runs on a server, and your address, ward and comment drafts stay in your browser.

## Run it

```
pip install -r requirements.txt
python3 pipeline/build.py          # validates review/matters.json, runs checks, writes site/data/muni.json
cd site && python3 -m http.server 8000
```

Then open http://localhost:8000.

## What's in it

| Feature | Where |
|---|---|
| Item Passport: find a matter by report, by-law or address number, including renumbered ones (2025-086 → 2025-087) | Home search |
| Decision Facts: seven fixed headings, each sentence with its source passage | Matter page |
| Windows Wall: deadlines only as quoted; open or closed is worked out in your browser | Matter page |
| Life of a Decision: one card per record in order | Matter page |
| Easy Read and status strip | Matter page toggle |
| Glass Box: provenance label on every sentence, plus a "Show without AI" switch | Matter page, How this works |
| Ward Match: pick a ward on the map, by location or from a list. Runs on your device. | Home |
| Exposure Preview: highlights personal details in a draft comment, offline | Have your say |
| Qualifier Keeper: blocks any claim that drops a condition from its source | `pipeline/build.py` |
| Drift Sentinel: flags guide wording that differs from the rule it paraphrases | `pipeline/build.py`, Staff page |

## Data and limits

- `review/matters.json` holds the reviewed records for four demo matters. They come from the 2026-11-13 research pass in the Waterloo classification guide. Passages marked "research note" are researcher summaries of a record, not verbatim text.
- Ward polygons come from the City's ArcGIS `Wards_2026` FeatureServer (P224).
- `pipeline/fetch.py` fetches sources with Playwright and system Chrome, then stores immutable snapshots (SHA-256, SQLite metadata) under `snapshots/`. The City meeting portal (events.waterloo.ca) returns 403 to headless Chrome, and we don't bypass it: download those files by hand into `manual_inbox/` and run `python3 pipeline/fetch.py --inbox P###`.
- `pipeline/parse_staff_report.py` reads staff-report headers from a PDF (pdfplumber, layout text). It hasn't been run on a real packet yet, because the portal blocked the download.
- `pipeline/wards.py` assigns a ward to a point with Shapely. The two heritage addresses were geocoded once at build time from OpenStreetMap Nominatim; both fall in Ward 7. Residents' own locations never leave the browser.
- Matter text is still curated by hand from the research pass, not parsed automatically.
- Qualifier Keeper catches dropped wording, not every possible omission.
- AI paraphrases are drafts that a person reviewed. AI never decides status, writes numbers or computes deadlines.

## Versions and licences

Python 3.12+, Pydantic 2.13.2 (MIT), Playwright 1.65.2 (Apache-2.0), pdfplumber 0.11.10 (MIT), Shapely 2.2.0 (BSD). Fonts: Fredoka and Source Serif 4 (OFL) from Google Fonts.
