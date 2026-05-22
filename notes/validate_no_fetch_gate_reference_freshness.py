#!/usr/bin/env python3
"""Validate no-fetch-before-gate paper/reference freshness.

This local workflow-maintenance check verifies that the paper references
`notes/no-fetch-before-gate-validation-output.json`, that the no-fetch gate
output remains current in ARTIFACT_INDEX.md, and that the gate is framed as
local workflow scheduling telemetry rather than endpoint stability, legal/status
evidence, public alerting, warning clearance, or publication approval.
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
NO_FETCH_OUTPUT = pathlib.Path("notes/no-fetch-before-gate-validation-output.json")
ARTIFACT_INDEX = pathlib.Path("ARTIFACT_INDEX.md")

REQUIRED_PAPER_FRAGMENTS = [
    "notes/no-fetch-before-gate-validation-output.json",
    "workflow scheduling telemetry",
    "legal effect",
    "signature validation",
    "public alerting",
    "warning clearance",
    "publication approval",
]

EQUIVALENT_PAPER_FRAGMENT_GROUPS = [
    ("endpoint stability", [
        "does not assert endpoint stability",
        "not endpoint stability",
        "not endpoint evidence",
        "does not say that public endpoints are unchanged",
    ]),
]

REQUIRED_OUTPUT_CAVEAT_FRAGMENTS = [
    "Local no-fetch gate validation",
    "not endpoint stability evidence",
    "legal compliance",
    "trusted-list legal effect",
    "signature validation",
    "public alerting",
    "regulated trust-service output",
    "legal review",
    "warning clearance",
    "publication approval",
]

FORBIDDEN_PAPER_FRAGMENTS = [
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees endpoint stability",
    "clears warnings",
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
    no_fetch_path = workspace / NO_FETCH_OUTPUT
    artifact_index_path = workspace / ARTIFACT_INDEX

    paper = paper_path.read_text(encoding="utf-8") if paper_path.exists() else ""
    no_fetch = json.loads(no_fetch_path.read_text(encoding="utf-8")) if no_fetch_path.exists() else {}
    artifact_index = artifact_index_path.read_text(encoding="utf-8") if artifact_index_path.exists() else ""

    if not paper:
        errors.append(f"missing paper: {PAPER}")
    if not no_fetch:
        errors.append(f"missing no-fetch gate output: {NO_FETCH_OUTPUT}")
    if not artifact_index:
        errors.append(f"missing artifact index: {ARTIFACT_INDEX}")

    paper_lower = paper.lower()
    missing_paper = [fragment for fragment in REQUIRED_PAPER_FRAGMENTS if fragment.lower() not in paper_lower]
    for label, variants in EQUIVALENT_PAPER_FRAGMENT_GROUPS:
        if not any(variant.lower() in paper_lower for variant in variants):
            missing_paper.append(label)
    if missing_paper:
        errors.append(f"paper lacks no-fetch gate reference/caveat fragments: {missing_paper}")
    forbidden_hits = [fragment for fragment in FORBIDDEN_PAPER_FRAGMENTS if fragment in paper_lower]
    if forbidden_hits:
        errors.append(f"paper contains forbidden no-fetch overclaiming fragments: {forbidden_hits}")

    if no_fetch:
        if no_fetch.get("status") != "ok" or no_fetch.get("error_count") != 0:
            errors.append(f"no-fetch output is not ok: status={no_fetch.get('status')} error_count={no_fetch.get('error_count')}")
        if no_fetch.get("snapshot_output_roots_mutated"):
            errors.append("no-fetch output reports snapshot output root mutation")
        today_guard = no_fetch.get("today_guard", {})
        if today_guard.get("status") != "refused_existing_outputs":
            errors.append(f"today guard is not refusing existing outputs: {today_guard.get('status')}")
        next_guard = no_fetch.get("next_eligible_guard", {})
        if next_guard.get("status") not in {"dry_run_ok", "refused_existing_outputs"}:
            errors.append(f"next eligible guard has unexpected status: {next_guard.get('status')}")
        cadence_report = no_fetch.get("cadence_report", {})
        if cadence_report.get("path") != "notes/daily-cadence-status-output.json":
            errors.append("no-fetch output is not linked to the daily-cadence status report")
        if not cadence_report.get("next_eligible_date"):
            errors.append("no-fetch output lacks next_eligible_date in cadence_report")
        caveat = no_fetch.get("research_caveat", "")
        missing_caveat = [fragment for fragment in REQUIRED_OUTPUT_CAVEAT_FRAGMENTS if fragment not in caveat]
        if missing_caveat:
            errors.append(f"no-fetch research caveat lacks required fragments: {missing_caveat}")
        if no_fetch.get("warning_count", 0):
            warnings.append(
                f"{NO_FETCH_OUTPUT} has warning_count={no_fetch.get('warning_count')}; preserve as workflow context"
            )

    current_hash = sha256_path(no_fetch_path) if no_fetch_path.exists() else None
    indexed_hashes = artifact_index_hashes(artifact_index, str(NO_FETCH_OUTPUT)) if artifact_index else []
    current_hash_indexed = bool(current_hash and current_hash in indexed_hashes)
    if not current_hash_indexed:
        errors.append(f"ARTIFACT_INDEX.md lacks current sha256 for {NO_FETCH_OUTPUT}")
    if len(indexed_hashes) > 1:
        warnings.append(
            f"ARTIFACT_INDEX.md has {len(indexed_hashes)} rows for {NO_FETCH_OUTPUT}; require at least one current row and preserve duplicates as maintenance context"
        )

    return {
        "schema": "urn:tyche:cassandra:no-fetch-gate-reference-freshness-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "paper": str(PAPER),
        "paper_sha256": sha256_path(paper_path) if paper_path.exists() else None,
        "no_fetch_output": str(NO_FETCH_OUTPUT),
        "no_fetch_output_sha256": current_hash,
        "no_fetch_status": no_fetch.get("status") if no_fetch else None,
        "no_fetch_warning_count": no_fetch.get("warning_count") if no_fetch else None,
        "live_today_utc": no_fetch.get("live_today_utc") if no_fetch else None,
        "latest_completed_date": no_fetch.get("cadence_report", {}).get("latest_completed_date") if no_fetch else None,
        "next_eligible_date": no_fetch.get("cadence_report", {}).get("next_eligible_date") if no_fetch else None,
        "artifact_index_hashes_for_no_fetch_output": indexed_hashes,
        "current_hash_indexed": current_hash_indexed,
        "research_caveat": "Local no-fetch gate reference freshness validation only; verifies paper/reference/hash alignment for workflow scheduling telemetry, not endpoint stability, legal compliance, trusted-list legal effect, signature validation, supervision, listed-entity status evidence, public alerting, regulated trust-service output, warning clearance, legal review, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/no-fetch-gate-reference-freshness-validation-output.json")
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
