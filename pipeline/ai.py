"""Local AI drafts (plan §7): paraphrases for claims and Easy Read lines, via Ollama.

The model only drafts. Every draft goes through the Qualifier Keeper, a check
for numbers, dates and status words the source doesn't have, and the optional
NLI check, then lands in review/suggestions/<matter-id>.yaml with status
"pending". Nothing here approves a draft or writes to the reviewed files in
review/matters/; a person copies a draft over after checking it.

Outputs are cached in pipeline/ai_cache.json by (model, prompt version, input
hash), with the date, so a rerun gives the same text. Every draft is also
appended to review/ai-log.jsonl.

Run: python3 pipeline/ai.py draft <matter-id>      (needs `ollama serve` running)
"""
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

import easyread
import review_io
from checks import nli, qualifier

ROOT = Path(__file__).resolve().parent.parent
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"
PARAPHRASE_PROMPT_VERSION = "paraphrase-v1"
EASY_READ_PROMPT_VERSION = "easy-read-v1"
CACHE_PATH = ROOT / "pipeline" / "ai_cache.json"
LOG_PATH = ROOT / "review" / "ai-log.jsonl"
SUGGESTIONS_DIR = ROOT / "review" / "suggestions"
# Drafts are always saved as this. Changing it is a reviewer's job, in the reviewed files.
DRAFT_STATUS = "pending"

STATUS_WORDS = ["approved", "adopted", "passed", "carried", "defeated", "rejected", "refused", "enacted",
                "repealed", "in force", "decided", "final", "confirmed"]
# "may" is left out because it's usually the verb; a written date still shows up through its figures
MONTHS = ["january", "february", "march", "april", "june", "july", "august", "september", "october",
          "november", "december"]

PARAPHRASE_PROMPT = """You rewrite one passage from a City of Waterloo record in plain language.

Rules:
- Write one or two short sentences. Use common words.
- Keep each of these words or phrases, or a word with the same meaning: {qualifiers}
- Do not add any number, amount, date or name that is not in the passage.
- Do not say that anything was approved, passed, decided, rejected or is in force unless the passage says so.
- Do not add advice or opinions.
- Reply with the sentences only.

Passage:
{passage}
"""

EASY_READ_PROMPT = """You write an Easy Read version of some checked sentences about a City of Waterloo matter.

Rules:
- Write one or two lines for each sentence below. Each line is one short sentence with common words.
- Start every line with the sentence's id and a colon, like "C-x1: ...".
- Keep the words listed after "Keep:" for that sentence, or a word with the same meaning.
- Do not add any number, amount, date or name that is not in that sentence.
- Do not say that anything was approved, passed, decided, rejected or is in force unless that sentence says so.
- Reply with the lines only.

Sentences:
{claims}
"""


# ---------- Ollama and the cache ----------

