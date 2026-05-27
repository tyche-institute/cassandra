#!/usr/bin/env python3
"""Validate the Cassandra publication/case-study kit inventory.

This is a mechanical readiness check for the paper and case-study packet. It
confirms that the requested reusable paper, dataset/evidence, dashboard/product,
and thesis/case artifacts exist, are non-empty, and keep the boundary vocabulary
visible. It is not trusted-list validation, source-signature validation,
legal-status determination, supervision, compliance judgment, public alerting,
endorsement, legal review, or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

RESEARCH_CAVEAT = (
    "Publication-kit inventory check only; not trusted-list validation, "
    "source-signature validation, legal-status determination, supervision, "
    "compliance judgment, public alerting, endorsement, legal review, or "
    "publication approval."
)

REQUIRED_FILES = {
    "paper": [
        "paper/draft.md",
        "paper/abstract-card.md",
        "paper/venue-fit-card.md",
        "paper/reviewer-objection-card.md",
        "paper/claims-and-evidence-table.md",
        "paper/limitations-card.md",
        "paper/thesis-chapter-card.md",
        "paper/related-work-card.md",
        "paper/reference-seed-bibliography.md",
        "paper/preprint/cassandra-preprint-v0.1.md",
        "paper/preprint/cassandra-preprint-v0.1.pdf",
        "paper/preprint/cassandra-preprint-v0.1.docx",
    ],
    "preprint_review": [
        "notes/preprint-review-packet-2026-05-27.md",
        "notes/preprint-review-packet-validation-output.json",
        "notes/preprint-deposit-metadata-draft-2026-05-27.md",
        "notes/preprint-deposit-metadata-validation-output.json",
        "notes/validate_preprint_review_packet.py",
        "notes/validate_preprint_deposit_metadata_draft.py",
        "notes/validate_preprint_candidate.py",
        "notes/preprint-candidate-validation-output.json",
    ],
    "dataset_evidence": [
        "notes/data-dictionary.md",
        "notes/fixture-matrix.md",
        "notes/fixture-to-claim-map.md",
        "notes/evidence-package-format.md",
        "notes/replay-capsule.md",
        "notes/public-index-schema.md",
        "notes/eatf-claim-boundary-card.md",
        "notes/mirror-bundle-card.md",
    ],
    "dashboard_product": [
        "observatory/public/data/index.json",
        "observatory/public/data/schema.json",
        "observatory/public/data/cards/index.json",
        "notes/dashboard-card-pack-2026-05-27.md",
        "notes/dashboard-card-pack-validation-output.json",
    ],
    "thesis_case": [
        "notes/thesis-integration-card.md",
        "notes/cassandra-vesta-icarus-xroad-map.md",
        "notes/eidas-to-ai-act-evidence-map.md",
        "notes/case-study-one-pager.md",
        "notes/press-safe-summary.md",
        "notes/case-study-maturity-matrix.md",
        "notes/cassandra-thesis-reference-atlas-2026-05-27.md",
        "notes/cassandra-evidence-infrastructure-manifest-2026-05-27.md",
        "notes/cassandra-checked-reference-ledger-2026-05-27.md",
    ],
    "validators": [
        "notes/paper-claim-safety-validation-output.json",
        "notes/paper-aggregate-only-naming-validation-output.json",
        "notes/paper-section-order-validation-output.json",
        "notes/paper-evidence-reference-validation-output.json",
        "notes/paper-draft-consolidation-validation-output.json",
        "notes/dashboard-card-pack-validation-output.json",
    ],
}

BOUNDARY_FRAGMENTS = [
    "not trusted-list validation",
    "trusted-list validation",
    "legal-status determination",
    "legal status",
    "legal interpretation",
    "legal effect",
    "signature validation",
    "signature validity",
    "supervision",
    "supervisory",
    "public alerting",
    "public alerts",
    "publication approval",
    "not a claim of deployment",
    "not a substitute",
    "without pretending",
    "do not imply",
    "do not use as proof",
]

FORBIDDEN_TOKENS = [
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees legal status",
    "public alert issued",
    "signature validity is confirmed",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def line_for(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    if idx < 0:
        return None
    return text.count("\n", 0, idx) + 1


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    groups: dict[str, list[dict[str, Any]]] = {}

    for group, rels in REQUIRED_FILES.items():
        records: list[dict[str, Any]] = []
        for rel in rels:
            path = workspace / rel
            record: dict[str, Any] = {"path": rel, "exists": path.exists()}
            if not path.exists():
                errors.append(f"missing required kit artifact: {rel}")
            elif path.is_file():
                size = path.stat().st_size
                record.update({"size_bytes": size, "sha256": sha256_path(path)})
                if size == 0:
                    errors.append(f"empty required kit artifact: {rel}")
                if path.suffix == ".json":
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                        record["json_ok"] = True
                        if rel.endswith("validation-output.json") and data.get("status") != "ok":
                            errors.append(f"validator status is not ok for {rel}: {data.get('status')}")
                    except Exception as exc:  # pragma: no cover - diagnostic path
                        record["json_ok"] = False
                        errors.append(f"invalid JSON in {rel}: {exc}")
                if path.suffix in {".md", ".py"}:
                    text = path.read_text(encoding="utf-8", errors="replace")
                    if path.suffix == ".md":
                        forbidden_hits = [
                            {"token": token, "line": line_for(text, token)}
                            for token in FORBIDDEN_TOKENS
                            if token in text
                        ]
                        if forbidden_hits:
                            errors.append(f"forbidden tokens in {rel}: {forbidden_hits}")
                    boundary_hits = [fragment for fragment in BOUNDARY_FRAGMENTS if fragment in text]
                    record["boundary_fragment_count"] = len(boundary_hits)
                    if path.suffix == ".md" and rel != "paper/draft.md" and not boundary_hits:
                        warnings.append(f"markdown artifact has no explicit boundary fragment from configured list: {rel}")
            records.append(record)
        groups[group] = records

    total_required = sum(len(v) for v in REQUIRED_FILES.values())
    total_present = sum(1 for records in groups.values() for record in records if record.get("exists"))

    return {
        "schema": "urn:tyche:cassandra:publication-case-kit-readiness:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "required_file_count": total_required,
        "present_file_count": total_present,
        "groups": groups,
        "research_caveat": RESEARCH_CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/publication-case-kit-readiness-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    output = workspace / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
