#!/usr/bin/env python3
"""Smoke test for duplicate-cleanup proposal validation.

The test confirms that validation is non-mutating, internally consistent with
the duplicate-row report, and preserves operator-review caveats. It does not
apply cleanup patches and makes no legal, supervisory, signature-validation,
public-alerting, or publication-readiness claim.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
SCRIPT = WORKSPACE / "notes" / "validate_artifact_index_cleanup_proposal.py"
OUTPUT = WORKSPACE / "notes" / "artifact-index-cleanup-proposal-validation-output.json"


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
    assert before == after, "validator must not rewrite ARTIFACT_INDEX.md"
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    stdout_payload = json.loads(proc.stdout)
    assert payload == stdout_payload
    assert payload["status"] == "ok"
    assert payload["mode"] == "validation_only_no_rewrite"
    assert payload["error_count"] == 0
    assert payload["cleanup_candidate_count"] == payload["expected_cleanup_candidate_count"]
    assert payload["artifact_index_sha256_before"] == payload["artifact_index_sha256_after"]
    assert payload["retained_current_row_count"] >= payload["duplicate_path_count"]
    caveat = payload["caveat"].lower()
    for fragment in [
        "does not rewrite",
        "does not apply patches",
        "does not assert legal effect",
        "does not perform signature validation",
        "does not supervise trusted lists",
        "does not provide public alerting",
        "does not assert publication readiness",
        "operator-reviewed",
    ]:
        assert fragment in caveat, fragment
    print(
        json.dumps(
            {
                "status": "ok",
                "script": str(SCRIPT.relative_to(WORKSPACE)),
                "cleanup_candidate_count": payload["cleanup_candidate_count"],
                "duplicate_path_count": payload["duplicate_path_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
