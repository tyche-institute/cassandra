#!/usr/bin/env python3
"""Validate the out-of-band policy for topology-report reference freshness.

This is workflow-maintenance telemetry only. It verifies that the local policy
note explains why the topology-report reference freshness checker remains
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

POLICY_REL = pathlib.Path("notes/topology-report-reference-freshness-policy.md")
CHECKER_OUTPUT_REL = pathlib.Path("notes/topology-report-reference-freshness-validation-output.json")
CHECKLIST_VALIDATOR_REL = pathlib.Path("notes/validate_release_readiness_checklist.py")
TOPOLOGY_REPORT_REL = pathlib.Path("notes/release-readiness-topology-report-output.json")
PAPER_REL = pathlib.Path("paper/draft.md")

REQUIRED_POLICY_FRAGMENTS = [
    "remains an out-of-band operator-review check",
    "intentionally not added to `notes/validate_release_readiness_checklist.py`",
    "checklist/topology/freshness loop",
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
    "topology_report_reference_freshness",
    "topology-report-reference-freshness-validation-output.json",
]

REQUIRED_CAVEAT_FRAGMENTS = [
    "not legal compliance",
    "trusted-list legal effect",
    "signature validation",
    "supervision",
    "public alerting",
    "regulated trust-service output",
    "legal review",
    "warning clearance",
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


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    policy_path = workspace / POLICY_REL
    checker_output_path = workspace / CHECKER_OUTPUT_REL
    checklist_validator_path = workspace / CHECKLIST_VALIDATOR_REL
    topology_report_path = workspace / TOPOLOGY_REPORT_REL
    paper_path = workspace / PAPER_REL

    for rel, path in [
        (POLICY_REL, policy_path),
        (CHECKER_OUTPUT_REL, checker_output_path),
        (CHECKLIST_VALIDATOR_REL, checklist_validator_path),
        (TOPOLOGY_REPORT_REL, topology_report_path),
        (PAPER_REL, paper_path),
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
            errors.append(f"topology freshness checker appears wired into release-readiness checklist despite out-of-band policy: {fragment}")

    paper_text = paper_path.read_text(encoding="utf-8") if paper_path.exists() else ""
    if str(TOPOLOGY_REPORT_REL) not in paper_text:
        errors.append("paper no longer references the release-readiness topology report")

    checker: dict[str, Any] = {}
    if checker_output_path.exists():
        try:
            checker = load_json(checker_output_path)
        except json.JSONDecodeError as exc:
            errors.append(f"topology freshness checker output is not JSON: {exc}")
    if checker.get("status") != "ok":
        errors.append(f"topology freshness checker status is not ok: {checker.get('status')}")
    if checker.get("error_count") not in (0, None):
        errors.append(f"topology freshness checker error_count is nonzero: {checker.get('error_count')}")
    if checker.get("operator_review_gate") is not True:
        errors.append("topology freshness checker does not mark operator_review_gate true")
    if checker.get("safe_to_auto_clear_warnings") is not False:
        errors.append("topology freshness checker does not refuse warning clearance")
    if checker.get("safe_to_auto_publish") is not False:
        errors.append("topology freshness checker does not refuse publication")
    caveat = str(checker.get("research_caveat", ""))
    for fragment in REQUIRED_CAVEAT_FRAGMENTS:
        if fragment not in caveat:
            errors.append(f"topology freshness checker research caveat lacks fragment: {fragment}")
    artifact_index = checker.get("artifact_index") if isinstance(checker.get("artifact_index"), dict) else {}
    if artifact_index.get("current_hash_indexed") is not True:
        errors.append("topology freshness checker does not confirm current topology-report hash is indexed")
    if isinstance(checker.get("warning_count"), int) and checker["warning_count"] > 0:
        warnings.append(f"topology freshness checker retains warning_count={checker['warning_count']} as manual-review context")

    topology: dict[str, Any] = {}
    if topology_report_path.exists():
        try:
            topology = load_json(topology_report_path)
        except json.JSONDecodeError as exc:
            errors.append(f"topology report output is not JSON: {exc}")
    if topology.get("status") != "ok":
        errors.append(f"topology report status is not ok: {topology.get('status')}")
    if topology.get("safe_to_auto_clear_warnings") is not False:
        errors.append("topology report does not refuse automatic warning clearance")
    if topology.get("safe_to_auto_publish") is not False:
        errors.append("topology report does not refuse automatic publication")

    return {
        "schema": "urn:tyche:cassandra:topology-reference-freshness-policy-validation:0.1",
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
            "topology_report": {"path": str(TOPOLOGY_REPORT_REL), "sha256": sha256_path(topology_report_path) if topology_report_path.exists() else None, "status": topology.get("status")},
            "paper": {"path": str(PAPER_REL), "sha256": sha256_path(paper_path) if paper_path.exists() else None},
        },
        "decision": {
            "checker_kept_out_of_band": True,
            "safe_to_wire_into_checklist_without_operator_review": False,
            "not_missing_provenance": True,
            "cycle_avoidance_reason": "The checker validates a paper reference and current topology-report artifact-index hash; making the checklist depend on it would create checklist/topology/freshness churn.",
        },
        "research_caveat": "Local topology-report reference freshness policy validation only; it does not clear warnings, approve publication, perform legal review, validate signatures, supervise trusted lists, determine listed-entity status, provide public alerting, assert trusted-list legal effect, or create regulated trust-service output.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/topology-report-reference-freshness-policy-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
