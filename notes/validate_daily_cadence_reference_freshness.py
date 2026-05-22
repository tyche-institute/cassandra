#!/usr/bin/env python3
"""Validate daily-cadence status paper/reference freshness.

This local workflow-maintenance check verifies that the paper still references
`notes/daily-cadence-status-output.json`, that the cadence report is current in
ARTIFACT_INDEX.md, and that same-date guard telemetry remains framed as local
workflow cadence rather than endpoint stability, legal/status evidence, public
alerting, or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

PAPER = pathlib.Path("paper/draft.md")
CADENCE_OUTPUT = pathlib.Path("notes/daily-cadence-status-output.json")
ARTIFACT_INDEX = pathlib.Path("ARTIFACT_INDEX.md")

REQUIRED_PAPER_FRAGMENTS = [
    "notes/daily-cadence-status-output.json",
    "workflow telemetry",
    "legal effect",
    "signature validity",
    "public alerting",
    "publication approval",
]

EQUIVALENT_PAPER_FRAGMENT_GROUPS = [
    ("endpoint stability", [
        "does not assert endpoint stability",
        "not assert endpoint stability",
        "does not assert that public sources are stable",
        "does not say that public endpoints are unchanged",
    ]),
]

REQUIRED_CAVEAT_FRAGMENTS = [
    "Local daily-cadence workflow telemetry only",
    "not endpoint stability evidence",
    "legal compliance",
    "trusted-list legal effect",
    "signature validation",
    "public alerting",
    "regulated trust-service output",
    "publication approval",
]

FORBIDDEN_PAPER_FRAGMENTS = [
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees endpoint stability",
    "approves publication",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact_index_hashes(index_text: str, rel_path: str) -> list[str]:
    pattern = re.compile(rf"`{re.escape(rel_path)}`\s*\|[^\n]*?`sha256:([0-9a-f]{{64}})`")
    return pattern.findall(index_text)


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    workspace = workspace.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    paper_path = workspace / PAPER
    cadence_path = workspace / CADENCE_OUTPUT
    artifact_index_path = workspace / ARTIFACT_INDEX

    paper = paper_path.read_text(encoding="utf-8") if paper_path.exists() else ""
    cadence = json.loads(cadence_path.read_text(encoding="utf-8")) if cadence_path.exists() else {}
    artifact_index = artifact_index_path.read_text(encoding="utf-8") if artifact_index_path.exists() else ""

    if not paper:
        errors.append(f"missing paper: {PAPER}")
    if not cadence:
        errors.append(f"missing cadence output: {CADENCE_OUTPUT}")
    if not artifact_index:
        errors.append(f"missing artifact index: {ARTIFACT_INDEX}")

    paper_lower = paper.lower()
    missing_paper = [fragment for fragment in REQUIRED_PAPER_FRAGMENTS if fragment.lower() not in paper_lower]
    for label, variants in EQUIVALENT_PAPER_FRAGMENT_GROUPS:
        if not any(variant.lower() in paper_lower for variant in variants):
            missing_paper.append(label)
    if missing_paper:
        errors.append(f"paper lacks daily-cadence reference/caveat fragments: {missing_paper}")
    forbidden_hits = [fragment for fragment in FORBIDDEN_PAPER_FRAGMENTS if fragment in paper_lower]
    if forbidden_hits:
        errors.append(f"paper contains forbidden cadence overclaiming fragments: {forbidden_hits}")

    if cadence:
        if cadence.get("status") != "ok" or cadence.get("error_count") != 0:
            errors.append(f"cadence output is not ok: status={cadence.get('status')} error_count={cadence.get('error_count')}")
        if cadence.get("today_guard", {}).get("status") != "refused_existing_outputs" and cadence.get("today_complete"):
            errors.append("cadence output marks today complete but same-date guard did not refuse existing outputs")
        if cadence.get("next_eligible_guard", {}).get("status") not in {"dry_run_ok", "refused_existing_outputs"}:
            errors.append("cadence output next eligible guard has unexpected status")
        caveat = cadence.get("research_caveat", "")
        missing_caveat = [fragment for fragment in REQUIRED_CAVEAT_FRAGMENTS if fragment not in caveat]
        if missing_caveat:
            errors.append(f"cadence research caveat lacks required fragments: {missing_caveat}")
        if cadence.get("warning_count", 0):
            warnings.append(
                f"{CADENCE_OUTPUT} has warning_count={cadence.get('warning_count')}; preserve same-date non-overwrite warning as workflow context"
            )

    current_hash = sha256_path(cadence_path) if cadence_path.exists() else None
    indexed_hashes = artifact_index_hashes(artifact_index, str(CADENCE_OUTPUT)) if artifact_index else []
    current_hash_indexed = bool(current_hash and current_hash in indexed_hashes)
    if not current_hash_indexed:
        errors.append(f"ARTIFACT_INDEX.md lacks current sha256 for {CADENCE_OUTPUT}")
    if len(indexed_hashes) > 1:
        warnings.append(
            f"ARTIFACT_INDEX.md has {len(indexed_hashes)} rows for {CADENCE_OUTPUT}; require at least one current row and preserve duplicates as maintenance context"
        )

    return {
        "schema": "urn:tyche:cassandra:daily-cadence-reference-freshness-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "paper": str(PAPER),
        "paper_sha256": sha256_path(paper_path) if paper_path.exists() else None,
        "cadence_output": str(CADENCE_OUTPUT),
        "cadence_output_sha256": current_hash,
        "cadence_status": cadence.get("status") if cadence else None,
        "cadence_warning_count": cadence.get("warning_count") if cadence else None,
        "today_utc": cadence.get("today_utc") if cadence else None,
        "latest_completed_date": cadence.get("latest_completed_date") if cadence else None,
        "next_eligible_date": cadence.get("next_eligible_date") if cadence else None,
        "artifact_index_hashes_for_cadence_output": indexed_hashes,
        "current_hash_indexed": current_hash_indexed,
        "research_caveat": "Local daily-cadence reference freshness validation only; verifies paper/reference/hash alignment for workflow telemetry, not endpoint stability, legal compliance, trusted-list legal effect, signature validation, supervision, listed-entity status evidence, public alerting, regulated trust-service output, warning clearance, legal review, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/daily-cadence-reference-freshness-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    output = pathlib.Path(args.output)
    if not output.is_absolute():
        output = workspace / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
