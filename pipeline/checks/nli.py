"""Optional second check (plan §6.4 step 4): does the passage support the sentence?

Runs the cross-encoder/nli-deberta-v3-base model on CPU with premise = passage
and hypothesis = claim or draft. A "contradiction" result, or an entailment
score below ENTAILMENT_FLOOR, flags the sentence for a reviewer. It never
approves anything: a clean result only means this check found no problem.

transformers and torch are optional. If they aren't installed, or the model
can't be downloaded, check() returns available=False with the reason and the
build carries on without it.

Results are cached in pipeline/nli_cache.json by (model, passage hash, sentence hash).
"""
import hashlib
import json
from pathlib import Path

MODEL_NAME = "cross-encoder/nli-deberta-v3-base"
CACHE_PATH = Path(__file__).resolve().parent.parent / "nli_cache.json"
ENTAILMENT_FLOOR = 0.5

# Loaded on first use; (tokenizer, model) once it works, or the reason it didn't.
_loaded = None
_load_error = None


def load_model(allow_download=True):
    """Load the model once. Returns True if it's ready. allow_download=False only uses the local cache."""
    global _loaded, _load_error
    if _loaded:
        return True
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as error:
        _load_error = f"transformers/torch not installed ({error})"
        return False
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=not allow_download)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, local_files_only=not allow_download)
    except OSError as error:
        # transformers raises OSError for "not downloaded yet", "no network" and "no such model"
        _load_error = f"couldn't load {MODEL_NAME}: {error}"
        return False
    model.eval()
    _loaded = (tokenizer, model)
    _load_error = None
    return True


def text_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def cache_key(premise, hypothesis):
    return f"{MODEL_NAME}|{text_hash(premise)}|{text_hash(hypothesis)}"


def read_cache():
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def write_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def scores(premise, hypothesis):
    """{label: probability} from the model."""
    import torch

    tokenizer, model = _loaded
    inputs = tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        probabilities = torch.softmax(model(**inputs).logits[0], dim=-1).tolist()
    labels = model.config.id2label
    return {labels[i].lower(): round(p, 4) for i, p in enumerate(probabilities)}


def judge(found):
    """Add label, flag and reason to a {label: probability} dict."""
    label = max(found, key=found.get)
    result = {"available": True, "model": MODEL_NAME, "scores": found, "label": label, "flag": False, "reason": ""}
    if label == "contradiction":
        result["flag"] = True
        result["reason"] = "The model reads the sentence as contradicting the passage."
    elif found.get("entailment", 0) < ENTAILMENT_FLOOR:
        result["flag"] = True
        result["reason"] = f"Entailment {found.get('entailment', 0):.2f} is below {ENTAILMENT_FLOOR}."
    return result


def check(premise, hypothesis, allow_download=True):
    """NLI result for one passage/sentence pair. Never says "approved"; a flag means "a person should look"."""
    key = cache_key(premise, hypothesis)
    cache = read_cache()
    if key in cache:
        return judge(cache[key])
    if not load_model(allow_download):
        return {"available": False, "model": MODEL_NAME, "flag": False, "reason": f"NLI skipped: {_load_error}"}
    found = scores(premise, hypothesis)
    cache[key] = found
    write_cache(cache)
    return judge(found)
