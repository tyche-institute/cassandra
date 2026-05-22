#!/usr/bin/env python3
"""Validate that cadence-gated maintenance did not run a real daily fetch.

This local checker is intentionally read-only with respect to Cassandra snapshot,
normalization, diff, and bundle directories. It is workflow telemetry only: it
must not be interpreted as endpoint stability evidence, legal effect, signature
validation, supervision, public alerting, listed-entity status evidence,
regulated trust-service output, legal review, warning clearance, or publication
approval.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys
from typing import Any

WORKSPACE_MODULE_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(WORKSPACE_MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_MODULE_ROOT))

import run_daily

SCHEMA = "urn:tyche:cassandra:no-fetch-before-gate:0.1"
RESEARCH_CAVEAT = (
    "Local no-fetch gate validation for Cassandra workflow scheduling only; "
    "not endpoint stability evidence, legal compliance, trusted-list legal "
    "effect, signature validation, supervision, listed-entity status evidence, "
    "public alerting, regulated trust-service output, legal review, warning "
    "clearance, or publication approval."
)
SNAPSHOT_OUTPUT_ROOTS = ("snapshots", "normalized", "diffs", "baselines", "bundles")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def list_state(workspace: pathlib.Path) -> dict[str, list[str]]:
    state: dict[str, list[str]] = {}
    for rel in SNAPSHOT_OUTPUT_ROOTS:
        root = workspace / rel
        if not root.exists():
            state[rel] = []
            continue
        paths: list[str] = []
        for path in root.rglob("*"):
            if path.is_file():
                paths.append(str(path.relative_to(workspace)))
        state[rel] = sorted(paths)
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--cadence", default="notes/daily-cadence-status-output.json")
    parser.add_argument("--output", default="notes/no-fetch-before-gate-validation-output.json")
    parser.add_argument("--today-utc", help="Override UTC date for deterministic tests.")
    return parser.parse_args()


def validate(workspace: pathlib.Path, cadence_path: pathlib.Path, today_utc: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    before_state = list_state(workspace)

    if not cadence_path.exists():
        errors.append(f"missing cadence report: {cadence_path.relative_to(workspace)}")
        cadence: dict[str, Any] = {}
    else:
        cadence = json.loads(cadence_path.read_text(encoding="utf-8"))

    live_today = today_utc or dt.datetime.now(dt.timezone.utc).date().isoformat()
    cadence_today = cadence.get("today_utc")
    latest_completed = cadence.get("latest_completed_date")
    next_eligible = cadence.get("next_eligible_date")
    future_dates = cadence.get("future_completed_dates_relative_to_today") or []

    if cadence.get("status") != "ok":
        errors.append("cadence report status is not ok")
    if cadence_today != live_today:
        warnings.append(
            f"cadence today_utc {cadence_today!r} differs from live/override date {live_today!r}; refresh cadence report before real fetch decisions"
        )
    if latest_completed and latest_completed >= live_today:
        if next_eligible <= latest_completed:
            errors.append("next_eligible_date does not advance beyond latest_completed_date")
        if not future_dates and latest_completed > live_today:
            errors.append("future completed lineage exists by date comparison but cadence report did not flag it")

    today_guard = run_daily.run_daily(
        workspace=workspace,
        date=live_today,
        baseline_date=None,
        no_update_baseline=False,
        allow_existing=False,
        dry_run=True,
    )
    next_guard = None
    if next_eligible:
        next_guard = run_daily.run_daily(
            workspace=workspace,
            date=next_eligible,
            baseline_date=None,
            no_update_baseline=False,
            allow_existing=False,
            dry_run=True,
        )
        if next_eligible > latest_completed and next_guard.get("status") != "dry_run_ok":
            errors.append("next eligible dry-run guard is not dry_run_ok")
        if next_guard.get("existing_outputs"):
            warnings.append("next eligible dry-run reports existing outputs; confirm before any real fetch")

    after_state = list_state(workspace)
    mutated_roots = [root for root in SNAPSHOT_OUTPUT_ROOTS if before_state.get(root) != after_state.get(root)]
    if mutated_roots:
        errors.append(f"validator mutated snapshot output roots: {mutated_roots}")

    out = {
        "schema": SCHEMA,
        "created": dt.datetime.now(dt.timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "errors": errors,
        "warning_count": len(warnings),
        "warnings": warnings,
        "cadence_report": {
            "path": str(cadence_path.relative_to(workspace)) if cadence_path.is_relative_to(workspace) else str(cadence_path),
            "sha256": sha256_file(cadence_path) if cadence_path.exists() else None,
            "status": cadence.get("status"),
            "today_utc": cadence_today,
            "latest_completed_date": latest_completed,
            "next_eligible_date": next_eligible,
            "future_completed_dates_relative_to_today": future_dates,
        },
        "live_today_utc": live_today,
        "today_guard": {
            "status": today_guard.get("status"),
            "dry_run": today_guard.get("dry_run"),
            "existing_outputs": today_guard.get("existing_outputs"),
        },
        "next_eligible_guard": None if next_guard is None else {
            "status": next_guard.get("status"),
            "dry_run": next_guard.get("dry_run"),
            "existing_outputs": next_guard.get("existing_outputs"),
            "planned_steps": next_guard.get("planned_steps"),
        },
        "snapshot_output_roots_mutated": mutated_roots,
        "research_caveat": RESEARCH_CAVEAT,
    }
    return out


def main() -> int:
    args = parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    cadence_path = (workspace / args.cadence).resolve()
    output_path = (workspace / args.output).resolve()
    result = validate(workspace, cadence_path, today_utc=args.today_utc)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
