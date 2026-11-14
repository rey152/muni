"""Drift Sentinel (plan §6.9): staff-facing consistency checks.

rule_drift:   a guidance passage states a different participation rule from the
              rule it paraphrases: time limits and their units, clock times,
              durations, channels or eligibility words.
source_drift: a source changed after a reviewer checked a claim against it, and
              the cited passage changed, vanished, or can't be compared.

Neither check says which source is right; a difference alone doesn't establish that.
"""
import re
from pathlib import Path

from bs4 import BeautifulSoup
from rapidfuzz import fuzz

from models import Discrepancy, PassageRef

ROOT = Path(__file__).resolve().parent.parent.parent

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "forty-five": 45,
    "sixty": 60, "ninety": 90,
}
# "ten (10) business days": the bracketed figure repeats the word, so it's skipped. "20-day" counts too.
NUMBER = r"(\d+|\b(?:" + "|".join(NUMBER_WORDS) + r")\b)[\s-]*(?:\(\d+\)[\s-]*)?"
TIME_LIMIT = re.compile(NUMBER + r"(?:(business|working|calendar|clear)\s+)?(day|week|month|year)s?\b")
DURATION = re.compile(NUMBER + r"(minute|min|hour|hr)s?\b")
CLOCK_TIME = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*([ap])\.?\s?m\b\.?|\b(\d{1,2}):(\d{2})\b|\b(noon|midnight)\b")

CHANNELS = {
    "e-mail": r"e-?mail",
    "online": r"online|web ?form",
    "in person": r"in[- ]person",
    "mail": r"(?<!e-)mail|canada post|by post",
    "phone": r"(?:tele)?phone",
    "fax": r"fax",
}
ELIGIBILITY = {
    "any person": r"any person|anyone|anybody",
    "resident": r"residents?",
    "property owner": r"(?:property )?owners?",
    "tenant": r"tenants?",
    "registered": r"registered|registrants?",
    "applicant": r"applicants?",
    "member of the public": r"members? of the public",
    "eligible": r"eligible|eligibility",
}

RULE_FIX = "Ask the page owner to check the guide wording against the by-law and quote the by-law's wording."
SOURCE_FIX = "Re-read the cited passage in the new snapshot, then re-approve, edit or reject the claim."
CAVEAT = "A difference alone does not establish which source is right."
# rapidfuzz partial match score (0-100) above which a passage counts as "changed" rather than "vanished"
CHANGED_SCORE = 70


def as_number(raw):
    return int(raw) if raw.isdigit() else NUMBER_WORDS[raw]


def plural(number, unit):
    return unit if number == 1 else unit + "s"


def time_limits(text):
    """Every time limit in text, e.g. {'10 business days'}."""
    found = set()
    for match in TIME_LIMIT.finditer(text.lower()):
        number = as_number(match.group(1))
        unit = plural(number, match.group(3))
        if match.group(2):
            unit = f"{match.group(2)} {unit}"
        found.add(f"{number} {unit}")
    return found


def durations(text):
    found = set()
    for match in DURATION.finditer(text.lower()):
        number = as_number(match.group(1))
        unit = "hour" if match.group(2) in ("hour", "hr") else "minute"
        found.add(f"{number} {plural(number, unit)}")
    return found


def clock_times(text):
    """Every clock time as 24-hour HH:MM, e.g. '10 a.m.' -> '10:00'."""
    found = set()
    for match in CLOCK_TIME.finditer(text.lower()):
        hour, minute, half, hour24, minute24, word = match.groups()
        if word:
            found.add("12:00" if word == "noon" else "00:00")
        elif half:
            hour = int(hour) % 12 + (12 if half == "p" else 0)
            found.add(f"{hour:02d}:{minute or '00'}")
        else:
            found.add(f"{int(hour24):02d}:{minute24}")
    return found


def words_found(text, table):
    """Names from table whose pattern appears as whole words ("residents" but not "presidents")."""
    lowered = text.lower()
    return {name for name, pattern in table.items() if re.search(r"\b(?:" + pattern + r")\b", lowered)}


def rule_values(text):
    """Comparable values in a participation rule, by kind."""
    return {
        "time limits": time_limits(text),
        "clock times": clock_times(text),
        "durations": durations(text),
        "channels": words_found(text, CHANNELS),
        "eligibility words": words_found(text, ELIGIBILITY),
    }


def listed(values):
    return " and ".join(sorted(values))


def compare_rule(guide_text, rule_text):
    """Say how the two passages differ, or None.

    A kind only counts when both sides mention it. If one side says nothing about
    channels, say, there's nothing to compare, and that isn't reported as drift.
    """
    guide = rule_values(guide_text)
    rule = rule_values(rule_text)
    differences = []
    for kind in guide:
        if not guide[kind] or not rule[kind] or guide[kind] == rule[kind]:
            continue
        if kind == "time limits":
            differences.append(f"Guide says {listed(guide[kind])}; the rule says {listed(rule[kind])}.")
        else:
            differences.append(f"{kind.capitalize()}: guide says {listed(guide[kind])}; "
                               f"the rule says {listed(rule[kind])}.")
    return " ".join(differences) or None


