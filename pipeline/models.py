"""Muni data model (implementation plan §5), as Pydantic v2 models.

Every review file, inventory row and export record goes through these models.
Rules that can be checked on one record alone live here as validators. Rules
that need several records (a passage exists, a quote is inside its passage)
live in build.py.

Run:
  python3 pipeline/models.py --schema   writes schema/<Model>.json
  python3 pipeline/models.py --uml      writes docs/uml.md (Mermaid class diagram)
"""
import json
import re
import sys
import types
import typing
from datetime import date
from pathlib import Path
from typing import Literal, Optional

from dateutil import parser as date_parser
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
UML_PATH = ROOT / "docs" / "uml.md"

# The seven Decision Facts headings, in page order (plan §6.2).
SECTIONS = ["applies_to", "what_and_why", "who_decides", "conditions", "not_decided", "have_a_say", "records"]

EVENT_KINDS = [
    "proposed", "staff_recommendation", "committee_action", "council_decision", "mayoral_instrument",
    "provincial_decision", "appeal_window", "in_force", "repealed", "amended", "implemented",
]

ROLE_CODE = r"^[A-G][1-3]$"
PARTICULAR_ID = r"^P\d{3}$"
SHA256 = r"^[0-9a-f]{64}$"
# Event dates can be partial ("2026") when the record gives no day.
PARTIAL_DATE = r"^\d{4}(-\d{2}(-\d{2})?)?$"

Provenance = Literal["quote", "extraction", "ai_paraphrase", "human"]
ReviewStatus = Literal["approved", "edit", "reject", "needs_recheck", "pending"]
Availability = Literal["ok", "blocked", "sign_in", "dead", "request_only"]
EventKind = Literal[
    "proposed", "staff_recommendation", "committee_action", "council_decision", "mayoral_instrument",
    "provincial_decision", "appeal_window", "in_force", "repealed", "amended", "implemented",
]
# What a reviewer stores. "dated" becomes open or closed at build time.
WindowInputState = Literal["dated", "rule_based", "not_published", "not_checked", "source_unavailable"]
WindowState = Literal["open", "closed", "rule_based", "not_published", "not_checked", "source_unavailable"]
IdentifierKind = Literal["report no.", "file no.", "by-law no.", "OPA no.", "MD no.", "address"]

MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December"
          "|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec")
MONTH_DATE = re.compile(r"\b(?:" + MONTHS + r")\.?\s+\d{1,2},?\s+\d{4}\b")
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def normalize_identifier(value):
    """Fold case, spaces, dashes, dots and underscores, and spell by-law one way.

    The site's search box (site/app.js norm()) does exactly the same thing.
    """
    value = value.lower()
    value = re.sub(r"by-?law", "bylaw", value)
    return re.sub(r"[\s\-_.]", "", value)


def check_iso_date(value):
    """Raise if value isn't a real YYYY-MM-DD date."""
    # fromisoformat alone also takes forms like 20261113, which wouldn't sort against other dates
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"'{value}' isn't a YYYY-MM-DD date")
    date.fromisoformat(value)
    return value


def dates_in_text(text):
    """Return every date written in text as YYYY-MM-DD, e.g. 'Nov 8, 2026' -> '2026-11-08'."""
    found = [date_parser.parse(m.group(0)).date().isoformat() for m in MONTH_DATE.finditer(text)]
    found += [m.group(0) for m in ISO_DATE.finditer(text)]
    return found


def expand_particular_ids(text):
    """Turn a snapshot's particular field such as 'P011-P014,P196' into ['P011', ..., 'P014', 'P196']."""
    ids = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        match = re.fullmatch(r"P(\d{3})-P(\d{3})", part)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            ids += [f"P{n:03d}" for n in range(start, end + 1)]
        elif re.fullmatch(PARTICULAR_ID, part):
            ids.append(part)
        else:
            raise ValueError(f"can't read particular id '{part}' (expected P### or P###-P###)")
    return ids


class Record(BaseModel):
    # Unknown keys are almost always typos in a hand-edited review file, so reject them.
    model_config = ConfigDict(extra="forbid")


# ---------- Review and evidence ----------

