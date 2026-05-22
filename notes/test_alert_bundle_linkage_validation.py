#!/usr/bin/env python3
"""Smoke-test the alert/bundle linkage validator."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
MODULE_PATH = WORKSPACE / "notes" / "validate_alert_bundle_linkage.py"
OUTPUT = WORKSPACE / "notes" / "test-alert-bundle-linkage-validation-output.json"

spec = importlib.util.spec_from_file_location("validate_alert_bundle_linkage", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

result = module.validate(WORKSPACE)
assert result["status"] == "ok", result
assert result["error_count"] == 0, result
assert result["entry_count"] >= 1, result
assert "2026-05-20" in result["dates"], result
assert "does not assert legal effect" in result["research_caveat"], result["research_caveat"]
matching_entries = 0
for entry in result["checked_entries"]:
    assert entry["artifacts"], entry
    if all(artifact["matches"] is True for artifact in entry["artifacts"]):
        matching_entries += 1
assert matching_entries >= 1, result

OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"status": "ok", "output": str(OUTPUT), "entry_count": result["entry_count"]}, sort_keys=True))
