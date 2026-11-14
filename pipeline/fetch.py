"""Fetch public sources with headless system Chrome and keep immutable snapshots (plan §3).

    python3 pipeline/fetch.py --all              every url in pipeline/sources.yaml
    python3 pipeline/fetch.py --retry            only urls never fetched or last lost to a network error
    python3 pipeline/fetch.py <url> [P###]       one url
    python3 pipeline/fetch.py --inbox [P###]     files a person saved into manual_inbox/
    python3 pipeline/fetch.py --report           rewrite snapshots/fetch-report.json from the database

Rules this file keeps:
- One persistent Chrome context with the browser's own default user agent. Nothing is spoofed.
- HTML: wait for network idle, save page.content(), a full-page screenshot and the data
  (xhr/fetch/JSON) requests the page made. PDFs and other files go through context.request
  in the same context.
- One request at a time, and 2-5 s between requests to the same host.
- A 401/403/429, a bot-check page or a sign-in redirect stops that host for the rest of the run.
  We never retry it another way; a person downloads the file into manual_inbox/ instead.
- Snapshots are never overwritten: files are named by sha256, so a new hash is a new version.

snapshots/snapshots.sqlite has two tables:
  snapshots  one row per body we saved and hashed (pipeline/store.py reads this one)
  fetch_log  one row per url we handled, including failures with nothing to hash
"""
import hashlib
import json
import mimetypes
import random
import re
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ROOT / "snapshots"
DB_PATH = SNAPSHOTS / "snapshots.sqlite"
PROFILE_DIR = SNAPSHOTS / ".chrome-profile"
REPORT_PATH = SNAPSHOTS / "fetch-report.json"
SOURCES_PATH = ROOT / "pipeline" / "sources.yaml"
INBOX = ROOT / "manual_inbox"

MAX_BYTES = 60 * 1024 * 1024
TOO_LARGE = "too large to snapshot, not hashed"
FILE_SUFFIXES = (".pdf", ".zip", ".csv", ".json", ".geojson", ".xlsx", ".xls", ".docx", ".doc")
FILE_HINTS = ("f=json", "f=pjson", "f=geojson", "filestream.ashx", "/download_file/", "/gbfs/")

# Wording that only appears on bot-check pages, never on an ordinary page that happens to load a CAPTCHA script.
BOT_CHECK_TITLES = ("just a moment", "attention required", "please wait", "access denied", "ddos-guard",
                    "verifying your browser")
BOT_CHECK_PHRASES = ("checking your browser", "verify you are human", "enable javascript and cookies to continue")
SIGN_IN_WORDS = ("signin", "sign-in", "login", "log-in", "/oauth", "/sso/", "/saml")
# Query parameters that carry an access key. Their values are kept out of the saved request lists.
KEY_PARAM = re.compile(r"([?&](?:access_token|api_?key|apikey|key|token|client_secret|sig|signature)=)[^&#]*", re.I)
# Failures on our side of the wire. They say nothing about whether the site lets us in.
NETWORK_ERRORS = ("ENOTFOUND", "ETIMEDOUT", "ECONNRESET", "ECONNREFUSED", "EAI_AGAIN", "ERR_NAME_NOT_RESOLVED",
                  "ERR_INTERNET_DISCONNECTED", "ERR_NETWORK_CHANGED", "ERR_CONNECTION_RESET", "ERR_TIMED_OUT")

SNAPSHOTS_TABLE = """CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY, url TEXT, final_url TEXT, status INTEGER,
  fetched_at TEXT, sha256 TEXT, content_type TEXT, particular TEXT,
  obtained_by TEXT, path TEXT)"""
# Added after the first version of the table, so older databases get them with ALTER TABLE.
# text_sha256 is the hash of a page's visible text. The rendered DOM of the same page differs
# on every load (script order, random form ids), so only the text hash tells a real change.
SNAPSHOTS_EXTRA = {"availability": "TEXT", "reason": "TEXT", "bytes": "INTEGER", "text_sha256": "TEXT",
                   "screenshot": "TEXT", "data_requests": "TEXT", "note": "TEXT"}