def rule_drift(pairs, passages, found_on=""):
    """Compare each RulePair's guide passage with its rule passage. passages maps id -> Passage."""
    found = []
    for pair in pairs:
        guide = passages[pair.guide_passage]
        rule = passages[pair.rule_passage]
        difference = compare_rule(guide.text, rule.text)
        if difference:
            found.append(Discrepancy(
                id=f"D-{pair.id}",
                kind="rule_drift",
                topic=pair.topic,
                guide=PassageRef(passage_id=guide.id, text=guide.text),
                rule=PassageRef(passage_id=rule.id, text=rule.text),
                difference=difference,
                suggested_fix=RULE_FIX,
                found_on=found_on,
            ))
    return found


# ---------- Source drift ----------

def snapshot_text(path):
    """Plain text of a fetched file (HTML, PDF or text), or None if the file isn't there."""
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        return None
    if path.suffix.lower() == ".pdf":
        import fitz  # PyMuPDF; only needed for PDFs and slow to import

        with fitz.open(path) as pdf:
            return "\n".join(page.get_text() for page in pdf)
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in (".html", ".htm"):
        soup = BeautifulSoup(raw, "lxml")
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text(" ")
    return raw


def squash(text):
    return re.sub(r"\s+", " ", text).strip()


def passage_change(passage, new_text):
    """How a cited passage looks in a newer snapshot.

    Returns {"state", "new_text", "reason"}. state is one of:
      unchanged       the passage is still there word for word
      changed         something close is there; new_text is that span
      vanished        nothing close is there
      not_comparable  a research note (not source text) or no new text to look in
    """
    if passage.kind != "verbatim":
        return {"state": "not_comparable", "new_text": None,
                "reason": f"{passage.id} is a research note, not source text, so it can't be found in the snapshot."}
    if new_text is None:
        return {"state": "not_comparable", "new_text": None,
                "reason": "The newer snapshot file isn't on disk, so the passage couldn't be looked up."}
    old = squash(passage.text)
    new = squash(new_text)
    if old in new:
        return {"state": "unchanged", "new_text": old, "reason": f"{passage.id} is still there word for word."}
    match = fuzz.partial_ratio_alignment(old, new)
    if match.score >= CHANGED_SCORE:
        return {"state": "changed", "new_text": new[match.dest_start:match.dest_end],
                "reason": f"{passage.id} changed in the newer snapshot."}
    return {"state": "vanished", "new_text": None,
            "reason": f"{passage.id} couldn't be found in the newer snapshot."}


def fetch_paths(fetches):
    """{sha256: file path} from store.read_fetch_rows() output."""
    return {info.sha256: info.path for info, _ in fetches}


def source_drift(claims, snapshots_now, found_on="", passages=None, paths_by_sha=None):
    """Flag claims whose checked snapshot has a newer, different hash and whose cited passage moved.

    snapshots_now maps snapshot id -> sha256 of the latest fetch of that
    snapshot's URL (build.py works this out from snapshots/snapshots.sqlite).
    A claim with no checked_against entry can't drift, so it's skipped.

    With passages (id -> Passage) and paths_by_sha (sha256 -> file path), each
    cited passage from that snapshot is looked up in the new file. If every one
    is still there word for word, the page changed somewhere else and the claim
    isn't flagged. Anything else, including "couldn't check", is flagged, so
    leaving out passages or paths flags every hash change.
    """
    found = []
    for claim in claims:
        for snapshot_id, checked_sha in claim.checked_against.items():
            latest_sha = snapshots_now.get(snapshot_id)
            if not latest_sha or latest_sha == checked_sha:
                continue
            reasons = []
            if passages is not None and paths_by_sha is not None:
                path = paths_by_sha.get(latest_sha)
                new_text = snapshot_text(path) if path else None
                cited = [passages[pid] for pid in claim.passage_ids if passages[pid].snapshot_id == snapshot_id]
                changes = [passage_change(passage, new_text) for passage in cited]
                if cited and all(change["state"] == "unchanged" for change in changes):
                    continue
                reasons = [change["reason"] for change in changes if change["state"] != "unchanged"]
                if not cited:
                    reasons = [f"No passage claim {claim.id} cites comes from {snapshot_id}."]
            difference = f"Snapshot {snapshot_id} changed since claim {claim.id} was checked."
            if reasons:
                difference += " " + " ".join(reasons)
            found.append(Discrepancy(
                id=f"D-{claim.id}-{snapshot_id}",
                kind="source_drift",
                topic=f"Claim {claim.id}",
                claim_id=claim.id,
                snapshot_id=snapshot_id,
                checked_sha256=checked_sha,
                latest_sha256=latest_sha,
                difference=difference,
                suggested_fix=SOURCE_FIX,
                found_on=found_on,
            ))
    return found


def mark_needs_recheck(claims, discrepancies):
    """Set review.status to needs_recheck on every claim a source-drift discrepancy names.

    Only changes the in-memory records; review files on disk are left alone.
    Returns the claim ids it changed.
    """
    drifted = {d.claim_id: d.id for d in discrepancies if d.kind == "source_drift"}
    changed = []
    for claim in claims:
        if claim.id in drifted:
            claim.review.status = "needs_recheck"
            claim.review.note = f"Source changed after review ({drifted[claim.id]}). {claim.review.note}".strip()
            changed.append(claim.id)
    return changed
