#!/usr/bin/env python3
"""Insert the Cassandra paper multi-day interpretation protocol section.

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

SECTION_TITLE = "## Multi-day comparison interpretation protocol"
INSERT_BEFORE = "## Limitations and reproducibility"
CHECK_OUTPUT = pathlib.Path("notes/paper-multiday-interpretation-section-check-output.json")
PAPER = pathlib.Path("paper/draft.md")

SECTION_BODY = """## Multi-day comparison interpretation protocol

Once Cassandra has more than one dated run, interpretation should remain deliberately slower than collection. The first comparison question is not whether a trusted list changed in a legally meaningful way, but whether the local structural-observation pipeline can reproduce a bounded, auditable description of differences between two saved artifacts. A multi-day result should therefore start from run metadata: which LOTL copy seeded the pointer set, which endpoints produced content or errors, which XML files normalized successfully, which records entered the diff baseline, and which bundle or alert files carry the hashes for the comparison. Those fields describe the research corpus; they are not a complete or authoritative registry and they do not assert legal effect.

Diff labels should be treated as descriptive buckets, not conclusions about status, compliance, service quality, or trustworthiness. Provider or service inventory additions, removals, supervisory-metadata changes, signature-shape observations, and qualified-status-field changes can guide later manual review, but the paper should present aggregate counts, date ranges, and evidence pointers before any narrative example. If a single named country, scheme, provider, or service would materially improve explanation, that example should wait for operator review and a separate release decision. The default text should say that a structural diff was observed in local XML snapshots and cite `diffs/<date>.json`, the corresponding bundle manifest, and the relevant validator outputs.

The comparison protocol should also preserve negative results carefully. A zero-change diff means only that this parser, normalizer, and baseline configuration did not emit configured structural changes for the saved inputs. It does not determine legal effect, does not validate signatures, does not supervise trusted lists, and does not support public alerting or reliance guidance. Multi-day charts should keep this caveat visible in captions and avoid ranking countries or authorities.
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
    "deliberately slower than collection",
    "local structural-observation pipeline",
    "not a complete or authoritative registry",
    "do not assert legal effect",
    "aggregate counts, date ranges, and evidence pointers",
    "operator review",
    "does not validate signatures",
    "does not supervise trusted lists",
    "does not support public alerting",
    "avoid ranking countries or authorities",
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
        "schema": "urn:tyche:cassandra:paper-multiday-interpretation-section-check:0.1",
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
