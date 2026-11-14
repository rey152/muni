import hashlib
import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import ai  # noqa: E402
import build  # noqa: E402
import diffs  # noqa: E402
import easyread  # noqa: E402
import models  # noqa: E402
import review_io  # noqa: E402
import staff_report  # noqa: E402
from checks import drift, nli, qualifier  # noqa: E402

TODAY = "2026-11-14"
P202_URL = "https://www.waterloo.ca/council-and-committees/council-and-committee-meetings/register-to-speak-at-a-council-meeting/"


def passage(pid, text, kind="verbatim", snapshot_id="S"):
    return models.Passage(id=pid, snapshot_id=snapshot_id, locator={"label": "x"}, kind=kind, text=text)


def claim(text, passage_ids=("p",), **extra):
    return models.Claim(id=extra.pop("id", "c"), section="conditions", text=text, provenance="human",
                        passage_ids=list(passage_ids), **extra)


@pytest.fixture(scope="module")
def export():
    return build.build(today=TODAY)


@pytest.fixture
def review_copy(tmp_path):
    target = tmp_path / "review"
    shutil.copytree(build.REVIEW_DIR, target)
    return target


def make_fetch_db(path, rows):
    """rows: [(url, sha, fetched_at, file path)]"""
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE snapshots (id INTEGER PRIMARY KEY, url TEXT, final_url TEXT, status INTEGER, "
                "fetched_at TEXT, sha256 TEXT, content_type TEXT, particular TEXT, obtained_by TEXT, path TEXT)")
    for url, sha, fetched_at, file_path in rows:
        con.execute("INSERT INTO snapshots (url, final_url, status, fetched_at, sha256, content_type, particular, "
                    "obtained_by, path) VALUES (?, ?, 200, ?, ?, 'text/html', 'P202', 'chromium', ?)",
                    (url, url, fetched_at, sha, file_path))
    con.commit()
    con.close()


# ---------- Qualifier Keeper ----------

def test_planted_dropped_condition_is_blocked_and_real_claims_pass(export):
    blocked = {b["id"]: b["missing"] for b in export["blocked_claims"]}
    assert blocked == {"C-planted": ["not a", "not yet"]}
    assert sum(len(m["claims"]) for m in export["matters"]) == 20


def test_equivalents_count_as_kept():
    source = ["The by-law comes into force only if no appeal is filed."]
    assert qualifier.missing_qualifiers("It starts only when no appeal is filed.", source)[1] == []
    assert qualifier.missing_qualifiers("It starts after the appeal period.", source)[1] == ["only if"]
    source = ["Not a borrowing approval; final limit not yet received."]
    assert qualifier.missing_qualifiers("This isn't a loan. The limit hasn't been received yet.", source)[1] == []
    assert qualifier.missing_qualifiers("It is not protected yet.", ["Approval pending."])[1] == []


def test_waived_marker_is_not_missing_but_still_required():
    p = passage("p", "Not a borrowing approval; limit not yet received.")
    c = claim("Debt is low.", qualifiers_waived={"not yet": "Stated under Not decided yet."})
    assert qualifier.check_claim(c, {"p": p}) == (["not a", "not yet"], ["not a"])


def test_only_if_is_not_also_counted_as_if():
    assert qualifier.find_qualifiers("In force only if no appeal is filed.") == ["only if"]
    assert qualifier.find_qualifiers("In force only if no appeal is filed. If one is filed, the OLT decides.") \
        == ["only if", "if"]


def test_the_month_may_is_not_a_hedge():
    assert qualifier.find_qualifiers("The meeting on May 5, 2026 was held in May.") == []
    assert qualifier.find_qualifiers("Council may defer the item.") == ["may"]


def test_modal_and_tentative_words_are_found():
    found = qualifier.find_qualifiers("Staff proposed a fee that would be subject to approval and could change.")
    assert found == ["subject to", "could", "would", "proposed"]


def test_easy_read_lines_for_a_claim_are_checked_together():
    p = passage("p", "Not a borrowing approval; final limit not yet received.")
    c = claim("This is not a borrowing approval. The limit is not yet received.")
    assert qualifier.check_easy_read(["This is not a loan approval.", "We don't have the limit yet."], c, {"p": p}) \
        == (["not a", "not yet"], [])
    assert qualifier.check_easy_read(["This is not a loan approval."], c, {"p": p})[1] == ["not yet"]


