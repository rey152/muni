"""Muni build: load review files -> validate -> checks -> export.

Run: python3 pipeline/build.py

The build stops with an error if any plan §5 hard rule is broken:
  - every claim cites at least one passage and has a provenance (models.Claim)
  - every window with a deadline_date has its quote and passage, and the date is
    written in that quote (models.ParticipationWindow + check_quotes_in_passages)
  - every event's outcome_text is verbatim from its passage
  - only approved items are exported
  - correspondence passages are never cited or exported

Claims that drop a qualifier, and Easy Read lines whose set for a claim drops one,
are held back rather than failing the build (blocked_claims, blocked_easy_read).
The NLI check only adds staff-facing flags; it never holds anything back.
"""
import sys
from datetime import date
from pathlib import Path

import easyread
import export
import inventory
import models
import review_io
import store
from checks import drift, nli, qualifier

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DIR = review_io.REVIEW_DIR

# Public-comment and correspondence families (guide DF11.1 bound consultation
# appendices, DF11.2 comment-response compilations). Passages from them can
# carry residents' names and addresses.
CORRESPONDENCE_SUBFAMILIES = {"DF11.1", "DF11.2"}
CORRESPONDENCE_ROLE = "C2"


class BuildError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise BuildError(message)


def every_item(review):
    """(matter, item) for every identifier, event, condition, window, claim and Easy Read line."""
    for matter in review.matters:
        for item in (matter.identifiers + matter.events + matter.conditions + matter.windows
                     + matter.claims + matter.easy_read):
            yield matter, item


def cited_passages(item):
    if hasattr(item, "passage_ids"):
        return item.passage_ids
    if hasattr(item, "passage_id"):
        return [item.passage_id]
    return []  # Easy Read lines cite their claim, not a passage


def item_label(matter, item):
    # identifiers have no id of their own, so name them by their value
    return f"{matter.id}/{getattr(item, 'id', None) or item.value}"


def labelled_items(review):
    """(item, label) for everything that cites a passage, except rule pairs."""
    found = [(item, item_label(matter, item)) for matter, item in every_item(review)]
    found += [(c, c.id) for c in review.planted_claims] + [(c, c.id) for c in review.channels]
    return found


def check_references(review):
    """Ids are unique and everything points at something that exists."""
    snapshot_ids = [s.id for s in review.snapshots]
    passage_ids = [p.id for p in review.passages]
    matter_ids = [m.id for m in review.matters]
    item_ids = [item.id for _, item in every_item(review) if hasattr(item, "id")]
    item_ids += [c.id for c in review.planted_claims] + [c.id for c in review.channels] + [r.id for r in review.rule_pairs]
    checks = [("snapshot", snapshot_ids), ("passage", passage_ids), ("matter", matter_ids), ("item", item_ids),
              ("topic slug", [t.slug for t in review.topics]), ("topic name", [t.name for t in review.topics]),
              ("authority", [a.id for a in review.authorities])]
    for name, ids in checks:
        repeated = sorted({i for i in ids if ids.count(i) > 1})
        require(not repeated, f"{name} ids used twice: {repeated}")

    snapshot_set, passage_set = set(snapshot_ids), set(passage_ids)
    for p in review.passages:
        require(p.snapshot_id in snapshot_set, f"passage {p.id} points to missing snapshot {p.snapshot_id}")

    topic_names = {t.name for t in review.topics}
    authority_ids = {a.id for a in review.authorities}
    for matter in review.matters:
        for topic in matter.topics:
            require(topic in topic_names, f"matter {matter.id} has unknown topic '{topic}'")
        for authority_id in matter.authority_ids:
            require(authority_id in authority_ids, f"matter {matter.id} has unknown authority {authority_id}")

    for item, label in labelled_items(review):
        for passage_id in cited_passages(item):
            require(passage_id in passage_set, f"{label} cites missing passage {passage_id}")
    for pair in review.rule_pairs:
        for passage_id in (pair.guide_passage, pair.rule_passage):
            require(passage_id in passage_set, f"rule pair {pair.id} cites missing passage {passage_id}")
    for claim in [c for m in review.matters for c in m.claims] + review.planted_claims:
        for snapshot_id in claim.checked_against:
            require(snapshot_id in snapshot_set, f"claim {claim.id} was checked against missing snapshot {snapshot_id}")
    for claim in review.planted_claims:
        require(claim.matter_id in set(matter_ids), f"planted claim {claim.id} points to missing matter {claim.matter_id}")


