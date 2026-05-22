#!/usr/bin/env python3
"""Smoke test for release-gate summary freshness validation."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = WORKSPACE / "notes/validate_release_gate_summary_freshness.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_release_gate_summary_freshness", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load freshness validator module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_module()
    result = module.validate(WORKSPACE, "notes/release-readiness-gate-summary-output.json")
    assert result["status"] == "ok", result
    assert result["error_count"] == 0, result
    assert result["warning_count"] == 0, result
    assert result["source_checks"], result
    for label, check in result["source_checks"].items():
        assert check["exists"], (label, check)
        assert check["embedded_present"], (label, check)
        assert check["matches_current_hash"], (label, check)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = pathlib.Path(tmp_dir)
        for rel in [
            "notes/release-readiness-gate-summary-output.json",
            "notes/release-readiness-checklist-validation-output.json",
            "notes/release-readiness-warning-report-output.json",
            "notes/release-readiness-persistent-warning-policy-validation-output.json",
        ]:
            src = WORKSPACE / rel
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
        summary_path = tmp / "notes/release-readiness-gate-summary-output.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["sources"]["warning_report"]["sha256"] = "0" * 64
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        stale = module.validate(tmp, "notes/release-readiness-gate-summary-output.json")
        assert stale["status"] == "needs_review", stale
        assert any("stale embedded hash for warning_report" in err for err in stale["errors"]), stale

    print(json.dumps({
        "status": "ok",
        "checked_sources": sorted(result["source_checks"].keys()),
        "stale_fixture_status": "needs_review",
        "research_caveat": "Smoke test only; not publication approval, legal review, signature validation, trusted-list supervision, listed-entity status evidence, public alerting, or regulated trust-service output.",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
