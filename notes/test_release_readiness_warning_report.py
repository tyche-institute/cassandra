#!/usr/bin/env python3
"""Smoke test for release-readiness warning report helper."""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "report_release_readiness_warnings.py"
OUTPUT = WORKSPACE / "notes" / "release-readiness-warning-report-output.json"
SOURCES = [
    WORKSPACE / "notes" / "release-readiness-checklist-validation-output.json",
    WORKSPACE / "notes" / "public-artifact-safety-validation-output.json",
    WORKSPACE / "notes" / "paper-claim-safety-validation-output.json",
    WORKSPACE / "notes" / "paper-evidence-reference-validation-output.json",
    WORKSPACE / "notes" / "hash-cycle-policy-reference-validation-output.json",
    WORKSPACE / "notes" / "status-only-release-gates-report-output.json",
    WORKSPACE / "notes" / "status-only-report-reference-checker-policy-validation-output.json",
    WORKSPACE / "notes" / "topology-report-reference-freshness-policy-validation-output.json",
    WORKSPACE / "notes" / "release-readiness-context-consistency-policy-validation-output.json",
]

spec = importlib.util.spec_from_file_location("report_release_readiness_warnings", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore[union-attr]

before = {path: module.sha256_path(path) for path in SOURCES}
result = module.report(WORKSPACE, Path("notes/release-readiness-checklist-validation-output.json"))
after = {path: module.sha256_path(path) for path in SOURCES}
assert before == after, {"before": before, "after": after}
assert result["schema"].endswith(":0.1"), result
assert result["status"] == "ok", result
assert result["error_count"] == 0, result
assert result["release_warning_count"] == 5, result
assert result["warning_validator_count"] == 5, result
assert result["safe_to_auto_clear_warnings"] is False, result
assert result["safe_to_auto_publish"] is False, result
assert "not legal compliance" in result["research_caveat"], result
assert result["out_of_band_warning_context"] == [
    {
        "name": "status_only_report_reference_checker_policy",
        "path": "notes/status-only-report-reference-checker-policy-validation-output.json",
        "sha256": module.sha256_path(WORKSPACE / "notes" / "status-only-report-reference-checker-policy-validation-output.json"),
        "status": "ok",
        "error_count": 0,
        "warning_count": 1,
        "warnings": ["checker output retains warning_count=1 as manual-review context"],
        "checker_kept_out_of_band": True,
        "safe_to_wire_into_checklist_without_operator_review": False,
        "safe_to_wire_into_topology_without_operator_review": None,
        "cycle_avoidance_reason": "The checker validates the report's embedded checklist hash; making the checklist depend on the checker would create checklist/report/checker freshness churn.",
        "counted_in_release_warning_count": False,
    },
    {
        "name": "topology_report_reference_freshness_policy",
        "path": "notes/topology-report-reference-freshness-policy-validation-output.json",
        "sha256": module.sha256_path(WORKSPACE / "notes" / "topology-report-reference-freshness-policy-validation-output.json"),
        "status": "ok",
        "error_count": 0,
        "warning_count": 1,
        "warnings": ["topology freshness checker retains warning_count=2 as manual-review context"],
        "checker_kept_out_of_band": True,
        "safe_to_wire_into_checklist_without_operator_review": False,
        "safe_to_wire_into_topology_without_operator_review": None,
        "cycle_avoidance_reason": "The checker validates a paper reference and current topology-report artifact-index hash; making the checklist depend on it would create checklist/topology/freshness churn.",
        "counted_in_release_warning_count": False,
    },
    {
        "name": "release_readiness_context_consistency_policy",
        "path": "notes/release-readiness-context-consistency-policy-validation-output.json",
        "sha256": module.sha256_path(WORKSPACE / "notes" / "release-readiness-context-consistency-policy-validation-output.json"),
        "status": "ok",
        "error_count": 0,
        "warning_count": 3,
        "warnings": [
            "checker_output warning_count=2 preserved as manual-review context",
            "topology_output warning_count=4 preserved as manual-review context",
            "status_only_report warning_count=2 preserved as manual-review context",
        ],
        "checker_kept_out_of_band": True,
        "safe_to_wire_into_checklist_without_operator_review": False,
        "safe_to_wire_into_topology_without_operator_review": False,
        "cycle_avoidance_reason": "The checker reads topology, warning-report, gate-summary, and status-only outputs; making topology or the release checklist depend on it would create topology/context-consistency or checklist/context refresh churn.",
        "counted_in_release_warning_count": False,
    },
], result
classes = result["aggregate_warning_class_counts"]
assert classes.get("caveated_public_alerting_phrase") == 1, classes
assert classes.get("caveated_relying_party_validation_phrase") == 1, classes
assert classes.get("artifact_index_duplicate_row_current_hash_present") == 1, classes
assert classes.get("manual_review_warning") == 3, classes
assert sum(classes.values()) == 35, classes

completed = subprocess.run(
    [
        str(WORKSPACE / ".venv" / "bin" / "python"),
        str(SCRIPT),
        "--workspace",
        str(WORKSPACE),
        "--validation-output",
        "notes/release-readiness-checklist-validation-output.json",
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
print(json.dumps({"status": "ok", "warning_classes": cli_result["aggregate_warning_class_counts"], "output": str(OUTPUT.relative_to(WORKSPACE))}, indent=2, sort_keys=True))
