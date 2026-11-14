"""Pipeline store: pipeline/muni.sqlite (gitignored, rebuilt by every build).

Tables mirror the models. Each row keeps a few columns to query on plus the
whole record as JSON in `record`. passages_fts is an FTS5 index over passage text.

It also reads, never writes, snapshots/snapshots.sqlite, which pipeline/fetch.py
fills with one row per real fetch. That's how curated snapshot ids get linked
to the sha256 of what was actually downloaded.
"""
import json
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from models import FetchInfo, expand_particular_ids

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "pipeline" / "muni.sqlite"
FETCH_DB_PATH = ROOT / "snapshots" / "snapshots.sqlite"

TABLES = """
CREATE TABLE IF NOT EXISTS snapshots (id TEXT PRIMARY KEY, url TEXT, sha256 TEXT, availability TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS passages (id TEXT PRIMARY KEY, snapshot_id TEXT, kind TEXT, text TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS authorities (id TEXT PRIMARY KEY, name TEXT, tier TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS topics (slug TEXT PRIMARY KEY, name TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS matters (id TEXT PRIMARY KEY, title TEXT, location TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS identifiers (normalized TEXT, value TEXT, kind TEXT, matter_id TEXT, passage_id TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, matter_id TEXT, kind TEXT, date TEXT, passage_id TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS conditions (id TEXT PRIMARY KEY, matter_id TEXT, passage_id TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS windows (id TEXT PRIMARY KEY, matter_id TEXT, state TEXT, deadline_date TEXT, passage_id TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, matter_id TEXT, section TEXT, provenance TEXT, review_status TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS easy_read (id TEXT PRIMARY KEY, matter_id TEXT, claim_id TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS channels (id TEXT PRIMARY KEY, passage_id TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS rule_pairs (id TEXT PRIMARY KEY, guide_passage TEXT, rule_passage TEXT, record TEXT);
CREATE TABLE IF NOT EXISTS fetches (sha256 TEXT, url TEXT, final_url TEXT, status INTEGER, availability TEXT,
                                    fetched_at TEXT, particular TEXT, record TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS passages_fts USING fts5(passage_id UNINDEXED, text);
"""


def connect(path=DB_PATH):
    con = sqlite3.connect(path)
    con.executescript(TABLES)
    return con


def fresh(path=DB_PATH):
    """Start from an empty database file."""
    path = Path(path)
    if path.exists():
        path.unlink()
    return connect(path)


def as_json(record):
    return json.dumps(record.model_dump(mode="json", by_alias=True), ensure_ascii=False)


def upsert_snapshot(con, snapshot):
    con.execute("INSERT OR REPLACE INTO snapshots VALUES (?, ?, ?, ?, ?)",
                (snapshot.id, snapshot.url, snapshot.sha256, snapshot.availability, as_json(snapshot)))


def add_passage(con, passage):
    con.execute("INSERT OR REPLACE INTO passages VALUES (?, ?, ?, ?, ?)",
                (passage.id, passage.snapshot_id, passage.kind, passage.text, as_json(passage)))
    con.execute("DELETE FROM passages_fts WHERE passage_id = ?", (passage.id,))
    con.execute("INSERT INTO passages_fts (passage_id, text) VALUES (?, ?)", (passage.id, passage.text))


def add_matter(con, matter):
    con.execute("INSERT OR REPLACE INTO matters VALUES (?, ?, ?, ?)",
                (matter.id, matter.title, matter.location, as_json(matter)))
    for i in matter.identifiers:
        con.execute("INSERT INTO identifiers VALUES (?, ?, ?, ?, ?, ?)",
                    (i.normalized, i.value, i.kind, matter.id, i.passage_id, as_json(i)))
    for e in matter.events:
        con.execute("INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?)",
                    (e.id, matter.id, e.kind, e.date, e.passage_id, as_json(e)))
    for c in matter.conditions:
        con.execute("INSERT OR REPLACE INTO conditions VALUES (?, ?, ?, ?)", (c.id, matter.id, c.passage_id, as_json(c)))
    for w in matter.windows:
        con.execute("INSERT OR REPLACE INTO windows VALUES (?, ?, ?, ?, ?, ?)",
                    (w.id, matter.id, w.state, w.deadline_date, w.passage_id, as_json(w)))
    for c in matter.claims:
        con.execute("INSERT OR REPLACE INTO claims VALUES (?, ?, ?, ?, ?, ?)",
                    (c.id, matter.id, c.section, c.provenance, c.review.status, as_json(c)))
    for line in matter.easy_read:
        con.execute("INSERT OR REPLACE INTO easy_read VALUES (?, ?, ?, ?)", (line.id, matter.id, line.claim_id, as_json(line)))


