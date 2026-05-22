#!/usr/bin/env python3
"""Append a cautious limitations/reproducibility section to paper/draft.md.

Research-only helper: this script does not publish or upload anything.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "paper" / "draft.md"
OUT = ROOT / "notes" / "paper-limitations-section-check-output.json"
MARKER = "## References and local evidence"
SECTION_HEADING = "## Limitations and reproducibility"
FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "we offer eIDAS-aligned trust services",
    "qualified trust service provider",
    "QTSP",
]

SECTION = """## Limitations and reproducibility

Cassandra’s observations are limited by the public pointers and network conditions present at collection time. A failed fetch, parser error, redirect, or non-XML response is preserved as telemetry, but it is not interpreted as evidence about the status of a scheme, provider, or service. The first run already shows why this distinction matters: the same LOTL-derived corpus can include XML files, PDF references, endpoint errors, and XML parsing failures. These cases are relevant to research reproducibility, yet they do not support legal or supervisory conclusions.

The normalized XML comparison is also intentionally conservative. Canonical serialization reduces noise from whitespace and attribute ordering, while summary fields and hashed inventory keys make repeated runs easier to compare. However, a normalized-hash change is only a prompt for later inspection. It may reflect metadata churn, publication tooling, namespace changes, textual edits, or structural updates. Cassandra records the class of observation and the affected local artifact path; it does not decide whether the change has legal effect or whether any listed service should be relied upon.

Reproducibility therefore depends on retaining the full local chain: the fetched LOTL copy, extracted pointer list, per-file metadata, snapshot manifest, normalization manifest, diff JSON, alert roll-up, and evidence bundle. Each dated run should be repeatable from these files without contacting external services again, except when deliberately collecting a new daily snapshot. The paper draft cites local paths rather than live web pages for run-specific counts so that later revisions can distinguish historical evidence from current endpoint behavior.

Future analysis should aggregate churn by date, territory code, artifact class, and diff class. Narrative prose should remain aggregate-only unless the operator explicitly approves named examples after legal and ethical review. This keeps the study focused on public-document dynamics rather than on status claims about individual listed entities.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    body = text.split("\n", 1)[1] if "\n" in text else text
    return len([token for token in body.replace("/", " ").split() if token.strip()])


def main() -> None:
    original = DRAFT.read_text(encoding="utf-8")
    if SECTION_HEADING in original:
        updated = original
        changed = False
    else:
        if MARKER not in original:
            raise SystemExit(f"marker not found: {MARKER}")
        updated = original.replace(MARKER, SECTION + "\n" + MARKER, 1)
        DRAFT.write_text(updated, encoding="utf-8")
        changed = True

    forbidden_hits = [phrase for phrase in FORBIDDEN if phrase in updated]
    result = {
        "status": "ok" if not forbidden_hits else "error",
        "changed": changed,
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "draft_path": str(DRAFT.relative_to(ROOT)),
        "draft_sha256": sha256(DRAFT),
        "section_heading": SECTION_HEADING,
        "section_word_count": word_count(SECTION),
        "forbidden_hits": forbidden_hits,
        "checks": {
            "has_tych_institute_affiliation": "Affiliation: Tyche Institute, Tallinn, Estonia" in updated,
            "mentions_zetes": "Zetes" in updated,
            "uses_aggregate_only_named_entity_policy": "aggregate-only" in SECTION,
        },
        "caveats": [
            "research-only structural observation",
            "no relying-party validation claim",
            "no legal-status determination",
            "no listed-entity names in narrative prose without approval",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if forbidden_hits or not result["checks"]["has_tych_institute_affiliation"] or result["checks"]["mentions_zetes"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
