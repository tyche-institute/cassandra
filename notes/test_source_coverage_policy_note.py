#!/usr/bin/env python3
"""Smoke test for source coverage policy note validation."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "notes" / "validate_source_coverage_policy_note.py"

spec = importlib.util.spec_from_file_location("validate_source_coverage_policy_note", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

result = module.validate(ROOT, Path("notes/source-coverage-policy-note.md"))
assert result["status"] == "ok", result
assert result["error_count"] == 0, result
assert result["note_sha256"], result
assert "publication approval" in result["research_caveat"], result
before = (ROOT / "SOURCES.md").read_bytes()
after = (ROOT / "SOURCES.md").read_bytes()
assert before == after
print(result)
