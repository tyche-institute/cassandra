#!/usr/bin/env python3
"""Smoke test for validate_paper_figure_refs.py two-date freshness checks."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "validate_paper_figure_refs.py"
OUTPUT = WORKSPACE / "notes" / "paper-figure-reference-validation-output.json"

spec = importlib.util.spec_from_file_location("validate_paper_figure_refs", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)  # type: ignore[union-attr]

result = module.validate(WORKSPACE)
assert result["status"] == "ok", result
assert result["schema"].endswith(":0.2"), result
assert result["aggregate_results"]["path"] == "notes/aggregate-results-2026-05-21-output.json", result
assert result["aggregate_results"]["dates"] == ["2026-05-20", "2026-05-21"], result
assert result["aggregate_results"]["row_count"] == 2, result
assert result["aggregate_results"]["diff_change_count_total"] == 0, result
assert all(item["artifact_index_has_current_sha256"] for item in result["figures"]), result
assert all(item["artifact_index_has_current_sha256"] for item in result["data_sources"]), result
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
print(json.dumps({"status": "ok", "aggregate_results": cli_result["aggregate_results"], "output": str(OUTPUT.relative_to(WORKSPACE))}, indent=2, sort_keys=True))
