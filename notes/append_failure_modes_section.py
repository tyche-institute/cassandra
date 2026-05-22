#!/usr/bin/env python3
"""Append/check Cassandra paper failure-mode and recovery discipline section.

Local research-only helper. It updates public-facing draft prose while keeping
Cassandra on the structural-observation side: no legal effect, no supervision,
no signature validation, no public alerting, and no publication readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-failure-modes-section-check-output.json"
HEADING = "## Failure-mode and recovery discipline"
INSERT_BEFORE = "## Limitations and reproducibility"
FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
]
REQUIRED_FRAGMENTS = [
    "does not assert legal effect",
    "does not validate signatures",
    "does not supervise trusted lists",
    "not public alerting",
    "not publication approval",
    "operator review",
]
SECTION = """## Failure-mode and recovery discipline

Cassandra treats collection failures, parser exceptions, and same-date guard refusals as workflow telemetry before treating them as research findings. A failed endpoint fetch is recorded with the attempted URL, exception class, timestamp, and local metadata path, but the draft does not convert that event into a statement about legal effect, availability duties, listed-entity status, or scheme quality. Likewise, an XML parse error is a parser-bound observation over saved bytes; it does not validate signatures, does not invalidate signatures, and does not supervise trusted lists. Recovery therefore starts by preserving the original metadata, rerunning only the bounded local step that failed, and comparing new outputs against recorded hashes.

The recovery policy is deliberately conservative. Same-date daily runs refuse to overwrite mature snapshot, normalization, diff, baseline, and bundle directories unless an explicit override is supplied, and autonomous iterations should prefer adding dated evidence or validation notes over rewriting historical registers. If a future run produces nonzero structural diffs, recovery first checks local lineage: raw snapshot manifest, normalized manifest, diff JSON, bundle manifest, alert entry, and artifact-index hash rows. Only after those links are internally consistent should the paper discuss aggregate patterns, and even then the discussion remains descriptive: it does not assert legal effect, does not provide reliance guidance, and is not public alerting.

This discipline also defines stopping points. Publication, named examples, destructive cleanup, external circulation, or changes that could resemble trust-service operation require operator review. Clean local validation output is useful reproducibility evidence, but it is not publication approval, legal review, supervision, signature validation, or a public status statement.
"""


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def extract_section(text: str, heading: str) -> str:
    start = text.index(heading)
    next_match = re.search(r"^##\s+", text[start + len(heading):], flags=re.MULTILINE)
    end = start + len(heading) + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    changed = False
    if HEADING not in text:
        if INSERT_BEFORE not in text:
            raise SystemExit(f"insert anchor not found: {INSERT_BEFORE}")
        text = text.replace(INSERT_BEFORE, SECTION + "\n" + INSERT_BEFORE, 1)
        PAPER.write_text(text, encoding="utf-8")
        changed = True

    text = PAPER.read_text(encoding="utf-8")
    section_text = extract_section(text, HEADING)
    forbidden_hits = [token for token in FORBIDDEN if token in text]
    missing_required = [frag for frag in REQUIRED_FRAGMENTS if frag not in section_text]
    wc = word_count(section_text)
    errors: list[str] = []
    if forbidden_hits:
        errors.append(f"forbidden/overclaiming tokens present: {forbidden_hits}")
    if missing_required:
        errors.append(f"section missing required cautious fragments: {missing_required}")
    if wc < 250 or wc > 400:
        errors.append(f"section word count {wc} outside 250-400 range")
    if "Tyche Institute, Tallinn, Estonia" not in text:
        errors.append("expected Tyche affiliation missing")

    result = {
        "schema": "urn:tyche:cassandra:paper-failure-modes-section-check:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "paper": str(PAPER.relative_to(WORKSPACE)),
        "paper_sha256": sha256_path(PAPER),
        "section_heading": HEADING,
        "section_word_count": wc,
        "changed": changed,
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "errors": errors,
        "forbidden_hits": forbidden_hits,
        "missing_required_fragments": missing_required,
        "research_caveat": "Local paper prose check only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
