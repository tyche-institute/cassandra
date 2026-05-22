#!/usr/bin/env python3
"""Validate the out-of-band policy for release-readiness context consistency.

This is workflow-maintenance telemetry only. It verifies that the local policy
note explains why the context-consistency validator remains outside the topology
report and release-readiness checklist dependency graph. It does not clear
warnings, approve publication, perform legal review, validate signatures,
supervise trusted lists, determine listed-entity status, provide public alerting,
assert trusted-list legal effect, or create regulated trust-service output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

POLICY_REL = pathlib.Path("notes/release-readiness-context-consistency-policy.md")
CHECKER_OUTPUT_REL = pathlib.Path("notes/release-readiness-context-consistency-validation-output.json")
CHECKLIST_VALIDATOR_REL = pathlib.Path("notes/validate_release_readiness_checklist.py")
TOPOLOGY_HELPER_REL = pathlib.Path("notes/report_release_readiness_topology.py")
TOPOLOGY_OUTPUT_REL = pathlib.Path("notes/release-readiness-topology-report-output.json")
WARNING_REPORT_REL = pathlib.Path("notes/release-readiness-warning-report-output.json")
GATE_SUMMARY_REL = pathlib.Path("notes/release-readiness-gate-summary-output.json")
STATUS_ONLY_REL = pathlib.Path("notes/status-only-release-gates-report-output.json")

REQUIRED_POLICY_FRAGMENTS = [
    "remains an out-of-band operator-review check",
    "intentionally not added to `notes/report_release_readiness_topology.py`",
    "intentionally not added to `notes/validate_release_readiness_checklist.py`",
    "topology/context-consistency loop",
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
    "release_readiness_context_consistency",
    "release-readiness-context-consistency-validation-output.json",
    "release-readiness-context-consistency-policy",
]

FORBIDDEN_TOPOLOGY_SOURCE_FRAGMENTS = [
    "release-readiness-context-consistency-validation-output.json",
    "release_readiness_context_consistency",
    "context_consistency_policy",
]

REQUIRED_CAVEAT_FRAGMENTS = [
    "not legal compliance",
    "trusted-list legal effect",
    "signature validation",
    "supervision",
    "public alerting",
    "regulated trust-service output",
    "publication approval",
]


def sha256_path(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def status_errors(label: str, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    # Deliberately do not turn transient upstream status/error_count values into
    # policy-validation errors: this validator is the out-of-band source that the
    # warning/gate/context outputs cite, so hard-failing on stale upstream outputs
    # can create a refresh cycle. Upstream status and error counts remain recorded
    # under inputs; this function only enforces safety flags and caveat wording.
    if data.get("safe_to_auto_clear_warnings") is not False:
        errors.append(f"{label} does not refuse automatic warning clearance")
    if data.get("safe_to_auto_publish") is not False:
        errors.append(f"{label} does not refuse automatic publication")
    caveat = str(data.get("research_caveat", "")).lower()
    for fragment in REQUIRED_CAVEAT_FRAGMENTS:
        if fragment not in caveat:
            errors.append(f"{label} research caveat lacks fragment: {fragment}")
    return errors


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    paths = {
        "policy_note": workspace / POLICY_REL,
        "checker_output": workspace / CHECKER_OUTPUT_REL,
        "checklist_validator": workspace / CHECKLIST_VALIDATOR_REL,
        "topology_helper": workspace / TOPOLOGY_HELPER_REL,
        "topology_output": workspace / TOPOLOGY_OUTPUT_REL,
        "warning_report": workspace / WARNING_REPORT_REL,
        "gate_summary": workspace / GATE_SUMMARY_REL,
        "status_only_report": workspace / STATUS_ONLY_REL,
    }
    for label, path in paths.items():
        if not path.exists():
            errors.append(f"missing required input {label}: {path.relative_to(workspace)}")

    policy_text = paths["policy_note"].read_text(encoding="utf-8") if paths["policy_note"].exists() else ""
    for fragment in REQUIRED_POLICY_FRAGMENTS:
        if fragment not in policy_text:
            errors.append(f"policy note lacks required fragment: {fragment}")

    checklist_source = paths["checklist_validator"].read_text(encoding="utf-8") if paths["checklist_validator"].exists() else ""
    for fragment in FORBIDDEN_CHECKLIST_FRAGMENTS:
        if fragment in checklist_source:
            errors.append(f"context-consistency checker appears wired into release-readiness checklist: {fragment}")

    topology_source = paths["topology_helper"].read_text(encoding="utf-8") if paths["topology_helper"].exists() else ""
    for fragment in FORBIDDEN_TOPOLOGY_SOURCE_FRAGMENTS:
        if fragment in topology_source:
            errors.append(f"context-consistency checker appears wired into topology report helper: {fragment}")

    loaded: dict[str, dict[str, Any]] = {}
    for label in ["checker_output", "topology_output", "warning_report", "gate_summary", "status_only_report"]:
        path = paths[label]
        if path.exists():
            try:
                loaded[label] = load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"{label} is not valid JSON: {exc}")
                loaded[label] = {}
        else:
            loaded[label] = {}

    for label, data in loaded.items():
        errors.extend(status_errors(label, data))
        if isinstance(data.get("warning_count"), int) and data["warning_count"] > 0:
            warnings.append(f"{label} warning_count={data['warning_count']} preserved as manual-review context")

    checker = loaded.get("checker_output", {})
    checked = checker.get("checked_context") if isinstance(checker.get("checked_context"), dict) else {}
    if sorted(checked.get("out_of_band_names", [])) != [
        "status_only_report_reference_checker_policy",
        "topology_report_reference_freshness_policy",
    ]:
        errors.append("context-consistency output does not confirm the expected out-of-band names")
    if checker.get("operator_review_gate") is not True:
        errors.append("context-consistency output does not mark operator_review_gate true")
    if checker.get("safe_to_auto_clear_warnings") is not False:
        errors.append("context-consistency output does not refuse warning clearance")
    if checker.get("safe_to_auto_publish") is not False:
        errors.append("context-consistency output does not refuse publication")

    topology = loaded.get("topology_output", {})
    topology_names = set(topology.get("topology", {}).get("out_of_band_check_names", [])) if isinstance(topology.get("topology"), dict) else set()
    if "release_readiness_context_consistency" in topology_names:
        errors.append("topology output lists context-consistency as an out-of-band check despite this policy")

    return {
        "schema": "urn:tyche:cassandra:release-readiness-context-consistency-policy-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "inputs": {
            label: {
                "path": str(path.relative_to(workspace)),
                "sha256": sha256_path(path) if path.exists() else None,
                "status": loaded.get(label, {}).get("status") if label in loaded else None,
                "warning_count": loaded.get(label, {}).get("warning_count") if label in loaded else None,
            }
            for label, path in paths.items()
        },
        "decision": {
            "checker_kept_out_of_band": True,
            "safe_to_wire_into_checklist_without_operator_review": False,
            "safe_to_wire_into_topology_without_operator_review": False,
            "not_missing_provenance": True,
            "cycle_avoidance_reason": "The checker reads topology, warning-report, gate-summary, and status-only outputs; making topology or the release checklist depend on it would create topology/context-consistency or checklist/context refresh churn.",
        },
        "research_caveat": "Local release-readiness context-consistency policy validation only; it does not clear warnings, approve publication, perform legal review, and is not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/release-readiness-context-consistency-policy-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
