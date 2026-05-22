#!/usr/bin/env python3
"""Smoke test for status-only release gate report reference validation."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = WORKSPACE / "notes" / "validate_status_only_release_gates_report_references.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_status_only_release_gates_report_references", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load status-only report reference validator module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_rel(tmp: pathlib.Path, rel: str) -> None:
    src = WORKSPACE / rel
    dst = tmp / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())


def main() -> int:
    module = load_module()
    result = module.validate(WORKSPACE)
    assert result["status"] == "ok", result
    assert result["error_count"] == 0, result
    assert result["inputs"]["status_only_release_gate_report"]["embedded_checklist_matches_current"] is True, result
    assert result["inputs"]["status_only_release_gate_report"]["status_only_gate_count"] == 3, result
    assert result["reference_check"]["manual_review_only"] is True, result
    assert result["reference_check"]["safe_to_clear_warnings"] is False, result
    assert result["reference_check"]["safe_to_publish"] is False, result
    assert "does not clear warnings" in result["research_caveat"], result

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = pathlib.Path(tmp_dir)
        for rel in [
            "paper/draft.md",
            "notes/validate_release_readiness_checklist.py",
            "notes/release-readiness-checklist-validation-output.json",
            "notes/status-only-release-gates-report-output.json",
        ]:
            copy_rel(tmp, rel)
        report_path = tmp / "notes" / "status-only-release-gates-report-output.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["source_checklist"]["sha256"] = "0" * 64
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale = module.validate(tmp)
        assert stale["status"] == "needs_review", stale
        assert any("embeds stale checklist hash" in err for err in stale["errors"]), stale

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = pathlib.Path(tmp_dir)
        for rel in [
            "paper/draft.md",
            "notes/validate_release_readiness_checklist.py",
            "notes/release-readiness-checklist-validation-output.json",
            "notes/status-only-release-gates-report-output.json",
        ]:
            copy_rel(tmp, rel)
        paper_path = tmp / "paper" / "draft.md"
        paper_path.write_text(
            paper_path.read_text(encoding="utf-8").replace(
                "notes/status-only-release-gates-report-output.json",
                "notes/status-only-release-gates-report-output.REMOVED.json",
                1,
            ),
            encoding="utf-8",
        )
        missing_reference = module.validate(tmp)
        assert missing_reference["status"] == "needs_review", missing_reference
        assert any("paper checklist lacks status-only report fragment" in err for err in missing_reference["errors"]), missing_reference

    print(json.dumps({
        "status": "ok",
        "checked_report": result["inputs"]["status_only_release_gate_report"]["path"],
        "embedded_checklist_matches_current": True,
        "stale_fixture_status": "needs_review",
        "missing_reference_fixture_status": "needs_review",
        "research_caveat": "Smoke test only; not publication approval, legal review, signature validation, trusted-list supervision, listed-entity status evidence, public alerting, or regulated trust-service output.",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
