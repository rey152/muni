"""Word-level diff between two passage texts, for the staff drift report.

Each op's text is its words joined by single spaces, so put a space between
ops when showing them. A replaced stretch comes out as a delete then an insert.
"""
import difflib


def word_diff(old_text, new_text):
    """[{op: equal|insert|delete, text}] turning old_text into new_text."""
    old_words = old_text.split()
    new_words = new_text.split()
    # autojunk would treat common words as noise in long texts and give odd diffs
    matcher = difflib.SequenceMatcher(a=old_words, b=new_words, autojunk=False)
    ops = []
    for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if tag == "equal":
            add(ops, "equal", old_words[old_start:old_end])
        if tag in ("delete", "replace"):
            add(ops, "delete", old_words[old_start:old_end])
        if tag in ("insert", "replace"):
            add(ops, "insert", new_words[new_start:new_end])
    return ops


def add(ops, op, words):
    if words:
        ops.append({"op": op, "text": " ".join(words)})


def summary(ops):
    """One line for a CSV cell, e.g. 'within 10 [-days-] {+business days+}'."""
    parts = []
    for item in ops:
        if item["op"] == "equal":
            parts.append(item["text"])
        elif item["op"] == "delete":
            parts.append(f"[-{item['text']}-]")
        else:
            parts.append(f"{{+{item['text']}+}}")
    return " ".join(parts)
