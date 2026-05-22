#!/usr/bin/env python3
"""Append a cautious figure reproducibility cross-reference section.

Research-only helper: updates paper/draft.md with aggregate-only wording about
local SVG figures and verifies that the section does not overclaim legal effect,
signature validity, supervision, public alerting, listed-entity status, or
publication readiness.
"""
from __future__ import annotations

import json
import pathlib
import re

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
DRAFT = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-figure-reproducibility-section-check-output.json"
SECTION_TITLE = "## Figure reproducibility cross-references"
SECTION = """## Figure reproducibility cross-references

The first rendered figures are intentionally modest because the available series currently contains one dated run. `figures/aggregate-run-telemetry.svg` visualizes collection and normalization counts from the aggregate-results table, while `figures/aggregate-diff-classes.svg` visualizes the same row's diff-class totals. Both figures are derived from `notes/aggregate-results-table.csv` and `notes/aggregate-results-2026-05-20-output.json`, so the draft should treat them as reproducible views of local telemetry rather than as independent evidence. A future revision with multiple dates can reuse the same paths and checks, but the caption discipline should remain unchanged.

Each figure should be cited together with its data source and hash-bearing artifact index entry. The useful claim is narrow: the local renderer produced parseable SVG files whose embedded metadata points back to the aggregate CSV hash and whose caveats reject legal-status, signature-validation, supervisory, public-alerting, and publication-readiness interpretations. The figures do not add authority to the underlying observations, and their visual form should not be used to imply ecosystem stability, public-warning significance, compliance significance, or any other conclusion beyond the recorded local counts.

For reproducibility, any paper revision that edits figure captions or filenames should rerun the figure renderer, the figure artifact validator, the aggregate-results validator, the paper figure-reference validator, and the public-artifact safety validator. This cross-check is deliberately mechanical. It ensures that the paper prose, rendered images, and local evidence table continue to refer to the same aggregate-only objects, while keeping listed names out of narrative text until the operator explicitly approves named examples and their wording. It also gives later reviewers a simple failure mode: if a path, hash, caveat, or data source no longer matches, the figure should be regenerated or the prose should be corrected before the draft is circulated.
"""

FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
    "public risk",
]
REQUIRED = [
    "figures/aggregate-run-telemetry.svg",
    "figures/aggregate-diff-classes.svg",
    "notes/aggregate-results-table.csv",
    "notes/aggregate-results-2026-05-20-output.json",
    "legal-status",
    "signature-validation",
    "supervisory",
    "public-alerting",
    "publication-readiness",
]


def word_count(section: str) -> int:
    body = section.split("\n", 1)[1]
    return len(re.findall(r"\b[\w'-]+\b", body))


def main() -> int:
    text = DRAFT.read_text(encoding="utf-8")
    if SECTION_TITLE not in text:
        marker = "## Limitations and reproducibility\n"
        if marker not in text:
            raise SystemExit("limitations marker not found")
        text = text.replace(marker, SECTION + "\n" + marker, 1)
        DRAFT.write_text(text, encoding="utf-8")

    updated = DRAFT.read_text(encoding="utf-8")
    start = updated.index(SECTION_TITLE)
    next_heading = updated.find("\n## ", start + 1)
    section_text = updated[start:] if next_heading == -1 else updated[start:next_heading]
    forbidden_hits = [token for token in FORBIDDEN if token in section_text]
    missing_required = [token for token in REQUIRED if token not in section_text]
    wc = word_count(section_text)
    result = {
        "status": "ok" if not forbidden_hits and not missing_required and 250 <= wc <= 400 else "needs_review",
        "section": SECTION_TITLE,
        "section_word_count": wc,
        "forbidden_hits": forbidden_hits,
        "missing_required": missing_required,
        "research_caveat": "Section is aggregate-only figure reproducibility prose; it does not assert legal effect, signature validity, supervision, public alerting, listed-entity status, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
