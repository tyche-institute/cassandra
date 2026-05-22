#!/usr/bin/env python3
"""Append cautious aggregate-only naming validation paper prose.

Local research-only helper. It updates the Cassandra working draft with a short
subsection explaining the hash-only paper naming validator. It does not assert
legal compliance, trusted-list legal effect, supervision, signature validation,
public alerting, regulated trust-service output, legal review, warning clearance,
or publication readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-aggregate-only-naming-section-check-output.json"
ANCHOR = "## Operator review gates and non-publication status"
HEADING = "## Aggregate-only naming validation"

SECTION = """## Aggregate-only naming validation

Cassandra now includes a local aggregate-only naming validator that checks whether `paper/draft.md` avoids reproducing raw listed names derived from the latest saved XML snapshots. The validator reads saved snapshot files, extracts candidate name-bearing fields such as provider and service-name structures, and compares them against the draft using hash-only reporting. Its purpose is a wording-boundary check: it helps keep public-facing prose at the level of dates, counts, classes, hashes, and artifact paths while leaving raw names inside local machine-readable evidence unless the operator approves a named example.

The safe interpretation of a clean validator result is narrow. A status of `ok` in `notes/paper-aggregate-only-naming-validation-output.json` indicates that this heuristic scan did not find raw listed-name candidates in the current draft and that the output did not echo those raw names. It does not prove legal review, does not determine listed-entity status, does not validate signatures, does not supervise trusted lists, does not clear warnings, and does not approve publication. It also does not mean that every possible name-like string has been semantically classified; parser errors and extraction limits remain workflow context.

This check is useful because the draft's default explanatory units should remain aggregate: run counts, diff classes, caveated roll-ups, and local evidence references. If a future revision needs a named country, scheme, provider, authority, or service for a research example, the validator should be treated as an abstention reminder rather than an obstacle to bypass. The example should move through operator review with the source path, bundle context, diff class, and exact non-status wording recorded first.

"""

REFS_ANCHOR = "- `notes/artifact-index-duplicate-report-output.json`.\n"
REFS_EXTRA = "- `notes/paper-aggregate-only-naming-validation-output.json`.\n- `notes/paper-aggregate-only-naming-section-check-output.json`.\n"

REQUIRED = [
    "aggregate-only naming validator",
    "hash-only reporting",
    "wording-boundary check",
    "does not prove legal review",
    "does not determine listed-entity status",
    "does not validate signatures",
    "does not supervise trusted lists",
    "does not clear warnings",
    "does not approve publication",
    "operator review",
]

FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
    "we provide eIDAS",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_section(text: str, heading: str) -> str:
    if heading not in text:
        return ""
    start = text.index(heading)
    next_idx = text.find("\n## ", start + 1)
    return text[start:] if next_idx == -1 else text[start:next_idx]


def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    errors: list[str] = []
    inserted = False
    refs_patched = False

    if HEADING not in text:
        if ANCHOR not in text:
            errors.append(f"missing anchor {ANCHOR!r}")
        else:
            text = text.replace(ANCHOR, SECTION + ANCHOR, 1)
            inserted = True

    if REFS_EXTRA not in text:
        if REFS_ANCHOR not in text:
            errors.append("missing references anchor for aggregate-only naming section check")
        else:
            text = text.replace(REFS_ANCHOR, REFS_ANCHOR + REFS_EXTRA, 1)
            refs_patched = True

    if not errors:
        PAPER.write_text(text, encoding="utf-8")

    updated = PAPER.read_text(encoding="utf-8")
    section = extract_section(updated, HEADING)
    word_count = len([w for w in section.split() if w.strip()]) if section else 0
    if not section:
        errors.append("section heading missing after update")
    elif not 250 <= word_count <= 400:
        errors.append(f"section word count outside 250-400 target: {word_count}")
    missing = [fragment for fragment in REQUIRED if fragment not in section]
    if missing:
        errors.append(f"section missing required cautious fragments: {missing}")
    forbidden_hits = [token for token in FORBIDDEN if token.lower() in section.lower()]
    if forbidden_hits:
        errors.append(f"section contains forbidden tokens: {forbidden_hits}")

    result = {
        "schema": "urn:tyche:cassandra:paper-aggregate-only-naming-section-check:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "paper": str(PAPER.relative_to(WORKSPACE)),
        "paper_sha256": sha256_path(PAPER),
        "heading": HEADING,
        "inserted": inserted,
        "refs_patched": refs_patched,
        "word_count": word_count,
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "errors": errors,
        "caveat": "Local paper prose check only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, legal review, warning clearance, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