# ---------- NLI (optional) ----------

def test_nli_skips_cleanly_when_model_unavailable(monkeypatch, tmp_path):
    monkeypatch.setattr(nli, "CACHE_PATH", tmp_path / "nli.json")
    monkeypatch.setattr(nli, "_loaded", None)
    monkeypatch.setattr(nli, "load_model", lambda allow_download=True: False)
    result = nli.check("Council approved it.", "Council approved it.")
    assert result["available"] is False and result["flag"] is False
    assert "approved" not in json.dumps({k: v for k, v in result.items() if k != "reason"})


def test_nli_flags_contradiction_and_low_entailment():
    contradiction = nli.judge({"contradiction": 0.9, "entailment": 0.05, "neutral": 0.05})
    neutral = nli.judge({"contradiction": 0.1, "entailment": 0.3, "neutral": 0.6})
    entailed = nli.judge({"contradiction": 0.01, "entailment": 0.95, "neutral": 0.04})
    assert contradiction["flag"] and neutral["flag"] and not entailed["flag"]
    assert set(entailed) == {"available", "model", "scores", "label", "flag", "reason"}


def test_nli_cache_key_uses_both_hashes():
    assert nli.cache_key("a", "b") != nli.cache_key("b", "a")
    assert nli.cache_key("a", "b") == nli.cache_key("a", "b")


def test_nli_model_when_installed(monkeypatch, tmp_path):
    if not nli.load_model(allow_download=False):
        pytest.skip("NLI model not installed locally")
    monkeypatch.setattr(nli, "CACHE_PATH", tmp_path / "nli.json")
    result = nli.check("Council approved the by-law.", "Council rejected the by-law.")
    assert result["label"] == "contradiction" and result["flag"]
    assert json.loads((tmp_path / "nli.json").read_text())


# ---------- Drift Sentinel: rule drift ----------

def test_ten_days_vs_ten_business_days_is_caught():
    difference = drift.compare_rule("within 10 days of the initial communication",
                                    "no later than ten (10) business days")
    assert difference == "Guide says 10 days; the rule says 10 business days."
    assert drift.compare_rule("within 10 business days", "no later than ten (10) business days") is None


def test_clock_time_mismatch_is_caught():
    difference = drift.compare_rule("Registration closes at 10 a.m. on Monday.", "Registration closes at noon on Monday.")
    assert difference == "Clock times: guide says 10:00; the rule says 12:00."
    assert drift.compare_rule("closes at 10 a.m.", "closes at 10:00 am") is None
    assert drift.clock_times("4:30 p.m. or 12 am") == {"16:30", "00:00"}
    assert drift.time_limits("a 20-day appeal period, or thirty (30) days") == {"20 days", "30 days"}


def test_durations_channels_and_eligibility_are_compared():
    assert "Durations" in drift.compare_rule("Speakers get 10 minutes.", "Delegations may speak for five minutes.")
    assert "Channels" in drift.compare_rule("Send it by e-mail.", "Send it by e-mail or mail.")
    assert "Eligibility" in drift.compare_rule("Any person may register.", "Residents may register.")


def test_channel_and_eligibility_words_match_whole_words_only():
    assert drift.words_found("Presidents and unregistered lieutenants", drift.ELIGIBILITY) == set()
    assert drift.words_found("Send an e-mail, a fax or regular mail", drift.CHANNELS) == {"e-mail", "fax", "mail"}
    assert drift.words_found("Send an email", drift.CHANNELS) == {"e-mail"}


def test_a_side_that_says_nothing_is_not_drift():
    assert drift.compare_rule("Register by e-mail.", "Register within 10 days.") is None


def test_rule_drift_keeps_both_passages():
    passages = {"g": passage("g", "within 10 days"), "r": passage("r", "ten (10) business days")}
    pair = models.RulePair(id="RP", topic="t", guide_passage="g", rule_passage="r")
    [found] = drift.rule_drift([pair], passages, TODAY)
    assert (found.guide.passage_id, found.rule.passage_id) == ("g", "r")


# ---------- Drift Sentinel: source drift ----------