class Review(Record):
    by: str = ""
    on: Optional[str] = None
    status: ReviewStatus = "pending"
    note: str = ""

    @field_validator("on")
    @classmethod
    def on_is_date(cls, value):
        return check_iso_date(value) if value else value

    @model_validator(mode="after")
    def approval_names_reviewer(self):
        if self.status == "approved" and not self.by:
            raise ValueError("an approved item needs a reviewer in review.by")
        return self


class Snapshot(Record):
    id: str
    url: str
    final_url: Optional[str] = None
    fetched_at: str
    checked_on: Optional[str] = None
    sha256: Optional[str] = Field(default=None, pattern=SHA256)
    content_type: Optional[str] = None
    status: Optional[int] = None
    obtained_by: Literal["chromium", "manual"]
    availability: Availability
    reason: str = ""
    particular: str = Field(default="", description="Inventory ids, e.g. 'P011-P014,P196'.")
    publisher: str
    title: str
    path: Optional[str] = None

    @model_validator(mode="after")
    def unavailable_needs_reason(self):
        if self.availability != "ok" and not self.reason:
            raise ValueError(f"snapshot {self.id} is {self.availability} but gives no reason")
        expand_particular_ids(self.particular)
        return self

    def particular_ids(self):
        return expand_particular_ids(self.particular)


class Locator(Record):
    page: Optional[int] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    element_path: Optional[str] = None
    label: str = Field(default="", description="Human-readable place, e.g. 'minutes s.9'.")

    @model_validator(mode="after")
    def says_where(self):
        if self.page is None and not self.element_path and not self.label:
            raise ValueError("a locator needs a page, an element path or a label")
        if self.char_start is not None and self.char_end is not None and self.char_end < self.char_start:
            raise ValueError("char_end is before char_start")
        return self


class Role(Record):
    code: str = Field(pattern=ROLE_CODE)
    method: Literal["rule", "llm", "human"]


class Passage(Record):
    id: str
    snapshot_id: str
    locator: Locator
    kind: Literal["verbatim", "research_note"]
    text: str = Field(min_length=1)
    roles: list[Role] = []
    note: str = ""


class Authority(Record):
    id: str
    name: str
    tier: Literal["City", "Region", "Province", "tribunal"]


class Topic(Record):
    slug: str = Field(pattern=r"^[a-z0-9-]+$")
    name: str
    description: str


# ---------- Matter and its parts ----------

class Identifier(Record):
    value: str
    normalized: str = ""
    kind: IdentifierKind
    matter_id: str = ""
    passage_id: str
    valid_from: str = ""
    valid_to: str = ""
    note: str = ""
    review: Review = Field(default_factory=Review)

    @model_validator(mode="after")
    def fill_normalized(self):
        expected = normalize_identifier(self.value)
        if self.normalized and self.normalized != expected:
            raise ValueError(f"identifier '{self.value}' should normalize to '{expected}'")
        self.normalized = expected
        for value in (self.valid_from, self.valid_to):
            if value:
                check_iso_date(value)
        return self


class Event(Record):
    id: str
    matter_id: str = ""
    kind: EventKind
    date: str = Field(pattern=PARTIAL_DATE)
    actor: str
    outcome_text: str = Field(min_length=1, description="Verbatim from the passage.")
    passage_id: str
    establishes: str
    not_establishes: str
    review: Review = Field(default_factory=Review)


class Condition(Record):
    id: str
    matter_id: str = ""
    text: str = Field(min_length=1)
    applies_to: str = ""
    imposed_by: Literal["decision", "report", "study_mitigation"]
    passage_id: str
    review: Review = Field(default_factory=Review)


