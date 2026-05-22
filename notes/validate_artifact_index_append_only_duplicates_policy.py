#!/usr/bin/env python3
"""Validate the append-only duplicate-row policy for ARTIFACT_INDEX.md.

This is local workflow-maintenance telemetry only. It confirms that duplicate
artifact-index rows are documented as append-only provenance when current-hash
validation is clean. It does not rewrite the index, clear warnings, approve
publication, perform legal review, validate signatures, supervise trusted lists,
determine listed-entity status, provide public alerting, or create regulated
trust-service output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

POLICY_REL = pathlib.Path("notes/artifact-index-append-only-duplicates-policy.md")
CURRENT_HASH_OUTPUT_REL = pathlib.Path("notes/artifact-index-current-hash-validation-output.json")
DUPLICATE_REPORT_REL = pathlib.Path("notes/artifact-index-duplicate-report-output.json")
DUPLICATE_REPORT_HELPER_REL = pathlib.Path("notes/report_artifact_index_duplicates.py")
DUPLICATE_PROPOSAL_HELPER_REL = pathlib.Path("notes/propose_artifact_index_duplicate_cleanup.py")

REQUIRED_POLICY_FRAGMENTS = [
    "append-only research ledger",
    "Duplicate rows for the same artifact path are expected",
    "at least one row for that path matches the artifact's current sha256",
    "Preserve historical duplicate rows",
    "Add a new row with the current sha256",
    "warning-context telemetry, not a hard failure",
    "proposal-only operator-review material",
    "neither helper should rewrite `ARTIFACT_INDEX.md`",
    "Do not wire duplicate-row cleanup into release-readiness gates",
    "does not assert endpoint stability",
    "legal effect",
    "signature validity",
    "supervision",
    "listed-entity status",
    "public alerting",
    "regulated trust-service output",
    "legal review",
    "warning clearance",
    "publication approval",
]

REQUIRED_CAVEAT_FRAGMENTS = [
    "legal effect",
    "signature",
    "supervise",
    "public alerting",
    "publication",
]


def sha256_path(path: pathlib.Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    inputs: dict[str, Any] = {}

    policy_path = workspace / POLICY_REL
    current_hash_path = workspace / CURRENT_HASH_OUTPUT_REL
    duplicate_report_path = workspace / DUPLICATE_REPORT_REL
    report_helper_path = workspace / DUPLICATE_REPORT_HELPER_REL
    proposal_helper_path = workspace / DUPLICATE_PROPOSAL_HELPER_REL

    for rel, path in [
        (POLICY_REL, policy_path),
        (CURRENT_HASH_OUTPUT_REL, current_hash_path),
        (DUPLICATE_REPORT_REL, duplicate_report_path),
        (DUPLICATE_REPORT_HELPER_REL, report_helper_path),
        (DUPLICATE_PROPOSAL_HELPER_REL, proposal_helper_path),
    ]:
        if not path.exists():
            errors.append(f"missing required input: {rel}")
        inputs[str(rel)] = {"path": str(rel), "sha256": sha256_path(path)}

    policy_text = policy_path.read_text(encoding="utf-8") if policy_path.exists() else ""
    for fragment in REQUIRED_POLICY_FRAGMENTS:
        if fragment not in policy_text:
            errors.append(f"policy note lacks required fragment: {fragment}")

    current_hash: dict[str, Any] = {}
    if current_hash_path.exists():
        try:
            current_hash = load_json(current_hash_path)
        except json.JSONDecodeError as exc:
            errors.append(f"current-hash validation output is not JSON: {exc}")
    if current_hash.get("status") != "ok":
        errors.append(f"current-hash validation status is not ok: {current_hash.get('status')}")
    if current_hash.get("missing_path_count") not in (0, None):
        errors.append(f"current-hash validation has missing paths: {current_hash.get('missing_path_count')}")
    if current_hash.get("stale_path_count") not in (0, None):
        errors.append(f"current-hash validation has stale paths: {current_hash.get('stale_path_count')}")
    duplicate_count = current_hash.get("duplicate_path_count")
    if isinstance(duplicate_count, int) and duplicate_count > 0:
        warnings.append(f"duplicate_path_count={duplicate_count} preserved as append-only ledger context")

    duplicate_report: dict[str, Any] = {}
    if duplicate_report_path.exists():
        try:
            duplicate_report = load_json(duplicate_report_path)
        except json.JSONDecodeError as exc:
            errors.append(f"duplicate report output is not JSON: {exc}")
    if duplicate_report and duplicate_report.get("mode") != "report_only_no_rewrite":
        errors.append(f"duplicate report mode is not report_only_no_rewrite: {duplicate_report.get('mode')}")
    caveat = str(duplicate_report.get("caveat", ""))
    if caveat:
        for fragment in REQUIRED_CAVEAT_FRAGMENTS:
            if fragment not in caveat:
                errors.append(f"duplicate report caveat lacks fragment: {fragment}")

    for rel, path in [
        (DUPLICATE_REPORT_HELPER_REL, report_helper_path),
        (DUPLICATE_PROPOSAL_HELPER_REL, proposal_helper_path),
    ]:
        source = path.read_text(encoding="utf-8") if path.exists() else ""
        if "does not" not in source or "rewrite" not in source:
            errors.append(f"helper lacks no-rewrite caveat: {rel}")
        if ".unlink(" in source:
            errors.append(f"helper contains unlink call despite no-cleanup policy: {rel}")

    return {
        "schema": "urn:tyche:cassandra:artifact-index-append-only-duplicates-policy-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "inputs": inputs,
        "decision": {
            "duplicate_rows_preserved": True,
            "requires_current_matching_hash_for_each_ordinary_artifact": True,
            "safe_to_auto_delete_duplicate_rows": False,
            "safe_to_wire_cleanup_into_release_gate_without_operator_review": False,
        },
        "research_caveat": "Local artifact-index append-only duplicate-row policy validation only; it does not assert endpoint stability, legal effect, signature validity, supervision, listed-entity status, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/artifact-index-append-only-duplicates-policy-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    output = pathlib.Path(args.output)
    if not output.is_absolute():
        output = workspace / output
    result = validate(workspace)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
