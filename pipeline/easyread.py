"""Easy Read checks (plan §6.7): reading grade per line and per set, plus the Qualifier Keeper.

The grade is Flesch-Kincaid from textstat. The target is about grade 5-6, as a
guide, not a gate: a line above it is pointed out, never blocked. Formulas like
this only count syllables and sentence length, so a low grade doesn't prove a
line is easy to understand.

The Qualifier Keeper reads all the lines for one claim together, since one
claim is often split over two short lines.

Run: python3 pipeline/easyread.py   (prints a report for every matter)
"""
import textstat

from checks import qualifier

TARGET_GRADE = 6
TARGET_NOTE = "About grade 5-6. A guide, not a gate."


def grade(text):
    # Flesch-Kincaid goes below zero on very short lines, which means nothing, so stop at 0
    return max(0.0, round(textstat.flesch_kincaid_grade(text), 1))


def lines_by_claim(lines):
    grouped = {}
    for line in lines:
        grouped.setdefault(line.claim_id, []).append(line.text)
    return grouped


def check_matter(matter, passages):
    """Grade and Qualifier Keeper results for a matter's Easy Read set. passages maps id -> Passage."""
    claims = {claim.id: claim for claim in matter.claims}
    missing_by_claim = {}
    required_by_claim = {}
    for claim_id, texts in lines_by_claim(matter.easy_read).items():
        required, missing = qualifier.check_easy_read(texts, claims[claim_id], passages)
        required_by_claim[claim_id] = required
        missing_by_claim[claim_id] = missing

    lines = []
    for line in matter.easy_read:
        line_grade = grade(line.text)
        lines.append({
            "id": line.id,
            "claim_id": line.claim_id,
            "text": line.text,
            "grade_level": line_grade,
            "above_target": line_grade > TARGET_GRADE,
            "qualifiers_required": required_by_claim[line.claim_id],
            "qualifiers_missing": missing_by_claim[line.claim_id],
        })
    set_text = " ".join(line.text for line in matter.easy_read)
    set_grade = grade(set_text) if set_text else None
    return {
        "matter_id": matter.id,
        "target": TARGET_NOTE,
        "set_grade_level": set_grade,
        "set_above_target": set_grade is not None and set_grade > TARGET_GRADE,
        "line_count": len(lines),
        "lines": lines,
        "claims_missing_qualifiers": {cid: missing for cid, missing in missing_by_claim.items() if missing},
    }


def set_grade_levels(matters):
    """Fill grade_level on every Easy Read line, in place."""
    for matter in matters:
        for line in matter.easy_read:
            line.grade_level = grade(line.text)


def main():
    import review_io

    review = review_io.read_review()
    passages = {p.id: p for p in review.passages}
    for matter in review.matters:
        report = check_matter(matter, passages)
        print(f"{matter.id}: {report['line_count']} lines, set grade {report['set_grade_level']} ({report['target']})")
        for line in report["lines"]:
            flag = "  above target" if line["above_target"] else ""
            print(f"  {line['id']} grade {line['grade_level']}{flag}: {line['text']}")
        for claim_id, missing in report["claims_missing_qualifiers"].items():
            print(f"  QUALIFIER: lines for {claim_id} drop {missing}")


if __name__ == "__main__":
    main()
