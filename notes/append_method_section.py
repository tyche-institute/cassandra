#!/usr/bin/env python3
"""Append a cautious method/evidence-bundle section to paper/draft.md.

Research-only helper: this script does not publish or upload anything.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "paper" / "draft.md"
OUT = ROOT / "notes" / "paper-method-section-check-output.json"
MARKER = "## Initial baseline telemetry (2026-05-20)"
SECTION_HEADING = "## Method and evidence-bundle design"
FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "we offer eIDAS-aligned trust services",
    "qualified trust service provider",
    "QTSP",
]

SECTION = """## Method and evidence-bundle design

Cassandra separates collection, normalization, comparison, and bundling so that each step can be checked independently. The collection step starts from a locally saved copy of the public European list-of-lists, extracts pointer URLs, and writes one dated snapshot directory per run. Each fetched file is paired with metadata that records the source URL, access timestamp, HTTP status or fetch error, and local hash. This makes endpoint availability visible as an observation in its own right, rather than silently excluding failed requests from the corpus.

The normalization step is intentionally narrower than a trusted-list processor. It parses XML-like artifacts, applies deterministic canonical serialization, and writes normalized files and a manifest of coarse structural fields. Non-XML/PDF artifacts and parser errors remain in the run telemetry, but they are not forced into the XML comparison set. Signature-related material is summarized only as shape metadata, such as the presence of signature elements and referenced algorithms, without making relying-party validation claims.

The diff step compares normalized records against a stored baseline. It records document additions or removals, normalized-hash changes, summary-field changes, and hashed provider/service inventory deltas. Hash-based inventory keys are used to support longitudinal comparison while keeping listed names out of narrative prose. The resulting JSON diff is therefore useful for triage and aggregation, but it is not a status register and does not determine whether any service or entity has changed legal position.

For each substantive run, Cassandra wraps the summary artifact in a MIRROR-style evidence bundle. The bundle contains a manifest, claims file, source copies or source references, notes, and local verification output. The manifest ties the artifact hash to the input manifests and the cautious claims made about them. This design favors reproducibility and auditability of the research process: a later reader can verify that the draft’s aggregate counts correspond to local files, while still treating legal interpretation and publication decisions as outside the automated lane.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    return len([token for token in text.replace("/", " ").split() if token.strip()])


def main() -> None:
    original = DRAFT.read_text(encoding="utf-8")
    if SECTION_HEADING in original:
        updated = original
        changed = False
    else:
        if MARKER not in original:
            raise SystemExit(f"marker not found: {MARKER}")
        updated = original.replace(MARKER, SECTION + "\n" + MARKER, 1)
        DRAFT.write_text(updated, encoding="utf-8")
        changed = True

    forbidden_hits = [phrase for phrase in FORBIDDEN if phrase in updated]
    result = {
        "status": "ok" if not forbidden_hits else "error",
        "changed": changed,
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "draft_path": str(DRAFT.relative_to(ROOT)),
        "draft_sha256": sha256(DRAFT),
        "section_heading": SECTION_HEADING,
        "section_word_count": word_count(SECTION),
        "forbidden_hits": forbidden_hits,
        "caveats": [
            "research-only structural observation",
            "no relying-party validation claim",
            "no legal-status determination",
            "no listed-entity names in narrative prose",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if forbidden_hits:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
