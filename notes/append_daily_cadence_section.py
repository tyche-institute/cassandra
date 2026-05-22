#!/usr/bin/env python3
"""Insert the Cassandra paper daily-cadence / overwrite-discipline section.

Local drafting helper only. It writes cautious, aggregate-only prose and does
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

SECTION_TITLE = "## Daily cadence and overwrite discipline"
INSERT_BEFORE = "## Operator review gates and non-publication status"
CHECK_OUTPUT = pathlib.Path("notes/paper-daily-cadence-section-check-output.json")
PAPER = pathlib.Path("paper/draft.md")

SECTION_BODY = """## Daily cadence and overwrite discipline

Cassandra's daily cadence should favor monotonically dated evidence over convenience. A normal run creates a new `snapshots/<date>/` directory, a matching normalization manifest, a dated diff JSON file, a dated bundle, and an alert-roll-up entry. If those paths already exist, the runner refuses to overwrite them unless an explicit override is supplied. That guard is part of the research method, not an operational status statement: it protects the historical trail from accidental replacement while leaving operator-reviewed reruns possible when a local artifact is known to be wrong.

This discipline is especially important while the first day remains the only completed snapshot date. Re-running the same-date command currently produces refusal telemetry rather than a second baseline, and the refusal output should be interpreted as workflow safety evidence only. It does not say that public endpoints are unchanged, that the corpus is stable, or that no legally relevant event occurred. It simply says that the lane preserved an existing dated state and declined to replace it without an explicit instruction.

Once a new UTC date is available, the intended sequence is narrow: run the daily orchestrator, create the MIRROR-style bundle, append or replace the idempotent alert entry for that date, regenerate aggregate tables and figures, and rerun validators that connect paper prose to the local artifacts. Each step should record hashes and caveats before the next step is treated as evidence. A missing second date should not be simulated with copied files or renamed directories; longitudinal claims should wait for actual dated collection records. This keeps the study aligned with reproducible observation rather than narrative pressure.
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
    "does not say that public endpoints are unchanged",
    "does not say that public endpoints are unchanged, that the corpus is stable, or that no legally relevant event occurred",
    "workflow safety evidence only",
    "not an operational status statement",
    "should not be simulated with copied files or renamed directories",
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
        "schema": "urn:tyche:cassandra:paper-daily-cadence-section-check:0.1",
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
