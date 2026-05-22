#!/usr/bin/env python3
"""Smoke test for release-readiness persistent-warning policy note validation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from validate_release_readiness_persistent_warning_policy import validate


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    workspace = Path.cwd()
    watched = [
        workspace / "notes/release-readiness-warning-report-output.json",
        workspace / "notes/release-readiness-checklist-validation-output.json",
    ]
    before = {str(p.relative_to(workspace)): sha256_file(p) for p in watched if p.exists()}
    result = validate(workspace)
    after = {str(p.relative_to(workspace)): sha256_file(p) for p in watched if p.exists()}
    assert result["status"] == "ok", result
    assert result["error_count"] == 0, result
    assert result["warning_class_count"] >= 1, result
    assert "artifact_index_duplicate_row_current_hash_present" in result["warning_classes"], result
    assert before == after, {"before": before, "after": after}
    print(json.dumps({"status": "ok", "result": result, "non_mutation_hashes": after}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
