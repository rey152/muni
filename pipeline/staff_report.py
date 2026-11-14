"""Drift Sentinel staff report (plan §6.9): staff/drift.csv and staff/drift.json.

One row per discrepancy and passage: both sides with their source links, what
differs (a word diff), and a suggested fix. It never says which source is
right; a difference alone doesn't establish that.

Run: python3 pipeline/staff_report.py   (runs the build checks in memory, writes only staff/)
"""
import csv
import json
from pathlib import Path

import build
import diffs
import store
from checks import drift
from models import Discrepancy

ROOT = Path(__file__).resolve().parent.parent
STAFF_DIR = ROOT / "staff"
COLUMNS = [
    "id", "kind", "topic", "found_on", "status",
    "passage_a_id", "passage_a_label", "passage_a_url", "passage_a_text",
    "passage_b_id", "passage_b_label", "passage_b_url", "passage_b_text",
    "difference", "word_diff", "suggested_fix", "caveat",
]


def source_link(passage, snapshots):
    """(label, url) for where a passage comes from."""
    snapshot = snapshots[passage.snapshot_id]
    label = f"{snapshot.title}, {passage.locator.label or passage.snapshot_id}"
    if passage.kind == "research_note":
        label += " (research note, not source text)"
    return label, snapshot.url


def side(passage_id, label, url, text):
    return {"passage_id": passage_id, "label": label, "url": url, "text": text}


def rule_row(discrepancy, passages, snapshots):
    guide = passages[discrepancy.guide.passage_id]
    rule = passages[discrepancy.rule.passage_id]
    return {
        "a": side(guide.id, *source_link(guide, snapshots), guide.text),
        "b": side(rule.id, *source_link(rule, snapshots), rule.text),
        "word_diff": diffs.word_diff(guide.text, rule.text),
    }


def source_rows(discrepancy, claim, passages, snapshots, fetches):
    """One row per cited passage from the changed snapshot: as checked (A) and in the newest fetch (B)."""
    latest = next((info for info, _ in reversed(fetches) if info.sha256 == discrepancy.latest_sha256), None)
    new_text = drift.snapshot_text(latest.path) if latest else None
    new_url = (latest.final_url or latest.url) if latest else ""
    cited = [passages[pid] for pid in claim.passage_ids if passages[pid].snapshot_id == discrepancy.snapshot_id]
    rows = []
    for passage in cited:
        change = drift.passage_change(passage, new_text)
        new_label = f"Newest fetch {discrepancy.latest_sha256[:12]}: {change['state'].replace('_', ' ')}"
        rows.append({
            "a": side(passage.id, *source_link(passage, snapshots), passage.text),
            "b": side(passage.id, new_label, new_url, change["new_text"] or ""),
            "word_diff": diffs.word_diff(passage.text, change["new_text"]) if change["new_text"] else [],
            "note": change["reason"],
        })
    if not rows:
        rows.append({"a": side("", "No cited passage comes from this snapshot", "", ""),
                     "b": side("", "", new_url, ""), "word_diff": []})
    return rows


def report(review_dir=build.REVIEW_DIR, today=None, fetch_db=store.FETCH_DB_PATH):
    """(generated_on, records): every discrepancy the build finds, as report records (dicts)."""
    result, review, fetches = build.run(review_dir, today, fetch_db)
    passages = {p.id: p for p in review.passages}
    snapshots = {s.id: s for s in review.snapshots}
    claims = {c.id: c for m in review.matters for c in m.claims}
    claims.update({c.id: c for c in review.planted_claims})

    records = []
    for data in result["discrepancies"]:
        discrepancy = Discrepancy(**data)
        if discrepancy.kind == "rule_drift":
            rows = [rule_row(discrepancy, passages, snapshots)]
        else:
            rows = source_rows(discrepancy, claims[discrepancy.claim_id], passages, snapshots, fetches)
        for row in rows:
            records.append({
                "id": discrepancy.id,
                "kind": discrepancy.kind,
                "topic": discrepancy.topic,
                "found_on": discrepancy.found_on,
                "status": discrepancy.status,
                "passage_a": row["a"],
                "passage_b": row["b"],
                "difference": " ".join(filter(None, [discrepancy.difference, row.get("note", "")])),
                "word_diff": row["word_diff"],
                "suggested_fix": discrepancy.suggested_fix,
                "caveat": drift.CAVEAT,
            })
    return result["generated_on"], records


def csv_row(record):
    row = {key: record[key] for key in ("id", "kind", "topic", "found_on", "status", "difference",
                                        "suggested_fix", "caveat")}
    for letter in ("a", "b"):
        passage = record[f"passage_{letter}"]
        row[f"passage_{letter}_id"] = passage["passage_id"]
        row[f"passage_{letter}_label"] = passage["label"]
        row[f"passage_{letter}_url"] = passage["url"]
        row[f"passage_{letter}_text"] = passage["text"]
    row["word_diff"] = diffs.summary(record["word_diff"])
    return row


def write_report(generated_on, records, staff_dir=STAFF_DIR):
    staff_dir.mkdir(parents=True, exist_ok=True)
    with open(staff_dir / "drift.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(csv_row(record))
    data = {"generated_on": generated_on, "caveat": drift.CAVEAT, "discrepancies": records}
    (staff_dir / "drift.json").write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return [staff_dir / "drift.csv", staff_dir / "drift.json"]


def main():
    generated_on, records = report()
    paths = write_report(generated_on, records)
    print(f"Wrote {len(records)} discrepancy rows to {', '.join(str(p.relative_to(ROOT)) for p in paths)}")
    for record in records:
        print(f"  {record['id']}: {record['difference']}")


if __name__ == "__main__":
    main()