def load_review(review, con):
    """Copy a validated ReviewSet into the store."""
    for snapshot in review.snapshots:
        upsert_snapshot(con, snapshot)
    for passage in review.passages:
        add_passage(con, passage)
    for authority in review.authorities:
        con.execute("INSERT OR REPLACE INTO authorities VALUES (?, ?, ?, ?)",
                    (authority.id, authority.name, authority.tier, as_json(authority)))
    for topic in review.topics:
        con.execute("INSERT OR REPLACE INTO topics VALUES (?, ?, ?)", (topic.slug, topic.name, as_json(topic)))
    for matter in review.matters:
        add_matter(con, matter)
    for channel in review.channels:
        con.execute("INSERT OR REPLACE INTO channels VALUES (?, ?, ?)", (channel.id, channel.passage_id, as_json(channel)))
    for pair in review.rule_pairs:
        con.execute("INSERT OR REPLACE INTO rule_pairs VALUES (?, ?, ?, ?)",
                    (pair.id, pair.guide_passage, pair.rule_passage, as_json(pair)))
    con.commit()


def search_passages(con, q, limit=20):
    """Full-text search over passage text. Each word is quoted, so FTS5 operators in q are just text."""
    words = re.findall(r"\w+", q)
    if not words:
        return []
    query = " ".join(f'"{word}"' for word in words)
    rows = con.execute(
        "SELECT p.id, p.snapshot_id, p.kind, p.text FROM passages_fts f JOIN passages p ON p.id = f.passage_id "
        "WHERE passages_fts MATCH ? ORDER BY rank LIMIT ?", (query, limit)).fetchall()
    return [{"id": r[0], "snapshot_id": r[1], "kind": r[2], "text": r[3]} for r in rows]


# ---------- Real fetches from pipeline/fetch.py ----------

def availability_from_status(status, obtained_by):
    """What an HTTP status says about access. None when it doesn't say."""
    if obtained_by == "manual":
        return "ok"
    if status is None:
        return None
    if 200 <= status < 300:
        return "ok"
    if status == 401:
        return "sign_in"
    if status == 403:
        return "blocked"
    if status in (404, 410):
        return "dead"
    return None


def read_fetch_rows(path=FETCH_DB_PATH):
    """Rows fetch.py wrote, oldest first, as FetchInfo plus their raw particular text. [] if no file yet."""
    path = Path(path)
    if not path.exists():
        return []
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT url, final_url, status, fetched_at, sha256, content_type, particular, obtained_by, path "
            "FROM snapshots ORDER BY fetched_at, id").fetchall()
    finally:
        con.close()
    fetches = []
    for url, final_url, status, fetched_at, sha256, content_type, particular, obtained_by, file_path in rows:
        info = FetchInfo(
            fetched_at=fetched_at, url=url, final_url=final_url, status=status,
            availability=availability_from_status(status, obtained_by), sha256=sha256,
            content_type=content_type, obtained_by=obtained_by, path=file_path,
        )
        fetches.append((info, expand_particular_ids(particular or "")))
    return fetches


def import_fetch_rows(con, fetches):
    for info, particular_ids in fetches:
        con.execute("INSERT INTO fetches VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (info.sha256, info.url, info.final_url, info.status, info.availability,
                     info.fetched_at, ",".join(particular_ids), as_json(info)))
    con.commit()


def is_specific_url(url):
    """False for a bare site root like https://www.waterloo.ca/.

    Some curated snapshots only record the site's home page, and every fetch of
    that page would otherwise look like a fetch of their document.
    """
    return urlparse(url).path not in ("", "/")


def fetches_by_snapshot(snapshots, fetches):
    """{snapshot id: [FetchInfo, oldest first]} matched on url or final url."""
    linked = {}
    for snapshot in snapshots:
        if not is_specific_url(snapshot.url):
            continue
        linked[snapshot.id] = [info for info, _ in fetches if snapshot.url in (info.url, info.final_url)]
    return linked
