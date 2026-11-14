"""Fetch public sources via headless Chrome and store immutable snapshots.

Rules (plan §3): normal browser, no bot bypass, 2-5 s delay per host,
snapshots never overwritten, addressed by sha256, metadata in SQLite.
"""
import hashlib
import mimetypes
import random
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "snapshots"
DB_PATH = SNAPSHOTS / "snapshots.sqlite"
INBOX = ROOT / "manual_inbox"
_last_hit: dict[str, float] = {}

SCHEMA = """CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY, url TEXT, final_url TEXT, status INTEGER,
  fetched_at TEXT, sha256 TEXT, content_type TEXT, particular TEXT,
  obtained_by TEXT, path TEXT)"""


def _db() -> sqlite3.Connection:
    SNAPSHOTS.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute(SCHEMA)
    return con


def _polite_wait(host: str) -> None:
    """Keep 2-5 s between requests to the same host."""
    gap = random.uniform(2, 5)
    elapsed = time.time() - _last_hit.get(host, 0)
    if elapsed < gap:
        time.sleep(gap - elapsed)
    _last_hit[host] = time.time()


def _ext(content_type: str, url: str) -> str:
    ct = (content_type or "").split(";")[0].strip()
    if ct == "text/html":
        return "html"
    guess = mimetypes.guess_extension(ct) if ct else None
    return (guess or Path(urlparse(url).path).suffix or ".bin").lstrip(".")


def store(data: bytes, *, url, final_url, status, content_type, particular, obtained_by) -> dict:
    """Write bytes to snapshots/<host>/<sha256>.<ext> (never overwrite) and log a row."""
    sha = hashlib.sha256(data).hexdigest()
    host = urlparse(final_url or url).netloc or "manual"
    path = SNAPSHOTS / host / f"{sha}.{_ext(content_type, final_url or url)}"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)
    row = dict(url=url, final_url=final_url, status=status,
               fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
               sha256=sha, content_type=content_type, particular=particular,
               obtained_by=obtained_by, path=str(path.relative_to(ROOT)))
    with _db() as con:
        con.execute(f"INSERT INTO snapshots ({','.join(row)}) VALUES ({','.join('?' * len(row))})",
                    list(row.values()))
    return row


def fetch(url: str, particular: str | None = None) -> dict:
    """Fetch one URL with headless Chrome; PDFs via the browser context's request API."""
    from playwright.sync_api import sync_playwright

    _polite_wait(urlparse(url).netloc)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context()
        try:
            if url.lower().split("?")[0].endswith(".pdf"):
                resp = context.request.get(url)
                data, final_url = resp.body(), resp.url
            else:
                page = context.new_page()
                resp = page.goto(url, wait_until="networkidle", timeout=60000)
                ctype = resp.headers.get("content-type", "") if resp else ""
                if "pdf" in ctype:
                    data = context.request.get(url).body()
                else:
                    data = page.content().encode("utf-8")
                final_url = page.url
            status = resp.status if resp else None
            ctype = resp.headers.get("content-type", "") if resp else ""
        finally:
            browser.close()
    return store(data, url=url, final_url=final_url, status=status,
                 content_type=ctype, particular=particular, obtained_by="chromium")


def ingest_manual_inbox(particular: str | None = None) -> list[dict]:
    """Ingest files a human saved into manual_inbox/ (obtained_by='manual')."""
    rows = []
    for f in sorted(INBOX.glob("*")):
        if f.is_file():
            ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            rows.append(store(f.read_bytes(), url=f"manual:{f.name}", final_url=None, status=None,
                              content_type=ctype, particular=particular, obtained_by="manual"))
            done = INBOX / "ingested"
            done.mkdir(exist_ok=True)
            shutil.move(str(f), done / f.name)
    return rows


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: fetch.py <url> [P###]   |   fetch.py --inbox [P###]")
    arg, part = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
    print(ingest_manual_inbox(part) if arg == "--inbox" else fetch(arg, part))
