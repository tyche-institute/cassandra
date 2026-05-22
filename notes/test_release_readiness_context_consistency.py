#!/usr/bin/env python3
"""Smoke tests for release-readiness context consistency validation."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = WORKSPACE / "notes" / "validate_release_readiness_context_consistency.py"
WATCHED = [
    WORKSPACE / "notes" / "release-readiness-topology-report-output.json",
    WORKSPACE / "notes" / "release-readiness-warning-report-output.json",
    WORKSPACE / "notes" / "release-readiness-gate-summary-output.json",
    WORKSPACE / "notes" / "status-only-release-gates-report-output.json",
]


def load_module():
    spec = importlib.util.spec_from_file_location("context_consistency", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    module = load_module()
    before = {str(path): sha(path) for path in WATCHED}
    live = module.validate(WORKSPACE)
    after = {str(path): sha(path) for path in WATCHED}
    assert before == after, "validator must not mutate source reports"
    assert live["status"] == "ok", live
    assert live["error_count"] == 0, live
    assert live["safe_to_auto_publish"] is False
    assert live["safe_to_auto_clear_warnings"] is False
    assert sorted(live["checked_context"]["out_of_band_names"]) == [
        "status_only_report_reference_checker_policy",
        "topology_report_reference_freshness_policy",
    ]
    assert sorted(live["checked_context"]["report_out_of_band_names"]) == [
        "release_readiness_context_consistency_policy",
        "status_only_report_reference_checker_policy",
        "topology_report_reference_freshness_policy",
    ]
    assert "not legal compliance" in live["research_caveat"]
    assert "publication approval" in live["research_caveat"]

    data = {
        "topology": load_json(WORKSPACE / module.TOPOLOGY_REL),
        "warning": load_json(WORKSPACE / module.WARNING_REL),
        "gate": load_json(WORKSPACE / module.GATE_REL),
        "status_only": load_json(WORKSPACE / module.STATUS_ONLY_REL),
    }

    broken_gate = copy.deepcopy(data)
    broken_gate["gate"]["out_of_band_policy_checks"] = broken_gate["gate"].get("out_of_band_policy_checks", [])[:1]
    broken_result = module.validate_data(WORKSPACE, broken_gate)
    assert broken_result["status"] == "needs_review"
    assert any("gate-summary out-of-band names mismatch" in error for error in broken_result["errors"]), broken_result

    broken_warning = copy.deepcopy(data)
    broken_warning["warning"]["warning_sources"] = broken_warning["warning"].get("warning_sources", [])[1:]
    broken_warning_result = module.validate_data(WORKSPACE, broken_warning)
    assert broken_warning_result["status"] == "needs_review"
    assert any("warning-report warning-source" in error or "warning-context names" in error for error in broken_warning_result["errors"]), broken_warning_result

    print(json.dumps({
        "status": "ok",
        "live_status": live["status"],
        "live_warning_count": live["warning_count"],
        "fixtures_checked": ["missing_out_of_band_gate_context", "warning_source_name_mismatch"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
