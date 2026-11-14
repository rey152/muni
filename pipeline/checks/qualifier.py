"""Qualifier Keeper (plan §6.4): a claim must keep the conditions and hedges in the passages it cites.

Rules only: a marker lexicon plus regexes, matched on whole words after
lowercasing. A marker counts as kept when the sentence has the marker itself
or one of its listed equivalents ("only if" ~ "only when"). Reviewers can
waive a marker on a claim, with a reason, in claim.qualifiers_waived.

It runs on claims and on Easy Read lines. It catches dropped wording, not
every possible omission, and it can't tell whether a kept word is used in
the same sense as in the source.
"""
import re

# "may" the month isn't a hedge, so skip it when a day or year follows or it reads "in May".
MAY = r"(?<!in )(?<!of )(?<!since )(?<!by )may(?!\s*\d)"
NOT_YET = r"not yet"
# "not protected yet", "don't know yet": a negation with "yet" up to three words later
NOT_THEN_YET = r"(?:not|\w*n't)(?:\s+\w+){1,3}\s+yet"

# Marker -> regex that finds it in a passage. The found list keeps this order,
# and a longer phrase comes before any shorter marker inside it ("only if" before "if").
MARKERS = {
    "subject to": r"subject to",
    "conditional on": r"conditional (?:on|upon)",
    "provided that": r"provided that",
    "unless": r"unless",
    "until": r"until",
    "pending": r"pending",
    "in principle": r"in principle",
    "draft": r"drafts?",
    "received for information": r"received for information",
    "approximately": r"approximately|approx\.",
    "estimated": r"estimated|estimates?",
    "only if": r"only if",
    "not a": r"not an?",
    "not yet": NOT_YET,
    "except": r"except",
    "may": MAY,
    "might": r"might",
    "could": r"could",
    "would": r"would",
    "should": r"should",
    "proposed": r"propos(?:ed|es|al)",
    "if": r"if",
}

# Marker -> other wordings that keep it. The marker's own regex always counts too.
EQUIVALENTS = {
    "subject to": [r"conditional (?:on|upon)", r"depends? on", r"dependent on"],
    "conditional on": [r"subject to", r"depends? on", r"dependent on"],
    "provided that": [r"as long as", r"so long as", r"on condition that", r"only if"],
    "unless": [r"except if", r"except when"],
    "until": [r"till"],
    "pending": [r"awaiting", r"waiting for", NOT_YET, NOT_THEN_YET],
    "draft": [r"propos(?:ed|es|al)", r"not final"],
    "received for information": [r"for information(?: only)?"],
    "approximately": [r"about", r"around", r"roughly"],
    "estimated": [r"projected", r"forecasts?"],
    "only if": [r"only when", r"only where", r"only in the event that"],
    "not a": [r"\w*n't an?"],
    "not yet": [NOT_THEN_YET, r"\w*n't yet", r"still (?:has|have|needs?) to"],
    "except": [r"excluding", r"other than", r"apart from", r"but not", r"not including"],
    "may": [r"might", r"could", r"can(?!')"],
    "might": [MAY, r"could"],
    "could": [MAY, r"might"],
    "proposed": [r"drafts?", r"recommend(?:s|ed)?"],
    "if": [r"in the event that", r"provided that", r"as long as"],
}


def normalize(text):
    text = text.lower().replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", text)


def whole_words(pattern):
    # \b would fail after "approx." so check for word characters on each side instead
    return r"(?<!\w)(?:" + pattern + r")(?!\w)"


def find_qualifiers(text):
    """Markers found in text, in MARKERS order.

    Once a longer marker is found its words are blanked out, so "only if" isn't
    also counted as "if". A separate "if" elsewhere still counts.
    """
    remaining = normalize(text)
    found = []
    for marker, pattern in MARKERS.items():
        regex = whole_words(pattern)
        if re.search(regex, remaining):
            found.append(marker)
            remaining = re.sub(regex, " ", remaining)
    return found


def keeps(text, marker):
    """True if text has the marker or one of its listed equivalents."""
    lowered = normalize(text)
    patterns = [MARKERS[marker]] + EQUIVALENTS.get(marker, [])
    return any(re.search(whole_words(p), lowered) for p in patterns)


def check_text(text, passage_texts, waived=None):
    """Return (required, missing) for any sentence against its source passages.

    required is every marker found in the passages. missing is the required
    markers text doesn't keep, minus any in waived (marker -> reason).
    """
    waived = waived or {}
    required = []
    for passage_text in passage_texts:
        for marker in find_qualifiers(passage_text):
            if marker not in required:
                required.append(marker)
    missing = [m for m in required if not keeps(text, m) and m not in waived]
    return required, missing


def missing_qualifiers(claim_text, passage_texts):
    """(required, missing) with no waivers."""
    return check_text(claim_text, passage_texts)


def check_claim(claim, passages):
    """Return (required, missing) for one claim.

    passages maps passage id -> Passage. required is every marker found in the
    cited passages. missing is the required markers the claim text leaves out,
    minus the ones a reviewer waived in claim.qualifiers_waived.
    """
    texts = [passages[passage_id].text for passage_id in claim.passage_ids]
    return check_text(claim.text, texts, claim.qualifiers_waived)


def check_easy_read(line_texts, claim, passages):
    """Return (required, missing) for the Easy Read lines that simplify one claim.

    The lines are read together, since one claim is often split over two short
    lines. They answer to the same passages as their claim, and the claim's
    waivers apply, because a line can't carry waivers of its own.
    """
    texts = [passages[passage_id].text for passage_id in claim.passage_ids]
    return check_text(" ".join(line_texts), texts, claim.qualifiers_waived)