def test_changed_source_sha_sets_needs_recheck():
    c = claim("t", checked_against={"S": "a" * 64}, review={"by": "x", "status": "approved"})
    assert drift.source_drift([c], {"S": "a" * 64}) == []
    found = drift.source_drift([c], {"S": "b" * 64}, TODAY)
    assert [d.claim_id for d in found] == ["c"]
    assert drift.mark_needs_recheck([c], found) == ["c"]
    assert c.review.status == "needs_recheck"


def test_source_drift_looks_up_the_cited_passage(tmp_path):
    new_file = tmp_path / "new.html"
    new_file.write_text("<html><script>x()</script><p>The last day for filing an objection is\n"
                        "November 9, 2026</p></html>")
    paths = {"b" * 64: str(new_file)}
    c = claim("t", checked_against={"S": "a" * 64})

    unchanged = {"p": passage("p", "The last day for filing an objection")}
    assert drift.source_drift([c], {"S": "b" * 64}, TODAY, unchanged, paths) == []

    changed = {"p": passage("p", "The last day for filing an objection is November 6, 2026")}
    [found] = drift.source_drift([c], {"S": "b" * 64}, TODAY, changed, paths)
    assert "changed in the newer snapshot" in found.difference

    note = {"p": passage("p", "The last day for filing an objection", kind="research_note")}
    [found] = drift.source_drift([c], {"S": "b" * 64}, TODAY, note, paths)
    assert "research note" in found.difference

    gone = {"p": passage("p", "Council approved the zoning by-law amendment for the plaza")}
    [found] = drift.source_drift([c], {"S": "b" * 64}, TODAY, gone, paths)
    assert "couldn't be found" in found.difference


def test_source_drift_through_build_and_staff_report(review_copy, tmp_path):
    review_io_path = review_copy / "matters" / "fees-2026.yaml"
    data = review_io.read_yaml(review_io_path)
    data["claims"][5]["checked_against"] = {"S-p202": "a" * 64}
    review_io.write_yaml(review_io_path, data)
    db = tmp_path / "fetch.sqlite"
    make_fetch_db(db, [(P202_URL, "a" * 64, "2026-11-13T00:00:00+00:00", "snapshots/missing-a.html"),
                       (P202_URL, "b" * 64, "2026-11-14T00:00:00+00:00", "snapshots/missing-b.html")])

    generated_on, records = staff_report.report(review_copy, TODAY, db)
    [source] = [r for r in records if r["kind"] == "source_drift"]
    assert source["passage_a"]["passage_id"] == "PA-p202-register"
    assert "research note" in source["difference"]
    assert source["caveat"] == "A difference alone does not establish which source is right."

    paths = staff_report.write_report(generated_on, records, tmp_path / "staff")
    assert [p.name for p in paths] == ["drift.csv", "drift.json"]
    assert "10 business days" in paths[0].read_text()
    assert len(json.loads(paths[1].read_text())["discrepancies"]) == len(records)


def test_staff_report_rule_row_has_both_passages_and_a_diff():
    generated_on, records = staff_report.report(today=TODAY)
    [rule] = [r for r in records if r["id"] == "D-RP-p253-lobbyist"]
    assert rule["passage_a"]["url"].startswith("https://") and rule["passage_b"]["url"].endswith(".pdf")
    assert {"op": "equal", "text": "days"} in rule["word_diff"]


# ---------- Easy Read ----------

def test_easy_read_grade_is_computed():
    assert easyread.grade("The City charges fees for some services.") == pytest.approx(5.7)
    assert easyread.grade("Yes.") == 0.0
    review = review_io.read_review()
    passages = {p.id: p for p in review.passages}
    report = easyread.check_matter(review.matters[0], passages)
    assert all(isinstance(line["grade_level"], float) for line in report["lines"])
    assert report["set_grade_level"] is not None and report["target"] == easyread.TARGET_NOTE
    easyread.set_grade_levels(review.matters)
    assert all(line.grade_level is not None for m in review.matters for line in m.easy_read)


