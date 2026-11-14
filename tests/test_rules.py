import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import build  # noqa: E402
import inventory  # noqa: E402
import models  # noqa: E402
import review_io  # noqa: E402
import store  # noqa: E402
from checks import drift, qualifier  # noqa: E402

TODAY = "2026-11-14"
NO_FETCHES = Path("/nonexistent/snapshots.sqlite")


@pytest.fixture(scope="module")
def export():
    return build.build(today=TODAY)


@pytest.fixture
def review_copy(tmp_path):
    """A throwaway copy of review/ that a test can edit."""
    target = tmp_path / "review"
    shutil.copytree(build.REVIEW_DIR, target)
    return target


def edit_yaml(path, change):
    data = review_io.read_yaml(path)
    change(data)
    review_io.write_yaml(path, data)


def exported_claim_ids(result):
    return {c["id"] for m in result["matters"] for c in m["claims"]}


# ---------- Schema ----------

def test_review_files_match_the_schema():
    review = review_io.read_review()
    assert len(review.matters) == 4
    assert {t.name for t in review.topics} >= {t for m in review.matters for t in m.topics}


def test_schema_files_and_uml_are_up_to_date():
    for model in models.MODELS:
        on_disk = json.loads((models.SCHEMA_DIR / f"{model.__name__}.json").read_text())
        assert on_disk == json.loads(json.dumps(model.model_json_schema(by_alias=True))), model.__name__
    assert models.UML_PATH.read_text() == models.uml_text()


def test_yaml_reads_on_and_dates_as_text(tmp_path):
    path = tmp_path / "x.yaml"
    path.write_text("review:\n  by: someone\n  on: 2026-11-13\n  status: approved\n")
    data = review_io.read_yaml(path)
    assert data["review"]["on"] == "2026-11-13"
    assert models.Review(**data["review"]).on == "2026-11-13"


# ---------- §5 hard rules ----------

def test_every_claim_has_passage_and_provenance(export):
    for matter in export["matters"]:
        for claim in matter["claims"]:
            assert claim["passage_ids"]
            assert claim["provenance"] in {"quote", "extraction", "ai_paraphrase", "human"}


def test_claim_without_passage_fails_schema():
    with pytest.raises(ValueError):
        models.Claim(id="x", section="applies_to", text="t", provenance="human", passage_ids=[])


def test_every_deadline_has_quote_and_passage(export):
    passages = {p["id"]: p["text"] for p in export["passages"]}
    for matter in export["matters"]:
        for window in matter["windows"]:
            if window["deadline_date"]:
                assert window["deadline_quote"]
                assert window["deadline_quote"] in passages[window["passage_id"]]


def test_date_without_quote_fails_schema():
    with pytest.raises(ValueError):
        models.ParticipationWindow(id="w", action="x", channel="y", state="dated", deadline_quote="",
                                   deadline_date="2026-11-06", passage_id="p")


def test_date_must_be_written_in_its_quote():
    quote = "The last day for filing an objection is November 6, 2026"
    window = models.ParticipationWindow(id="w", action="x", state="dated", deadline_quote=quote,
                                        deadline_date="2026-11-06", passage_id="p")
    assert window.deadline_date == "2026-11-06"
    with pytest.raises(ValueError):
        models.ParticipationWindow(id="w", action="x", state="dated", deadline_quote=quote,
                                   deadline_date="2026-11-07", passage_id="p")


def test_event_outcome_must_be_verbatim(review_copy):
    def reword(matter):
        matter["events"][0]["outcome_text"] = "Staff proposed new fees."
    edit_yaml(review_copy / "matters" / "fees-2026.yaml", reword)
    with pytest.raises(build.BuildError, match="verbatim"):
        build.build(review_copy, TODAY, NO_FETCHES)


def test_unapproved_claim_not_exported(review_copy):
    def unapprove(matter):
        matter["claims"][0]["review"]["status"] = "needs_recheck"
    edit_yaml(review_copy / "matters" / "fees-2026.yaml", unapprove)
    result = build.build(review_copy, TODAY, NO_FETCHES)
    assert "C-f1" not in exported_claim_ids(result)
    fees = result["matters"][0]
    assert all(line["claim_id"] != "C-f1" for line in fees["easy_read"])
    assert "C-f1" not in json.dumps(result["search_docs"])  # the claim's text isn't searchable either
    assert "C-f2" in exported_claim_ids(result)


