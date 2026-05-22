#!/usr/bin/env python3
"""Smoke test for hash-cycle policy reference validation."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "validate_hash_cycle_policy_references.py"
OUTPUT = WORKSPACE / "notes" / "hash-cycle-policy-reference-validation-output.json"

spec = importlib.util.spec_from_file_location("validate_hash_cycle_policy_references", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore[union-attr]

before = {
    rel: (WORKSPACE / rel).read_bytes()
    for rel in [
        Path("paper/draft.md"),
        Path("notes/validate_release_readiness_checklist.py"),
        Path("notes/release-gate-hash-cycle-policy-report-output.json"),
    ]
}

result = module.validate(WORKSPACE)
assert result["schema"].endswith(":0.1"), result
assert result["status"] == "ok", result
assert result["error_count"] == 0, result
assert result["policy_reference_check"]["manual_review_only"] is True, result
assert result["policy_reference_check"]["safe_to_publish"] is False, result
assert result["inputs"]["hash_cycle_policy_report"]["status"] == "ok", result
assert result["inputs"]["hash_cycle_policy_report"]["not_missing_provenance"] is True, result
assert "does not clear warnings" in result["research_caveat"], result

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

for rel, content in before.items():
    assert (WORKSPACE / rel).read_bytes() == content, rel

with tempfile.TemporaryDirectory() as tmp:
    tmp_workspace = Path(tmp) / "workspace"
    shutil.copytree(WORKSPACE, tmp_workspace, ignore=shutil.ignore_patterns(".venv", "__pycache__"))
    paper = tmp_workspace / "paper" / "draft.md"
    paper.write_text(
        paper.read_text(encoding="utf-8").replace("notes/release-gate-hash-cycle-policy-report-output.json", "notes/MISSING-policy.json"),
        encoding="utf-8",
    )
    fixture_result = module.validate(tmp_workspace)
    assert fixture_result["status"] == "needs_review", fixture_result
    assert any("paper checklist lacks hash-cycle policy fragment" in err for err in fixture_result["errors"]), fixture_result

print(json.dumps({"status": "ok", "output": str(OUTPUT.relative_to(WORKSPACE)), "warning_count": cli_result["warning_count"]}, indent=2, sort_keys=True))