def check_quotes_in_passages(review):
    """Event outcomes, deadline quotes, conditions and channel statements are verbatim from their passage."""
    passages = {p.id: p for p in review.passages}
    for matter in review.matters:
        for event in matter.events:
            require(event.outcome_text in passages[event.passage_id].text,
                    f"event {event.id} in {matter.id}: outcome_text is not verbatim from {event.passage_id}")
        for window in matter.windows:
            if window.deadline_quote:
                require(window.deadline_quote in passages[window.passage_id].text,
                        f"window {window.id} in {matter.id}: deadline quote not found in {window.passage_id}")
        for condition in matter.conditions:
            require(condition.text in passages[condition.passage_id].text,
                    f"condition {condition.id} in {matter.id}: text not found in {condition.passage_id}")
    for channel in review.channels:
        require(channel.statement in passages[channel.passage_id].text,
                f"channel {channel.id}: statement not found in {channel.passage_id}")


def correspondence_passage_ids(review, inv):
    """Passages tagged C2, or taken from a snapshot of a DF11.1/DF11.2 particular."""
    subfamily = {p.id: p.subfamily for p in inv.particulars}
    correspondence_snapshots = set()
    for snapshot in review.snapshots:
        if any(subfamily[pid] in CORRESPONDENCE_SUBFAMILIES for pid in snapshot.particular_ids()):
            correspondence_snapshots.add(snapshot.id)
    found = set()
    for passage in review.passages:
        roles = {role.code for role in passage.roles}
        if CORRESPONDENCE_ROLE in roles or passage.snapshot_id in correspondence_snapshots:
            found.add(passage.id)
    return found


def check_correspondence(review, correspondence_ids):
    """Nothing published may cite a correspondence passage."""
    found = [(cited_passages(item), label) for item, label in labelled_items(review)]
    found += [([pair.guide_passage, pair.rule_passage], pair.id) for pair in review.rule_pairs]
    for passage_ids, label in found:
        cited = [pid for pid in passage_ids if pid in correspondence_ids]
        require(not cited, f"{label} cites correspondence passage(s) {cited}; those can't be published")


def window_state(window, today):
    if window.state == "dated":
        return "open" if window.deadline_date >= today else "closed"
    return window.state


def latest_ok_sha(fetches):
    ok = [f for f in fetches if f.availability == "ok"]
    return ok[-1].sha256 if ok else None


def attach_particular_fetches(inv, review, fetches, snapshot_fetches):
    """Give each particular its most recent real fetch, matched by particular id, its own URLs or its snapshots."""
    snapshot_by_id = {s.id: s for s in review.snapshots}
    for particular in inv.particulars:
        urls = {particular.url, *particular.retrieval_urls}
        matched = [info for info, ids in fetches if particular.id in ids or info.url in urls]
        for snapshot_id in particular.linked_snapshot_ids:
            if snapshot_id in snapshot_by_id:
                matched += snapshot_fetches.get(snapshot_id, [])
        if matched:
            particular.latest_fetch = max(matched, key=lambda info: info.fetched_at)


def hold_back_easy_read(matter, passages):
    """Drop Easy Read lines whose set for a claim loses a qualifier (plan §6.4.5).

    Returns (check, held): the Easy Read check for the lines before anything was
    dropped, and the lines that were dropped. Expects matter.claims and
    matter.easy_read to be cut down to what would be exported already.
    """
    check = easyread.check_matter(matter, passages)
    missing = check["claims_missing_qualifiers"]
    held = [{"id": line.id, "matter_id": matter.id, "claim_id": line.claim_id, "text": line.text,
             "missing": missing[line.claim_id]}
            for line in matter.easy_read if line.claim_id in missing]
    matter.easy_read = [line for line in matter.easy_read if line.claim_id not in missing]
    return check, held


def publish(review, today):
    """Copy of the review cut down to what may be exported, plus what the Qualifier Keeper held back.

    Returns (published, held). held has "claims" and "easy_read" (what was
    held back) and "easy_read_checks" (one Easy Read check per matter).
    Claims Drift Sentinel sent back to review are no longer approved, so
    they're left out like any other unapproved claim.
    """
    published = review.model_copy(deep=True)
    passages = {p.id: p for p in published.passages}
    held = {"claims": [], "easy_read": [], "easy_read_checks": []}
    for matter in published.matters:
        planted = [c for c in published.planted_claims if c.matter_id == matter.id]
        planted_ids = {c.id for c in planted}
        kept = []
        for claim in matter.claims + planted:
            required, missing = qualifier.check_claim(claim, passages)
            claim.qualifiers_required = required
            if claim.review.status != "approved":
                continue
            if missing:
                held["claims"].append({"id": claim.id, "matter_id": matter.id, "text": claim.text, "missing": missing})
                continue
            if claim.id in planted_ids:
                # a planted claim that passes every check is exported as a plain claim
                claim = models.Claim(**claim.model_dump(exclude={"note"}))
            kept.append(claim)
        matter.claims = kept
        kept_ids = {c.id for c in kept}
        matter.easy_read = [line for line in matter.easy_read
                            if line.claim_id in kept_ids and line.review.status == "approved"]
        check, held_lines = hold_back_easy_read(matter, passages)
        held["easy_read_checks"].append(check)
        held["easy_read"] += held_lines
        matter.identifiers = [i for i in matter.identifiers if i.review.status == "approved"]
        matter.events = [e for e in matter.events if e.review.status == "approved"]
        matter.conditions = [c for c in matter.conditions if c.review.status == "approved"]
        matter.windows = [w for w in matter.windows if w.review.status == "approved"]
        for window in matter.windows:
            window.computed_state = window_state(window, today)
            window.checked_on = window.checked_on or published.checked_on
    published.channels = [c for c in published.channels if c.review.status == "approved"]
    published.planted_claims = []
    easyread.set_grade_levels(published.matters)
    return published, held


