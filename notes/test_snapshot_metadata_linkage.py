#!/usr/bin/env python3
"""Smoke test for validate_snapshot_metadata_linkage.py."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
MODULE_PATH = WORKSPACE / "notes" / "validate_snapshot_metadata_linkage.py"

spec = importlib.util.spec_from_file_location("validate_snapshot_metadata_linkage", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

result = module.validate_date(WORKSPACE, "2026-05-20")
assert result["status"] == "ok", result
assert result["item_count"] == 43, result
assert result["ok_count"] == 41, result
assert result["error_count_checked"] == 2, result
assert result["error_count"] == 0, result
assert "not trusted-list validation" in result["research_caveat"], result
assert result["territory_count"] >= 30, result
assert result["content_type_counts"], result
print(json.dumps({
    "status": "ok",
    "checked_date": result["date"],
    "item_count": result["item_count"],
    "ok_count": result["ok_count"],
    "error_count_checked": result["error_count_checked"],
    "territory_count": result["territory_count"],
}, indent=2, sort_keys=True))