LOG_TABLE = """CREATE TABLE IF NOT EXISTS fetch_log (
  id INTEGER PRIMARY KEY, url TEXT, final_url TEXT, status INTEGER, availability TEXT,
  reason TEXT, sha256 TEXT, bytes INTEGER, content_length INTEGER, content_type TEXT,
  fetched_at TEXT, particular TEXT, obtained_by TEXT, path TEXT, screenshot TEXT,
  data_requests TEXT, note TEXT, in_snapshots INTEGER)"""
LOG_EXTRA = {"text_sha256": "TEXT"}
LOG_COLUMNS = ["url", "final_url", "status", "availability", "reason", "sha256", "bytes", "content_length",
               "content_type", "fetched_at", "particular", "obtained_by", "path", "screenshot",
               "data_requests", "note", "in_snapshots", "text_sha256"]

last_request_at = {}   # host -> time.time() of our last request to it
blocked_hosts = {}     # host -> why we stopped asking it, for this run only


# ---------- Database ----------

def connect_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute(SNAPSHOTS_TABLE)
    con.execute(LOG_TABLE)
    add_missing_columns(con, "snapshots", SNAPSHOTS_EXTRA)
    add_missing_columns(con, "fetch_log", LOG_EXTRA)
    con.commit()
    return con


def add_missing_columns(con, table, columns):
    have = {row[1] for row in con.execute(f"PRAGMA table_info({table})")}
    for column, kind in columns.items():
        if column not in have:
            con.execute(f"ALTER TABLE {table} ADD COLUMN {column} {kind}")


def record(con, outcome):
    """Log one outcome; also add it to `snapshots` when it has a saved, hashed body.

    pipeline/store.py works out availability from the HTTP status alone, so a 200 that
    turned out to be a bot-check or sign-in page is kept out of `snapshots` (it would read as ok).
    """
    status = outcome["status"]
    status_says_ok = status is not None and 200 <= status < 300
    misleading = status_says_ok and outcome["availability"] != "ok"
    outcome["in_snapshots"] = int(bool(outcome["sha256"]) and not misleading)
    con.execute(f"INSERT INTO fetch_log ({','.join(LOG_COLUMNS)}) VALUES ({','.join('?' * len(LOG_COLUMNS))})",
                [outcome[c] for c in LOG_COLUMNS])
    if outcome["in_snapshots"]:
        columns = ["url", "final_url", "status", "fetched_at", "sha256", "content_type", "particular",
                   "obtained_by", "path", "availability", "reason", "bytes", "text_sha256", "screenshot",
                   "data_requests", "note"]
        con.execute(f"INSERT INTO snapshots ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})",
                    [outcome[c] for c in columns])
    con.commit()


def new_outcome(url, particular, obtained_by="chromium"):
    return {"url": url, "final_url": None, "status": None, "availability": None, "reason": "",
            "sha256": None, "bytes": None, "content_length": None, "content_type": None,
            "fetched_at": now_utc(), "particular": particular or "", "obtained_by": obtained_by,
            "path": None, "text_sha256": None, "screenshot": None, "data_requests": None, "note": "",
            "in_snapshots": 0}


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------- Files on disk ----------

def file_suffix(content_type, url):
    content_type = (content_type or "").split(";")[0].strip().lower()
    if content_type == "text/html":
        return "html"
    url_suffix = Path(urlparse(url).path).suffix.lower()
    if url_suffix in FILE_SUFFIXES:
        return url_suffix.lstrip(".")
    guess = mimetypes.guess_extension(content_type) if content_type else None
    return (guess or ".bin").lstrip(".")