class ParticipationWindow(Record):
    id: str
    matter_id: str = ""
    action: str
    channel: str = ""
    state: WindowInputState
    deadline_quote: str = ""
    deadline_date: Optional[str] = None
    passage_id: str
    checked_on: Optional[str] = None
    note: str = ""
    review: Review = Field(default_factory=Review)
    computed_state: Optional[WindowState] = None

    @model_validator(mode="after")
    def deadline_comes_from_quote(self):
        if self.deadline_date:
            if not self.deadline_quote or not self.passage_id:
                raise ValueError(f"window {self.id}: a deadline_date needs a deadline_quote and a passage_id")
            check_iso_date(self.deadline_date)
            if self.deadline_date not in dates_in_text(self.deadline_quote):
                raise ValueError(f"window {self.id}: deadline_date {self.deadline_date} isn't written in its quote")
        if self.state == "dated" and not self.deadline_date:
            raise ValueError(f"window {self.id}: state 'dated' needs a deadline_date")
        if self.state != "dated" and self.deadline_date:
            raise ValueError(f"window {self.id}: only a 'dated' window can have a deadline_date")
        if self.state == "rule_based" and not self.deadline_quote:
            raise ValueError(f"window {self.id}: a rule_based window needs the rule quoted in deadline_quote")
        if self.state == "source_unavailable" and not self.note:
            raise ValueError(f"window {self.id}: say in note why the source is unavailable")
        if self.checked_on:
            check_iso_date(self.checked_on)
        return self


class Claim(Record):
    id: str
    matter_id: str = ""
    section: str
    text: str = Field(min_length=1)
    provenance: Provenance
    passage_ids: list[str]
    fallback: str = ""
    review: Review = Field(default_factory=Review)
    checked_against: dict[str, str] = Field(default={}, description="snapshot_id -> sha256 the reviewer checked.")
    qualifiers_required: list[str] = []
    qualifiers_waived: dict[str, str] = Field(default={}, description="marker -> reason it isn't material.")

    @model_validator(mode="after")
    def has_source(self):
        if not self.passage_ids:
            raise ValueError(f"claim {self.id} cites no passage")
        if self.section not in SECTIONS:
            raise ValueError(f"claim {self.id} has unknown section {self.section}")
        if self.provenance == "ai_paraphrase" and not self.fallback:
            raise ValueError(f"AI claim {self.id} needs a source fallback for 'Show without AI'")
        for marker, reason in self.qualifiers_waived.items():
            if not reason.strip():
                raise ValueError(f"claim {self.id} waives '{marker}' without a reason")
        for snapshot_id, sha in self.checked_against.items():
            if not re.fullmatch(SHA256, sha):
                raise ValueError(f"claim {self.id}: checked_against[{snapshot_id}] isn't a sha256")
        return self


class PlantedClaim(Claim):
    """A deliberately bad claim kept in review/planted.yaml to prove the checks block it."""
    note: str = ""

    @model_validator(mode="after")
    def names_its_matter(self):
        if not self.matter_id:
            raise ValueError(f"planted claim {self.id} needs a matter_id")
        return self


class EasyReadLine(Record):
    id: str
    matter_id: str = ""
    text: str = Field(min_length=1)
    claim_id: str
    grade_level: Optional[float] = None
    review: Review = Field(default_factory=Review)


class Matter(Record):
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    title: str
    topics: list[str] = Field(min_length=1, description="Topic names, as in review/topics.yaml.")
    authority: str = Field(description="Display text naming who decides.")
    authority_ids: list[str] = Field(min_length=1)
    location: str = Field(description="An address, a place name or 'citywide'.")
    wards: list[int] = []
    identifiers: list[Identifier] = []
    events: list[Event] = []
    conditions: list[Condition] = []
    windows: list[ParticipationWindow] = []
    claims: list[Claim] = []
    easy_read: list[EasyReadLine] = []

    @model_validator(mode="after")
    def parts_belong_here(self):
        for ward in self.wards:
            if not 1 <= ward <= 7:
                raise ValueError(f"matter {self.id}: Waterloo has wards 1-7, not {ward}")
        parts = self.identifiers + self.events + self.conditions + self.windows + self.claims + self.easy_read
        for part in parts:
            if part.matter_id and part.matter_id != self.id:
                raise ValueError(f"matter {self.id} holds an item that says it belongs to {part.matter_id}")
            part.matter_id = self.id
        seen = set()
        for part in parts:
            item_id = getattr(part, "id", None)
            if item_id is None:
                continue
            if item_id in seen:
                raise ValueError(f"matter {self.id} uses id {item_id} twice")
            seen.add(item_id)
        claim_ids = {c.id for c in self.claims}
        for line in self.easy_read:
            if line.claim_id not in claim_ids:
                raise ValueError(f"Easy Read line {line.id} points to {line.claim_id}, which isn't a claim in {self.id}")
        return self


