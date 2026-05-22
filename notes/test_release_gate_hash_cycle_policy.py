#!/usr/bin/env python3
"""Smoke test for release gate hash-cycle policy report."""
from __future__ import annotations

import json
import pathlib
import tempfile

import report_release_gate_hash_cycle_policy as policy


def test_live_report() -> None:
    workspace = pathlib.Path(__file__).resolve().parents[1]
    before = (workspace / "notes/release-readiness-checklist-validation-output.json").read_bytes()
    result = policy.report(workspace)
    after = (workspace / "notes/release-readiness-checklist-validation-output.json").read_bytes()
    assert before == after, "policy report must not mutate checklist validation output"
    assert result["status"] == "ok", result["errors"]
    assert result["policy"]["not_missing_provenance"] is True
    assert result["policy"]["hash_policy"] == policy.STATUS_ONLY_POLICY
    freshness_input = result["inputs"]["release_gate_summary_freshness"]
    assert freshness_input["checklist_record_hash_policy"] == policy.STATUS_ONLY_POLICY
    assert freshness_input["checklist_record_has_sha256"] is False
    caveat = result["research_caveat"].lower()
    for fragment in [
        "not publication approval",
        "legal review",
        "signature validation",
        "trusted-list supervision",
        "listed-entity status",
        "public alerting",
        "regulated trust-service output",
    ]:
        assert fragment in caveat


def test_missing_hash_policy_fixture() -> None:
    workspace = pathlib.Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        notes = root / "notes"
        notes.mkdir()
        for rel in [
            policy.CHECKLIST_REL,
            policy.SUMMARY_REL,
            policy.FRESHNESS_REL,
            policy.CHECKLIST_VALIDATOR_REL,
        ]:
            src = workspace / rel
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
        checklist_path = root / policy.CHECKLIST_REL
        checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
        for record in checklist["validators"]:
            if record.get("name") == "release_gate_summary_freshness":
                record.pop("hash_policy", None)
                record["sha256"] = "0" * 64
        checklist_path.write_text(json.dumps(checklist, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = policy.report(root)
        assert result["status"] == "needs_review"
        assert any("lacks expected status-only hash policy" in error for error in result["errors"])
        assert any("unexpectedly contains sha256" in error for error in result["errors"])


if __name__ == "__main__":
    test_live_report()
    test_missing_hash_policy_fixture()
    print(json.dumps({"status": "ok", "tests": 2}, indent=2, sort_keys=True))