def save_body(outcome, data):
    """Write bytes to snapshots/<host>/<sha256>.<ext> unless that exact file is already there."""
    sha = hashlib.sha256(data).hexdigest()
    url = outcome["final_url"] or outcome["url"]
    host = urlparse(url).netloc or "manual"
    path = SNAPSHOTS / host / f"{sha}.{file_suffix(outcome['content_type'], url)}"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(data)
    outcome["sha256"] = sha
    outcome["bytes"] = len(data)
    outcome["path"] = str(path.relative_to(ROOT))
    return path


# ---------- Politeness and access ----------

def polite_wait(host):
    """Keep 2-5 s between our requests to the same host."""
    gap = random.uniform(2, 5)
    elapsed = time.time() - last_request_at.get(host, 0)
    if elapsed < gap:
        time.sleep(gap - elapsed)
    last_request_at[host] = time.time()


def access_problem(status, final_url, title="", text=""):
    """(availability, reason) when the response is a block, a sign-in wall or a dead link, else None."""
    title = (title or "").strip().lower()
    text = (text or "").lower()
    bot_check = title.startswith(BOT_CHECK_TITLES) or any(p in text[:3000] for p in BOT_CHECK_PHRASES)
    if status == 401:
        return "sign_in", "HTTP 401 (sign-in required)"
    if status == 403:
        return "blocked", "HTTP 403" + (" (bot-check page)" if bot_check else "")
    if status == 429:
        return "blocked", "HTTP 429 (too many requests)"
    if status in (404, 410):
        return "dead", f"HTTP {status}"
    if bot_check:
        return "blocked", f"bot-check page (HTTP {status})"
    final = urlparse(final_url or "")
    if any(word in (final.path + "?" + final.query).lower() for word in SIGN_IN_WORDS):
        # The query of a sign-in url is mostly one-time state, so the reason keeps only where it went.
        return "sign_in", f"redirected to a sign-in page: {final.scheme}://{final.netloc}{final.path}"
    if status is None or status >= 400:
        return "error", f"HTTP {status}"
    return None


def looks_like_file(url):
    lowered = url.lower()
    return urlparse(lowered).path.endswith(FILE_SUFFIXES) or any(hint in lowered for hint in FILE_HINTS)


def without_keys(url):
    """url with the values of key-like query parameters (a page's map token, say) replaced by REDACTED.

    The request list is our own note of what a page asked for, not evidence, so nothing hashed changes.
    """
    return KEY_PARAM.sub(r"\1REDACTED", url)


def short_error(error):
    return str(error).strip().splitlines()[0][:300]


# ---------- Fetching ----------

def fetch_file(context, url, outcome):
    """PDFs, JSON and other files, through the browser context so cookies and headers match a visit."""
    host = urlparse(url).netloc
    polite_wait(host)
    # Some servers refuse HEAD but serve GET, so HEAD only tells us the size, never the access state.
    try:
        head = context.request.head(url, timeout=60_000)
    except Exception:
        head = None
    if head and head.ok and head.headers.get("content-length", "").isdigit():
        outcome["content_length"] = int(head.headers["content-length"])
    if outcome["content_length"] and outcome["content_length"] > MAX_BYTES:
        outcome.update(status=head.status, final_url=head.url, availability="ok", reason=TOO_LARGE,
                       content_type=head.headers.get("content-type"))
        return outcome

    polite_wait(host)
    response = context.request.get(url, timeout=300_000)
    data = response.body()
    outcome.update(status=response.status, final_url=response.url,
                   content_type=response.headers.get("content-type"))
    title, text = html_title_and_text(data, outcome["content_type"])
    problem = access_problem(response.status, response.url, title, text)
    if len(data) > MAX_BYTES and not problem:
        # No content-length came back from HEAD, so we only learn the size after downloading.
        outcome.update(availability="ok", reason=TOO_LARGE, bytes=len(data))
        return outcome
    save_body(outcome, data)
    if problem:
        outcome["availability"], outcome["reason"] = problem
    else:
        outcome["availability"] = "ok"
    return outcome


