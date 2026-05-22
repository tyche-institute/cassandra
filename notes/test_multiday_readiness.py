#!/usr/bin/env python3
"""Smoke test for validate_multiday_readiness.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "validate_multiday_readiness.py"
OUTPUT = WORKSPACE / "notes" / "multiday-readiness-validation-output.json"

spec = importlib.util.spec_from_file_location("validate_multiday_readiness", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore[union-attr]

result = module.validate(WORKSPACE)
assert result["status"] == "ok", result
assert result["date_counts"]["completed"] >= 2, result
assert result["completed_dates"] == ["2026-05-20", "2026-05-21"], result
assert result["multi_day_mode"] is True, result
assert result["aggregate_results"]["path"] == "notes/aggregate-results-2026-05-21-output.json", result
assert result["aggregate_results"]["dates"] == result["completed_dates"], result
assert result["aggregate_results"]["row_count"] == result["date_counts"]["completed"], result
assert result["aggregate_results"]["diff_change_count_total"] == 0, result
assert result["synthetic_second_date_detected"] is False, result
assert "does not assert legal" in result["caveat"], result

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
print(json.dumps({"status": "ok", "completed_dates": cli_result["completed_dates"], "output": str(OUTPUT.relative_to(WORKSPACE))}, indent=2, sort_keys=True))
