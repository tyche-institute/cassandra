#!/usr/bin/env python3
"""Smoke tests for validate_no_fetch_before_gate.py."""
from __future__ import annotations

import json
import pathlib
import tempfile

import validate_no_fetch_before_gate as gate


def write_json(path: pathlib.Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_workspace() -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp(prefix="cassandra-no-fetch-gate-test-"))
    for rel in [
        "snapshots/2026-05-22/manifest.json",
        "normalized/2026-05-22/manifest.json",
        "diffs/2026-05-22.json",
        "baselines/2026-05-22.json",
    ]:
        write_json(root / rel, {"ok": True})
    write_json(root / "notes/daily-cadence-status-output.json", {
        "status": "ok",
        "today_utc": "2026-05-21",
        "latest_completed_date": "2026-05-22",
        "next_eligible_date": "2026-05-23",
        "future_completed_dates_relative_to_today": ["2026-05-22"],
    })
    return root


def test_future_dated_lineage_gate_ok() -> None:
    workspace = make_workspace()
    result = gate.validate(
        workspace,
        workspace / "notes/daily-cadence-status-output.json",
        today_utc="2026-05-21",
    )
    assert result["status"] == "ok", result
    assert result["today_guard"]["status"] == "dry_run_ok"
    assert result["next_eligible_guard"]["status"] == "dry_run_ok"
    assert result["snapshot_output_roots_mutated"] == []


def test_same_date_existing_outputs_refused() -> None:
    workspace = make_workspace()
    write_json(workspace / "snapshots/2026-05-21/manifest.json", {"ok": True})
    write_json(workspace / "normalized/2026-05-21/manifest.json", {"ok": True})
    write_json(workspace / "diffs/2026-05-21.json", {"ok": True})
    write_json(workspace / "baselines/2026-05-21.json", {"ok": True})
    result = gate.validate(
        workspace,
        workspace / "notes/daily-cadence-status-output.json",
        today_utc="2026-05-21",
    )
    assert result["status"] == "ok", result
    assert result["today_guard"]["status"] == "refused_existing_outputs"
    assert "snapshots/2026-05-21" in result["today_guard"]["existing_outputs"]


def test_missing_future_warning_detected() -> None:
    workspace = make_workspace()
    cadence_path = workspace / "notes/daily-cadence-status-output.json"
    cadence = json.loads(cadence_path.read_text(encoding="utf-8"))
    cadence["future_completed_dates_relative_to_today"] = []
    write_json(cadence_path, cadence)
    result = gate.validate(workspace, cadence_path, today_utc="2026-05-21")
    assert result["status"] == "needs_review", result
    assert any("future completed lineage exists" in error for error in result["errors"])


def main() -> int:
    tests = [
        test_future_dated_lineage_gate_ok,
        test_same_date_existing_outputs_refused,
        test_missing_future_warning_detected,
    ]
    failures: list[str] = []
    for test in tests:
        try:
            test()
        except Exception as exc:  # pragma: no cover - standalone smoke runner
            failures.append(f"{test.__name__}: {exc}")
    result = {"status": "ok" if not failures else "failed", "test_count": len(tests), "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