class Channel(Record):
    id: str
    channel: str
    statement: str = Field(description="What the channel's official page says about publication.")
    passage_id: str
    review: Review = Field(default_factory=Review)


class RulePair(Record):
    id: str
    topic: str
    guide_passage: str
    rule_passage: str


class PassageRef(Record):
    passage_id: str
    text: str


class Discrepancy(Record):
    id: str
    kind: Literal["rule_drift", "source_drift"]
    topic: str = ""
    guide: Optional[PassageRef] = Field(default=None, description="Rule drift: the guidance side (source A).")
    rule: Optional[PassageRef] = Field(default=None, description="Rule drift: the binding side (source B).")
    claim_id: Optional[str] = None
    snapshot_id: Optional[str] = None
    checked_sha256: Optional[str] = None
    latest_sha256: Optional[str] = None
    difference: str
    suggested_fix: str = ""
    found_on: str = ""
    status: Literal["open", "resolved"] = "open"


# ---------- Research inventory (data/inventory) ----------

class SecondaryRole(Record):
    code: str = Field(pattern=ROLE_CODE)
    reason: str


class FetchInfo(Record):
    """One row from snapshots/snapshots.sqlite, as written by pipeline/fetch.py."""
    fetched_at: str
    url: str
    final_url: Optional[str] = None
    status: Optional[int] = None
    availability: Optional[Availability] = None
    sha256: str = Field(pattern=SHA256)
    content_type: Optional[str] = None
    obtained_by: str
    path: str


class Particular(Record):
    id: str = Field(pattern=PARTICULAR_ID)
    title: str
    level: str
    family: str = Field(pattern=r"^DF\d{2}$")
    family_name: str
    subfamily: str = Field(pattern=r"^DF\d{2}\.\d+$")
    subfamily_name: str
    components: list[str] = Field(default=[], description="Document-family codes of components inside it.")
    group: str
    authority: str
    url: str
    retrieval_urls: list[str] = []
    access: str
    access_note: str
    pull_confirmed: str
    original_response_status: Optional[int] = None
    original_response_kind: Optional[str] = None
    publication_structure: str
    transferability: str
    extraction: str
    summary: str
    primary_role: str = Field(pattern=ROLE_CODE)
    primary_reason: str
    secondary_roles: list[SecondaryRole] = []
    role_note: str = ""
    supplied_roles: str = ""
    supplied_primary: str = Field(pattern=ROLE_CODE, description="Primary role in the earlier baseline / graph.")
    categories: list[str] = Field(default=[], description="Graph role codes (earlier baseline).")
    classification_reason: str = ""
    parsing_note: str = ""
    evidence: str
    evidence_detail: str = ""
    evidence_references: list[str] = []
    cross_refs: list[str] = []
    authority_status: str = ""
    linked_snapshot_ids: list[str] = []
    linked_matter_ids: list[str] = []
    latest_fetch: Optional[FetchInfo] = None


class Endpoint(Record):
    kind: Literal["particular", "role", "description"]
    value: str


class Relationship(Record):
    model_config = ConfigDict(extra="forbid", validate_by_name=True, validate_by_alias=True)

    id: str
    categories: str = Field(description="The edge as written in the graph, e.g. 'C1 → C2 → C3'.")
    from_: list[Endpoint] = Field(alias="from")
    to: list[Endpoint]
    chain: list[list[Endpoint]] = Field(description="Every node in order; from = first, to = last.")
    arrows: list[Literal["→", "↔"]]
    families: list[str] = Field(min_length=1)
    meaning: str
    condition: str
    evidence: str
    url: str
    limitation: str
    connection_basis: str = ""
    dependency: str = ""
    retrieval_dependency: str = ""
    access_context: str = ""
    evidence_url_current_test: str = ""
    evidence_particular_ids: list[str] = Field(default=[], description="Particulars whose URL is the evidence URL.")

    @field_validator("families")
    @classmethod
    def families_are_r_codes(cls, families):
        for family in families:
            if not re.fullmatch(r"R[1-8]", family):
                raise ValueError(f"relationship family {family} isn't R1-R8")
        return families


