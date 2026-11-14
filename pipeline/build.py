"""Muni build pipeline: validate reviewed records, run checks, export site/data/muni.json.

Run: python3 pipeline/build.py
"""
import json
import re
import sys
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, model_validator

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "review" / "matters.json"
OUTPUT = ROOT / "site" / "data" / "muni.json"

SECTIONS = ["applies_to", "what_and_why", "who_decides", "conditions", "not_decided", "have_a_say"]

# Words and phrases that carry a condition, exception or hedge (Qualifier Keeper).
QUALIFIER_MARKERS = [
    "subject to", "conditional on", "provided that", "unless", "until", "pending",
    "in principle", "draft", "received for information", "approximately", "estimated",
    "only if", "not a", "not yet", "except", "may", "if",
]


# ---------- Data model ----------

class Snapshot(BaseModel):
    id: str
    particular: str
    title: str
    publisher: str
    url: str
    fetched_at: str
    obtained_by: Literal["chromium", "manual"]
    availability: Literal["ok", "blocked", "sign_in", "dead", "request_only"]
    reason: str = ""


class Passage(BaseModel):
    id: str
    snapshot_id: str
    locator: str
    kind: Literal["verbatim", "research_note"]
    text: str
    roles: list[str]
    note: str = ""


class Identifier(BaseModel):
    value: str
    kind: str
    passage_id: str
    valid_from: str = ""
    valid_to: str = ""
    note: str = ""


class Event(BaseModel):
    kind: str
    date: str
    actor: str
    outcome_text: str
    passage_id: str
    establishes: str
    not_establishes: str


class Condition(BaseModel):
    text: str
    imposed_by: str
    passage_id: str


class Window(BaseModel):
    action: str
    channel: str
    state: Literal["dated", "rule_based", "not_published", "not_checked", "source_unavailable"]
    deadline_quote: str
    deadline_date: Optional[str] = None
    passage_id: str

    @model_validator(mode="after")
    def date_needs_quote(self):
        if self.deadline_date and not self.deadline_quote:
            raise ValueError("a deadline_date needs a deadline_quote")
        return self


class Claim(BaseModel):
    id: str
    section: str
    text: str
    provenance: Literal["quote", "extraction", "ai_paraphrase", "human"]
    passage_ids: list[str]
    fallback: str = ""
    review: str = "approved"
    qualifiers_required: list[str] = []
    qualifiers_waived: dict[str, str] = {}

    @model_validator(mode="after")
    def has_passage(self):
        if not self.passage_ids:
            raise ValueError(f"claim {self.id} cites no passage")
        if self.section not in SECTIONS:
            raise ValueError(f"claim {self.id} has unknown section {self.section}")
        if self.provenance == "ai_paraphrase" and not self.fallback:
            raise ValueError(f"AI claim {self.id} needs a source fallback for 'Show without AI'")
        return self


class EasyReadLine(BaseModel):
    text: str
    claim_id: str


class Matter(BaseModel):
    id: str
    title: str
    topics: list[str]
    authority: str
    location: str
    wards: list[int]
    identifiers: list[Identifier]
    events: list[Event]
    conditions: list[Condition]
    windows: list[Window]
    claims: list[Claim]
    easy_read: list[EasyReadLine]


# ---------- Item Passport ----------

def normalize_identifier(value):
    value = value.lower()
    value = re.sub(r"by-?law", "bylaw", value)
    return re.sub(r"[\s\-_.]", "", value)


# ---------- Qualifier Keeper ----------

def find_qualifiers(text):
    lowered = text.lower()
    found = []
    for marker in QUALIFIER_MARKERS:
        if re.search(r"\b" + re.escape(marker) + r"\b", lowered):
            # Skip short markers already covered by a longer one ("if" inside "only if").
            if any(marker in longer and marker != longer for longer in found):
                continue
            found.append(marker)
    return found


def missing_qualifiers(claim_text, passage_texts):
    required = []
    for text in passage_texts:
        for marker in find_qualifiers(text):
            if marker not in required:
                required.append(marker)
    claim_lower = claim_text.lower()
    missing = [m for m in required if not re.search(r"\b" + re.escape(m) + r"\b", claim_lower)]
    return required, missing


# ---------- Drift Sentinel ----------

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "five": 5, "ten": 10, "fifteen": 15, "thirty": 30}


