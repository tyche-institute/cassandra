#!/usr/bin/env python3
"""Smoke tests for release-readiness topology report."""
from __future__ import annotations

import json
import pathlib
import tempfile

import report_release_readiness_topology as topology

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]


def sha(path: pathlib.Path) -> str:
    return topology.sha256_path(path)


def test_live_report_ok_and_non_mutating() -> None:
    watched = [
        WORKSPACE / "notes" / "release-readiness-checklist-validation-output.json",
        WORKSPACE / "notes" / "release-readiness-warning-report-output.json",
        WORKSPACE / "notes" / "release-readiness-gate-summary-output.json",
        WORKSPACE / "notes" / "status-only-release-gates-report-output.json",
        WORKSPACE / "notes" / "status-only-report-reference-checker-policy-validation-output.json",
        WORKSPACE / "notes" / "topology-report-reference-freshness-policy-validation-output.json",
    ]
    before = {str(path): sha(path) for path in watched}
    result = topology.report(WORKSPACE)
    after = {str(path): sha(path) for path in watched}
    assert before == after
    assert result["status"] == "ok", result
    assert result["error_count"] == 0
    assert result["topology"]["checklist_validator_count"] == 16
    assert result["topology"]["hash_recorded_validator_count"] == 13
    assert result["topology"]["status_only_gate_count"] == 3
    assert result["topology"]["out_of_band_check_count"] == 2
    assert result["topology"]["checker_kept_out_of_band"] is True
    assert result["topology"]["topology_reference_freshness_policy_kept_out_of_band"] is True
    assert result["topology"]["topology_reference_freshness_policy_not_missing_provenance"] is True
    assert "out_of_band_topology_report_reference_freshness_policy" in result["sources"]
    assert result["safe_to_auto_clear_warnings"] is False
    assert result["safe_to_auto_publish"] is False
    caveat = result["research_caveat"].lower()
    for fragment in ["not legal compliance", "signature validation", "supervision", "public alerting", "publication approval"]:
        assert fragment in caveat


def test_fixture_flags_wired_out_of_band_checker() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "notes").mkdir()
        for rel in [
            "notes/release-readiness-checklist-validation-output.json",
            "notes/release-readiness-warning-report-output.json",
            "notes/release-readiness-gate-summary-output.json",
            "notes/status-only-release-gates-report-output.json",
            "notes/status-only-report-reference-checker-policy-validation-output.json",
            "notes/topology-report-reference-freshness-policy-validation-output.json",
        ]:
            source = WORKSPACE / rel
            dest = root / rel
            dest.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        checklist_path = root / "notes/release-readiness-checklist-validation-output.json"
        checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
        checklist["validators"].append({
            "name": "status_only_report_reference_checker_policy",
            "path": "notes/status-only-report-reference-checker-policy-validation-output.json",
            "exists": True,
            "status": "ok",
            "warning_count": 1,
            "hash_policy": "fixture_should_remain_out_of_band",
        })
        checklist["validator_count"] = len(checklist["validators"])
        checklist_path.write_text(json.dumps(checklist, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = topology.report(root)
        assert result["status"] == "needs_review"
        assert any("out-of-band checker policy appears wired" in error for error in result["errors"])


def test_fixture_flags_wired_topology_reference_freshness_policy() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "notes").mkdir()
        for rel in [
            "notes/release-readiness-checklist-validation-output.json",
            "notes/release-readiness-warning-report-output.json",
            "notes/release-readiness-gate-summary-output.json",
            "notes/status-only-release-gates-report-output.json",
            "notes/status-only-report-reference-checker-policy-validation-output.json",
            "notes/topology-report-reference-freshness-policy-validation-output.json",
        ]:
            source = WORKSPACE / rel
            dest = root / rel
            dest.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        checklist_path = root / "notes/release-readiness-checklist-validation-output.json"
        checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
        checklist["validators"].append({
            "name": "topology_report_reference_freshness_policy",
            "path": "notes/topology-report-reference-freshness-policy-validation-output.json",
            "exists": True,
            "status": "ok",
            "warning_count": 1,
            "hash_policy": "fixture_should_remain_out_of_band",
        })
        checklist["validator_count"] = len(checklist["validators"])
        checklist_path.write_text(json.dumps(checklist, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = topology.report(root)
        assert result["status"] == "needs_review"
        assert any("topology-reference freshness policy appears wired" in error for error in result["errors"])


if __name__ == "__main__":
    test_live_report_ok_and_non_mutating()
    test_fixture_flags_wired_out_of_band_checker()
    test_fixture_flags_wired_topology_reference_freshness_policy()
    print(json.dumps({"status": "ok", "tests": 3}, indent=2, sort_keys=True))