def test_claim_without_review_is_pending_and_not_exported(review_copy):
    def drop_review(matter):
        del matter["claims"][1]["review"]
    edit_yaml(review_copy / "matters" / "fees-2026.yaml", drop_review)
    assert "C-f2" not in exported_claim_ids(build.build(review_copy, TODAY, NO_FETCHES))


def test_unapproved_window_not_exported(review_copy):
    def unapprove(matter):
        matter["windows"][0]["review"]["status"] = "pending"
    edit_yaml(review_copy / "matters" / "heritage-131-william.yaml", unapprove)
    result = build.build(review_copy, TODAY, NO_FETCHES)
    assert result["matters"][2]["windows"] == []


def add_correspondence(review_dir, snapshot_particular="P214", roles=None):
    """A comment-response table passage with made-up personal details."""
    edit_yaml(review_dir / "snapshots.yaml", lambda d: d["snapshots"].append({
        "id": "S-test-comments", "url": "https://example.org/comments.pdf", "fetched_at": "2026-11-13",
        "obtained_by": "manual", "availability": "ok", "particular": snapshot_particular,
        "publisher": "Test", "title": "Test comment table"}))
    edit_yaml(review_dir / "passages.yaml", lambda d: d["passages"].append({
        "id": "PA-test-comment", "snapshot_id": "S-test-comments", "locator": {"page": 2},
        "kind": "verbatim", "text": "Jane Testperson, 12 Example St, jane.testperson@example.org, objects.",
        "roles": roles or []}))


def test_correspondence_passage_is_not_exported(review_copy):
    add_correspondence(review_copy)
    result = build.build(review_copy, TODAY, NO_FETCHES)
    text = json.dumps(result)
    assert "PA-test-comment" not in {p["id"] for p in result["passages"]}
    assert "jane.testperson@example.org" not in text
    assert "Jane Testperson" not in text


def test_c2_tagged_passage_counts_as_correspondence(review_copy):
    add_correspondence(review_copy, snapshot_particular="P202", roles=[{"code": "C2", "method": "human"}])
    result = build.build(review_copy, TODAY, NO_FETCHES)
    assert "jane.testperson@example.org" not in json.dumps(result)


def test_claim_citing_correspondence_fails_build(review_copy):
    add_correspondence(review_copy)
    edit_yaml(review_copy / "matters" / "fees-2026.yaml",
              lambda m: m["claims"][0]["passage_ids"].append("PA-test-comment"))
    with pytest.raises(build.BuildError, match="correspondence"):
        build.build(review_copy, TODAY, NO_FETCHES)


def test_missing_passage_fails_build(review_copy):
    edit_yaml(review_copy / "matters" / "fees-2026.yaml",
              lambda m: m["claims"][0]["passage_ids"].append("PA-does-not-exist"))
    with pytest.raises(build.BuildError, match="missing passage"):
        build.build(review_copy, TODAY, NO_FETCHES)


# ---------- Checks ----------

def test_planted_dropped_condition_is_blocked(export):
    blocked = {b["id"]: b for b in export["blocked_claims"]}
    assert "C-planted" in blocked
    assert blocked["C-planted"]["missing"] == ["not a", "not yet"]
    assert "C-planted" not in exported_claim_ids(export)


def test_qualifier_keeper_finds_markers():
    required, missing = qualifier.missing_qualifiers("Debt is low.", ["Not a borrowing approval; limit not yet received."])
    assert "not a" in missing and "not yet" in missing


def test_qualifier_keeper_respects_waivers():
    passage = models.Passage(id="p", snapshot_id="s", locator={"label": "x"}, kind="verbatim",
                             text="Not a borrowing approval; limit not yet received.")
    claim = models.Claim(id="c", section="applies_to", text="Debt is low.", provenance="human",
                         passage_ids=["p"], qualifiers_waived={"not a": "Said elsewhere."})
    required, missing = qualifier.check_claim(claim, {"p": passage})
    assert required == ["not a", "not yet"]
    assert missing == ["not yet"]


def test_drift_sentinel_catches_business_days(export):
    diffs = [d["difference"] for d in export["discrepancies"] if d["kind"] == "rule_drift"]
    assert any("10 days" in d and "10 business days" in d for d in diffs)


