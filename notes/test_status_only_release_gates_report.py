#!/usr/bin/env python3
"""Smoke test for status-only release-readiness gate report."""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "report_status_only_release_gates.py"
OUTPUT = WORKSPACE / "notes" / "status-only-release-gates-report-output.json"
CHECKLIST = WORKSPACE / "notes" / "release-readiness-checklist-validation-output.json"
STATUS_ONLY_OUTPUTS = [
    WORKSPACE / "notes" / "release-gate-summary-freshness-validation-output.json",
    WORKSPACE / "notes" / "hash-cycle-policy-reference-validation-output.json",
    WORKSPACE / "notes" / "status-only-release-gates-report-output.json",
]

spec = importlib.util.spec_from_file_location("report_status_only_release_gates", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore[union-attr]

before = {path: module.sha256_path(path) for path in [CHECKLIST, *STATUS_ONLY_OUTPUTS]}
result = module.report(WORKSPACE)
after = {path: module.sha256_path(path) for path in [CHECKLIST, *STATUS_ONLY_OUTPUTS]}
assert before == after, {"before": before, "after": after}
assert result["schema"].endswith(":0.2"), result
assert result["status"] == "ok", result
assert result["error_count"] == 0, result
assert result["status_only_gate_count"] == 3, result
assert {record["name"] for record in result["status_only_gates"]} == {"release_gate_summary_freshness", "hash_cycle_policy_references", "status_only_release_gates_report"}, result
assert all(record["not_missing_provenance"] is True for record in result["status_only_gates"]), result
assert all(record["safe_to_add_checklist_sha256"] is False for record in result["status_only_gates"]), result
assert all(record["output_status"] == "ok" for record in result["status_only_gates"]), result
assert all(record["current_output_sha256_for_operator_trace_only"] for record in result["status_only_gates"]), result
assert result["source_checklist"]["validator_count"] == 16, result
assert result["non_status_only_validator_hash_count"] == 13, result
assert result["safe_to_auto_clear_warnings"] is False, result
assert result["safe_to_auto_publish"] is False, result
assert result["operator_review_context"] is True, result
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
print(json.dumps({"status": "ok", "status_only_gate_count": cli_result["status_only_gate_count"], "warnings": cli_result["warnings"], "output": str(OUTPUT.relative_to(WORKSPACE))}, indent=2, sort_keys=True))
