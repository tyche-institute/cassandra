#!/usr/bin/env python3
"""Append parser-scope and signature-shape observation prose to Cassandra paper.

Local research-only helper. It updates the working draft with cautious prose and
performs minimal local checks. It does not assert legal compliance, trusted-list
legal effect, supervision, signature validation, public alerting, regulated
trust-service output, or publication readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-parser-scope-section-check-output.json"
ANCHOR = "## Limitations and reproducibility"
HEADING = "## Parser scope and signature-shape observation"

SECTION = """## Parser scope and signature-shape observation

The parser is deliberately narrower than an implementation that would consume trusted lists for relying-party decisions. It reads saved XML-like artifacts from the dated snapshot directory, normalizes serialization details that otherwise create noisy byte-level comparisons, and extracts a small set of structural fields for longitudinal comparison. Signature-related fields are treated as shape observations only: the tooling records whether signature elements, reference elements, digest-method declarations, signature-method declarations, and certificate-bearing subtrees are present in the saved XML structure. Those records are useful for checking whether the research pipeline is consistently seeing comparable XML layouts, but they are not cryptographic validation output and are not evidence that any signature is valid, invalid, current, or fit for reliance.

This boundary also affects how parser errors are interpreted. A parse failure is first a local workflow event associated with a saved path, parser version, and timestamped run output. It may indicate non-XML content, transport anomalies preserved as source bytes, an XML edge case the prototype has not implemented, or a local dependency issue. The paper therefore treats parser outcomes as reproducibility telemetry before interpretation. When a future daily run changes parser counts, provider/service inventory counts, or signature-shape counters, the default description should be "structural difference observed in the local corpus" with links to `snapshots/<date>/manifest.json`, `normalized/<date>/manifest.json`, and `diffs/<date>.json`.

The same rule applies to hashed provider and service inventory keys. They are stable local comparison keys derived to avoid listed-name prose, not identifiers for public status, service quality, legal effect, or supervisory assessment. Any named example, if later considered useful for publication, requires operator review against the saved source, bundle notes, and compliance rails before being moved from machine-readable local records into narrative text.

"""

REQUIRED = [
    "not cryptographic validation output",
    "not evidence that any signature is valid",
    "structural difference observed in the local corpus",
    "not identifiers for public status",
    "requires operator review",
]
FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
]

def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    errors: list[str] = []
    inserted = False
    if HEADING in text:
        # Idempotent: leave existing section in place.
        updated = text
    else:
        if ANCHOR not in text:
            errors.append(f"missing anchor {ANCHOR!r}")
            updated = text
        else:
            updated = text.replace(ANCHOR, SECTION + ANCHOR, 1)
            PAPER.write_text(updated, encoding="utf-8")
            inserted = True
    section_present = HEADING in updated
    if not section_present:
        errors.append("section heading missing after update")
    if section_present:
        start = updated.index(HEADING)
        next_idx = updated.find("\n## ", start + 1)
        section = updated[start:] if next_idx == -1 else updated[start:next_idx]
        word_count = len([w for w in section.split() if w.strip()])
        if not 250 <= word_count <= 400:
            errors.append(f"section word count outside 250-400 target: {word_count}")
        missing = [frag for frag in REQUIRED if frag not in section]
        if missing:
            errors.append(f"section missing required cautious fragments: {missing}")
        forbidden_hits = [token for token in FORBIDDEN if token in section]
        if forbidden_hits:
            errors.append(f"section contains forbidden tokens: {forbidden_hits}")
    else:
        word_count = 0
    result = {
        "schema": "urn:tyche:cassandra:paper-parser-scope-section-check:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "paper": str(PAPER.relative_to(WORKSPACE)),
        "paper_sha256": sha256_path(PAPER),
        "heading": HEADING,
        "inserted": inserted,
        "word_count": word_count,
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "errors": errors,
        "caveat": "Local paper prose check only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