def extract_time_limit(text):
    """Return (number, unit) such as (10, 'business days'), or None."""
    match = re.search(r"(\d+|\b(?:" + "|".join(NUMBER_WORDS) + r")\b)\s*(?:\(\d+\)\s*)?(business days|calendar days|days|minutes|hours)", text.lower())
    if not match:
        return None
    raw = match.group(1)
    number = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
    return number, match.group(2)


def compare_rule(guide_text, rule_text):
    guide = extract_time_limit(guide_text)
    rule = extract_time_limit(rule_text)
    if guide is None or rule is None or guide == rule:
        return None
    return f"Guide says {guide[0]} {guide[1]}; the rule says {rule[0]} {rule[1]}."


# ---------- Export ----------

def build(source=SOURCE):
    data = json.loads(Path(source).read_text())
    snapshots = [Snapshot(**s) for s in data["snapshots"]]
    passages = {p["id"]: Passage(**p) for p in data["passages"]}
    snapshot_ids = {s.id for s in snapshots}
    for p in passages.values():
        if p.snapshot_id not in snapshot_ids:
            raise ValueError(f"passage {p.id} points to missing snapshot {p.snapshot_id}")

    matters = [Matter(**m) for m in data["matters"]]
    planted = [(c["matter_id"], Claim(**{k: v for k, v in c.items() if k not in ("matter_id", "note")}))
               for c in data.get("planted_claims", [])]

    blocked = []
    alias = {}
    for matter in matters:
        for ident in matter.identifiers:
            if ident.passage_id not in passages:
                raise ValueError(f"identifier {ident.value} cites missing passage")
            alias[normalize_identifier(ident.value)] = matter.id
        for event in matter.events:
            if event.outcome_text != passages[event.passage_id].text:
                raise ValueError(f"event outcome in {matter.id} is not verbatim from {event.passage_id}")
        for window in matter.windows:
            if window.deadline_date and window.deadline_quote not in passages[window.passage_id].text:
                raise ValueError(f"deadline quote in {matter.id} not found in its passage")

        claims_with_planted = matter.claims + [c for mid, c in planted if mid == matter.id]
        kept = []
        for claim in claims_with_planted:
            for pid in claim.passage_ids:
                if pid not in passages:
                    raise ValueError(f"claim {claim.id} cites missing passage {pid}")
            texts = [passages[pid].text for pid in claim.passage_ids]
            required, missing = missing_qualifiers(claim.text, texts)
            claim.qualifiers_required = required
            if claim.review != "approved":
                continue
            missing = [m for m in missing if m not in claim.qualifiers_waived]
            if missing:
                blocked.append({"id": claim.id, "matter_id": matter.id, "text": claim.text, "missing": missing})
                continue
            kept.append(claim)
        matter.claims = kept
        claim_ids = {c.id for c in kept}
        matter.easy_read = [line for line in matter.easy_read if line.claim_id in claim_ids]

    discrepancies = []
    for pair in data.get("rule_pairs", []):
        guide = passages[pair["guide_passage"]]
        rule = passages[pair["rule_passage"]]
        difference = compare_rule(guide.text, rule.text)
        if difference:
            discrepancies.append({
                "kind": "rule_drift",
                "topic": pair["topic"],
                "guide": {"passage_id": guide.id, "text": guide.text},
                "rule": {"passage_id": rule.id, "text": rule.text},
                "difference": difference,
                "suggested_fix": "Ask the page owner to check the guide wording against the by-law and quote the by-law's unit.",
            })

    export = {
        "checked_on": data["checked_on"],
        "snapshots": [s.model_dump() for s in snapshots],
        "passages": [p.model_dump() for p in passages.values()],
        "matters": [m.model_dump() for m in matters],
        "channels": data.get("channels", []),
        "alias": alias,
        "blocked_claims": blocked,
        "discrepancies": discrepancies,
    }
    return export


def main():
    export = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(export, indent=1))
    claims = sum(len(m["claims"]) for m in export["matters"])
    print(f"Exported {len(export['matters'])} matters, {claims} claims, "
          f"{len(export['blocked_claims'])} blocked, {len(export['discrepancies'])} discrepancies -> {OUTPUT}")
    for b in export["blocked_claims"]:
        print(f"  BLOCKED {b['id']}: missing {b['missing']}")


if __name__ == "__main__":
    sys.exit(main())
