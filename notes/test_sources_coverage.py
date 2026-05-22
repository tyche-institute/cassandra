#!/usr/bin/env python3
"""Smoke test for the Cassandra SOURCES.md coverage validator."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "validate_sources_coverage.py"
OUTPUT = WORKSPACE / "notes" / "test-sources-coverage-validation-output.json"

spec = importlib.util.spec_from_file_location("validate_sources_coverage", SCRIPT)
assert spec and spec.loader, "could not load validator module"
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore[union-attr]
result = mod.validate(WORKSPACE, ["2026-05-20", "2026-05-21"])
assert result["status"] == "ok", result
assert result["snapshot_item_count"] >= 80, result["snapshot_item_count"]
assert result["snapshot_item_covered_count"] == result["snapshot_item_count"], result
assert result["bundle_records"] and len(result["bundle_records"]) == 2, result.get("bundle_records")
assert "does not perform trusted-list validation" in result["research_caveat"]
assert "legal-status determination" in result["research_caveat"]
proc = subprocess.run(
    [sys.executable, str(SCRIPT), "--workspace", str(WORKSPACE), "--date", "2026-05-20", "--date", "2026-05-21", "--output", str(OUTPUT.relative_to(WORKSPACE))],
    cwd=WORKSPACE,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert proc.returncode == 0, proc.stderr + proc.stdout
cli_result = json.loads(OUTPUT.read_text(encoding="utf-8"))
assert cli_result["status"] == "ok", cli_result
assert cli_result["snapshot_item_covered_count"] == cli_result["snapshot_item_count"], cli_result
print(json.dumps({"status": "ok", "snapshot_item_count": cli_result["snapshot_item_count"], "bundle_count": len(cli_result["bundle_records"]), "output": str(OUTPUT.relative_to(WORKSPACE))}, indent=2, sort_keys=True))
