"""Shape the published data into the one JSON file the website reads (docs/data-contract.md).

build.py decides what may be published; this module only arranges it. It never
adds a claim, event or window that build.py left out.

Written to web/public/data/muni.json and site/data/muni.json (the old prototype,
until it's retired), with wards.geojson copied next to the first.
"""
import json
import shutil
from collections import Counter
from pathlib import Path

from inventory import passages_cited_by

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = [ROOT / "web" / "public" / "data" / "muni.json", ROOT / "site" / "data" / "muni.json"]
WARDS_SOURCE = ROOT / "site" / "data" / "wards.geojson"
WARDS_COPIES = [ROOT / "web" / "public" / "data" / "wards.geojson"]


def dump(record):
    return record.model_dump(mode="json", by_alias=True)


def locator_text(locator):
    """The old site shows locator as one string, so keep that and send the parts separately."""
    if locator.label:
        return locator.label
    if locator.page is not None:
        return f"p.{locator.page}"
    return locator.element_path or ""


def review_summary(review):
    reviewer = review.by or "not recorded"
    reviewed_on = review.on or "not recorded"
    return f"{review.status.replace('_', ' ').capitalize()}. Reviewer: {reviewer}. Date: {reviewed_on}."


def latest_event(matter):
    """The event with the latest date; ties go to the one listed last. Partial dates sort as text."""
    if not matter.events:
        return None
    latest = matter.events[0]
    for event in matter.events[1:]:
        if event.date >= latest.date:
            latest = event
    return {"latest_event_id": latest.id, "latest_event_kind": latest.kind, "latest_event_date": latest.date}


def export_snapshot(snapshot, checked_on, fetches):
    data = dump(snapshot)
    data["checked_on"] = snapshot.checked_on or checked_on
    data["particular_ids"] = snapshot.particular_ids()
    data["fetch_count"] = len(fetches)
    data["latest_fetch"] = dump(fetches[-1]) if fetches else None
    return data


def export_passage(passage):
    data = dump(passage)
    data["locator"] = locator_text(passage.locator)
    data["locator_detail"] = dump(passage.locator)
    return data


def export_matter(matter, passages, topic_slugs, particular_ids):
    data = dump(matter)
    data["topic_slugs"] = [topic_slugs[name] for name in matter.topics]
    data["status_summary"] = latest_event(matter)
    data["particular_ids"] = particular_ids
    cited = passages_cited_by(matter)
    data["snapshot_ids"] = sorted({passages[pid].snapshot_id for pid in cited})
    for event in data["events"]:
        event["outcome_kind"] = passages[event["passage_id"]].kind
    for claim, claim_data in zip(matter.claims, data["claims"]):
        claim_data["review_summary"] = review_summary(claim.review)
    return data


def alias_map(matters):
    """Normalized identifier -> matter id. Two matters sharing one identifier is an error, not a guess."""
    alias = {}
    for matter in matters:
        for identifier in matter.identifiers:
            owner = alias.get(identifier.normalized)
            if owner and owner != matter.id:
                raise ValueError(f"identifier '{identifier.value}' points to both {owner} and {matter.id}")
            alias[identifier.normalized] = matter.id
    return alias


def search_doc(matter):
    texts = [claim.text for claim in matter.claims] + [line.text for line in matter.easy_read]
    return {
        "id": matter.id,
        "title": matter.title,
        "topics": matter.topics,
        "location": matter.location,
        "identifiers": [identifier.value for identifier in matter.identifiers],
        "text": " ".join(texts),
    }


def counts(values):
    return dict(sorted(Counter(values).items()))


def coverage(inventory, snapshots):
    particulars = inventory.particulars
    any_roles = []
    for p in particulars:
        any_roles += sorted({p.primary_role} | {s.code for s in p.secondary_roles})
    return {
        "particulars": len(particulars),
        "by_access": counts(p.access for p in particulars),
        "by_response_status": counts(str(p.original_response_status or "none") for p in particulars),
        "by_evidence": counts(p.evidence for p in particulars),
        "by_fetch_availability": counts(
            (p.latest_fetch.availability or "unknown") if p.latest_fetch else "not_fetched" for p in particulars),
        "by_snapshot_availability": counts(s.availability for s in snapshots),
        "by_family": counts(p.family for p in particulars),
        "by_level": counts(p.level for p in particulars),
        "by_authority": counts(p.authority for p in particulars),
        "by_primary_role": counts(p.primary_role for p in particulars),
        "by_any_role": counts(any_roles),
        "linked_to_matters": sum(1 for p in particulars if p.linked_matter_ids),
        "linked_to_snapshots": sum(1 for p in particulars if p.linked_snapshot_ids),
        "relationships": len(inventory.relationships),
        "by_relationship_family": counts(f for r in inventory.relationships for f in r.families),
        "historical_retrieval": inventory.retrieval_audit["overall"],
        "retrieval_audit_checked": inventory.retrieval_audit["checked"],
        "limits": inventory.retrieval_limits,
    }


def build_export(published, inventory, blocked, discrepancies, snapshot_fetches, matter_particulars,
                 excluded_passage_ids, today, staff_checks=None):
    """Arrange everything the site reads. `published` is a ReviewSet already cut down to approved items.

    staff_checks holds the staff-only check results build.py worked out:
    blocked_easy_read, easy_read_checks and nli_checks. Each becomes a top-level
    key, an empty list when missing.
    """
    passages = {p.id: p for p in published.passages}
    topic_slugs = {t.name: t.slug for t in published.topics}
    staff_checks = staff_checks or {}
    return {
        "checked_on": published.checked_on,
        "generated_on": today,
        "snapshots": [export_snapshot(s, published.checked_on, snapshot_fetches.get(s.id, []))
                      for s in published.snapshots],
        "passages": [export_passage(p) for p in published.passages if p.id not in excluded_passage_ids],
        "matters": [export_matter(m, passages, topic_slugs, matter_particulars.get(m.id, []))
                    for m in published.matters],
        "channels": [dump(c) for c in published.channels],
        "alias": alias_map(published.matters),
        "blocked_claims": blocked,
        "blocked_easy_read": staff_checks.get("blocked_easy_read", []),
        "easy_read_checks": staff_checks.get("easy_read_checks", []),
        "nli_checks": staff_checks.get("nli_checks", []),
        "discrepancies": [dump(d) for d in discrepancies],
        "topics": [dump(t) for t in published.topics],
        "authorities": [dump(a) for a in published.authorities],
        "search_docs": [search_doc(m) for m in published.matters],
        "particulars": [dump(p) for p in inventory.particulars],
        "relationships": [dump(r) for r in inventory.relationships],
        "relationship_families": [dump(f) for f in inventory.relationship_families],
        "document_components": [dump(c) for c in inventory.document_components],
        "families": inventory.families,
        "roles": inventory.roles,
        "inventory": {"generated": inventory.generated, "source_check_date": inventory.source_check_date,
                      "described_endpoints": inventory.described_endpoints},
        "coverage": coverage(inventory, published.snapshots),
    }


def write_export(export, outputs=OUTPUTS):
    text = json.dumps(export, indent=1, ensure_ascii=False)
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for path in WARDS_COPIES:
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(WARDS_SOURCE, path)
    return outputs
