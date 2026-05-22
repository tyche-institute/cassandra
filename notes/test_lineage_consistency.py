#!/usr/bin/env python3
"""Smoke test for snapshot-to-normalization-to-diff lineage validator."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
MODULE_PATH = WORKSPACE / "notes" / "validate_lineage_consistency.py"

spec = importlib.util.spec_from_file_location("validate_lineage_consistency", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

result = module.validate_date(WORKSPACE, "2026-05-20")
assert result["status"] == "ok", json.dumps(result, indent=2, sort_keys=True)
assert result["error_count"] == 0
assert result["counts"]["snapshot_ok_count"] == result["counts"]["normalized_count"] == 41
assert result["counts"]["normalized_ok_count"] == result["counts"]["diff_current_record_count"] == 31
assert result["counts"]["diff_change_count"] == 0
assert result["hashes"]["normalized_manifest_sha256"]
assert "legal effect" in result["research_caveat"]
assert "publication readiness" in result["research_caveat"]
print(json.dumps({
    "status": "ok",
    "checked": "validate_lineage_consistency.validate_date",
    "date": result["date"],
    "counts": result["counts"],
    "warning_count": result["warning_count"],
}, indent=2, sort_keys=True))