def fetch_page(context, url, outcome):
    """An HTML page: rendered DOM, full-page screenshot and the data requests it made."""
    polite_wait(urlparse(url).netloc)
    page = context.new_page()
    data_requests = []

    def remember_data_request(response):
        content_type = response.headers.get("content-type", "")
        if response.request.resource_type in ("xhr", "fetch") or "json" in content_type:
            data_requests.append({"url": without_keys(response.url), "method": response.request.method,
                                  "status": response.status, "content_type": content_type})

    page.on("response", remember_data_request)
    try:
        try:
            response = page.goto(url, wait_until="load", timeout=90_000)
        except Exception as error:
            if "Download is starting" in str(error):
                return fetch_file(context, url, outcome)
            raise
        if response is None:
            outcome.update(availability="error", reason="the browser got no response for the page")
            return outcome

        content_type = response.headers.get("content-type", "")
        # Only a successful non-HTML answer is fetched again as a file. Asking a host that
        # just refused us a second time would be retrying a block.
        if response.ok and "html" not in content_type.lower():
            outcome["note"] = f"page answered with {content_type or 'no content type'}; fetched as a file"
            return fetch_file(context, url, outcome)

        try:
            page.wait_for_load_state("networkidle", timeout=20_000)
        except Exception:
            outcome["note"] = "network not idle after 20 s; saved what had loaded"
        outcome.update(status=response.status, final_url=page.url, content_type=content_type)
        title, text = page_title_and_text(page)
        path = save_body(outcome, page.content().encode("utf-8"))
        if text:
            outcome["text_sha256"] = hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()

        problem = access_problem(response.status, page.url, title, text)
        if problem:
            outcome["availability"], outcome["reason"] = problem
            return outcome
        outcome["availability"] = "ok"
        save_page_extras(page, path, data_requests, outcome)
        return outcome
    finally:
        page.close()


def html_title_and_text(data, content_type):
    """Rough title and text of an HTML body that came back on the file route, to spot a bot-check page."""
    if "html" not in (content_type or "").lower():
        return "", ""
    html = data[:200_000].decode("utf-8", errors="replace")
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>|<[^>]+>", " ", html, flags=re.S | re.I)
    return (title.group(1) if title else ""), " ".join(text.split())


def page_title_and_text(page):
    try:
        return page.title(), page.inner_text("body", timeout=5_000)
    except Exception:
        return "", ""


def save_page_extras(page, html_path, data_requests, outcome):
    """Screenshot and data-request list, named after the HTML snapshot they belong to."""
    shot = html_path.with_suffix(".png")
    try:
        if not shot.exists():
            page.screenshot(path=str(shot), full_page=True, timeout=60_000)
        outcome["screenshot"] = str(shot.relative_to(ROOT))
    except Exception as error:
        outcome["note"] = (outcome["note"] + "; " if outcome["note"] else "") + f"no screenshot: {short_error(error)}"
    if data_requests:
        listing = html_path.with_suffix(".requests.json")
        if not listing.exists():
            listing.write_text(json.dumps(data_requests, indent=1), encoding="utf-8")
        outcome["data_requests"] = str(listing.relative_to(ROOT))


def fetch_with_context(context, con, url, particular=None):
    """Fetch one url in an open browser context, record what happened and return the outcome."""
    url = urldefrag(url).url
    host = urlparse(url).netloc
    outcome = new_outcome(url, particular)
    if host in blocked_hosts:
        outcome.update(availability="not_tried", reason=f"not requested: {blocked_hosts[host]}")
        record(con, outcome)
        return outcome
    try:
        if looks_like_file(url):
            fetch_file(context, url, outcome)
        else:
            fetch_page(context, url, outcome)
    except Exception as error:
        outcome.update(availability="error", reason=short_error(error))
    outcome["fetched_at"] = now_utc()
    if outcome["availability"] in ("blocked", "sign_in"):
        blocked_hosts[host] = f"{host} gave \"{outcome['reason']}\" for {url} earlier in this run"
    record(con, outcome)
    return outcome


