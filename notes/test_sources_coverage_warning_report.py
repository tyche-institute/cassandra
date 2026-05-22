#!/usr/bin/env python3
"""Smoke test for the SOURCES.md coverage warning report helper."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "report_sources_coverage_warnings.py"
VALIDATION = WORKSPACE / "notes" / "sources-coverage-validation-output.json"
OUTPUT = WORKSPACE / "notes" / "test-sources-coverage-warning-report-output.json"

spec = importlib.util.spec_from_file_location("report_sources_coverage_warnings", SCRIPT)
assert spec and spec.loader, "could not load report helper"
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore[union-attr]
report = mod.build_report(WORKSPACE, VALIDATION)
assert report["status"] == "ok", report
assert report["source_validation_error_count"] == 0, report
assert report["source_validation_warning_count"] == 3, report
assert report["snapshot_item_covered_count"] == report["snapshot_item_count"], report
assert report["warning_classes"].get("legacy_pointer_record_caveat") == 1, report["warning_classes"]
assert report["warning_classes"].get("missing_date_specific_bundle_sources_row") == 2, report["warning_classes"]
assert report["safe_to_auto_rewrite_historical_bundles"] is False, report
assert "does not perform trusted-list validation" in report["research_caveat"], report["research_caveat"]
assert "publication approval" in report["research_caveat"], report["research_caveat"]

sources_before = (WORKSPACE / "SOURCES.md").read_bytes()
proc = subprocess.run(
    [
        sys.executable,
        str(SCRIPT),
        "--workspace",
        str(WORKSPACE),
        "--validation-output",
        str(VALIDATION.relative_to(WORKSPACE)),
        "--output",
        str(OUTPUT.relative_to(WORKSPACE)),
    ],
    cwd=WORKSPACE,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert proc.returncode == 0, proc.stderr + proc.stdout
cli_report = json.loads(OUTPUT.read_text(encoding="utf-8"))
assert cli_report["status"] == "ok", cli_report
assert cli_report["non_mutating"] is True, cli_report
assert cli_report["non_mutation_hash_check"]["unchanged"] is True, cli_report["non_mutation_hash_check"]
assert (WORKSPACE / "SOURCES.md").read_bytes() == sources_before, "SOURCES.md was mutated"
print(json.dumps({
    "status": "ok",
    "warning_count": cli_report["warning_count"],
    "warning_classes": cli_report["warning_classes"],
    "output": str(OUTPUT.relative_to(WORKSPACE)),
}, indent=2, sort_keys=True))
