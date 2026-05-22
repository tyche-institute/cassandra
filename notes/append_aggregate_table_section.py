#!/usr/bin/env python3
"""Idempotently append a cautious aggregate-table interpretation section to paper/draft.md."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DRAFT = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-aggregate-table-section-check-output.json"
SECTION_TITLE = "## Aggregate telemetry table interpretation"
INSERT_BEFORE = "## Results presentation and figure design"

SECTION = """## Aggregate telemetry table interpretation

The current aggregate-results table is deliberately small: it contains one dated row for the first local run. That limitation is useful because it fixes the semantics of the table before a longer series creates pressure for interpretation. The row for 2026-05-20 records 43 LOTL-derived pointer attempts, 41 fetched content files, 2 fetch errors, 31 normalized XML artifacts, 9 non-XML skips, 1 XML parsing error, and 31 comparable records in the baseline comparison. It also records zero diff entries because the comparison initialized the baseline rather than comparing against an earlier day. These values should be read as workflow telemetry with local evidence pointers, not as statements about the public legal status of any list, provider, service, or authority.

The table also exposes the future shape of the longitudinal dataset. Provider and service totals can be summarized as aggregate counts, while provider/service inventory changes remain machine-readable diff classes keyed by local hashes. Signature-shape records can be counted across comparable XML artifacts, but the count only says that signature-shaped XML structures were observed by the parser. It does not say that a signature was verified, that the document should be relied upon, or that a national list has any particular legal effect.

A later multi-day table should preserve the same discipline. Dates with endpoint errors, parser failures, or non-XML references should not be dropped merely because they complicate the story. They are part of the collection environment and can explain why a diff row has fewer comparable XML records. Conversely, a day with zero structural diff entries should not be presented as stability of the underlying legal ecosystem; it only means that Cassandra does not emit structural diff records under the configured method and baseline for that local run.
"""

FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer eIDAS-aligned trust services",
    "provides eIDAS trust services",
]
REQUIRED_PHRASES = [
    "does not say that a signature was verified",
    "does not emit structural diff records",
    "not as statements about the public legal status",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(section: str) -> int:
    body = re.sub(r"^## .*$", "", section, count=1, flags=re.MULTILINE)
    return len(re.findall(r"\b[\w'-]+\b", body))


def main() -> int:
    text = DRAFT.read_text(encoding="utf-8")
    changed = False
    if SECTION_TITLE not in text:
        if INSERT_BEFORE not in text:
            raise SystemExit(f"missing insertion marker: {INSERT_BEFORE}")
        text = text.replace(INSERT_BEFORE, SECTION.rstrip() + "\n\n" + INSERT_BEFORE, 1)
        DRAFT.write_text(text, encoding="utf-8")
        changed = True

    final_text = DRAFT.read_text(encoding="utf-8")
    forbidden_hits = [phrase for phrase in FORBIDDEN if phrase in final_text]
    missing_required = [phrase for phrase in REQUIRED_PHRASES if phrase not in final_text]
    section_match = re.search(r"## Aggregate telemetry table interpretation\n\n(?P<body>.*?)(?=\n## |\Z)", final_text, re.S)
    section_word_count = word_count(section_match.group(0)) if section_match else 0
    errors = []
    if forbidden_hits:
        errors.append("forbidden phrase present")
    if missing_required:
        errors.append("required cautious phrase missing")
    if not (250 <= section_word_count <= 400):
        errors.append(f"section word count out of range: {section_word_count}")
    if "Affiliation: Tyche Institute, Tallinn, Estonia" not in final_text:
        errors.append("required Tyche affiliation missing")

    result = {
        "status": "ok" if not errors else "error",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "changed": changed,
        "draft_path": str(DRAFT.relative_to(WORKSPACE)),
        "draft_sha256": sha256(DRAFT),
        "section_title": SECTION_TITLE,
        "section_word_count": section_word_count,
        "forbidden_hits": forbidden_hits,
        "missing_required_phrases": missing_required,
        "errors": errors,
        "caveat": "Local paper wording check only; it does not assert legal compliance, trusted-list legal effect, signature validity, supervision, public alerting, regulated trust-service output, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
