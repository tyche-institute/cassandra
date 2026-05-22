#!/usr/bin/env python3
"""Validate hash-cycle policy references in Cassandra release-readiness gates.

This checker is local workflow-maintenance telemetry. It verifies that the
release gate hash-cycle policy report stays referenced by both the paper
operator-review checklist and the release-readiness checklist validator source.
It does not clear warnings, approve publication, perform legal review, validate
trusted-list signatures, supervise trusted lists, determine listed-entity status,
provide public alerting, or create regulated trust-service output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

PAPER_REL = pathlib.Path("paper/draft.md")
CHECKLIST_VALIDATOR_REL = pathlib.Path("notes/validate_release_readiness_checklist.py")
POLICY_REPORT_REL = pathlib.Path("notes/release-gate-hash-cycle-policy-report-output.json")
CHECKLIST_OUTPUT_REL = pathlib.Path("notes/release-readiness-checklist-validation-output.json")
CHECKLIST_HEADING = "## Release-readiness checklist for operator review"

PAPER_REQUIRED_FRAGMENTS = [
    "release gate hash-cycle policy report",
    "notes/release-gate-hash-cycle-policy-report-output.json",
    "status-only inside the checklist",
    "not as missing-hash repair",
    "warning clearance",
    "publication approval",
    "legal review",
    "signature validation",
    "trusted-list supervision",
    "listed-entity status evidence",
    "public alerting",
    "regulated trust-service output",
]

VALIDATOR_REQUIRED_FRAGMENTS = [
    "release gate hash-cycle policy report",
    "notes/release-gate-hash-cycle-policy-report-output.json",
    "status-only inside the checklist",
    "not as missing-hash repair",
]

POLICY_REPORT_REQUIRED = {
    "status": "ok",
    "policy.not_missing_provenance": True,
}


def sha256_path(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^{re.escape(heading)}\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(0) if match else ""


def nested_get(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def status_from_json(data: dict[str, Any]) -> str | None:
    if isinstance(data.get("status"), str):
        return data["status"]
    if isinstance(data.get("result"), dict) and isinstance(data["result"].get("status"), str):
        return data["result"]["status"]
    return None


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    paper_path = workspace / PAPER_REL
    validator_path = workspace / CHECKLIST_VALIDATOR_REL
    policy_report_path = workspace / POLICY_REPORT_REL
    checklist_output_path = workspace / CHECKLIST_OUTPUT_REL

    for rel, path in [
        (PAPER_REL, paper_path),
        (CHECKLIST_VALIDATOR_REL, validator_path),
        (POLICY_REPORT_REL, policy_report_path),
        (CHECKLIST_OUTPUT_REL, checklist_output_path),
    ]:
        if not path.exists():
            errors.append(f"missing required input: {rel}")

    paper_text = paper_path.read_text(encoding="utf-8") if paper_path.exists() else ""
    validator_text = validator_path.read_text(encoding="utf-8") if validator_path.exists() else ""
    checklist = section(paper_text, CHECKLIST_HEADING)
    if not checklist:
        errors.append("paper lacks release-readiness checklist section")
    for fragment in PAPER_REQUIRED_FRAGMENTS:
        if fragment not in checklist:
            errors.append(f"paper checklist lacks hash-cycle policy fragment: {fragment}")

    for fragment in VALIDATOR_REQUIRED_FRAGMENTS:
        if fragment not in validator_text:
            errors.append(f"release-readiness checklist validator source lacks policy fragment: {fragment}")

    policy_report: dict[str, Any] = {}
    if policy_report_path.exists():
        try:
            policy_report = load_json(policy_report_path)
        except json.JSONDecodeError as exc:
            errors.append(f"policy report is not JSON: {exc}")
    for dotted, expected in POLICY_REPORT_REQUIRED.items():
        actual = nested_get(policy_report, dotted)
        if actual != expected:
            errors.append(f"policy report {dotted} is {actual!r}, expected {expected!r}")
    report_caveat = str(policy_report.get("research_caveat", ""))
    for fragment in [
        "not publication approval",
        "legal review",
        "signature validation",
        "trusted-list supervision",
        "listed-entity status evidence",
        "public alerting",
        "regulated trust-service output",
    ]:
        if fragment not in report_caveat.lower():
            errors.append(f"policy report caveat lacks fragment: {fragment}")

    checklist_output: dict[str, Any] = {}
    if checklist_output_path.exists():
        try:
            checklist_output = load_json(checklist_output_path)
        except json.JSONDecodeError as exc:
            errors.append(f"release-readiness checklist output is not JSON: {exc}")
    checklist_status = status_from_json(checklist_output)
    if checklist_status != "ok":
        errors.append(f"release-readiness checklist output status is not ok: {checklist_status}")
    if isinstance(checklist_output.get("warning_count"), int) and checklist_output["warning_count"] > 0:
        warnings.append(
            f"release-readiness checklist retains warning_count={checklist_output['warning_count']} as manual-review context"
        )

    return {
        "schema": "urn:tyche:cassandra:hash-cycle-policy-reference-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "inputs": {
            "paper": {"path": str(PAPER_REL), "sha256": sha256_path(paper_path) if paper_path.exists() else None},
            "release_readiness_checklist_validator": {
                "path": str(CHECKLIST_VALIDATOR_REL),
                "sha256": sha256_path(validator_path) if validator_path.exists() else None,
            },
            "hash_cycle_policy_report": {
                "path": str(POLICY_REPORT_REL),
                "sha256": sha256_path(policy_report_path) if policy_report_path.exists() else None,
                "status": policy_report.get("status"),
                "not_missing_provenance": nested_get(policy_report, "policy.not_missing_provenance"),
            },
            "release_readiness_checklist_output": {
                "path": str(CHECKLIST_OUTPUT_REL),
                "sha256": sha256_path(checklist_output_path) if checklist_output_path.exists() else None,
                "status": checklist_status,
                "warning_count": checklist_output.get("warning_count"),
            },
        },
        "policy_reference_check": {
            "paper_section": CHECKLIST_HEADING,
            "paper_required_fragment_count": len(PAPER_REQUIRED_FRAGMENTS),
            "validator_required_fragment_count": len(VALIDATOR_REQUIRED_FRAGMENTS),
            "manual_review_only": True,
            "safe_to_clear_warnings": False,
            "safe_to_publish": False,
        },
        "research_caveat": "Local hash-cycle policy reference validation only; it does not clear warnings, approve publication, perform legal review, validate signatures, supervise trusted lists, determine listed-entity status, provide public alerting, or create regulated trust-service output.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/hash-cycle-policy-reference-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
