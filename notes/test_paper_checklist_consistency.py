#!/usr/bin/env python3
"""Smoke tests for paper/checklist consistency validation."""
from __future__ import annotations

import json
import pathlib
import shutil
import tempfile

import validate_paper_checklist_consistency as validator

ROOT = pathlib.Path(__file__).resolve().parents[1]


def copy_fixture() -> pathlib.Path:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cassandra-paper-checklist-"))
    for rel in [
        "paper/draft.md",
        "notes/validate_release_readiness_checklist.py",
        "notes/release-readiness-checklist-validation-output.json",
        "notes/release-readiness-context-consistency-policy-validation-output.json",
    ]:
        src = ROOT / rel
        dst = tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return tmp


def assert_live_ok() -> None:
    result = validator.validate(ROOT)
    assert result["status"] == "ok", result
    assert result["error_count"] == 0, result
    assert result["context_consistency_validator_is_checklist_dependency"] is False, result
    assert result["configured_validator_count"] == 16, result


def assert_detects_accidental_context_dependency() -> None:
    tmp = copy_fixture()
    try:
        path = tmp / "notes/validate_release_readiness_checklist.py"
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "    (\"artifact_index_current_hashes\", pathlib.Path(\"notes/artifact-index-current-hash-validation-output.json\")),\n]",
            "    (\"artifact_index_current_hashes\", pathlib.Path(\"notes/artifact-index-current-hash-validation-output.json\")),\n    (\"release_readiness_context_consistency\", pathlib.Path(\"notes/release-readiness-context-consistency-validation-output.json\")),\n]",
        )
        path.write_text(text, encoding="utf-8")
        result = validator.validate(tmp)
        assert result["status"] == "needs_review", result
        assert any("promoted into release-readiness checklist" in err for err in result["errors"]), result
    finally:
        shutil.rmtree(tmp)


def assert_detects_missing_policy_reference() -> None:
    tmp = copy_fixture()
    try:
        path = tmp / "paper/draft.md"
        text = path.read_text(encoding="utf-8").replace(
            "`notes/release-readiness-context-consistency-policy-validation-output.json`",
            "`notes/removed-context-consistency-policy-validation-output.json`",
        )
        path.write_text(text, encoding="utf-8")
        result = validator.validate(tmp)
        assert result["status"] == "needs_review", result
        assert any("does not reference context-consistency policy output" in err for err in result["errors"]), result
    finally:
        shutil.rmtree(tmp)


def main() -> int:
    tests = [
        assert_live_ok,
        assert_detects_accidental_context_dependency,
        assert_detects_missing_policy_reference,
    ]
    results = []
    for test in tests:
        test()
        results.append({"test": test.__name__, "status": "ok"})
    print(json.dumps({"status": "ok", "tests": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