def call_ollama(prompt):
    """Text Ollama returns for prompt, at temperature 0."""
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0, "seed": 0}}).encode("utf-8")
    request = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.loads(response.read())["response"].strip()
    except urllib.error.URLError as error:
        raise RuntimeError(f"Ollama isn't answering at {OLLAMA_URL} ({error}). Start it with `ollama serve`.") from error


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_cache():
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def generate(prompt, prompt_version):
    """(text, entry) for prompt, from the cache when the same model and prompt version already ran it."""
    input_hash = text_hash(prompt)
    key = f"{MODEL}|{prompt_version}|{input_hash}"
    cache = read_cache()
    if key in cache:
        return cache[key]["output"], dict(cache[key], cached=True)
    output = call_ollama(prompt)
    entry = {"model": MODEL, "prompt_version": prompt_version, "input_hash": input_hash,
             "date": date.today().isoformat(), "output": output}
    cache[key] = entry
    CACHE_PATH.write_text(json.dumps(cache, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return output, dict(entry, cached=False)


# ---------- Checks on a draft ----------

def numbers_in(text):
    """Figures in text with commas and trailing dots dropped, e.g. '$7.44M' -> '7.44'."""
    return {n.replace(",", "").rstrip(".") for n in re.findall(r"\d[\d,.]*", text)}


def words_in(text, words):
    lowered = text.lower()
    return {w for w in words if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", lowered)}


def draft_checks(draft, source_text, required):
    """What a reviewer needs to know about a draft. flags lists every problem in plain words."""
    missing = [m for m in required if not qualifier.keeps(draft, m)]
    added_numbers = sorted(numbers_in(draft) - numbers_in(source_text))
    added_months = sorted(words_in(draft, MONTHS) - words_in(source_text, MONTHS))
    added_status = sorted(words_in(draft, STATUS_WORDS) - words_in(source_text, STATUS_WORDS))
    nli_result = nli.check(source_text, draft)
    flags = []
    if missing:
        flags.append(f"Drops qualifier(s): {', '.join(missing)}.")
    if added_numbers or added_months:
        flags.append(f"Adds numbers or dates not in the source: {', '.join(added_numbers + added_months)}.")
    if added_status:
        flags.append(f"Adds status words not in the source: {', '.join(added_status)}.")
    if nli_result["flag"]:
        flags.append(f"NLI: {nli_result['reason']}")
    return {
        "qualifiers_required": required,
        "qualifiers_missing": missing,
        "numbers_added": added_numbers + added_months,
        "status_words_added": added_status,
        "nli": nli_result,
        "flags": flags,
    }


# ---------- Drafting ----------

def draft_paraphrase(passage_text, qualifiers):
    """A pending paraphrase draft of passage_text that should keep every marker in qualifiers."""
    prompt = PARAPHRASE_PROMPT.format(qualifiers=", ".join(f'"{q}"' for q in qualifiers) or "(none listed)",
                                      passage=passage_text)
    text, made = generate(prompt, PARAPHRASE_PROMPT_VERSION)
    return {
        "text": text,
        "provenance": "ai_paraphrase",
        "review": {"status": DRAFT_STATUS},
        "made_by": made_by(made),
        "checks": draft_checks(text, passage_text, qualifiers),
    }


def keep_list(claim):
    """Markers a line for this claim must keep: what the claim's sources need, minus its waivers."""
    return [m for m in claim.qualifiers_required if m not in claim.qualifiers_waived]


def draft_easy_read(claims):
    """Pending Easy Read draft lines for claims, each linked to the claim it simplifies.

    Each claim's qualifiers_required should be filled in first (qualifier.check_claim).
    Lines the model doesn't start with a known claim id are dropped, since an
    Easy Read line must link to a parent claim.
    """
    if not claims:
        return []
    listed = []
    for claim in claims:
        keep = ", ".join(f'"{m}"' for m in keep_list(claim)) or "(none)"
        listed.append(f"{claim.id}: {claim.text}\n  Keep: {keep}")
    prompt = EASY_READ_PROMPT.format(claims="\n".join(listed))
    text, made = generate(prompt, EASY_READ_PROMPT_VERSION)

    by_id = {claim.id: claim for claim in claims}
    lines = []
    for raw in text.splitlines():
        match = re.match(r"^\s*[-*]?\s*(C-[\w-]+)\s*:[\s:]*(.+?)\s*$", raw)
        if match and match.group(1) in by_id:
            lines.append({"claim_id": match.group(1), "text": match.group(2)})

    for line in lines:
        claim = by_id[line["claim_id"]]
        group = " ".join(other["text"] for other in lines if other["claim_id"] == claim.id)
        line["grade_level"] = easyread.grade(line["text"])
        line["review"] = {"status": DRAFT_STATUS}
        line["made_by"] = made_by(made)
        # qualifiers are checked over all the lines for this claim together, like easyread.check_matter does
        checks = draft_checks(line["text"], claim.text, required=[])
        missing = [m for m in keep_list(claim) if not qualifier.keeps(group, m)]
        checks["qualifiers_required"] = keep_list(claim)
        checks["qualifiers_missing"] = missing
        if missing:
            checks["flags"].insert(0, f"Lines for {claim.id} drop qualifier(s): {', '.join(missing)}.")
        line["checks"] = checks
    return lines


def made_by(made):
    return {"model": made["model"], "prompt_version": made["prompt_version"], "date": made["date"],
            "input_hash": made["input_hash"], "cached": made["cached"]}


# ---------- Saving ----------

def log(record):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def draft_matter(matter_id, review_dir=review_io.REVIEW_DIR):
    """Draft paraphrases and an Easy Read set for one matter and save them as pending suggestions."""
    review = review_io.read_review(review_dir)
    matter = next((m for m in review.matters if m.id == matter_id), None)
    if matter is None:
        raise SystemExit(f"No matter '{matter_id}'. Matters: {', '.join(m.id for m in review.matters)}")
    passages = {p.id: p for p in review.passages}
    for claim in matter.claims:
        claim.qualifiers_required = qualifier.check_claim(claim, passages)[0]

    paraphrases = []
    for claim in matter.claims:
        source = " ".join(passages[pid].text for pid in claim.passage_ids)
        draft = draft_paraphrase(source, claim.qualifiers_required)
        paraphrases.append({"claim_id": claim.id, "passage_ids": claim.passage_ids, **draft})

    approved = [c for c in matter.claims if c.review.status == "approved"]
    easy_read = [{"id": f"ER-ai-{matter.id}-{number}", **line}
                 for number, line in enumerate(draft_easy_read(approved), start=1)]

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for kind, drafts in (("paraphrase", paraphrases), ("easy_read", easy_read)):
        for draft in drafts:
            log({"at": now, "matter_id": matter.id, "kind": kind, "claim_id": draft["claim_id"],
                 "text": draft["text"], "status": draft["review"]["status"], "made_by": draft["made_by"],
                 "flags": draft["checks"]["flags"]})

    suggestions = {
        "matter_id": matter.id,
        "generated_at": now,
        "note": "AI drafts for a reviewer. Not reviewed and never published from this file. "
                "To use one, copy it into review/matters/ and review it there.",
        "paraphrases": paraphrases,
        "easy_read": easy_read,
    }
    path = SUGGESTIONS_DIR / f"{matter.id}.yaml"
    review_io.write_yaml(path, suggestions)
    return suggestions, path


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "draft":
        sys.exit("usage: python3 pipeline/ai.py draft <matter-id>")
    started = time.perf_counter()
    suggestions, path = draft_matter(sys.argv[2])
    seconds = time.perf_counter() - started
    drafts = suggestions["paraphrases"] + suggestions["easy_read"]
    cached = sum(1 for d in drafts if d["made_by"]["cached"])
    flagged = sum(1 for d in drafts if d["checks"]["flags"])
    print(f"Wrote {len(suggestions['paraphrases'])} paraphrases and {len(suggestions['easy_read'])} Easy Read "
          f"lines to {path.relative_to(ROOT)} in {seconds:.1f}s ({cached} from cache). "
          f"{flagged} flagged. All pending review.")
    for draft in drafts:
        print(f"  {draft['claim_id']}: {draft['text']}")
        for flag in draft["checks"]["flags"]:
            print(f"      FLAG {flag}")


if __name__ == "__main__":
    main()
