#!/usr/bin/env python3
"""Smoke test for the release-readiness gate summary helper."""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "summarize_release_readiness_gate.py"
OUTPUT = WORKSPACE / "notes" / "release-readiness-gate-summary-output.json"
SOURCES = [
    WORKSPACE / "notes" / "release-readiness-checklist-validation-output.json",
    WORKSPACE / "notes" / "release-readiness-warning-report-output.json",
    WORKSPACE / "notes" / "release-readiness-persistent-warning-policy-validation-output.json",
    WORKSPACE / "notes" / "status-only-report-reference-checker-policy-validation-output.json",
    WORKSPACE / "notes" / "topology-report-reference-freshness-policy-validation-output.json",
    WORKSPACE / "notes" / "release-readiness-context-consistency-policy-validation-output.json",
]

spec = importlib.util.spec_from_file_location("summarize_release_readiness_gate", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore[union-attr]

before = {path: module.sha256_path(path) for path in SOURCES}
result = module.summarize(WORKSPACE)
after = {path: module.sha256_path(path) for path in SOURCES}
assert before == after, {"before": before, "after": after}
assert result["schema"].endswith(":0.1"), result
assert result["status"] == "ok", result
assert result["error_count"] == 0, result
assert result["validator_count"] == 16, result
assert result["validator_status_counts"] == {"ok": 16}, result
assert result["warning_validator_count"] == 5, result
assert set(result["warning_validator_names"]) == {"public_artifact_safety", "paper_claim_safety", "paper_evidence_refs", "hash_cycle_policy_references", "status_only_release_gates_report"}, result
assert result["release_warning_count"] == 5, result
assert result["persistent_warning_class_count"] == len(result["persistent_warning_classes"]), result
assert set(result["aggregate_warning_class_counts"]) == set(result["persistent_warning_classes"]), result
assert result["out_of_band_policy_checks"] == [
    {
        "name": "status_only_report_reference_checker_policy",
        "path": "notes/status-only-report-reference-checker-policy-validation-output.json",
        "status": "ok",
        "warning_count": 1,
        "checker_kept_out_of_band": True,
        "safe_to_wire_into_checklist_without_operator_review": False,
        "safe_to_wire_into_topology_without_operator_review": None,
        "cycle_avoidance_reason": "The checker validates the report's embedded checklist hash; making the checklist depend on the checker would create checklist/report/checker freshness churn.",
    },
    {
        "name": "topology_report_reference_freshness_policy",
        "path": "notes/topology-report-reference-freshness-policy-validation-output.json",
        "status": "ok",
        "warning_count": 1,
        "checker_kept_out_of_band": True,
        "safe_to_wire_into_checklist_without_operator_review": False,
        "safe_to_wire_into_topology_without_operator_review": None,
        "cycle_avoidance_reason": "The checker validates a paper reference and current topology-report artifact-index hash; making the checklist depend on it would create checklist/topology/freshness churn.",
    },
    {
        "name": "release_readiness_context_consistency_policy",
        "path": "notes/release-readiness-context-consistency-policy-validation-output.json",
        "status": "ok",
        "warning_count": 3,
        "checker_kept_out_of_band": True,
        "safe_to_wire_into_checklist_without_operator_review": False,
        "safe_to_wire_into_topology_without_operator_review": False,
        "cycle_avoidance_reason": "The checker reads topology, warning-report, gate-summary, and status-only outputs; making topology or the release checklist depend on it would create topology/context-consistency or checklist/context refresh churn.",
    },
], result
assert result["safe_to_auto_clear_warnings"] is False, result
assert result["safe_to_auto_publish"] is False, result
assert result["operator_review_gate"] is True, result
assert "not legal compliance" in result["research_caveat"], result

completed = subprocess.run(
    [
        str(WORKSPACE / ".venv" / "bin" / "python"),
        str(SCRIPT),
        "--workspace",
        str(WORKSPACE),
        "--output",
        str(OUTPUT.relative_to(WORKSPACE)),
    ],
    cwd=WORKSPACE,
    check=True,
    text=True,
    capture_output=True,
)
cli_result = json.loads(completed.stdout)
assert cli_result["status"] == "ok", cli_result
assert OUTPUT.exists(), OUTPUT
print(json.dumps({"status": "ok", "validator_count": cli_result["validator_count"], "warning_classes": cli_result["aggregate_warning_class_counts"], "out_of_band_policy_checks": cli_result["out_of_band_policy_checks"], "output": str(OUTPUT.relative_to(WORKSPACE))}, indent=2, sort_keys=True))
