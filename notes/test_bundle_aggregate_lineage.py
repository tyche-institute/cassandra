#!/usr/bin/env python3
"""Smoke test for bundle-to-aggregate lineage validation."""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "validate_bundle_aggregate_lineage.py"
OUTPUT = WORKSPACE / "notes" / "bundle-aggregate-lineage-validation-output.json"
RUN = WORKSPACE / "notes" / "bundle-aggregate-lineage-validation-run.json"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_bundle_aggregate_lineage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> int:
    before_index = (WORKSPACE / "ARTIFACT_INDEX.md").read_bytes()
    proc = subprocess.run(
        [
            str(WORKSPACE / ".venv" / "bin" / "python"),
            str(SCRIPT),
            "--workspace",
            str(WORKSPACE),
            "--date",
            "2026-05-20",
            "--output",
            str(OUTPUT.relative_to(WORKSPACE)),
        ],
        cwd=WORKSPACE,
        check=False,
        text=True,
        capture_output=True,
    )
    RUN.write_text(proc.stdout, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr + proc.stdout
    result = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert result["status"] == "ok", result
    assert result["error_count"] == 0, result
    assert result["checked"]["count_checks"]["pointer_attempts"]["matches"] is True
    assert result["checked"]["count_checks"]["diff_change_count"]["matches"] is True
    assert "legal-status determination" in result["research_caveat"]
    assert "publication readiness" in result["research_caveat"]
    after_index = (WORKSPACE / "ARTIFACT_INDEX.md").read_bytes()
    assert before_index == after_index, "validator must not rewrite ARTIFACT_INDEX.md"
    module = load_module()
    inline = module.validate(WORKSPACE, "2026-05-20")
    assert inline["status"] == "ok"
    print(json.dumps({
        "status": "ok",
        "validated_output": str(OUTPUT.relative_to(WORKSPACE)),
        "warning_count": result["warning_count"],
        "count_checks": sorted(result["checked"]["count_checks"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