def test_easy_read_check_reports_dropped_qualifier():
    p = passage("p", "Not a borrowing approval; limit not yet received.")
    c = claim("This is not a borrowing approval. The limit is not yet received.", id="C-x")
    line = models.EasyReadLine(id="ER-x", text="The City can borrow money.", claim_id="C-x")
    matter = models.Matter(id="m", title="t", topics=["x"], authority="a", authority_ids=["a"], location="citywide",
                           claims=[c], easy_read=[line])
    report = easyread.check_matter(matter, {"p": p})
    assert report["claims_missing_qualifiers"] == {"C-x": ["not a", "not yet"]}


# ---------- Diffs ----------

def test_diff_ops():
    assert diffs.word_diff("within 10 days", "within 10 business days") == [
        {"op": "equal", "text": "within 10"}, {"op": "insert", "text": "business"}, {"op": "equal", "text": "days"}]
    assert diffs.word_diff("closes at 10 a.m.", "closes at noon") == [
        {"op": "equal", "text": "closes at"}, {"op": "delete", "text": "10 a.m."}, {"op": "insert", "text": "noon"}]
    assert diffs.word_diff("same", "same") == [{"op": "equal", "text": "same"}]
    assert diffs.summary(diffs.word_diff("a b", "a c")) == "a [-b-] {+c+}"


# ---------- AI drafts ----------

def fake_ollama(calls):
    def answer(prompt):
        calls.append(prompt)
        if "Easy Read" in prompt:
            return ("C-d1: : The City checks how much it can borrow.\n"
                    "C-d2: Debt was 9% and it was approved.\n"
                    "Here are your lines.\n"
                    "C-zz: A line for a claim that doesn't exist.")
        return "Debt charges were 3.37% of revenue."
    return answer


def hashes(folder):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*.yaml"))}


def test_ai_drafts_are_never_approved(monkeypatch, tmp_path, review_copy):
    calls = []
    monkeypatch.setattr(ai, "call_ollama", fake_ollama(calls))
    monkeypatch.setattr(ai, "CACHE_PATH", tmp_path / "ai_cache.json")
    monkeypatch.setattr(ai, "LOG_PATH", tmp_path / "ai-log.jsonl")
    monkeypatch.setattr(ai, "SUGGESTIONS_DIR", tmp_path / "suggestions")
    monkeypatch.setattr(nli, "check", lambda premise, hypothesis: {"available": False, "flag": False, "reason": "off"})
    before = hashes(review_copy)

    suggestions, path = ai.draft_matter("debt-limit-2026", review_copy)

    drafts = suggestions["paraphrases"] + suggestions["easy_read"]
    assert drafts and all(d["review"]["status"] == "pending" for d in drafts)
    assert "status: approved" not in path.read_text()
    assert hashes(review_copy) == before
    assert path.parent == tmp_path / "suggestions"
    log = [json.loads(line) for line in (tmp_path / "ai-log.jsonl").read_text().splitlines()]
    assert len(log) == len(drafts) and {entry["status"] for entry in log} == {"pending"}

    # every claim cites the same passage, so the model ran once for paraphrases and once for Easy Read
    assert len(calls) == 2
    assert [line["claim_id"] for line in suggestions["easy_read"]] == ["C-d1", "C-d2"]
    assert suggestions["easy_read"][0]["text"] == "The City checks how much it can borrow."
    flags = " ".join(suggestions["easy_read"][1]["checks"]["flags"])
    assert "drop qualifier(s): not a, not yet" in flags and "9" in flags and "approved" in flags
    assert suggestions["paraphrases"][0]["checks"]["qualifiers_missing"] == ["not a", "not yet"]


def test_ai_cache_reuses_output(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(ai, "call_ollama", fake_ollama(calls))
    monkeypatch.setattr(ai, "CACHE_PATH", tmp_path / "ai_cache.json")
    monkeypatch.setattr(nli, "check", lambda premise, hypothesis: {"available": False, "flag": False, "reason": "off"})
    first = ai.draft_paraphrase("Debt charges were 3.37% of revenue.", [])
    second = ai.draft_paraphrase("Debt charges were 3.37% of revenue.", [])
    assert len(calls) == 1
    assert (first["made_by"]["cached"], second["made_by"]["cached"]) == (False, True)
    assert second["made_by"]["model"] == ai.MODEL and second["made_by"]["prompt_version"] == "paraphrase-v1"
    assert first["review"]["status"] == second["review"]["status"] == "pending"
