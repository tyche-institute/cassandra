#!/usr/bin/env python3
"""Append evidence-release checklist and abstention rules prose to Cassandra paper.

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
OUTPUT = WORKSPACE / "notes" / "paper-evidence-release-checklist-section-check-output.json"
ANCHOR = "## Limitations and reproducibility"
HEADING = "## Evidence release checklist and abstention rules"

SECTION = """## Evidence release checklist and abstention rules

Cassandra needs an explicit abstention layer because its raw corpus contains public trusted-list material while the paper's default narrative stance is aggregate, research-only, and non-adjudicative. Before any local artifact is treated as release candidate material, the workspace should show four kinds of evidence: a dated raw snapshot manifest with adjacent endpoint metadata, a normalization manifest with parser outcomes, a structural diff record tied to a stated baseline, and a MIRROR-style bundle whose manifest, claims file, notes, and verification report can be checked without network access. Absence of any one layer should stop release packaging rather than invite reconstruction from live endpoints.

The checklist is intentionally conservative. Clean validator output means only that configured local files were present, parseable, hash-consistent, and caveated at the time of the run. It is not publication approval, legal review, endpoint certification, or a statement about listed-entity status. A dated run with zero structural diff entries should be described as "no structural diff emitted by this configured local comparison" and not as stability of the trusted-list ecosystem. A dated run with nonzero diff entries should be described as "structural diff observed" with local evidence pointers, not as legal effect, service quality, supervision, or public alerting.

Abstention rules also govern examples. The default paper text should avoid listed names even when machine-readable local records contain enough material to identify changed provider or service structures. A named example may become appropriate only after operator review confirms that the example is necessary for research explanation, that the source copy and bundle context are cited, and that the prose remains on the specification and longitudinal-observation side of the compliance boundary. Until then, aggregate counts, class labels, dates, hashes, and local paths are the safer explanatory units.

"""

REQUIRED = [
    "aggregate, research-only, and non-adjudicative",
    "not publication approval",
    "no structural diff emitted by this configured local comparison",
    "structural diff observed",
    "not as legal effect",
    "avoid listed names",
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
        updated = text
    else:
        if ANCHOR not in text:
            errors.append(f"missing anchor {ANCHOR!r}")
            updated = text
        else:
            updated = text.replace(ANCHOR, SECTION + ANCHOR, 1)
            PAPER.write_text(updated, encoding="utf-8")
            inserted = True
    if HEADING not in updated:
        errors.append("section heading missing after update")
        section = ""
    else:
        start = updated.index(HEADING)
        next_idx = updated.find("\n## ", start + 1)
        section = updated[start:] if next_idx == -1 else updated[start:next_idx]
    word_count = len([w for w in section.split() if w.strip()]) if section else 0
    if section and not 250 <= word_count <= 400:
        errors.append(f"section word count outside 250-400 target: {word_count}")
    missing = [frag for frag in REQUIRED if frag not in section]
    if missing:
        errors.append(f"section missing required cautious fragments: {missing}")
    forbidden_hits = [token for token in FORBIDDEN if token in section]
    if forbidden_hits:
        errors.append(f"section contains forbidden tokens: {forbidden_hits}")
    result = {
        "schema": "urn:tyche:cassandra:paper-evidence-release-checklist-section-check:0.1",
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