def make_fetch_db(path, url, sha):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE snapshots (id INTEGER PRIMARY KEY, url TEXT, final_url TEXT, status INTEGER, "
                "fetched_at TEXT, sha256 TEXT, content_type TEXT, particular TEXT, obtained_by TEXT, path TEXT)")
    con.execute("INSERT INTO snapshots (url, final_url, status, fetched_at, sha256, content_type, particular, "
                "obtained_by, path) VALUES (?, ?, 200, '2026-11-14T00:00:00+00:00', ?, 'text/html', 'P202', "
                "'chromium', 'snapshots/x.html')", (url, url, sha))
    con.commit()
    con.close()


def test_source_drift_sends_claim_back_to_review(review_copy, tmp_path):
    p202 = "https://www.waterloo.ca/council-and-committees/council-and-committee-meetings/register-to-speak-at-a-council-meeting/"
    edit_yaml(review_copy / "matters" / "fees-2026.yaml",
              lambda m: m["claims"][5].update(checked_against={"S-p202": "a" * 64}))

    same = tmp_path / "same.sqlite"
    make_fetch_db(same, p202, "a" * 64)
    result = build.build(review_copy, TODAY, same)
    assert "C-f6" in exported_claim_ids(result)
    assert not [d for d in result["discrepancies"] if d["kind"] == "source_drift"]

    changed = tmp_path / "changed.sqlite"
    make_fetch_db(changed, p202, "b" * 64)
    result = build.build(review_copy, TODAY, changed)
    assert "C-f6" not in exported_claim_ids(result)
    found = [d for d in result["discrepancies"] if d["kind"] == "source_drift"]
    assert found[0]["claim_id"] == "C-f6" and found[0]["latest_sha256"] == "b" * 64


def test_source_drift_function_skips_unchecked_claims():
    claim = models.Claim(id="c", section="applies_to", text="t", provenance="human", passage_ids=["p"])
    assert drift.source_drift([claim], {"S": "b" * 64}) == []


def test_source_drift_marks_the_claim_needs_recheck(review_copy, tmp_path):
    p202 = "https://www.waterloo.ca/council-and-committees/council-and-committee-meetings/register-to-speak-at-a-council-meeting/"
    changed = tmp_path / "changed.sqlite"
    make_fetch_db(changed, p202, "b" * 64)
    result, review, _ = build.run(review_copy, TODAY, changed)
    [c_f6] = [c for c in review.matters[0].claims if c.id == "C-f6"]
    assert c_f6.review.status == "needs_recheck"
    assert "D-C-f6-S-p202" in c_f6.review.note
    assert "C-f6" not in exported_claim_ids(result)


def test_checked_against_matches_the_linked_snapshots():
    review = review_io.read_review()
    snapshot_sha = {s.id: s.sha256 for s in review.snapshots if s.availability == "ok" and s.sha256}
    snapshot_of = {p.id: p.snapshot_id for p in review.passages}
    for matter in review.matters:
        for claim in matter.claims:
            expected = {snapshot_of[pid]: snapshot_sha[snapshot_of[pid]]
                        for pid in claim.passage_ids if snapshot_of[pid] in snapshot_sha}
            assert claim.checked_against == expected, claim.id


# ---------- Easy Read ----------

def test_easy_read_lines_get_a_grade(export):
    lines = [line for m in export["matters"] for line in m["easy_read"]]
    assert lines and all(isinstance(line["grade_level"], float) for line in lines)
    checks = {c["matter_id"]: c for c in export["easy_read_checks"]}
    assert set(checks) == {m["id"] for m in export["matters"]}
    assert export["blocked_easy_read"] == []


def test_easy_read_set_that_drops_a_qualifier_is_held_back(review_copy):
    def link_back(matter):
        [line] = [line for line in matter["easy_read"] if line["id"] == "ER-d4"]
        line["claim_id"] = "C-d4"
    edit_yaml(review_copy / "matters" / "debt-limit-2026.yaml", link_back)
    result = build.build(review_copy, TODAY, NO_FETCHES)
    held = {line["id"]: line for line in result["blocked_easy_read"]}
    assert set(held) == {"ER-d2", "ER-d3"}
    assert held["ER-d2"]["missing"] == ["not yet"]
    debt = next(m for m in result["matters"] if m["id"] == "debt-limit-2026")
    assert [line["id"] for line in debt["easy_read"]] == ["ER-d1", "ER-d4"]
    assert "C-d2" in exported_claim_ids(result)  # the claim itself keeps "not yet", so it still goes out
    [check] = [c for c in result["easy_read_checks"] if c["matter_id"] == "debt-limit-2026"]
    assert check["claims_missing_qualifiers"] == {"C-d2": ["not yet"]}


