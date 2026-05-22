#!/usr/bin/env python3
"""Append cautious future-dated local lineage handling prose.

Local research-only helper. It updates the Cassandra working draft with a short
aggregate-only subsection about cadence scheduling when a local dated lineage is
ahead of live UTC. It does not assert legal compliance, trusted-list legal
effect, supervision, signature validation, public alerting, regulated
trust-service output, legal review, or publication readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-future-dated-lineage-section-check-output.json"
ANCHOR = "## Operator review gates and non-publication status"
HEADING = "## Future-dated local lineage handling"

SECTION = """## Future-dated local lineage handling

The cadence report can now surface a local lineage whose snapshot date is later than the live UTC date observed by the worker. This condition appeared after the local 2026-05-22 run was completed while the live clock still reported 2026-05-21. Cassandra treats that situation as workflow-scheduling context only. It is useful because it prevents a later worker from silently interpreting the latest completed local date as an ordinary same-day collection opportunity, but it is not evidence about public endpoint stability, trusted-list legal effect, or the presence or absence of any legally relevant event.

The safe handling rule is conservative. If `notes/daily-cadence-status-output.json` reports `future_completed_dates_relative_to_today`, the next worker should not overwrite the future-dated snapshot merely to align labels with the live clock. Instead, it should preserve the dated lineage, keep the non-overwrite guard active, and wait for the next eligible date unless the operator explicitly authorizes an overwrite or recovery action. The report may still be used to plan local validation work, paper prose, or aggregate-only review, provided that those tasks do not fetch, republish, or reinterpret endpoint content as a public status signal.

For paper and release-readiness purposes, the warning belongs with the same abstention discipline as duplicate artifact-index rows and persistent manual-review warnings. It records that Cassandra is an autonomous local workflow with dated artifacts, not a supervisory process. Clean cadence validation does not assert legal effect, does not perform signature validation, does not supervise trusted lists, does not determine listed-entity status, does not provide public alerting, and does not approve publication. Any later explanation of why a future-dated lineage exists should cite the local cadence report and progress diary, not speculate about external authorities or endpoint behavior.

"""

REFS_ANCHOR = "- `notes/daily-cadence-status-output.json`.\n"
REFS_EXTRA = "- `notes/paper-future-dated-lineage-section-check-output.json`.\n"

REQUIRED = [
    "future_completed_dates_relative_to_today",
    "workflow-scheduling context only",
    "not evidence about public endpoint stability",
    "does not assert legal effect",
    "does not perform signature validation",
    "does not supervise trusted lists",
    "does not determine listed-entity status",
    "does not provide public alerting",
    "does not approve publication",
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
            errors.append("missing references anchor for future-dated lineage section check")
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
        "schema": "urn:tyche:cassandra:paper-future-dated-lineage-section-check:0.1",
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
        "caveat": "Local paper prose check only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, legal review, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
