#!/usr/bin/env python3
"""Smoke tests for release-readiness context-consistency out-of-band policy."""
from __future__ import annotations

import json
import pathlib
import tempfile

import validate_release_readiness_context_consistency_policy as policy

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    policy.POLICY_REL,
    policy.CHECKER_OUTPUT_REL,
    policy.CHECKLIST_VALIDATOR_REL,
    policy.TOPOLOGY_HELPER_REL,
    policy.TOPOLOGY_OUTPUT_REL,
    policy.WARNING_REPORT_REL,
    policy.GATE_SUMMARY_REL,
    policy.STATUS_ONLY_REL,
]


def sha(path: pathlib.Path) -> str:
    return policy.sha256_path(path)


def copy_fixture(root: pathlib.Path) -> None:
    for rel in REQUIRED_FILES:
        source = WORKSPACE / rel
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def test_live_policy_ok_and_non_mutating() -> None:
    watched = [WORKSPACE / rel for rel in REQUIRED_FILES]
    before = {str(path): sha(path) for path in watched}
    result = policy.validate(WORKSPACE)
    after = {str(path): sha(path) for path in watched}
    assert before == after
    assert result["status"] == "ok", result
    assert result["error_count"] == 0
    assert result["decision"]["checker_kept_out_of_band"] is True
    assert result["decision"]["safe_to_wire_into_checklist_without_operator_review"] is False
    assert result["decision"]["safe_to_wire_into_topology_without_operator_review"] is False
    assert result["decision"]["not_missing_provenance"] is True
    caveat = result["research_caveat"].lower()
    for fragment in ["not legal compliance", "trusted-list legal effect", "signature validation", "supervision", "public alerting", "publication approval"]:
        assert fragment in caveat


def test_fixture_flags_checklist_wiring() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        copy_fixture(root)
        checklist = root / policy.CHECKLIST_VALIDATOR_REL
        checklist.write_text(checklist.read_text(encoding="utf-8") + "\n# release-readiness-context-consistency-validation-output.json\n", encoding="utf-8")
        result = policy.validate(root)
        assert result["status"] == "needs_review"
        assert any("release-readiness checklist" in error for error in result["errors"])


def test_fixture_flags_topology_wiring() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        copy_fixture(root)
        topology = root / policy.TOPOLOGY_HELPER_REL
        topology.write_text(topology.read_text(encoding="utf-8") + "\n# release_readiness_context_consistency\n", encoding="utf-8")
        result = policy.validate(root)
        assert result["status"] == "needs_review"
        assert any("topology report helper" in error for error in result["errors"])


def test_fixture_flags_missing_policy_caveat() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        copy_fixture(root)
        note = root / policy.POLICY_REL
        text = note.read_text(encoding="utf-8").replace("not missing provenance", "")
        note.write_text(text, encoding="utf-8")
        result = policy.validate(root)
        assert result["status"] == "needs_review"
        assert any("not missing provenance" in error for error in result["errors"])


if __name__ == "__main__":
    test_live_policy_ok_and_non_mutating()
    test_fixture_flags_checklist_wiring()
    test_fixture_flags_topology_wiring()
    test_fixture_flags_missing_policy_caveat()
    print(json.dumps({"status": "ok", "tests": 4}, indent=2, sort_keys=True))
