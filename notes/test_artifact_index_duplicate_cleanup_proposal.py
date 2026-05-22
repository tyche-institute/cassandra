#!/usr/bin/env python3
"""Smoke tests for proposal-only ARTIFACT_INDEX duplicate cleanup planning.

Workflow maintenance only. This test verifies that the proposal helper is
non-mutating and includes cautious caveats; it does not apply any cleanup patch
and makes no legal, supervisory, signature-validation, public-alerting, or
publication-readiness claim.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "propose_artifact_index_duplicate_cleanup.py"
OUTPUT = WORKSPACE / "notes" / "artifact-index-duplicate-cleanup-proposal-output.json"


def main() -> int:
    before = (WORKSPACE / "ARTIFACT_INDEX.md").read_bytes()
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
    after = (WORKSPACE / "ARTIFACT_INDEX.md").read_bytes()
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert before == after, "proposal helper must not rewrite ARTIFACT_INDEX.md"
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    stdout_payload = json.loads(proc.stdout)
    assert payload == stdout_payload
    assert payload["status"] == "ok"
    assert payload["artifact"] == "ARTIFACT_INDEX.md"
    assert payload["mode"] == "proposal_only_no_rewrite"
    assert payload["duplicate_path_count"] >= 0
    assert payload["cleanup_candidate_count"] == len(payload["cleanup_candidates"])
    assert "patch_sketch_sha256" in payload
    caveat = payload["caveat"].lower()
    for fragment in [
        "does not rewrite",
        "does not apply patches",
        "operator-reviewed",
        "does not assert legal effect",
        "does not perform signature validation",
        "does not assert publication readiness",
    ]:
        assert fragment in caveat, fragment
    if payload["cleanup_candidates"]:
        first = payload["cleanup_candidates"][0]
        assert first["safe_to_auto_apply"] is False
        assert first["current_sha256"]
        assert "candidate stale duplicate row" in payload["patch_sketch"]
    print(
        json.dumps(
            {
                "status": "ok",
                "script": str(SCRIPT.relative_to(WORKSPACE)),
                "cleanup_candidate_count": payload["cleanup_candidate_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