def open_browser(playwright):
    return playwright.chromium.launch_persistent_context(str(PROFILE_DIR), channel="chrome", headless=True)


def fetch(url, particular=None):
    """Fetch a single url (plan §3's fetch(url))."""
    from playwright.sync_api import sync_playwright

    con = connect_db()
    with sync_playwright() as playwright:
        context = open_browser(playwright)
        try:
            return fetch_with_context(context, con, url, particular)
        finally:
            context.close()
            con.close()


# ---------- --all ----------

def read_sources():
    data = yaml.safe_load(SOURCES_PATH.read_text(encoding="utf-8"))
    return (data.get("inventory") or []) + (data.get("demo") or [])


def planned_urls(rows):
    """{url without #fragment: comma-separated particular ids}, in first-seen order."""
    particulars = {}
    for row in rows:
        url = urldefrag(row["url"]).url
        ids = particulars.setdefault(url, [])
        for pid in str(row.get("particular") or "").split(","):
            if pid.strip() and pid.strip() not in ids:
                ids.append(pid.strip())
    return {url: ",".join(sorted(ids)) for url, ids in particulars.items()}


def interleave_by_host(urls):
    """Take one url from each host in turn, so the per-host wait overlaps with other hosts' requests."""
    queues = {}
    for url in urls:
        queues.setdefault(urlparse(url).netloc, []).append(url)
    ordered = []
    while queues:
        for host in list(queues):
            ordered.append(queues[host].pop(0))
            if not queues[host]:
                del queues[host]
    return ordered


def latest_chromium_outcome(con, url):
    """(availability, reason) of the newest browser fetch of url, or None if it was never fetched."""
    return con.execute("SELECT availability, reason FROM fetch_log WHERE url = ? AND obtained_by = 'chromium' "
                       "ORDER BY id DESC LIMIT 1", (url,)).fetchone()


def hosts_that_refused(con):
    """{host: why} for every host whose latest answer to us was a block or a sign-in wall."""
    refused = {}
    for url, availability, reason in con.execute(
            "SELECT url, availability, reason FROM fetch_log WHERE obtained_by = 'chromium' ORDER BY id"):
        host = urlparse(url).netloc
        if availability in ("blocked", "sign_in"):
            refused[host] = f"{host} gave \"{reason}\" for {url} in an earlier run"
        elif availability == "ok":
            refused.pop(host, None)
    return refused


def is_network_error(reason):
    return any(code in (reason or "") for code in NETWORK_ERRORS)


def fetch_all(retry_only=False):
    """Fetch every planned url, or with retry_only just the ones that never got an answer.

    retry_only picks urls with no fetch yet and urls whose last fetch died on a network error
    (DNS, timeout, reset). Hosts that refused us before stay refused: they are not asked again.
    """
    from playwright.sync_api import sync_playwright

    plan = planned_urls(read_sources())
    con = connect_db()
    if retry_only:
        blocked_hosts.update(hosts_that_refused(con))
        retry = {}
        for url, particular in plan.items():
            latest = latest_chromium_outcome(con, url)
            if latest is None or (latest[0] == "error" and is_network_error(latest[1])):
                retry[url] = particular
        plan = retry
    order = interleave_by_host(plan)
    print(f"Fetching {len(order)} urls from {len({urlparse(u).netloc for u in order})} hosts", flush=True)
    with sync_playwright() as playwright:
        context = open_browser(playwright)
        try:
            for number, url in enumerate(order, 1):
                outcome = fetch_with_context(context, con, url, plan[url])
                size = outcome["bytes"] if outcome["bytes"] is not None else "-"
                print(f"[{number}/{len(order)}] {outcome['availability']:<9} {outcome['status'] or '-':<4} "
                      f"{size:>9} {url} {outcome['reason']}", flush=True)
        finally:
            context.close()
    write_report(con)
    con.close()


