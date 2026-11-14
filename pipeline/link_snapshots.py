"""Point the curated snapshots in review/snapshots.yaml at what pipeline/fetch.py really got.

    python3 pipeline/link_snapshots.py            update review/snapshots.yaml
    python3 pipeline/link_snapshots.py --dry-run  only print what would change

Only url, final_url, sha256, fetched_at, availability, reason, status, content_type and path
are ever changed.

- A placeholder url (a bare site root such as https://www.waterloo.ca/) is replaced with the
  document url in REAL_URLS, but only after a fetch of that url came back ok and the file's
  text contains the words that identify the document. Otherwise it stays and we say so.
- The other fields come from the latest fetch of the snapshot's url made the same way
  (obtained_by). A url that was skipped because its host blocked us earlier in that run
  takes the block it was skipped for. A fetch that failed for another reason (a timeout,
  say) tells us nothing about access, so it is passed over.
- sha256 is only ever the hash of an ok download, never of a block page. content_type and path
  belong to that same download.
"""
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse

import fitz

from models import Snapshot
from review_io import REVIEW_DIR, read_yaml, write_yaml

ROOT = Path(__file__).resolve().parent.parent
FETCH_DB = ROOT / "snapshots" / "snapshots.sqlite"
SNAPSHOTS_YAML = REVIEW_DIR / "snapshots.yaml"
LINKED_FIELDS = ["url", "final_url", "sha256", "fetched_at", "availability", "reason", "status", "content_type", "path"]
ACCESS_STATES = ("ok", "blocked", "sign_in", "dead")

# Real urls for curated snapshots that only recorded the site's home page. The research dossiers
# docs/research/ideas/N21.md, N58.md and N124.md downloaded these exact PDFs (HTTP 200) and quote
# them. Each comes with words its text must contain before we accept the fetched file is that document.
REAL_URLS = {
    "S-bylaw-2026-047": ("https://media-002-ca.cdn.govstack.com/waterloo-013-ca/media/zeqjquvr/fees-and-charges-bylaw.pdf",
                         ["2026-047", "Fees and Charges"]),
    "S-p209": ("https://www.waterloo.ca/media/jtzfarez/notice-of-intention-to-designate-131-william-st-w.pdf",
               ["131 William", "intention to designate"]),
    "S-p210": ("https://media-002-ca.cdn.govstack.com/waterloo-013-ca/media/kj2cb4ri/15-king-street-north-notice-of-passing.pdf",
               ["2026-080", "15 King"]),
}


def is_placeholder(url):
    return urlparse(url).path in ("", "/")


def latest_attempt(con, url, obtained_by):
    """Newest fetch_log row for url that says something about access, as a dict, or None."""
    rows = con.execute(
        "SELECT id, url, final_url, status, availability, reason, sha256, fetched_at FROM fetch_log "
        "WHERE (url = ? OR final_url = ?) AND obtained_by = ? ORDER BY id DESC", (url, url, obtained_by)).fetchall()
    for row in rows:
        attempt = dict(zip(["id", "url", "final_url", "status", "availability", "reason", "sha256", "fetched_at"], row))
        if attempt["availability"] in ACCESS_STATES:
            return attempt
        if attempt["availability"] == "not_tried":
            return block_that_stopped(con, attempt)
    return None


def block_that_stopped(con, skipped):
    """The fetch that made fetch.py stop asking this url's host, worded for the skipped url."""
    host = urlparse(skipped["url"]).netloc
    rows = con.execute("SELECT url, availability, reason, fetched_at FROM fetch_log "
                       "WHERE id < ? AND availability IN ('blocked', 'sign_in') ORDER BY id DESC", (skipped["id"],))
    for url, availability, reason, fetched_at in rows:
        if urlparse(url).netloc == host:
            return {"url": skipped["url"], "final_url": None, "status": None, "availability": availability,
                    "reason": f"not requested: {host} gave \"{reason}\" for {url}, so the host was left alone",
                    "sha256": None, "fetched_at": fetched_at}
    return None


