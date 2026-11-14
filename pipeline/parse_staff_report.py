"""Extract staff report numbers and header fields from a council PDF."""
import re
import sys

import pdfplumber

REPORT_NO = re.compile(r"\b[A-Z]{2,5}\d{4}-\d{3}(?:\.\d)?\b")
LABELS = {
    "title": r"Title",
    "report_no": r"Report No\.?",
    "council_date": r"(?:Council|Meeting) Date",
    "ward_no": r"Ward No\.?(?:\(s\))?",
    "prepared_by": r"Prepared By",
}


def extract_text(pdf_path: str) -> list[str]:
    """Return layout-preserving text, one string per page."""
    with pdfplumber.open(pdf_path) as pdf:
        return [page.extract_text(layout=True) or "" for page in pdf.pages]


def find_headers(text: str) -> list[dict]:
    """Find label: value pairs for each header label on a page."""
    hits = []
    for key, label in LABELS.items():
        for m in re.finditer(rf"^\s*{label}\s*:?\s+(.+?)\s*$", text, re.MULTILINE):
            hits.append({"field": key, "value": m.group(1)})
    return hits


def parse(pdf_path: str) -> dict:
    pages = extract_text(pdf_path)
    numbers = sorted({m.group(0) for t in pages for m in REPORT_NO.finditer(t)})
    headers = [dict(h, page=i + 1) for i, t in enumerate(pages) for h in find_headers(t)]
    return {"pages": len(pages), "report_numbers": numbers, "headers": headers}


if __name__ == "__main__":
    import json
    print(json.dumps(parse(sys.argv[1]), indent=1))
