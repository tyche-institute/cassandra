#!/usr/bin/env python3
"""Validate Cassandra paper section order and local-evidence references.

Local research-safety helper only. It checks mechanical structure of the working
paper draft: expected heading order, absence of duplicate headings, required
local-evidence references, and cautious wording fragments. It does not assert
legal compliance, trusted-list legal effect, supervision, signature validation,
public alerting, regulated trust-service output, or publication readiness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

EXPECTED_HEADINGS = [
    "# Cassandra: Longitudinal Structural Observation of European Trusted-List XML",
    "## Abstract",
    "## Claim-safety note",
    "## Outline",
    "## Background",
    "## Dataset boundary and source handling",
    "## Method and evidence-bundle design",
    "## Initial baseline telemetry (2026-05-20)",
    "## Planned longitudinal aggregation and alert taxonomy",
    "## Aggregate telemetry table interpretation",
    "## Results presentation and figure design",
    "## Figure reproducibility cross-references",
    "## Limitations and reproducibility",
    "## Conclusion",
    "## References and local evidence",
]

REQUIRED_REFERENCES = [
    "sources/eu-lotl.xml",
    "sources/eu-lotl.xml.meta.json",
    "notes/pointers.json",
    "snapshots/2026-05-20/manifest.json",
    "normalized/2026-05-20/manifest.json",
    "diffs/2026-05-20.json",
    "alerts.jsonl",
    "bundles/2026-05-20/snapshot-summary.json.bundle/",
    "notes/aggregate-results-table.csv",
    "notes/aggregate-results-2026-05-20-output.json",
    "figures/aggregate-run-telemetry.svg",
    "figures/aggregate-diff-classes.svg",
]

REQUIRED_CAVEATS = [
    "does not assert legal effect",
    "does not determine",
    "does not describe relying-party validation",
    "not a relying-party process",
    "not as a complete or authoritative registry",
    "not public alerts",
]

FORBIDDEN_TOKENS = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
]

RESEARCH_CAVEAT = (
    "Local paper section-order/reference validation only; not legal compliance, "
    "trusted-list legal effect, supervision, signature validation, public "
    "alerting, regulated trust-service output, or publication readiness."
)

HEADING_RE = re.compile(r"^(#{1,2})\s+.+$", re.MULTILINE)


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
    paper_path = workspace / "paper" / "draft.md"
    paper = paper_path.read_text(encoding="utf-8")
    headings = [m.group(0).strip() for m in HEADING_RE.finditer(paper)]

    errors: list[str] = []
    warnings: list[str] = []

    expected_positions: dict[str, int | None] = {heading: line_for(paper, heading) for heading in EXPECTED_HEADINGS}
    missing_headings = [heading for heading, line in expected_positions.items() if line is None]
    if missing_headings:
        errors.append(f"paper missing expected headings: {missing_headings}")

    duplicate_headings = sorted({heading for heading in headings if headings.count(heading) > 1})
    if duplicate_headings:
        errors.append(f"paper has duplicate headings: {duplicate_headings}")

    present_sequence = [heading for heading in EXPECTED_HEADINGS if expected_positions[heading] is not None]
    line_sequence = [expected_positions[heading] for heading in present_sequence]
    if any(a >= b for a, b in zip(line_sequence, line_sequence[1:]) if a is not None and b is not None):
        errors.append("expected headings are not in the configured order")

    references: list[dict[str, Any]] = []
    for rel in REQUIRED_REFERENCES:
        line = line_for(paper, rel)
        path = workspace / rel
        record: dict[str, Any] = {"path": rel, "mentioned": line is not None, "paper_line": line, "exists": path.exists()}
        if line is None:
            errors.append(f"paper missing required local-evidence reference: {rel}")
        if not path.exists():
            errors.append(f"required local-evidence path does not exist: {rel}")
        elif path.is_file():
            record["sha256"] = sha256_path(path)
        elif path.is_dir():
            record["type"] = "directory"
        references.append(record)

    missing_caveats = [fragment for fragment in REQUIRED_CAVEATS if fragment not in paper]
    if missing_caveats:
        errors.append(f"paper missing required caveat fragments: {missing_caveats}")

    forbidden_hits = []
    for token in FORBIDDEN_TOKENS:
        if token in paper:
            forbidden_hits.append({"token": token, "line": line_for(paper, token)})
    if forbidden_hits:
        errors.append(f"paper contains forbidden/overclaiming tokens: {forbidden_hits}")

    outline_items = re.findall(r"^\d+\.\s+(.+)$", paper, flags=re.MULTILINE)
    if len(outline_items) < 8:
        warnings.append("outline has fewer than eight numbered items")
    if "## References and local evidence" in paper and "## Limitations and reproducibility" in paper:
        if line_for(paper, "## References and local evidence") < line_for(paper, "## Limitations and reproducibility"):
            errors.append("references section appears before limitations section")

    return {
        "schema": "urn:tyche:cassandra:paper-section-order-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "paper": str(paper_path.relative_to(workspace)),
        "paper_sha256": sha256_path(paper_path),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "heading_count": len(headings),
        "expected_heading_count": len(EXPECTED_HEADINGS),
        "expected_heading_lines": expected_positions,
        "duplicate_headings": duplicate_headings,
        "required_reference_count": len(REQUIRED_REFERENCES),
        "references": references,
        "research_caveat": RESEARCH_CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/paper-section-order-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
