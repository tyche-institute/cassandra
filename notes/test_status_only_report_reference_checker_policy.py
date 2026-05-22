#!/usr/bin/env python3
"""Smoke test for status-only report reference-checker policy validation."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = WORKSPACE / "notes" / "validate_status_only_report_reference_checker_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_status_only_report_reference_checker_policy", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load policy validator module")
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
    assert result["decision"]["checker_kept_out_of_band"] is True, result
    assert result["decision"]["safe_to_wire_into_checklist_without_operator_review"] is False, result
    assert result["decision"]["not_missing_provenance"] is True, result
    assert result["inputs"]["status_only_release_gate_report"]["status_only_gate_count"] == 3, result
    assert "does not clear warnings" in result["research_caveat"], result

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = pathlib.Path(tmp_dir)
        for rel in [
            "notes/status-only-report-reference-checker-policy.md",
            "notes/status-only-release-gates-report-reference-validation-output.json",
            "notes/validate_release_readiness_checklist.py",
            "notes/status-only-release-gates-report-output.json",
        ]:
            copy_rel(tmp, rel)
        validator_path = tmp / "notes" / "validate_release_readiness_checklist.py"
        validator_path.write_text(
            validator_path.read_text(encoding="utf-8")
            + "\n# accidental future wiring: status-only-release-gates-report-reference-validation-output.json\n",
            encoding="utf-8",
        )
        wired = module.validate(tmp)
        assert wired["status"] == "needs_review", wired
        assert any("checker appears wired into release-readiness checklist" in err for err in wired["errors"]), wired

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = pathlib.Path(tmp_dir)
        for rel in [
            "notes/status-only-report-reference-checker-policy.md",
            "notes/status-only-release-gates-report-reference-validation-output.json",
            "notes/validate_release_readiness_checklist.py",
            "notes/status-only-release-gates-report-output.json",
        ]:
            copy_rel(tmp, rel)
        policy_path = tmp / "notes" / "status-only-report-reference-checker-policy.md"
        policy_path.write_text(policy_path.read_text(encoding="utf-8").replace("not missing provenance", "MISSING_PHRASE"), encoding="utf-8")
        missing_policy = module.validate(tmp)
        assert missing_policy["status"] == "needs_review", missing_policy
        assert any("policy note lacks required fragment" in err for err in missing_policy["errors"]), missing_policy

    print(json.dumps({
        "status": "ok",
        "checked_policy": str(module.POLICY_REL),
        "checker_kept_out_of_band": True,
        "wired_fixture_status": "needs_review",
        "missing_policy_fixture_status": "needs_review",
        "research_caveat": "Smoke test only; not publication approval, legal review, signature validation, trusted-list supervision, listed-entity status evidence, public alerting, or regulated trust-service output.",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
