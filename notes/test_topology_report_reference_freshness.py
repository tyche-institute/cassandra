#!/usr/bin/env python3
"""Smoke tests for validate_topology_report_reference_freshness.py."""
from __future__ import annotations

import json
import pathlib
import tempfile

import validate_topology_report_reference_freshness as validator


def test_live_workspace_non_mutating() -> None:
    workspace = pathlib.Path(__file__).resolve().parents[1]
    before = {
        rel: (workspace / rel).read_bytes()
        for rel in [
            validator.TOPOLOGY_REPORT,
            validator.PAPER,
            validator.ARTIFACT_INDEX,
        ]
    }
    result = validator.validate(workspace)
    assert result["status"] == "ok", json.dumps(result, indent=2)
    assert result["error_count"] == 0
    assert result["artifact_index"]["current_hash_indexed"] is True
    assert result["paper_reference"]["line"] is not None
    for rel, content in before.items():
        assert (workspace / rel).read_bytes() == content


def write_minimal_report_and_paper(workspace: pathlib.Path) -> pathlib.Path:
    (workspace / "notes").mkdir()
    (workspace / "paper").mkdir()
    report = workspace / "notes" / "release-readiness-topology-report-output.json"
    report.write_text(
        json.dumps(
            {
                "status": "ok",
                "error_count": 0,
                "warning_count": 0,
                "safe_to_auto_clear_warnings": False,
                "safe_to_auto_publish": False,
                "research_caveat": "not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, publication approval",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (workspace / "paper" / "draft.md").write_text(
        "## Release-readiness checklist for operator review\n"
        "This references the release-readiness topology report at "
        "notes/release-readiness-topology-report-output.json. It is not an additional release gate "
        "and not a release decision.\n",
        encoding="utf-8",
    )
    return report


def test_detects_stale_artifact_index_hash() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        write_minimal_report_and_paper(workspace)
        (workspace / "ARTIFACT_INDEX.md").write_text(
            "| Path | Purpose | sha256 | Verified |\n"
            "|---|---|---|---|\n"
            "| `notes/release-readiness-topology-report-output.json` | stale | `sha256:"
            + "0" * 64
            + "` | no |\n",
            encoding="utf-8",
        )
        result = validator.validate(workspace)
        assert result["status"] == "needs_review"
        assert any("hash mismatch" in error for error in result["errors"])


def test_allows_refreshed_artifact_index_row_with_stale_duplicate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        report = write_minimal_report_and_paper(workspace)
        digest = validator.sha256_path(report)
        (workspace / "ARTIFACT_INDEX.md").write_text(
            "| Path | Purpose | sha256 | Verified |\n"
            "|---|---|---|---|\n"
            "| `notes/release-readiness-topology-report-output.json` | expired before refresh | `sha256:"
            + "0" * 64
            + "` | historical duplicate |\n"
            f"| `notes/release-readiness-topology-report-output.json` | refreshed current row | `sha256:{digest}` | yes |\n",
            encoding="utf-8",
        )
        result = validator.validate(workspace)
        assert result["status"] == "ok", json.dumps(result, indent=2)
        assert result["error_count"] == 0
        assert result["artifact_index"]["current_hash_indexed"] is True
        assert any("multiple rows" in warning for warning in result["warnings"])


def test_detects_missing_paper_reference() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        workspace = pathlib.Path(tmp)
        (workspace / "notes").mkdir()
        (workspace / "paper").mkdir()
        report = workspace / "notes" / "release-readiness-topology-report-output.json"
        report.write_text(
            json.dumps(
                {
                    "status": "ok",
                    "error_count": 0,
                    "warning_count": 0,
                    "safe_to_auto_clear_warnings": False,
                    "safe_to_auto_publish": False,
                    "research_caveat": "not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, publication approval",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        digest = validator.sha256_path(report)
        (workspace / "paper" / "draft.md").write_text("## Release-readiness checklist for operator review\nNo path here.\n", encoding="utf-8")
        (workspace / "ARTIFACT_INDEX.md").write_text(
            "| Path | Purpose | sha256 | Verified |\n"
            "|---|---|---|---|\n"
            f"| `notes/release-readiness-topology-report-output.json` | current | `sha256:{digest}` | yes |\n",
            encoding="utf-8",
        )
        result = validator.validate(workspace)
        assert result["status"] == "needs_review"
        assert any("paper lacks required topology-report fragment" in error for error in result["errors"])


if __name__ == "__main__":
    test_live_workspace_non_mutating()
    test_detects_stale_artifact_index_hash()
    test_allows_refreshed_artifact_index_row_with_stale_duplicate()
    test_detects_missing_paper_reference()
    print(json.dumps({"status": "ok", "tests": 4}, indent=2, sort_keys=True))