class RelationshipFamily(Record):
    code: str = Field(pattern=r"^R[1-8]$")
    name: str
    verbs: str
    meaning: str


class DocumentComponent(Record):
    id: str
    label: str
    element_type: str
    description: str
    source_particular: str = Field(pattern=PARTICULAR_ID)
    url: str
    subcategory_codes: list[str]


# ---------- Schema and UML generation ----------

# Order here is the order in schema/ and docs/uml.md.
MODELS = [
    Snapshot, Locator, Role, Passage, Authority, Topic, Matter, Identifier, Event, Condition,
    ParticipationWindow, Claim, PlantedClaim, EasyReadLine, Review, Channel, RulePair, PassageRef,
    Discrepancy, Particular, SecondaryRole, FetchInfo, Relationship, Endpoint, RelationshipFamily,
    DocumentComponent,
]

# Fields that hold another record's id, for the dotted "refers to" arrows in the UML.
ID_FIELDS = {
    "snapshot_id": "Snapshot", "passage_id": "Passage", "passage_ids": "Passage", "claim_id": "Claim",
    "matter_id": "Matter", "authority_ids": "Authority", "guide_passage": "Passage",
    "rule_passage": "Passage", "source_particular": "Particular", "cross_refs": "Particular",
    "linked_snapshot_ids": "Snapshot", "linked_matter_ids": "Matter", "evidence_particular_ids": "Particular",
}


def write_schemas(schema_dir=SCHEMA_DIR):
    schema_dir.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        schema = model.model_json_schema(by_alias=True)
        (schema_dir / f"{model.__name__}.json").write_text(json.dumps(schema, indent=1, ensure_ascii=False) + "\n")
    return len(MODELS)


def type_label(annotation):
    """A short Mermaid-safe type name, e.g. list~Claim~ or Optional~str~."""
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin is Literal:
        return "enum"
    if origin is list:
        return f"list~{type_label(args[0])}~"
    if origin is dict:
        return "dict"
    if origin in (typing.Union, types.UnionType):
        inner = [a for a in args if a is not type(None)]
        return f"Optional~{type_label(inner[0])}~"
    return getattr(annotation, "__name__", str(annotation))


def nested_models(annotation):
    """Model classes used inside a field type, e.g. list[Claim] -> [Claim]."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return [annotation]
    found = []
    for arg in typing.get_args(annotation):
        found += nested_models(arg)
    return found


def uml_text():
    lines = [
        "# Muni data model (UML)",
        "",
        "Generated from `pipeline/models.py` by `python3 pipeline/models.py --uml`. Don't edit by hand.",
        "",
        "Solid diamonds mean one record contains the other. Dotted arrows mean a field holds the other record's id.",
        "",
        "```mermaid",
        "classDiagram",
    ]
    links = []
    for model in MODELS:
        lines.append(f"  class {model.__name__} {{")
        for name, field in model.model_fields.items():
            shown = field.alias or name
            lines.append(f"    +{type_label(field.annotation)} {shown}")
            for inner in nested_models(field.annotation):
                links.append(f"  {model.__name__} *-- {inner.__name__} : {shown}")
            if name in ID_FIELDS:
                links.append(f"  {model.__name__} ..> {ID_FIELDS[name]} : {name}")
        lines.append("  }")
    lines.append("  Claim <|-- PlantedClaim")
    lines += sorted(set(links))
    lines += ["```", ""]
    return "\n".join(lines)


def write_uml(path=UML_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(uml_text())


if __name__ == "__main__":
    if "--schema" in sys.argv:
        print(f"Wrote {write_schemas()} schemas to {SCHEMA_DIR}")
    if "--uml" in sys.argv:
        write_uml()
        print(f"Wrote {UML_PATH}")
    if "--schema" not in sys.argv and "--uml" not in sys.argv:
        sys.exit("usage: models.py --schema | --uml")