def nli_checks(published):
    """NLI result for every exported claim against its cited passages. Staff-facing flags, never a gate.

    allow_download=False: the build only uses a model that's already on disk, so
    it never reaches the network. Without one, every result says available: false.
    """
    passages = {p.id: p for p in published.passages}
    found = []
    for matter in published.matters:
        for claim in matter.claims:
            premise = "\n".join(passages[pid].text for pid in claim.passage_ids)
            result = nli.check(premise, claim.text, allow_download=False)
            found.append({"claim_id": claim.id, "matter_id": matter.id, **result})
    return found


def run(review_dir=REVIEW_DIR, today=None, fetch_db=store.FETCH_DB_PATH,
        classified_path=inventory.CLASSIFIED_PATH, graph_path=inventory.GRAPH_PATH):
    """Run the whole pipeline in memory. Returns (export dict, review, fetch rows). Raises on any broken rule."""
    today = today or date.today().isoformat()
    review = review_io.read_review(review_dir)
    inv = inventory.load_inventory(classified_path, graph_path)

    check_references(review)
    check_quotes_in_passages(review)
    # link_usage also checks every snapshot's particular ids exist, which the correspondence check relies on
    matter_particulars = inventory.link_usage(inv, review)
    correspondence_ids = correspondence_passage_ids(review, inv)
    check_correspondence(review, correspondence_ids)

    fetches = store.read_fetch_rows(fetch_db)
    snapshot_fetches = store.fetches_by_snapshot(review.snapshots, fetches)
    attach_particular_fetches(inv, review, fetches, snapshot_fetches)

    passages = {p.id: p for p in review.passages}
    snapshots_now = {sid: latest_ok_sha(found) for sid, found in snapshot_fetches.items()}
    all_claims = [c for m in review.matters for c in m.claims] + review.planted_claims
    source_changes = drift.source_drift(all_claims, snapshots_now, today, passages, drift.fetch_paths(fetches))
    drift.mark_needs_recheck(all_claims, source_changes)
    discrepancies = drift.rule_drift(review.rule_pairs, passages, today) + source_changes

    published, held = publish(review, today)
    staff_checks = {"blocked_easy_read": held["easy_read"], "easy_read_checks": held["easy_read_checks"],
                    "nli_checks": nli_checks(published)}
    try:
        result = export.build_export(published, inv, held["claims"], discrepancies, snapshot_fetches,
                                     matter_particulars, correspondence_ids, today, staff_checks)
    except ValueError as error:
        raise BuildError(str(error)) from error
    return result, review, fetches


def build(review_dir=REVIEW_DIR, today=None, fetch_db=store.FETCH_DB_PATH):
    """The export dict only; this is what the tests look at."""
    return run(review_dir, today, fetch_db)[0]


def write_store(review, fetches):
    con = store.fresh()
    try:
        store.load_review(review, con)
        store.import_fetch_rows(con, fetches)
    finally:
        con.close()


def main():
    result, review, fetches = run()
    export.write_export(result)
    write_store(review, fetches)
    models.write_schemas()
    models.write_uml()
    claims = sum(len(m["claims"]) for m in result["matters"])
    outputs = ", ".join(str(p.relative_to(ROOT)) for p in export.OUTPUTS)
    print(f"Exported {len(result['matters'])} matters, {claims} claims, "
          f"{len(result['blocked_claims'])} blocked, {len(result['discrepancies'])} discrepancies -> {outputs}")
    for b in result["blocked_claims"]:
        print(f"  BLOCKED {b['id']}: missing {b['missing']}")
    for line in result["blocked_easy_read"]:
        print(f"  HELD BACK Easy Read {line['id']} ({line['claim_id']}): missing {line['missing']}")
    nli_results = result["nli_checks"]
    if nli_results and not nli_results[0]["available"]:
        print(f"  {nli_results[0]['reason']}")
    else:
        flagged = [r["claim_id"] for r in nli_results if r["flag"]]
        print(f"  NLI (staff only, not a gate): {len(nli_results)} claims checked, {len(flagged)} flagged {flagged}")


if __name__ == "__main__":
    try:
        main()
    except (BuildError, ValueError) as error:
        sys.exit(f"Build failed: {error}")
