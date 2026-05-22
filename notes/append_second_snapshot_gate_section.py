#!/usr/bin/env python3
"""Insert the Cassandra paper second-snapshot readiness gate section.

Local drafting helper only. It writes cautious, aggregate-oriented prose and does
not assert legal compliance, trusted-list legal effect, supervision, signature
validation, public alerting, regulated trust-service output, or publication
readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone

SECTION_TITLE = "## Second-snapshot readiness and collection gate"
INSERT_BEFORE = "## Limitations and reproducibility"
CHECK_OUTPUT = pathlib.Path("notes/paper-second-snapshot-gate-section-check-output.json")
PAPER = pathlib.Path("paper/draft.md")

SECTION_BODY = """## Second-snapshot readiness and collection gate

The second dated snapshot is the first point at which Cassandra can test longitudinal mechanics rather than only bootstrap integrity. Until that run exists, the paper should treat all results as single-row calibration evidence: useful for verifying local fetch, normalization, diff, bundle, alert, and validation wiring, but not yet sufficient for trend language. The collection gate is therefore procedural. A new dated run should use a date label that does not collide with existing snapshot, normalization, diff, baseline, or bundle outputs; it should preserve the same LOTL-derived pointer discipline; and it should record endpoint errors, parser outcomes, and diff configuration in machine-readable files before any narrative interpretation is drafted.

After the second run, the first review step should be lineage parity, not meaning assignment. The operator or a later worker should check that `snapshots/<date>/manifest.json`, `normalized/<date>/manifest.json`, `diffs/<date>.json`, `bundles/<date>/snapshot-summary.json.bundle/manifest.json`, and the matching alert entry are all present, hashed, and internally linked. Only then should aggregate tables or figures be refreshed. Even then, a nonzero diff should be described as a structural diff observed in saved XML-derived artifacts, and a zero diff should be described as no configured structural diff emitted by this parser/baseline pair.

This gate also limits paper prose. Before a second completed date exists, Cassandra should not use phrases such as trend, churn rate, stability, volatility, or national comparison except as planned-analysis vocabulary. After a second date exists, those words still need aggregate scope, visible caveats, and evidence pointers. The gate does not determine legal effect, does not validate signatures, does not supervise trusted lists, does not provide reliance guidance, and does not support public alerting or publication approval.
"""

FORBIDDEN_TOKENS = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
]
REQUIRED_FRAGMENTS = [
    "single-row calibration evidence",
    "does not collide with existing snapshot",
    "record endpoint errors, parser outcomes, and diff configuration",
    "lineage parity, not meaning assignment",
    "structural diff observed in saved XML-derived artifacts",
    "no configured structural diff emitted by this parser/baseline pair",
    "does not determine legal effect",
    "does not validate signatures",
    "does not supervise trusted lists",
    "does not support public alerting",
    "publication approval",
]
RESEARCH_CAVEAT = (
    "Local Cassandra drafting helper only; not legal compliance, trusted-list legal effect, "
    "supervision, signature validation, relying-party processing, public alerting, regulated "
    "trust-service output, or publication readiness."
)


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def section_word_count(text: str) -> int:
    section = text.split(SECTION_TITLE, 1)[1]
    next_heading = re.search(r"\n## ", section)
    if next_heading:
        section = section[: next_heading.start()]
    return len(re.findall(r"\b[\w'-]+\b", section))


def main() -> int:
    paper = PAPER.read_text(encoding="utf-8")
    changed = False
    if SECTION_TITLE not in paper:
        if INSERT_BEFORE not in paper:
            raise SystemExit(f"missing insertion anchor: {INSERT_BEFORE}")
        paper = paper.replace(INSERT_BEFORE, SECTION_BODY + "\n" + INSERT_BEFORE, 1)
        PAPER.write_text(paper, encoding="utf-8")
        changed = True

    paper = PAPER.read_text(encoding="utf-8")
    forbidden_hits = [token for token in FORBIDDEN_TOKENS if token in paper]
    missing_fragments = [fragment for fragment in REQUIRED_FRAGMENTS if fragment not in paper]
    word_count = section_word_count(paper)
    errors: list[str] = []
    if forbidden_hits:
        errors.append(f"forbidden tokens present: {forbidden_hits}")
    if missing_fragments:
        errors.append(f"missing required fragments: {missing_fragments}")
    if not (250 <= word_count <= 400):
        errors.append(f"section word count outside 250-400 range: {word_count}")

    result = {
        "schema": "urn:tyche:cassandra:paper-second-snapshot-gate-section-check:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if not errors else "needs_review",
        "changed": changed,
        "section_title": SECTION_TITLE,
        "section_word_count": word_count,
        "paper": str(PAPER),
        "paper_sha256": sha256_path(PAPER),
        "error_count": len(errors),
        "errors": errors,
        "forbidden_hits": forbidden_hits,
        "missing_required_fragments": missing_fragments,
        "research_caveat": RESEARCH_CAVEAT,
    }
    CHECK_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
