"""Read and write the git-tracked review files in review/ (plan §8).

Layout:
  review/index.yaml              checked_on date and the matters, in the order the site lists them
  review/snapshots.yaml          every snapshot
  review/passages.yaml           every passage claims and events cite
  review/topics.yaml             the six public topics
  review/authorities.yaml        City, Region, Province and tribunal bodies
  review/matters/<matter>.yaml   one matter: identifiers, events, conditions, windows, claims, easy_read
  review/rule_pairs.yaml         guide passage vs the rule it paraphrases (Drift Sentinel)
  review/channels.yaml           what each comment channel says about publication (Exposure Preview)
  review/planted.yaml            the planted dropped-condition claim the build must block
"""
import re
from pathlib import Path

import yaml
from pydantic import BaseModel

from models import Authority, Channel, Matter, Passage, PlantedClaim, RulePair, Snapshot, Topic, check_iso_date

REVIEW_DIR = Path(__file__).resolve().parent.parent / "review"

BOOL_TAG = "tag:yaml.org,2002:bool"
TIMESTAMP_TAG = "tag:yaml.org,2002:timestamp"


class ReviewLoader(yaml.SafeLoader):
    """Plain YAML 1.1 would turn `on:` into True and 2026-11-13 into a date object.

    Review files use `on:` for the review date and lots of bare dates, so only
    true/false count as booleans here and dates stay strings.
    """


ReviewLoader.yaml_implicit_resolvers = {
    first: [(tag, regexp) for tag, regexp in resolvers if tag not in (BOOL_TAG, TIMESTAMP_TAG)]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
ReviewLoader.add_implicit_resolver(BOOL_TAG, re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$"), list("tTfF"))


class ReviewSet(BaseModel):
    checked_on: str
    topics: list[Topic]
    authorities: list[Authority]
    snapshots: list[Snapshot]
    passages: list[Passage]
    matters: list[Matter]
    planted_claims: list[PlantedClaim] = []
    rule_pairs: list[RulePair] = []
    channels: list[Channel] = []


def read_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=ReviewLoader) or {}


def write_yaml(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=110)
    path.write_text(text, encoding="utf-8")


def read_list(path, key):
    data = read_yaml(path)
    if key not in data:
        raise ValueError(f"{path} has no '{key}' list")
    return data[key] or []


def read_review(review_dir=REVIEW_DIR):
    """Load every review file and validate it against the models. Raises on the first bad record."""
    review_dir = Path(review_dir)
    index = read_yaml(review_dir / "index.yaml")
    checked_on = index.get("checked_on")
    if not checked_on:
        raise ValueError("review/index.yaml needs a checked_on date")
    check_iso_date(checked_on)

    listed = index.get("matters") or []
    on_disk = sorted(path.stem for path in (review_dir / "matters").glob("*.yaml"))
    if sorted(listed) != on_disk or len(set(listed)) != len(listed):
        raise ValueError(f"review/index.yaml lists matters {listed} but review/matters/ has {on_disk}")
    matters = []
    for matter_id in listed:
        matter = read_yaml(review_dir / "matters" / f"{matter_id}.yaml")
        if matter.get("id") != matter_id:
            raise ValueError(f"{matter_id}.yaml holds matter '{matter.get('id')}'; the file name must match the id")
        matters.append(matter)

    return ReviewSet(
        checked_on=checked_on,
        topics=read_list(review_dir / "topics.yaml", "topics"),
        authorities=read_list(review_dir / "authorities.yaml", "authorities"),
        snapshots=read_list(review_dir / "snapshots.yaml", "snapshots"),
        passages=read_list(review_dir / "passages.yaml", "passages"),
        matters=matters,
        planted_claims=read_list(review_dir / "planted.yaml", "planted_claims"),
        rule_pairs=read_list(review_dir / "rule_pairs.yaml", "rule_pairs"),
        channels=read_list(review_dir / "channels.yaml", "channels"),
    )


def dump(record):
    """A model as plain YAML-ready data, leaving out fields that are still at their default."""
    return record.model_dump(mode="json", by_alias=True, exclude_defaults=True)


def write_review(review, review_dir=REVIEW_DIR):
    """Write a ReviewSet back out in the layout above."""
    review_dir = Path(review_dir)
    write_yaml(review_dir / "index.yaml",
               {"checked_on": review.checked_on, "matters": [m.id for m in review.matters]})
    write_yaml(review_dir / "snapshots.yaml", {"snapshots": [dump(s) for s in review.snapshots]})
    write_yaml(review_dir / "passages.yaml", {"passages": [dump(p) for p in review.passages]})
    write_yaml(review_dir / "topics.yaml", {"topics": [dump(t) for t in review.topics]})
    write_yaml(review_dir / "authorities.yaml", {"authorities": [dump(a) for a in review.authorities]})
    write_yaml(review_dir / "planted.yaml", {"planted_claims": [dump(c) for c in review.planted_claims]})
    write_yaml(review_dir / "rule_pairs.yaml", {"rule_pairs": [dump(r) for r in review.rule_pairs]})
    write_yaml(review_dir / "channels.yaml", {"channels": [dump(c) for c in review.channels]})
    for matter in review.matters:
        write_yaml(review_dir / "matters" / f"{matter.id}.yaml", matter_for_file(matter))


def matter_for_file(matter):
    """Matter data for its own file. matter_id and normalized are filled in on load, so leave them out."""
    data = dump(matter)
    for key in ("identifiers", "events", "conditions", "windows", "claims", "easy_read"):
        for item in data.get(key, []):
            item.pop("matter_id", None)
            item.pop("normalized", None)
    return data
