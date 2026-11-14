"""Load the research inventory (data/inventory) into Particular, Relationship and DocumentComponent models.

Two files describe the same 267 particulars (P001-P267):
  Waterloo-particulars-classified.json  this research pass: family, roles, summary, parsing notes
  Claude-Waterloo-context.json          the earlier graph: url, access result, group, 21 relationships

Both are merged by id. Loading fails if an id is missing or repeated, or if a
cross-reference or relationship endpoint points at something that doesn't exist.
"""
import json
import re
from pathlib import Path

from pydantic import BaseModel

from models import (
    DocumentComponent, Endpoint, Particular, Relationship, RelationshipFamily, SecondaryRole,
    expand_particular_ids,
)

ROOT = Path(__file__).resolve().parent.parent
CLASSIFIED_PATH = ROOT / "data" / "inventory" / "Waterloo-particulars-classified.json"
GRAPH_PATH = ROOT / "data" / "inventory" / "Claude-Waterloo-context.json"
EXPECTED_IDS = [f"P{n:03d}" for n in range(1, 268)]

# Graph edges whose end is a description, not a role code or particular. Each needs a reason.
DESCRIBED_ENDPOINTS = {
    "linked A/B/etc. resources": "L21: guide and catalogue pages link out to many resource types; the graph names no single target.",
}


class Inventory(BaseModel):
    generated: str
    source_check_date: str
    families: dict
    roles: dict
    particulars: list[Particular]
    relationships: list[Relationship]
    relationship_families: list[RelationshipFamily]
    document_components: list[DocumentComponent]
    retrieval_audit: dict
    retrieval_limits: list[str]
    described_endpoints: dict[str, str]

    def particular_ids(self):
        return {p.id for p in self.particulars}


def read_roles(categories):
    """Flatten the graph's A-G categories into {code: {name, description, category, category_name}}."""
    roles = {}
    for letter, (name, description, subcategories) in categories.items():
        for code, (sub_name, sub_description) in subcategories.items():
            roles[code] = {"code": code, "name": sub_name, "description": sub_description,
                           "category": letter, "category_name": name, "category_description": description}
    return roles


def merge_particular(row, graph_row, families):
    supplied = row["supplied"]
    family = families[row["family"]]
    return Particular(
        id=row["id"],
        title=row["title"],
        level=row["level"],
        family=row["family"],
        family_name=family["name"],
        subfamily=row["subfamily"],
        subfamily_name=family["subfamilies"][row["subfamily"]]["name"],
        components=row["components"],
        group=supplied["group"],
        authority=supplied["authority"],
        url=supplied["url"],
        retrieval_urls=supplied["retrieval_urls"],
        access=supplied["access"],
        access_note=supplied["access_note"],
        pull_confirmed=supplied["pull_confirmed"],
        original_response_status=graph_row["original_response_status"],
        original_response_kind=graph_row["original_response_kind"],
        publication_structure=supplied["publication_structure"],
        transferability=supplied["transferability"],
        extraction=supplied["extraction"],
        summary=row["summary"],
        primary_role=row["primary"],
        primary_reason=row["primary_reason"],
        secondary_roles=[SecondaryRole(**s) for s in row["secondary"]],
        role_note=row["role_note"],
        supplied_roles=row["supplied_roles"],
        supplied_primary=graph_row["primary_subcategory"],
        categories=graph_row["categories"],
        classification_reason=graph_row["classification_reason"],
        parsing_note=row["parsing_note"],
        evidence=row["evidence"],
        evidence_detail=row["evidence_detail"],
        evidence_references=graph_row["evidence_references"],
        cross_refs=row["cross_refs"],
        authority_status=row["authority_status"],
    )


def check_ids(ids, source):
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"{source} repeats particular ids {duplicates}")
    missing = sorted(set(EXPECTED_IDS) - set(ids))
    extra = sorted(set(ids) - set(EXPECTED_IDS))
    if missing or extra:
        raise ValueError(f"{source}: missing {missing}, unexpected {extra}")


def parse_node(node, particular_ids, roles):
    """One side of an edge, e.g. 'F1/D3' -> two role endpoints."""
    node = node.strip()
    parts = [part.strip() for part in node.split("/")]
    if all(part in roles or part in particular_ids for part in parts):
        return [Endpoint(kind="role" if part in roles else "particular", value=part) for part in parts]
    if node in DESCRIBED_ENDPOINTS:
        return [Endpoint(kind="description", value=node)]
    raise ValueError(f"relationship endpoint '{node}' is not a role code, a particular id or a listed description")


def parse_relationship(row, particular_ids, roles, url_owners):
    pieces = re.split(r"\s*(→|↔)\s*", row["categories"].strip())
    nodes, arrows = pieces[0::2], pieces[1::2]
    if len(nodes) < 2:
        raise ValueError(f"relationship {row['id']} has no arrow in '{row['categories']}'")
    chain = [parse_node(node, particular_ids, roles) for node in nodes]
    fields = {key: value for key, value in row.items() if key != "categories"}
    return Relationship(
        categories=row["categories"],
        chain=chain,
        arrows=arrows,
        to=chain[-1],
        evidence_particular_ids=sorted(url_owners.get(row["url"], [])),
        **{"from": chain[0]},
        **fields,
    )


