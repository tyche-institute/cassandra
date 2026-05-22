#!/usr/bin/env python3
"""Smoke test for release-readiness checklist validation."""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "validate_release_readiness_checklist.py"
OUTPUT = WORKSPACE / "notes" / "release-readiness-checklist-validation-output.json"

spec = importlib.util.spec_from_file_location("validate_release_readiness_checklist", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore[union-attr]

result = module.validate(WORKSPACE)
paper_text = (WORKSPACE / "paper" / "draft.md").read_text(encoding="utf-8")
assert result["schema"].endswith(":0.6"), result
assert result["validator_count"] == 16, result
assert result["checklist_heading"] == "## Release-readiness checklist for operator review", result
assert "release-readiness warning report" in paper_text, result
assert "release-readiness gate summary" in paper_text, result
assert "not a release decision" in paper_text, result
assert "release gate hash-cycle policy report" in paper_text, result
assert "notes/release-gate-hash-cycle-policy-report-output.json" in paper_text, result
assert "status-only inside the checklist" in paper_text, result
assert "not as missing-hash repair" in paper_text, result
assert "hash-cycle policy reference validator" in paper_text, result
assert "notes/hash-cycle-policy-reference-validation-output.json" in paper_text, result
assert "status-only release gate report" in paper_text, result
assert "notes/status-only-release-gates-report-output.json" in paper_text, result
assert "dependency-context status-only gate" in paper_text, result
assert result["status"] == "ok", result
assert result["error_count"] == 0, result
assert all(item["exists"] for item in result["validators"]), result
assert all(item.get("status") == "ok" for item in result["validators"]), result
freshness = next(item for item in result["validators"] if item["name"] == "release_gate_summary_freshness")
assert freshness.get("hash_policy") == "status_only_to_avoid_release_checklist_gate_summary_hash_cycle", freshness
assert "sha256" not in freshness, freshness
reference_gate = next(item for item in result["validators"] if item["name"] == "hash_cycle_policy_references")
assert reference_gate.get("hash_policy") == "status_only_to_avoid_release_checklist_gate_summary_hash_cycle", reference_gate
assert "sha256" not in reference_gate, reference_gate
status_only_report = next(item for item in result["validators"] if item["name"] == "status_only_release_gates_report")
assert status_only_report.get("hash_policy") == "status_only_to_avoid_release_checklist_gate_summary_hash_cycle", status_only_report
assert "sha256" not in status_only_report, status_only_report
assert "not legal compliance" in result["research_caveat"], result

completed = subprocess.run(
    [str(WORKSPACE / ".venv" / "bin" / "python"), str(SCRIPT), "--workspace", str(WORKSPACE), "--output", str(OUTPUT.relative_to(WORKSPACE))],
    cwd=WORKSPACE,
    check=True,
    text=True,
    capture_output=True,
)
cli_result = json.loads(completed.stdout)
assert cli_result["status"] == "ok", cli_result
assert OUTPUT.exists(), OUTPUT
print(json.dumps({"status": "ok", "validator_count": cli_result["validator_count"], "output": str(OUTPUT.relative_to(WORKSPACE))}, indent=2, sort_keys=True))
