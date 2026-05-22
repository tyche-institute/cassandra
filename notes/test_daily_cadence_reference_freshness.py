#!/usr/bin/env python3
"""Smoke tests for daily-cadence reference freshness validation."""
from __future__ import annotations

import json
import pathlib
import tempfile

import validate_daily_cadence_reference_freshness as validator


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_live_workspace() -> dict:
    root = pathlib.Path(__file__).resolve().parents[1]
    before = (root / "ARTIFACT_INDEX.md").read_text(encoding="utf-8")
    result = validator.validate(root)
    after = (root / "ARTIFACT_INDEX.md").read_text(encoding="utf-8")
    assert before == after, "validator must not mutate ARTIFACT_INDEX.md"
    assert result["status"] == "ok", result
    assert result["current_hash_indexed"] is True, result
    return {"name": "live_workspace", "status": "ok", "warning_count": result["warning_count"]}


def fixture_workspace(*, paper_text: str, index_hash: str | None = None) -> pathlib.Path:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cassandra-cadence-ref-"))
    write(tmp / "paper/draft.md", paper_text)
    cadence = {
        "status": "ok",
        "error_count": 0,
        "warning_count": 1,
        "today_utc": "2026-05-21",
        "today_complete": True,
        "today_guard": {"status": "refused_existing_outputs"},
        "next_eligible_guard": {"status": "dry_run_ok"},
        "latest_completed_date": "2026-05-21",
        "next_eligible_date": "2026-05-22",
        "research_caveat": "Local daily-cadence workflow telemetry only; same-date guard status is not endpoint stability evidence, legal compliance, trusted-list legal effect, signature validation, supervision, listed-entity status evidence, public alerting, regulated trust-service output, or publication approval.",
    }
    write(tmp / "notes/daily-cadence-status-output.json", json.dumps(cadence, indent=2, sort_keys=True) + "\n")
    current = validator.sha256_path(tmp / "notes/daily-cadence-status-output.json")
    index_hash = index_hash or current
    write(
        tmp / "ARTIFACT_INDEX.md",
        "# Artifact index\n\n"
        f"| `notes/daily-cadence-status-output.json` | fixture | `sha256:{index_hash}` | yes |\n",
    )
    return tmp


def test_missing_paper_reference() -> dict:
    root = fixture_workspace(
        paper_text="Daily cadence is useful workflow telemetry but this fixture omits the concrete reference and caveats."
    )
    result = validator.validate(root)
    assert result["status"] == "needs_review", result
    assert any("paper lacks daily-cadence" in err for err in result["errors"]), result
    return {"name": "missing_paper_reference", "status": "ok"}


def test_stale_artifact_index_hash() -> dict:
    paper = (
        "The report `notes/daily-cadence-status-output.json` is workflow telemetry and does not assert endpoint stability, "
        "legal effect, signature validity, public alerting, or publication approval."
    )
    root = fixture_workspace(paper_text=paper, index_hash="0" * 64)
    result = validator.validate(root)
    assert result["status"] == "needs_review", result
    assert any("lacks current sha256" in err for err in result["errors"]), result
    return {"name": "stale_artifact_index_hash", "status": "ok"}


def main() -> int:
    tests = [test_live_workspace(), test_missing_paper_reference(), test_stale_artifact_index_hash()]
    print(json.dumps({"status": "ok", "tests": tests}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