# ---------- NLI ----------

def test_nli_flags_are_reported_but_never_hold_anything_back(monkeypatch):
    def always_flag(premise, hypothesis, allow_download=True):
        assert allow_download is False  # the build never downloads a model
        return {"available": True, "model": "test", "flag": True, "reason": "test flag"}
    monkeypatch.setattr(build.nli, "check", always_flag)
    result = build.build(today=TODAY, fetch_db=NO_FETCHES)
    claim_ids = [c["id"] for m in result["matters"] for c in m["claims"]]
    assert len(claim_ids) == 20
    assert [r["claim_id"] for r in result["nli_checks"]] == claim_ids
    assert all(r["flag"] for r in result["nli_checks"])


# ---------- Item Passport ----------

def test_renumbered_bylaw_resolves_to_same_matter(export):
    alias = export["alias"]
    assert alias[models.normalize_identifier("By-law 2025-086")] == alias[models.normalize_identifier("bylaw 2025 087")]
    assert alias[models.normalize_identifier("corp2025-042")] == "fees-2026"


def test_identifier_shared_by_two_matters_fails_build(review_copy):
    edit_yaml(review_copy / "matters" / "debt-limit-2026.yaml", lambda m: m["identifiers"].append(
        {"value": "COM2025-034", "kind": "report no.", "passage_id": "PA-debt-calc",
         "review": {"by": "test", "status": "approved"}}))
    with pytest.raises(build.BuildError, match="points to both"):
        build.build(review_copy, TODAY, NO_FETCHES)


# ---------- Windows ----------

def test_dated_window_is_open_or_closed_by_build_date():
    before = build.build(today="2026-11-01", fetch_db=NO_FETCHES)
    after = build.build(today="2026-11-14", fetch_db=NO_FETCHES)
    state = lambda result: {w["id"]: w["computed_state"] for m in result["matters"] for w in m["windows"]}
    assert state(before)["W-h1"] == "open" and state(after)["W-h1"] == "closed"
    assert state(after)["W-f1"] == "rule_based" and state(after)["W-d1"] == "not_published"


# ---------- Inventory, store and export contract ----------

def test_inventory_has_every_particular_and_relationship(export):
    assert [p["id"] for p in export["particulars"]] == inventory.EXPECTED_IDS
    assert len(export["relationships"]) == 21
    assert len(export["document_components"]) == 2
    for relationship in export["relationships"]:
        for node in relationship["chain"]:
            assert all(e["kind"] in {"role", "particular", "description"} for e in node)


def test_unknown_relationship_endpoint_is_rejected():
    with pytest.raises(ValueError):
        inventory.parse_node("Z9", set(), {"A1": {}})


def test_store_search_finds_passages(tmp_path):
    con = store.connect(tmp_path / "m.sqlite")
    store.load_review(review_io.read_review(), con)
    hits = store.search_passages(con, "business days")
    assert hits[0]["id"] == "PA-p253-bylaw"
    # FTS5 syntax in the query is treated as plain words, not operators
    assert store.search_passages(con, '"(') == []
    assert all("and" in hit["text"].lower() for hit in store.search_passages(con, 'AND "('))
    con.close()


def test_export_keeps_every_field_the_old_site_reads(export):
    for key in ["checked_on", "snapshots", "passages", "matters", "channels", "alias", "blocked_claims", "discrepancies"]:
        assert key in export
    for key in ["blocked_easy_read", "easy_read_checks", "nli_checks"]:  # staff-only, added later
        assert isinstance(export[key], list)
    snapshot = export["snapshots"][0]
    assert {"id", "url", "title", "publisher", "fetched_at", "availability", "reason"} <= snapshot.keys()
    passage = export["passages"][0]
    assert isinstance(passage["locator"], str) and {"snapshot_id", "kind", "text"} <= passage.keys()
    matter = export["matters"][0]
    assert {"id", "title", "topics", "authority", "location", "wards", "identifiers", "events", "conditions",
            "windows", "claims", "easy_read"} <= matter.keys()
    assert matter["windows"][0]["state"] in {"dated", "rule_based", "not_published", "not_checked", "source_unavailable"}


def test_review_files_round_trip(tmp_path):
    review = review_io.read_review()
    review_io.write_review(review, tmp_path)
    assert review_io.read_review(tmp_path) == review
