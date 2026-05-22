#!/usr/bin/env python3
"""Orchestrate one non-overwriting Cassandra daily snapshot run.

Research-only helper: fetches public LOTL-derived snapshot inputs, normalizes
XML-like artifacts, and emits structural diffs. It does not perform
relying-party validation, supervision, signature verification, legal-status
determination, or external publication.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from typing import Any

import diff as diff_engine
import fetch
import parse

RESEARCH_CAVEAT = (
    "Daily Cassandra run orchestration for structural observation only; not "
    "signature validation, supervision, legal-status determination, relying-party "
    "processing, or public alerting."
)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def existing_outputs(workspace: pathlib.Path, date: str) -> list[str]:
    candidates = [
        workspace / "snapshots" / date,
        workspace / "normalized" / date,
        workspace / "diffs" / f"{date}.json",
        workspace / "baselines" / f"{date}.json",
    ]
    return [str(path.relative_to(workspace)) for path in candidates if path.exists()]


def summarize_run(
    *,
    workspace: pathlib.Path,
    date: str,
    snapshot_manifest: dict[str, Any] | None,
    normalized_manifest: dict[str, Any] | None,
    diff_doc: dict[str, Any] | None,
    dry_run: bool,
    existing: list[str],
) -> dict[str, Any]:
    return {
        "created": now_iso(),
        "date": date,
        "dry_run": dry_run,
        "existing_outputs": existing,
        "snapshot": None if snapshot_manifest is None else {
            "path": f"snapshots/{date}/manifest.json",
            "count": snapshot_manifest.get("count"),
            "ok_count": snapshot_manifest.get("ok_count"),
            "error_count": snapshot_manifest.get("error_count"),
        },
        "normalization": None if normalized_manifest is None else {
            "path": f"normalized/{date}/manifest.json",
            "count": normalized_manifest.get("count"),
            "ok_count": normalized_manifest.get("ok_count"),
            "skipped_count": normalized_manifest.get("skipped_count"),
            "error_count": normalized_manifest.get("error_count"),
        },
        "diff": None if diff_doc is None else {
            "path": f"diffs/{date}.json",
            "baseline_source": diff_doc.get("baseline_source"),
            "current_record_count": diff_doc.get("current_record_count"),
            "change_count": diff_doc.get("change_count"),
            "summary": diff_doc.get("summary"),
        },
        "research_caveat": RESEARCH_CAVEAT,
    }


def run_daily(
    workspace: pathlib.Path,
    date: str,
    *,
    baseline_date: str | None,
    no_update_baseline: bool,
    allow_existing: bool,
    dry_run: bool,
) -> dict[str, Any]:
    existing = existing_outputs(workspace, date)
    if existing and not allow_existing:
        result = summarize_run(
            workspace=workspace,
            date=date,
            snapshot_manifest=None,
            normalized_manifest=None,
            diff_doc=None,
            dry_run=dry_run,
            existing=existing,
        )
        result["status"] = "refused_existing_outputs"
        result["message"] = "Refusing to overwrite existing dated snapshot/diff outputs without --allow-existing."
        return result

    if dry_run:
        result = summarize_run(
            workspace=workspace,
            date=date,
            snapshot_manifest=None,
            normalized_manifest=None,
            diff_doc=None,
            dry_run=True,
            existing=existing,
        )
        result["status"] = "dry_run_ok"
        result["planned_steps"] = [
            "fetch.fetch_nationals",
            "parse.normalize_snapshot",
            "diff.run_diff",
        ]
        return result

    snapshot_items = fetch.fetch_nationals(workspace, date=date)
    snapshot_manifest = json.loads((workspace / "snapshots" / date / "manifest.json").read_text(encoding="utf-8"))
    normalized_manifest = parse.normalize_snapshot(workspace, date)
    diff_doc = diff_engine.run_diff(
        workspace=workspace,
        date=date,
        baseline_date=baseline_date,
        update_baseline=not no_update_baseline,
    )
    result = summarize_run(
        workspace=workspace,
        date=date,
        snapshot_manifest=snapshot_manifest,
        normalized_manifest=normalized_manifest,
        diff_doc=diff_doc,
        dry_run=False,
        existing=existing,
    )
    result["status"] = "ok"
    result["snapshot_item_count"] = len(snapshot_items)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--baseline-date", help="Optional normalized snapshot date to compare against instead of baselines/current.json")
    parser.add_argument("--no-update-baseline", action="store_true")
    parser.add_argument("--allow-existing", action="store_true", help="Permit overwriting outputs for an existing date; intended only for explicit operator-controlled reruns.")
    parser.add_argument("--dry-run", action="store_true", help="Report planned action and overwrite guard state without fetching or writing snapshot outputs.")
    parser.add_argument("--output", help="Optional JSON path for the run summary.")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    result = run_daily(
        workspace=workspace,
        date=args.date,
        baseline_date=args.baseline_date,
        no_update_baseline=args.no_update_baseline,
        allow_existing=args.allow_existing,
        dry_run=args.dry_run,
    )
    if args.output:
        write_json(workspace / args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") in {"ok", "dry_run_ok", "refused_existing_outputs"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