def latest_ok_download(con, url, obtained_by):
    """(sha256, path, content_type) of the newest ok download of url, or three Nones."""
    row = con.execute(
        "SELECT sha256, path, content_type FROM fetch_log WHERE (url = ? OR final_url = ?) AND obtained_by = ? "
        "AND availability = 'ok' AND sha256 IS NOT NULL ORDER BY id DESC LIMIT 1", (url, url, obtained_by)).fetchone()
    return row if row else (None, None, None)


def squashed(text):
    """Text without spaces, lower case, every kind of dash as "-". PDFs print "2026 –047" for 2026-047."""
    return re.sub(r"[\u2010-\u2015\u2212]", "-", re.sub(r"\s+", "", text)).lower()


def file_text(path):
    path = ROOT / path
    if path.suffix == ".pdf":
        with fitz.open(path) as pdf:
            return "\n".join(page.get_text() for page in pdf)
    return path.read_text(encoding="utf-8", errors="replace")


def verify_real_url(con, snapshot_id, obtained_by):
    """(url, None) when the replacement url was fetched ok and its text matches, else (None, why not)."""
    url, words = REAL_URLS[snapshot_id]
    sha, path, _ = latest_ok_download(con, url, obtained_by)
    if not sha:
        return None, f"no ok fetch of {url} yet"
    text = squashed(file_text(path))
    missing = [word for word in words if squashed(word) not in text]
    if missing:
        return None, f"fetched {url} but its text lacks {missing}"
    return url, None


def link_snapshot(con, snapshot):
    """Update one snapshot dict in place. Returns a line describing what happened."""
    obtained_by = snapshot["obtained_by"]
    if is_placeholder(snapshot["url"]):
        if snapshot["id"] not in REAL_URLS:
            return f"{snapshot['id']}: left alone, its url {snapshot['url']} is a site root and no real url is known"
        url, problem = verify_real_url(con, snapshot["id"], obtained_by)
        if problem:
            return f"{snapshot['id']}: url not replaced ({problem})"
        snapshot["url"] = url

    attempt = latest_attempt(con, snapshot["url"], obtained_by)
    if attempt is None:
        return f"{snapshot['id']}: no usable fetch of {snapshot['url']} yet; nothing changed"

    if attempt["final_url"]:
        snapshot["final_url"] = attempt["final_url"]
    snapshot["fetched_at"] = attempt["fetched_at"]
    snapshot["availability"] = attempt["availability"]
    if attempt["reason"]:
        snapshot["reason"] = attempt["reason"]
    else:
        snapshot.pop("reason", None)
    if attempt["status"]:
        snapshot["status"] = attempt["status"]
    else:
        snapshot.pop("status", None)
    sha, path, content_type = latest_ok_download(con, snapshot["url"], obtained_by)
    if sha:
        snapshot["sha256"] = sha
        snapshot["path"] = path
        if content_type:
            snapshot["content_type"] = content_type
    how = f"HTTP {attempt['status']}" if attempt["status"] else attempt["reason"]
    return (f"{snapshot['id']}: {attempt['availability']} ({how}) "
            f"sha256 {sha[:12] + '...' if sha else 'none'} fetched {attempt['fetched_at']}")


def in_model_order(snapshot):
    """Keys in the order the Snapshot model lists them, so the file reads the same way for every record."""
    return {key: snapshot[key] for key in Snapshot.model_fields if key in snapshot}


def main(dry_run=False):
    data = read_yaml(SNAPSHOTS_YAML)
    con = sqlite3.connect(f"file:{FETCH_DB}?mode=ro", uri=True)
    before = [dict(s) for s in data["snapshots"]]
    linked = []
    for snapshot in data["snapshots"]:
        print(link_snapshot(con, snapshot))
        unchanged = {k: v for k, v in snapshot.items() if k not in LINKED_FIELDS}
        original = next(s for s in before if s["id"] == snapshot["id"])
        assert unchanged == {k: v for k, v in original.items() if k not in LINKED_FIELDS}
        Snapshot(**snapshot)
        linked.append(in_model_order(snapshot))
    con.close()
    if dry_run:
        print("dry run: review/snapshots.yaml not written")
        return
    write_yaml(SNAPSHOTS_YAML, {"snapshots": linked})
    print(f"Wrote {SNAPSHOTS_YAML.relative_to(ROOT)}")


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
