#!/usr/bin/env python3
"""Smoke tests for artifact-index append-only duplicate-row policy validation."""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "notes" / "validate_artifact_index_append_only_duplicates_policy.py"


def run_validator(workspace: pathlib.Path, output: str = "out.json") -> tuple[int, dict]:
    proc = subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), str(VALIDATOR), "--workspace", str(workspace), "--output", output],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    data = json.loads((workspace / output).read_text(encoding="utf-8"))
    return proc.returncode, data


def copy_fixture() -> pathlib.Path:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cassandra-artifact-index-policy-"))
    (tmp / "notes").mkdir(parents=True)
    for rel in [
        "notes/artifact-index-append-only-duplicates-policy.md",
        "notes/artifact-index-current-hash-validation-output.json",
        "notes/artifact-index-duplicate-report-output.json",
        "notes/report_artifact_index_duplicates.py",
        "notes/propose_artifact_index_duplicate_cleanup.py",
    ]:
        src = ROOT / rel
        dst = tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return tmp


def test_live_workspace_ok() -> None:
    code, data = run_validator(ROOT, "notes/artifact-index-append-only-duplicates-policy-validation-run.json")
    assert code == 0, data
    assert data["status"] == "ok"
    assert data["decision"]["safe_to_auto_delete_duplicate_rows"] is False


def test_policy_must_preserve_current_hash_requirement() -> None:
    tmp = copy_fixture()
    try:
        policy = tmp / "notes" / "artifact-index-append-only-duplicates-policy.md"
        policy.write_text(policy.read_text(encoding="utf-8").replace("Add a new row with the current sha256", "Add a row"), encoding="utf-8")
        code, data = run_validator(tmp)
        assert code == 1
        assert data["status"] == "needs_review"
        assert any("Add a new row with the current sha256" in error for error in data["errors"])
    finally:
        shutil.rmtree(tmp)


def test_stale_current_hash_output_fails() -> None:
    tmp = copy_fixture()
    try:
        path = tmp / "notes" / "artifact-index-current-hash-validation-output.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["status"] = "needs_review"
        data["stale_path_count"] = 1
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        code, result = run_validator(tmp)
        assert code == 1
        assert any("current-hash validation status is not ok" in error for error in result["errors"])
        assert any("stale paths" in error for error in result["errors"])
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    tests = [
        test_live_workspace_ok,
        test_policy_must_preserve_current_hash_requirement,
        test_stale_current_hash_output_fails,
    ]
    results = []
    for test in tests:
        test()
        results.append({"test": test.__name__, "status": "ok"})
    print(json.dumps({"status": "ok", "tests": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
