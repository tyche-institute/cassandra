#!/usr/bin/env python3
"""Validate the out-of-band policy for the status-only report reference checker.

This is workflow-maintenance telemetry only. It verifies that the local policy
note explains why the status-only report reference/freshness checker remains
outside the release-readiness checklist gate. It does not clear warnings,
approve publication, perform legal review, validate signatures, supervise
trusted lists, determine listed-entity status, provide public alerting, or create
regulated trust-service output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

POLICY_REL = pathlib.Path("notes/status-only-report-reference-checker-policy.md")
CHECKER_OUTPUT_REL = pathlib.Path("notes/status-only-release-gates-report-reference-validation-output.json")
CHECKLIST_VALIDATOR_REL = pathlib.Path("notes/validate_release_readiness_checklist.py")
STATUS_REPORT_REL = pathlib.Path("notes/status-only-release-gates-report-output.json")

REQUIRED_POLICY_FRAGMENTS = [
    "remains an out-of-band operator-review check",
    "intentionally not added to `notes/validate_release_readiness_checklist.py`",
    "checklist/report/checker freshness loop",
    "not missing provenance",
    "deliberate cycle avoidance",
    "does not clear warnings",
    "approve publication",
    "perform legal review",
    "validate signatures",
    "supervise trusted lists",
    "determine listed-entity status",
    "provide public alerting",
    "trusted-list legal effect",
    "regulated trust-service output",
]

FORBIDDEN_CHECKLIST_FRAGMENTS = [
    "status_only_release_gates_report_references",
    "status-only-release-gates-report-reference-validation-output.json",
]

REQUIRED_CAVEAT_FRAGMENTS = [
    "does not clear warnings",
    "approve publication",
    "legal review",
    "validate signatures",
    "supervise trusted lists",
    "determine listed-entity status",
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
    return json.loads(path.read_text(encoding="utf-8"))


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    policy_path = workspace / POLICY_REL
    checker_output_path = workspace / CHECKER_OUTPUT_REL
    checklist_validator_path = workspace / CHECKLIST_VALIDATOR_REL
    status_report_path = workspace / STATUS_REPORT_REL

    for rel, path in [
        (POLICY_REL, policy_path),
        (CHECKER_OUTPUT_REL, checker_output_path),
        (CHECKLIST_VALIDATOR_REL, checklist_validator_path),
        (STATUS_REPORT_REL, status_report_path),
    ]:
        if not path.exists():
            errors.append(f"missing required input: {rel}")

    policy_text = policy_path.read_text(encoding="utf-8") if policy_path.exists() else ""
    for fragment in REQUIRED_POLICY_FRAGMENTS:
        if fragment not in policy_text:
            errors.append(f"policy note lacks required fragment: {fragment}")

    checklist_source = checklist_validator_path.read_text(encoding="utf-8") if checklist_validator_path.exists() else ""
    for fragment in FORBIDDEN_CHECKLIST_FRAGMENTS:
        if fragment in checklist_source:
            errors.append(f"checker appears wired into release-readiness checklist despite out-of-band policy: {fragment}")

    checker: dict[str, Any] = {}
    if checker_output_path.exists():
        try:
            checker = load_json(checker_output_path)
        except json.JSONDecodeError as exc:
            errors.append(f"checker output is not JSON: {exc}")
    if checker.get("status") != "ok":
        errors.append(f"checker output status is not ok: {checker.get('status')}")
    if checker.get("error_count") not in (0, None):
        errors.append(f"checker output error_count is nonzero: {checker.get('error_count')}")
    reference_check = checker.get("reference_check") if isinstance(checker.get("reference_check"), dict) else {}
    if reference_check.get("manual_review_only") is not True:
        errors.append("checker output does not mark manual_review_only true")
    if reference_check.get("safe_to_clear_warnings") is not False:
        errors.append("checker output does not refuse warning clearance")
    if reference_check.get("safe_to_publish") is not False:
        errors.append("checker output does not refuse publication")
    hash_cycle_note = str(reference_check.get("hash_cycle_note", ""))
    if "deliberately remains outside the release-readiness checklist" not in hash_cycle_note:
        errors.append("checker hash_cycle_note no longer states it remains outside the checklist")
    caveat = str(checker.get("research_caveat", ""))
    for fragment in REQUIRED_CAVEAT_FRAGMENTS:
        if fragment not in caveat:
            errors.append(f"checker research caveat lacks fragment: {fragment}")
    if isinstance(checker.get("warning_count"), int) and checker["warning_count"] > 0:
        warnings.append(f"checker output retains warning_count={checker['warning_count']} as manual-review context")

    status_report: dict[str, Any] = {}
    if status_report_path.exists():
        try:
            status_report = load_json(status_report_path)
        except json.JSONDecodeError as exc:
            errors.append(f"status-only report output is not JSON: {exc}")
    if status_report.get("status") != "ok":
        errors.append(f"status-only report status is not ok: {status_report.get('status')}")
    if status_report.get("safe_to_auto_clear_warnings") is not False:
        errors.append("status-only report does not refuse automatic warning clearance")
    if status_report.get("safe_to_auto_publish") is not False:
        errors.append("status-only report does not refuse automatic publication")
    if status_report.get("status_only_gate_count") != 3:
        errors.append(f"unexpected status-only gate count; out-of-band checker policy expects 3 checklist gates: {status_report.get('status_only_gate_count')}")

    return {
        "schema": "urn:tyche:cassandra:status-only-report-reference-checker-policy-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "inputs": {
            "policy_note": {"path": str(POLICY_REL), "sha256": sha256_path(policy_path) if policy_path.exists() else None},
            "checker_output": {"path": str(CHECKER_OUTPUT_REL), "sha256": sha256_path(checker_output_path) if checker_output_path.exists() else None, "status": checker.get("status"), "warning_count": checker.get("warning_count")},
            "release_readiness_checklist_validator": {"path": str(CHECKLIST_VALIDATOR_REL), "sha256": sha256_path(checklist_validator_path) if checklist_validator_path.exists() else None},
            "status_only_release_gate_report": {"path": str(STATUS_REPORT_REL), "sha256": sha256_path(status_report_path) if status_report_path.exists() else None, "status_only_gate_count": status_report.get("status_only_gate_count")},
        },
        "decision": {
            "checker_kept_out_of_band": True,
            "safe_to_wire_into_checklist_without_operator_review": False,
            "not_missing_provenance": True,
            "cycle_avoidance_reason": "The checker validates the report's embedded checklist hash; making the checklist depend on the checker would create checklist/report/checker freshness churn.",
        },
        "research_caveat": "Local status-only report reference-checker policy validation only; it does not clear warnings, approve publication, perform legal review, validate signatures, supervise trusted lists, determine listed-entity status, provide public alerting, assert trusted-list legal effect, or create regulated trust-service output.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/status-only-report-reference-checker-policy-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
