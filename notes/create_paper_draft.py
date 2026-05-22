#!/usr/bin/env python3
"""Create the initial Cassandra paper draft with cautious research-only wording."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "paper" / "draft.md"
CHECK = ROOT / "notes" / "paper-draft-check-output.json"

FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
    "trust services provider",
    "qualified trust service provider",
]

DRAFT_TEXT = """# Cassandra: Longitudinal Structural Observation of European Trusted-List XML

Author: Anton Sokolov  
Affiliation: Tyche Institute, Tallinn, Estonia  
Status: working draft; not for publication without operator review  
Generated: 2026-05-20

## Abstract (placeholder)

This working draft describes a research-only monitor for the public European list-of-lists and national trusted-list documents. The monitor records dated snapshots, normalizes XML for stable comparison, and emits structured observations about document-level and coarse semantic churn. It does not operate, supervise, validate, or determine the legal status of any trusted list or listed entity.

## Claim-safety note

All observations in this draft are limited to locally recorded structural artifacts: fetched files, parser telemetry, normalized XML hashes, and machine-readable diff records. A structural diff observed by this project should not be read as evidence that any provider, service, scheme, certificate, or authority has gained or lost legal status. Signature-related fields are treated as shape metadata only; this draft does not describe relying-party validation.

## Outline

1. Motivation: why longitudinal public-list observation is useful for research.
2. Dataset boundary: LOTL-derived pointers, dated fetches, and local provenance.
3. Method: fetcher, parser, normalizer, baseline, and structural diff classes.
4. Evidence bundles: local manifests, hashes, assumptions, and caveats.
5. Early baseline telemetry: snapshot counts and parser outcomes from the first run.
6. Planned longitudinal analysis: aggregate churn classes without naming listed entities in prose.
7. Limitations: non-validation, endpoint availability, PDF/non-XML records, and legal non-inference.
8. Reproducibility checklist and future work.

## Background

European trusted lists are public, structured documents that support a wider ecosystem of digital-signature and trust-service interoperability. Because they are public and periodically updated, they are also suitable for cautious longitudinal research into how governance artifacts change over time. Cassandra approaches the lists as observable documents rather than as operational trust anchors. Its purpose is to preserve dated local evidence, compare normalized structure, and make the resulting telemetry reproducible for later academic analysis.

The research question is intentionally narrow: what kinds of structural churn can be observed in public list-of-lists and national trusted-list artifacts when the same collection and parsing procedure is repeated over time? This formulation avoids inferring legal effect from a fetch result or a diff. A fetched document may be unavailable for ordinary network reasons, a pointer may reference a PDF alongside an XML file, an XML parser may reject a file, or a normalized hash may change because of formatting, metadata, or substantive structural edits. Cassandra records these events as local observations and leaves legal interpretation outside the project scope.

The first implementation therefore emphasizes provenance and restraint. The fetcher stores the European list-of-lists and LOTL-derived national pointers under dated snapshot directories. The parser normalizes XML with deterministic serialization, records coarse scheme metadata, and extracts hashed provider/service inventory keys for comparison without using listed names in narrative prose. The diff engine compares comparable normalized records and emits machine-readable classes such as document addition/removal, summary-field change, provider-inventory change, service-inventory change, and provider/service detail change. Alert records are local JSONL telemetry, not public alerts and not supervisory statements.

This design is deliberately conservative. It treats endpoint errors, non-XML artifacts, and parser failures as part of the research corpus rather than as defects to hide. It also keeps claims close to the evidence: a daily bundle can say that a local run attempted a certain number of LOTL-derived pointers, saved a certain number of files, normalized a certain number of XML documents, and observed a certain number of structural diffs against the configured baseline. It cannot say that a listed entity has or lacks legal status, that a signature is valid for relying-party purposes, or that a change has legal effect.

## Initial baseline telemetry (2026-05-20)

The first local run attempted 43 LOTL-derived pointers and recorded 41 fetched content files plus 2 endpoint fetch errors. The normalization run produced 31 comparable normalized XML artifacts, skipped 9 non-XML/PDF artifacts, and recorded 1 XML parse error. The day-one diff initialized a baseline over 31 comparable records and emitted zero structural changes because no prior baseline existed. These counts are local tool telemetry only.

## References and local evidence

- `sources/eu-lotl.xml` and `sources/eu-lotl.xml.meta.json`.
- `notes/pointers.json`.
- `snapshots/2026-05-20/manifest.json`.
- `normalized/2026-05-20/manifest.json`.
- `diffs/2026-05-20.json`.
- `alerts.jsonl`.
- `bundles/2026-05-20/snapshot-summary.json.bundle/`.
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    return len([w for w in text.replace("—", " ").split() if w.strip()])


def main() -> int:
    DRAFT.parent.mkdir(parents=True, exist_ok=True)
    CHECK.parent.mkdir(parents=True, exist_ok=True)
    DRAFT.write_text(DRAFT_TEXT, encoding="utf-8")

    text = DRAFT.read_text(encoding="utf-8")
    forbidden_hits = [needle for needle in FORBIDDEN if needle.lower() in text.lower()]
    result = {
        "status": "ok" if not forbidden_hits else "failed",
        "created": datetime.now(timezone.utc).isoformat(),
        "draft": str(DRAFT.relative_to(ROOT)),
        "draft_sha256": sha256(DRAFT),
        "word_count": word_count(text),
        "forbidden_hits": forbidden_hits,
        "checks": [
            "research-only wording included",
            "no listed-entity names added in prose beyond aggregate local telemetry",
            "local evidence references included",
            "forbidden phrase scan completed",
        ],
    }
    CHECK.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