# ---------- Report ----------

def write_report(con=None):
    """snapshots/fetch-report.json: the latest outcome for every url in sources.yaml."""
    con = con or connect_db()
    rows = read_sources()
    plan = planned_urls(rows)
    demo_ids = {}
    for row in rows:
        if row.get("id"):
            demo_ids.setdefault(urldefrag(row["url"]).url, []).append(row["id"])

    report_rows = []
    for url, particular in plan.items():
        latest = con.execute(
            "SELECT final_url, status, availability, reason, sha256, text_sha256, bytes, content_length, "
            "content_type, fetched_at, note FROM fetch_log WHERE url = ? AND obtained_by = 'chromium' "
            "ORDER BY id DESC LIMIT 1",
            (url,)).fetchone()
        row = {"particular": particular, "url": url, "demo_ids": demo_ids.get(url, [])}
        if latest is None:
            row.update(final_url=None, status=None, availability="not_fetched", reason="no fetch recorded yet",
                       sha256=None, text_sha256=None, bytes=None, content_length=None, content_type=None,
                       fetched_at=None, note="")
        else:
            keys = ["final_url", "status", "availability", "reason", "sha256", "text_sha256", "bytes",
                    "content_length", "content_type", "fetched_at", "note"]
            row.update(dict(zip(keys, latest)))
        report_rows.append(row)

    counts = {}
    by_host = {}
    for row in report_rows:
        counts[row["availability"]] = counts.get(row["availability"], 0) + 1
        host = by_host.setdefault(urlparse(row["url"]).netloc, {})
        host[row["availability"]] = host.get(row["availability"], 0) + 1
    report = {"generated_at": now_utc(), "urls": len(report_rows), "by_availability": counts,
              "by_host": by_host, "rows": report_rows}
    REPORT_PATH.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(ROOT)}: {len(report_rows)} urls {counts}")
    for host, host_counts in sorted(by_host.items()):
        print(f"  {host:<62} {host_counts}")


# ---------- Manual inbox ----------

def ingest_manual_inbox(particular=None):
    """Snapshot files a person saved into manual_inbox/ (obtained_by='manual').

    Put the source url on the first line of a sidecar file named <file>.url, e.g.
    manual_inbox/packet.pdf + manual_inbox/packet.pdf.url, so the snapshot links to its page.
    """
    con = connect_db()
    done = INBOX / "ingested"
    outcomes = []
    for file in sorted(INBOX.glob("*")):
        if not file.is_file() or file.suffix == ".url" or file.name.startswith(".") or file.name == "README.md":
            continue
        sidecar = file.with_name(file.name + ".url")
        source_url = sidecar.read_text(encoding="utf-8").strip().splitlines()[0] if sidecar.exists() else ""
        outcome = new_outcome(source_url or f"manual:{file.name}", particular, obtained_by="manual")
        outcome["content_type"] = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
        outcome["availability"] = "ok"
        outcome["note"] = f"saved by hand as {file.name}"
        save_body(outcome, file.read_bytes())
        record(con, outcome)
        outcomes.append(outcome)
        done.mkdir(exist_ok=True)
        for moved in (file, sidecar):
            if moved.exists():
                shutil.move(str(moved), done / moved.name)
    con.close()
    return outcomes


def main(args):
    if not args:
        sys.exit("usage: fetch.py --all | fetch.py --retry | fetch.py <url> [P###] | fetch.py --inbox [P###] | fetch.py --report")
    if args[0] == "--all":
        fetch_all()
    elif args[0] == "--retry":
        fetch_all(retry_only=True)
    elif args[0] == "--report":
        write_report()
    elif args[0] == "--inbox":
        for outcome in ingest_manual_inbox(args[1] if len(args) > 1 else None):
            print(json.dumps(outcome))
    else:
        print(json.dumps(fetch(args[0], args[1] if len(args) > 1 else None), indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
