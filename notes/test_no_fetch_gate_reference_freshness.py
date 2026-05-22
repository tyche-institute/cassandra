#!/usr/bin/env python3
"""Smoke tests for no-fetch gate reference freshness validation."""
from __future__ import annotations

import json
import pathlib
import tempfile

import validate_no_fetch_gate_reference_freshness as validator


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
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="cassandra-no-fetch-ref-"))
    write(tmp / "paper/draft.md", paper_text)
    no_fetch = {
        "status": "ok",
        "error_count": 0,
        "warning_count": 0,
        "live_today_utc": "2026-05-21",
        "snapshot_output_roots_mutated": [],
        "today_guard": {"status": "refused_existing_outputs"},
        "next_eligible_guard": {"status": "dry_run_ok"},
        "cadence_report": {
            "path": "notes/daily-cadence-status-output.json",
            "latest_completed_date": "2026-05-22",
            "next_eligible_date": "2026-05-23",
        },
        "research_caveat": "Local no-fetch gate validation for Cassandra workflow scheduling only; not endpoint stability evidence, legal compliance, trusted-list legal effect, signature validation, supervision, listed-entity status evidence, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
    }
    write(tmp / "notes/no-fetch-before-gate-validation-output.json", json.dumps(no_fetch, indent=2, sort_keys=True) + "\n")
    current = validator.sha256_path(tmp / "notes/no-fetch-before-gate-validation-output.json")
    index_hash = index_hash or current
    write(
        tmp / "ARTIFACT_INDEX.md",
        "# Artifact index\n\n"
        f"| `notes/no-fetch-before-gate-validation-output.json` | fixture | `sha256:{index_hash}` | yes |\n",
    )
    return tmp


def test_missing_paper_reference() -> dict:
    root = fixture_workspace(
        paper_text="No-fetch gate checks are useful workflow scheduling telemetry, but this fixture omits the concrete reference and caveats."
    )
    result = validator.validate(root)
    assert result["status"] == "needs_review", result
    assert any("paper lacks no-fetch gate" in err for err in result["errors"]), result
    return {"name": "missing_paper_reference", "status": "ok"}


def test_stale_artifact_index_hash() -> dict:
    paper = (
        "The report `notes/no-fetch-before-gate-validation-output.json` is workflow scheduling telemetry and does not assert endpoint stability, "
        "legal effect, signature validation, public alerting, warning clearance, or publication approval."
    )
    root = fixture_workspace(paper_text=paper, index_hash="0" * 64)
    result = validator.validate(root)
    assert result["status"] == "needs_review", result
    assert any("lacks current sha256" in err for err in result["errors"]), result
    return {"name": "stale_artifact_index_hash", "status": "ok"}


def test_mutation_detection() -> dict:
    paper = (
        "The report `notes/no-fetch-before-gate-validation-output.json` is workflow scheduling telemetry and not endpoint stability evidence; "
        "it does not assert legal effect, signature validation, public alerting, warning clearance, or publication approval."
    )
    root = fixture_workspace(paper_text=paper)
    data = json.loads((root / "notes/no-fetch-before-gate-validation-output.json").read_text(encoding="utf-8"))
    data["snapshot_output_roots_mutated"] = ["snapshots/2026-05-23"]
    write(root / "notes/no-fetch-before-gate-validation-output.json", json.dumps(data, indent=2, sort_keys=True) + "\n")
    current = validator.sha256_path(root / "notes/no-fetch-before-gate-validation-output.json")
    write(
        root / "ARTIFACT_INDEX.md",
        "# Artifact index\n\n"
        f"| `notes/no-fetch-before-gate-validation-output.json` | fixture | `sha256:{current}` | yes |\n",
    )
    result = validator.validate(root)
    assert result["status"] == "needs_review", result
    assert any("snapshot output root mutation" in err for err in result["errors"]), result
    return {"name": "mutation_detection", "status": "ok"}


def main() -> int:
    tests = [
        test_live_workspace(),
        test_missing_paper_reference(),
        test_stale_artifact_index_hash(),
        test_mutation_detection(),
    ]
    print(json.dumps({"status": "ok", "tests": tests}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
