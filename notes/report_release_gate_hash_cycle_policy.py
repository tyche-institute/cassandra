#!/usr/bin/env python3
"""Explain Cassandra's release-checklist/gate-summary hash-cycle policy.

This report is local workflow-maintenance telemetry. It explains why the
release gate-summary freshness validator is status-only in the release-readiness
checklist records: hashing that freshness output inside the checklist would
create a needless checklist/summary freshness hash-churn cycle. The report does
not clear warnings, approve publication, perform legal review, validate
trusted-list signatures, supervise trusted lists, determine listed-entity status,
provide public alerting, or create regulated trust-service output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

CHECKLIST_REL = "notes/release-readiness-checklist-validation-output.json"
SUMMARY_REL = "notes/release-readiness-gate-summary-output.json"
FRESHNESS_REL = "notes/release-gate-summary-freshness-validation-output.json"
CHECKLIST_VALIDATOR_REL = "notes/validate_release_readiness_checklist.py"
STATUS_ONLY_POLICY = "status_only_to_avoid_release_checklist_gate_summary_hash_cycle"

REQUIRED_CAVEAT_FRAGMENTS = [
    "not publication approval",
    "legal review",
    "signature validation",
    "trusted-list supervision",
    "listed-entity status",
    "public alerting",
    "regulated trust-service output",
]


def sha256_path(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def caveat_errors(label: str, caveat: str | None) -> list[str]:
    if not caveat:
        return [f"{label} lacks research_caveat"]
    lower = caveat.lower()
    return [
        f"{label} caveat lacks required fragment: {fragment}"
        for fragment in REQUIRED_CAVEAT_FRAGMENTS
        if fragment not in lower
    ]


def find_validator(checklist: dict[str, Any], name: str) -> dict[str, Any] | None:
    validators = checklist.get("validators", [])
    if not isinstance(validators, list):
        return None
    for record in validators:
        if isinstance(record, dict) and record.get("name") == name:
            return record
    return None


def report(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    checklist_path = workspace / CHECKLIST_REL
    summary_path = workspace / SUMMARY_REL
    freshness_path = workspace / FRESHNESS_REL
    validator_path = workspace / CHECKLIST_VALIDATOR_REL

    checklist = load_json(checklist_path)
    summary = load_json(summary_path)
    freshness = load_json(freshness_path)

    freshness_record = find_validator(checklist, "release_gate_summary_freshness")
    if freshness_record is None:
        errors.append("release_gate_summary_freshness record is absent from checklist validators")
        freshness_record = {}

    if freshness_record.get("status") != "ok":
        errors.append(f"freshness validator checklist status is not ok: {freshness_record.get('status')}")
    if freshness_record.get("hash_policy") != STATUS_ONLY_POLICY:
        errors.append("freshness validator checklist record lacks expected status-only hash policy")
    if "sha256" in freshness_record:
        errors.append("freshness validator checklist record unexpectedly contains sha256")

    if checklist.get("status") != "ok":
        errors.append(f"checklist status is not ok: {checklist.get('status')}")
    if summary.get("status") != "ok":
        errors.append(f"gate summary status is not ok: {summary.get('status')}")
    if freshness.get("status") != "ok":
        errors.append(f"freshness validation status is not ok: {freshness.get('status')}")

    source_checks = freshness.get("source_checks", {})
    checklist_source = source_checks.get("release_readiness_checklist", {}) if isinstance(source_checks, dict) else {}
    if checklist_source.get("matches_current_hash") is not True:
        errors.append("freshness output does not confirm current checklist hash")
    if checklist_source.get("current_sha256") != sha256_path(checklist_path):
        errors.append("freshness output current checklist hash does not match live checklist file")

    summary_sources = summary.get("sources", {})
    summary_checklist_source = summary_sources.get("release_readiness_checklist", {}) if isinstance(summary_sources, dict) else {}
    if summary_checklist_source.get("sha256") != sha256_path(checklist_path):
        errors.append("gate summary embedded checklist hash does not match live checklist file")

    errors.extend(caveat_errors("freshness", freshness.get("research_caveat")))

    if "STATUS_ONLY_OUTPUTS" not in validator_path.read_text(encoding="utf-8"):
        errors.append("checklist validator source lacks STATUS_ONLY_OUTPUTS marker")
    if STATUS_ONLY_POLICY not in validator_path.read_text(encoding="utf-8"):
        warnings.append("checklist validator source lacks literal status-only policy string; output record still checked")

    return {
        "schema": "urn:tyche:cassandra:release-gate-hash-cycle-policy-report:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "policy": {
            "status_only_validator": "release_gate_summary_freshness",
            "status_only_path": FRESHNESS_REL,
            "hash_policy": STATUS_ONLY_POLICY,
            "reason": "The freshness validator checks the release-readiness checklist output as an upstream of the gate-summary output. Recording the freshness-output sha256 inside the checklist would create a recurring checklist/summary/freshness hash-churn cycle. Cassandra therefore requires the freshness validator status to be ok while deliberately omitting its sha256 from the checklist record.",
            "not_missing_provenance": True,
            "operator_review_note": "The status-only record is an explicit cycle-avoidance policy, not an accidental missing hash, warning clearance, legal review, or publication approval.",
        },
        "inputs": {
            "release_readiness_checklist": {
                "path": CHECKLIST_REL,
                "sha256": sha256_path(checklist_path),
                "status": checklist.get("status"),
                "validator_count": checklist.get("validator_count"),
                "warning_count": checklist.get("warning_count"),
            },
            "release_gate_summary": {
                "path": SUMMARY_REL,
                "sha256": sha256_path(summary_path),
                "status": summary.get("status"),
                "validator_count": summary.get("validator_count"),
            },
            "release_gate_summary_freshness": {
                "path": FRESHNESS_REL,
                "sha256": sha256_path(freshness_path),
                "status": freshness.get("status"),
                "checklist_record_hash_policy": freshness_record.get("hash_policy"),
                "checklist_record_has_sha256": "sha256" in freshness_record,
            },
            "checklist_validator_source": {
                "path": CHECKLIST_VALIDATOR_REL,
                "sha256": sha256_path(validator_path),
            },
        },
        "research_caveat": "Local hash-cycle policy report only; it is not publication approval, legal review, signature validation, trusted-list supervision, listed-entity status evidence, public alerting, or regulated trust-service output.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/release-gate-hash-cycle-policy-report-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = report(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
