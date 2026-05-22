#!/usr/bin/env python3
"""Smoke test for the Cassandra public-artifact safety validator."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "validate_public_artifact_safety.py"
OUTPUT = WORKSPACE / "notes" / "public-artifact-safety-validation-output.json"


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=WORKSPACE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"validator failed with {result.returncode}: {result.stderr}\n{result.stdout}")
    if not OUTPUT.exists():
        raise AssertionError(f"expected validator output at {OUTPUT}")
    doc = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert doc["status"] == "ok", doc
    assert doc["error_count"] == 0, doc
    scanned = {item["path"] for item in doc["file_stats"]}
    assert "alerts.jsonl" in scanned, scanned
    assert "bundles/2026-05-20/snapshot-summary.json.bundle/notes.md" in scanned, scanned
    assert "bundles/2026-05-20/snapshot-summary.json.bundle/manifest.json" in scanned, scanned
    assert "bundles/2026-05-20/snapshot-summary.json.bundle/claims.json" in scanned, scanned
    assert "notes/bundle-generic-existing-guard-output.json" in scanned, scanned
    assert "notes/bundle-generic-missing-inputs-output.json" in scanned, scanned
    assert "notes/bundle-generic-helper-check-output.json" in scanned, scanned
    assert "figures/aggregate-run-telemetry.svg" in scanned, scanned
    assert "figures/aggregate-diff-classes.svg" in scanned, scanned
    assert doc["jsonl_stats"]["alerts.jsonl"]["entry_count"] >= 2, doc["jsonl_stats"]
    assert any(item.get("path") == "bundles/2026-05-20/snapshot-summary.json.bundle/manifest.json" and item.get("source_count") >= 1 for item in doc["file_stats"]), doc["file_stats"]
    assert any(item.get("path") == "bundles/2026-05-20/snapshot-summary.json.bundle/claims.json" and item.get("claim_count") >= 1 for item in doc["file_stats"]), doc["file_stats"]
    helper_stats = [item for item in doc["file_stats"] if item.get("kind") == "bundle_helper_output"]
    assert len(helper_stats) == 3, helper_stats
    assert {item.get("status") for item in helper_stats} == {"refused_existing_outputs", "missing_inputs", "ok"}, helper_stats
    required = doc["required_presence_by_path"]
    for path, phrases in required.items():
        missing = [phrase for phrase, present in phrases.items() if not present]
        assert not missing, {path: missing}
    print(json.dumps({"status": "ok", "scanned": sorted(scanned)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
