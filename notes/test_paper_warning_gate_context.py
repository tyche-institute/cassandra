#!/usr/bin/env python3
"""Smoke tests for paper warning/gate context validator."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "notes" / "validate_paper_warning_gate_context.py"

spec = importlib.util.spec_from_file_location("validate_paper_warning_gate_context", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def copy_minimal_workspace(dst: pathlib.Path) -> None:
    (dst / "notes").mkdir(parents=True)
    (dst / "paper").mkdir(parents=True)
    for rel in [
        "paper/draft.md",
        "notes/release-readiness-warning-report-output.json",
        "notes/release-readiness-gate-summary-output.json",
        "ARTIFACT_INDEX.md",
    ]:
        src = ROOT / rel
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)


def test_live_workspace_ok_and_non_mutating() -> None:
    before = (ROOT / "paper" / "draft.md").read_bytes()
    result = module.validate(ROOT)
    after = (ROOT / "paper" / "draft.md").read_bytes()
    assert before == after, "validator must not mutate paper draft"
    assert result["status"] == "ok", result
    assert result["error_count"] == 0, result
    assert "release_readiness_context_consistency_policy" in result["warning_report_out_of_band_contexts"], result
    assert "release_readiness_context_consistency_policy" in result["gate_summary_out_of_band_contexts"], result


def test_missing_paper_non_clearance_wording_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        copy_minimal_workspace(workspace)
        paper = (workspace / "paper" / "draft.md").read_text(encoding="utf-8")
        paper = paper.replace("does not clear warnings, rewrite historical artifacts, approve external circulation, validate signatures", "approves external circulation and validates signatures")
        (workspace / "paper" / "draft.md").write_text(paper, encoding="utf-8")
        result = module.validate(workspace)
        assert result["status"] == "needs_review", result
        assert any("warning-report-output.json" in err for err in result["errors"]), result


def test_missing_out_of_band_context_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        copy_minimal_workspace(workspace)
        path = workspace / "notes" / "release-readiness-gate-summary-output.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["out_of_band_policy_checks"] = [
            item for item in data.get("out_of_band_policy_checks", [])
            if item.get("name") != "release_readiness_context_consistency_policy"
        ]
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        # Keep artifact-index hash permissive for this fixture; the missing context
        # should be sufficient to fail.
        digest = module.sha256_path(path)
        with (workspace / "ARTIFACT_INDEX.md").open("a", encoding="utf-8") as fh:
            fh.write(f"\n| `notes/release-readiness-gate-summary-output.json` | fixture row | `sha256:{digest}` | yes |\n")
        result = module.validate(workspace)
        assert result["status"] == "needs_review", result
        assert any("gate_summary missing out-of-band context" in err for err in result["errors"]), result


def main() -> int:
    test_live_workspace_ok_and_non_mutating()
    test_missing_paper_non_clearance_wording_fails()
    test_missing_out_of_band_context_fails()
    print(json.dumps({"status": "ok", "tests": 3}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