def load_inventory(classified_path=CLASSIFIED_PATH, graph_path=GRAPH_PATH):
    classified = json.loads(Path(classified_path).read_text())
    graph = json.loads(Path(graph_path).read_text())

    rows = classified["particulars"]
    graph_rows = graph["particulars"]
    check_ids([r["id"] for r in rows], Path(classified_path).name)
    check_ids([r["id"] for r in graph_rows], Path(graph_path).name)
    graph_by_id = {r["id"]: r for r in graph_rows}

    families = classified["families"]
    roles = read_roles(graph["categories"])
    subfamilies = {code for family in families.values() for code in family["subfamilies"]}

    particulars = []
    for row in rows:
        particular = merge_particular(row, graph_by_id[row["id"]], families)
        members = families[particular.family]["subfamilies"].get(particular.subfamily, {}).get("members", [])
        if particular.id not in members:
            raise ValueError(f"{particular.id} says subfamily {particular.subfamily}, which doesn't list it")
        for code in particular.components:
            if code not in subfamilies:
                raise ValueError(f"{particular.id} has unknown component family {code}")
        for code in [particular.primary_role] + [s.code for s in particular.secondary_roles]:
            if code not in roles:
                raise ValueError(f"{particular.id} has unknown role {code}")
        particulars.append(particular)

    particular_ids = {p.id for p in particulars}
    for particular in particulars:
        unknown = [ref for ref in particular.cross_refs if ref not in particular_ids]
        if unknown:
            raise ValueError(f"{particular.id} cross-references unknown particulars {unknown}")

    url_owners = {}
    for particular in particulars:
        for url in [particular.url] + particular.retrieval_urls:
            url_owners.setdefault(url, set()).add(particular.id)

    relationships = [parse_relationship(r, particular_ids, roles, url_owners) for r in graph["relationships"]]
    relationship_ids = [r.id for r in relationships]
    if len(relationship_ids) != len(set(relationship_ids)):
        raise ValueError("relationship ids repeat")

    relationship_families = [
        RelationshipFamily(code=code, name=name, verbs=verbs, meaning=meaning)
        for code, (name, verbs, meaning) in graph["relationship_families"].items()
    ]
    family_codes = {f.code for f in relationship_families}
    for relationship in relationships:
        for family in relationship.families:
            if family not in family_codes:
                raise ValueError(f"relationship {relationship.id} uses unknown family {family}")

    components = [
        DocumentComponent(
            id=c["id"], label=c["label"], element_type=c["element type"], description=c["description"],
            source_particular=c["source particular"], url=c["url"], subcategory_codes=c["subcategory codes"],
        )
        for c in graph["graph_document_components"]
    ]
    for component in components:
        if component.source_particular not in particular_ids:
            raise ValueError(f"component {component.id} points to unknown {component.source_particular}")

    return Inventory(
        generated=classified["generated"],
        source_check_date=graph["source_check_date"],
        families=families,
        roles=roles,
        particulars=particulars,
        relationships=relationships,
        relationship_families=relationship_families,
        document_components=components,
        retrieval_audit=graph["retrieval_audit"],
        retrieval_limits=graph["retrieval_limits"],
        described_endpoints=DESCRIBED_ENDPOINTS,
    )


def passages_cited_by(matter):
    cited = set()
    for item in matter.identifiers + matter.events + matter.conditions + matter.windows:
        cited.add(item.passage_id)
    for claim in matter.claims:
        cited.update(claim.passage_ids)
    return cited


def link_usage(inventory, review):
    """Record on each particular which snapshots and matters use it.

    Returns {matter_id: [particular ids]}. Raises if a snapshot names a particular
    that isn't in the inventory.
    """
    known = inventory.particular_ids()
    by_id = {p.id: p for p in inventory.particulars}
    snapshot_particulars = {}
    for snapshot in review.snapshots:
        ids = expand_particular_ids(snapshot.particular)
        unknown = [i for i in ids if i not in known]
        if unknown:
            raise ValueError(f"snapshot {snapshot.id} names particulars not in the inventory: {unknown}")
        snapshot_particulars[snapshot.id] = ids
        for particular_id in ids:
            by_id[particular_id].linked_snapshot_ids.append(snapshot.id)

    passage_snapshot = {p.id: p.snapshot_id for p in review.passages}
    matter_particulars = {}
    for matter in review.matters:
        ids = set()
        for passage_id in passages_cited_by(matter):
            snapshot_id = passage_snapshot.get(passage_id)
            ids.update(snapshot_particulars.get(snapshot_id, []))
        matter_particulars[matter.id] = sorted(ids)
        for particular_id in ids:
            by_id[particular_id].linked_matter_ids.append(matter.id)
    return matter_particulars
