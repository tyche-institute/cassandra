#!/usr/bin/env python3
"""Smoke tests for ARTIFACT_INDEX duplicate-row reporting.

Research-workflow maintenance only: this does not rewrite historical rows and
makes no legal, supervisory, signature-validation, public-alerting, or
publication-readiness claim.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "report_artifact_index_duplicates.py"
OUTPUT = WORKSPACE / "notes" / "artifact-index-duplicate-report-output.json"


def main() -> int:
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--workspace",
            str(WORKSPACE),
            "--output",
            str(OUTPUT),
        ],
        cwd=WORKSPACE,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    stdout_payload = json.loads(proc.stdout)
    assert payload == stdout_payload
    assert payload["status"] == "ok"
    assert payload["artifact"] == "ARTIFACT_INDEX.md"
    assert payload["mode"] == "report_only_no_rewrite"
    assert isinstance(payload["duplicate_paths"], list)
    assert payload["duplicate_path_count"] == len(payload["duplicate_paths"])
    assert payload["row_count"] >= payload["unique_path_count"] >= 1
    caveat = payload["caveat"].lower()
    for fragment in [
        "does not rewrite",
        "does not assert legal effect",
        "does not perform signature validation",
        "does not assert publication readiness",
    ]:
        assert fragment in caveat, fragment
    if payload["duplicate_paths"]:
        first = payload["duplicate_paths"][0]
        assert "path" in first
        assert first["row_occurrences"] >= 2
        assert first["current_matching_row_count"] >= 1
        assert isinstance(first["rows"], list)
    print(json.dumps({"status": "ok", "script": str(SCRIPT.relative_to(WORKSPACE)), "duplicate_path_count": payload["duplicate_path_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
