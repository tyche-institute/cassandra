#!/usr/bin/env python3
"""Smoke tests for daily-cadence status reporting."""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from notes import report_daily_cadence_status as report


def touch(path: pathlib.Path, content: str = "{}\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def seed_completed_date(workspace: pathlib.Path, date: str) -> None:
    touch(workspace / "snapshots" / date / "manifest.json")
    touch(workspace / "normalized" / date / "manifest.json")
    touch(workspace / "bundles" / date / "snapshot-summary.json")
    touch(workspace / "diffs" / f"{date}.json")
    touch(workspace / "baselines" / f"{date}.json")


def test_live_workspace_reports_ok() -> None:
    result = report.validate(WORKSPACE, today="2026-05-21")
    assert result["status"] == "ok", result
    assert result["latest_completed_date"] == "2026-05-22", result
    assert result["today_complete"] is True, result
    assert result["today_guard"]["status"] == "refused_existing_outputs", result
    assert result["next_eligible_date"] == "2026-05-23", result
    assert result["next_eligible_guard"]["status"] == "dry_run_ok", result
    assert result["future_completed_dates_relative_to_today"] == ["2026-05-22"], result
    assert any("future-dated completed local lineage" in warning for warning in result["warnings"]), result
    assert "publication approval" in result["research_caveat"], result


def test_future_today_without_completed_lineage_dry_runs() -> None:
    with tempfile.TemporaryDirectory() as td:
        workspace = pathlib.Path(td)
        seed_completed_date(workspace, "2026-05-20")
        result = report.validate(workspace, today="2026-05-21")
        assert result["status"] == "ok", result
        assert result["today_complete"] is False, result
        assert result["today_guard"]["status"] == "dry_run_ok", result
        assert result["next_eligible_date"] == "2026-05-21", result
        assert result["next_eligible_guard"]["status"] == "dry_run_ok", result
        assert result["future_completed_dates_relative_to_today"] == [], result


def test_future_dated_completed_lineage_warns_without_blocking() -> None:
    with tempfile.TemporaryDirectory() as td:
        workspace = pathlib.Path(td)
        seed_completed_date(workspace, "2026-05-21")
        seed_completed_date(workspace, "2026-05-22")
        result = report.validate(workspace, today="2026-05-21")
        assert result["status"] == "ok", result
        assert result["latest_completed_date"] == "2026-05-22", result
        assert result["future_completed_dates_relative_to_today"] == ["2026-05-22"], result
        assert result["next_eligible_date"] == "2026-05-23", result
        assert any("future-dated completed local lineage" in warning for warning in result["warnings"]), result
        assert "publication approval" in result["research_caveat"], result


def test_missing_state_warns_but_does_not_claim_status() -> None:
    with tempfile.TemporaryDirectory() as td:
        workspace = pathlib.Path(td)
        result = report.validate(workspace, today="2026-05-21")
        assert result["status"] == "ok", result
        assert result["completed_date_count"] == 0, result
        assert result["warnings"], result
        assert "legal effect" in result["research_caveat"], result


def main() -> int:
    tests = [
        test_live_workspace_reports_ok,
        test_future_today_without_completed_lineage_dry_runs,
        test_future_dated_completed_lineage_warns_without_blocking,
        test_missing_state_warns_but_does_not_claim_status,
    ]
    for test in tests:
        test()
    print(json.dumps({"status": "ok", "tests": [t.__name__ for t in tests]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
