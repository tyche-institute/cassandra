#!/usr/bin/env python3
"""Idempotently append a cautious dataset-boundary/source-handling section to paper/draft.md."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DRAFT = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-dataset-boundary-section-check-output.json"
SECTION_TITLE = "## Dataset boundary and source handling"
INSERT_BEFORE = "## Method and evidence-bundle design"

SECTION = """## Dataset boundary and source handling

The dataset boundary is the public list-of-lists snapshot and the national document pointers extracted from that local XML copy. Cassandra does not add ad hoc targets, search for alternative national endpoints, or treat a missing response as permission to substitute another source. This keeps each run tied to a reproducible input: the saved list-of-lists file, the extracted pointer JSON, and the dated snapshot manifest. When a pointer leads to a PDF, a non-XML response, a parser error, or a fetch error, the event remains inside the run record as collection telemetry rather than being converted into a status judgment.

This boundary also shapes how sources are cited in the draft. Run-specific counts should cite local artifacts, such as `snapshots/<date>/manifest.json`, `normalized/<date>/manifest.json`, `diffs/<date>.json`, and the corresponding evidence bundle, instead of re-querying live endpoints while writing prose. Live URLs remain source provenance for the collected files, but the historical claim is about what the local run recorded at its access time. That distinction protects the study from confusing current endpoint behavior with the evidence preserved for an earlier date.

Source handling is therefore conservative by design. The fetcher records HTTP status or exception text, local hashes, and access timestamps; the parser records which files were normalized and which were skipped or rejected; the diff engine records only structural comparison classes against a configured baseline. None of these records says that a trusted list is valid, invalid, current, obsolete, supervised, or legally effective. The paper should describe the corpus as LOTL-derived structural-observation material, not as a complete or authoritative registry of European trust-service status.

The same boundary should govern future extensions. If the project later imports ETSI specifications, schema files, or operator-approved named case studies, those inputs should be recorded as separate sources with their own hashes, access dates, and claim-safety notes. They should not retroactively change what a dated snapshot row means. A daily run is a local observation of public documents under one method; it is not a relying-party process, supervisory act, public alert, or trust-service output.
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
    "not as a complete or authoritative registry",
    "does not add ad hoc targets",
    "not a relying-party process",
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
    section_match = re.search(r"## Dataset boundary and source handling\n\n(?P<body>.*?)(?=\n## |\Z)", final_text, re.S)
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
