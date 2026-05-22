#!/usr/bin/env python3
"""Report Cassandra daily-cadence status without fetching or overwriting.

This local workflow-maintenance report distinguishes same-date non-overwrite
state from endpoint or legal-status observations. It does not fetch public
trusted-list material, validate signatures, supervise trusted lists, provide
public alerting, determine listed-entity status, create regulated trust-service
output, or approve publication.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from hashlib import sha256
from typing import Any

WORKSPACE_MODULE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(WORKSPACE_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_MODULE_DIR))

import run_daily

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RESEARCH_CAVEAT = (
    "Local daily-cadence workflow telemetry only; same-date guard status is not "
    "endpoint stability evidence, legal compliance, trusted-list legal effect, "
    "signature validation, supervision, listed-entity status evidence, public "
    "alerting, regulated trust-service output, or publication approval."
)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def sha256_file(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dated_dirs(base: pathlib.Path) -> set[str]:
    if not base.exists():
        return set()
    return {p.name for p in base.iterdir() if p.is_dir() and DATE_RE.match(p.name)}


def dated_json_stems(base: pathlib.Path) -> set[str]:
    if not base.exists():
        return set()
    return {p.stem for p in base.glob("*.json") if DATE_RE.match(p.stem)}


def completed_dates(workspace: pathlib.Path) -> list[str]:
    return sorted(
        dated_dirs(workspace / "snapshots")
        & dated_dirs(workspace / "normalized")
        & dated_dirs(workspace / "bundles")
        & dated_json_stems(workspace / "diffs")
        & dated_json_stems(workspace / "baselines")
    )


def validate(workspace: pathlib.Path, *, today: str | None = None) -> dict[str, Any]:
    workspace = workspace.resolve()
    created = now_utc()
    today = today or created.date().isoformat()
    errors: list[str] = []
    warnings: list[str] = []

    completed = completed_dates(workspace)
    latest = completed[-1] if completed else None
    today_complete = today in completed
    future_completed = [date for date in completed if date > today]

    today_guard = run_daily.run_daily(
        workspace,
        today,
        baseline_date=latest,
        no_update_baseline=True,
        allow_existing=False,
        dry_run=True,
    )
    expected_today_status = "refused_existing_outputs" if today_complete else "dry_run_ok"
    if today_guard.get("status") != expected_today_status:
        errors.append(
            "today daily guard status mismatch: "
            f"expected {expected_today_status}, got {today_guard.get('status')}"
        )
    if today_complete and not today_guard.get("existing_outputs"):
        errors.append("today is complete but same-date guard did not list existing outputs")

    next_date = (dt.date.fromisoformat(latest) + dt.timedelta(days=1)).isoformat() if latest else today
    next_guard = run_daily.run_daily(
        workspace,
        next_date,
        baseline_date=latest,
        no_update_baseline=True,
        allow_existing=False,
        dry_run=True,
    )
    if next_date in completed:
        expected_next_status = "refused_existing_outputs"
    else:
        expected_next_status = "dry_run_ok"
    if next_guard.get("status") != expected_next_status:
        errors.append(
            "next eligible daily dry-run status mismatch: "
            f"expected {expected_next_status}, got {next_guard.get('status')}"
        )

    if today_complete:
        warnings.append(
            "today already has a completed local lineage; do not rerun same-date fetch without explicit operator-controlled overwrite intent"
        )
    if future_completed:
        warnings.append(
            "future-dated completed local lineage exists relative to today_utc; treat cadence output as workflow-scheduling telemetry, not endpoint/status evidence"
        )
    if not completed:
        warnings.append("no completed local dated lineage found; bootstrap state should be reviewed before collection")

    artifacts: list[dict[str, str]] = []
    for rel in [
        f"snapshots/{latest}/manifest.json" if latest else None,
        f"normalized/{latest}/manifest.json" if latest else None,
        f"diffs/{latest}.json" if latest else None,
        f"baselines/{latest}.json" if latest else None,
    ]:
        if rel is None:
            continue
        path = workspace / rel
        if path.exists():
            artifacts.append({"path": rel, "sha256": sha256_file(path)})

    return {
        "schema": "urn:tyche:cassandra:daily-cadence-status:0.1",
        "created": created.isoformat(),
        "workspace": str(workspace),
        "today_utc": today,
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "completed_dates": completed,
        "completed_date_count": len(completed),
        "latest_completed_date": latest,
        "future_completed_dates_relative_to_today": future_completed,
        "today_complete": today_complete,
        "today_guard": {
            "status": today_guard.get("status"),
            "existing_outputs": today_guard.get("existing_outputs"),
            "dry_run": today_guard.get("dry_run"),
        },
        "next_eligible_date": next_date,
        "next_eligible_guard": {
            "status": next_guard.get("status"),
            "existing_outputs": next_guard.get("existing_outputs"),
            "planned_steps": next_guard.get("planned_steps"),
            "dry_run": next_guard.get("dry_run"),
        },
        "artifacts_checked": artifacts,
        "research_caveat": RESEARCH_CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--today", help="Override UTC date for deterministic tests, YYYY-MM-DD")
    parser.add_argument("--output", default="notes/daily-cadence-status-output.json")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace, today=args.today)
    output = pathlib.Path(args.output)
    if not output.is_absolute():
        output = workspace / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
