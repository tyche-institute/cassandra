#!/usr/bin/env python3
"""Insert the Cassandra paper data-retention / redaction-discipline section.

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

SECTION_TITLE = "## Data retention and local redaction discipline"
INSERT_BEFORE = "## Limitations and reproducibility"
CHECK_OUTPUT = pathlib.Path("notes/paper-data-retention-section-check-output.json")
PAPER = pathlib.Path("paper/draft.md")

SECTION_BODY = """## Data retention and local redaction discipline

Cassandra keeps raw public XML and adjacent metadata because longitudinal reproducibility depends on being able to re-run parsers against the exact bytes collected on a dated run. Retention in this workspace is therefore a local evidence practice, not a statement that the lane operates, supervises, republishes, or validates trusted lists. The raw files, manifests, normalized XML, diffs, and bundles are treated as research records with hashes and caveats. They should remain inside the workspace unless Anton separately approves external circulation.

The paper layer should continue to use aggregation and local evidence pointers rather than named examples. Machine-readable diff records may contain hashed provider or service inventory keys for reproducible comparison, but prose should describe classes of structural change, counts, and methodology. If a future section needs to discuss a concrete country, scheme, or listed entity, that is an operator-review decision, not an autonomous drafting default. The safe default is to cite artifact paths such as `snapshots/<date>/manifest.json`, `diffs/<date>.json`, and bundle manifests while leaving detailed names in local machine-readable records.

Redaction here means narrative minimization rather than alteration of the retained evidence. The source bytes should not be edited to make prose safer; instead, public-facing text should avoid unnecessary names, avoid legal-status interpretation, and state the observation boundary directly. If a bundle or figure is later prepared for release, the release review should check whether any copied source excerpt, caption, or table row creates a service-provision, supervision, or legal-effect implication. Clean local validation output is useful reproducibility evidence, but it is not publication approval.
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
    "local evidence practice",
    "not a statement that the lane operates, supervises, republishes, or validates trusted lists",
    "aggregation and local evidence pointers rather than named examples",
    "operator-review decision",
    "narrative minimization rather than alteration of the retained evidence",
    "not publication approval",
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
        "schema": "urn:tyche:cassandra:paper-data-retention-section-check:0.1",
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
