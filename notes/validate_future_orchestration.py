#!/usr/bin/env python3
"""Validate Cassandra daily-run/bundle/alert orchestration guards.

Research-only local verifier: exercises non-overwrite and missing-input guards for
future dated runs without fetching, publishing, or changing trusted-list state. It
does not perform relying-party validation, supervision, signature verification,
legal-status determination, public alerting, or publication readiness review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

WORKSPACE_MODULE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(WORKSPACE_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_MODULE_DIR))

import alert_rollup
import create_bundle
import run_daily

RESEARCH_CAVEAT = (
    "Local orchestration-guard validation for research-only structural observation; "
    "not legal-status determination, supervision, signature validation, relying-party "
    "processing, public alerting, regulated trust-service output, or publication readiness."
)


def now_z() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate(workspace: pathlib.Path, *, known_date: str, missing_date: str) -> dict[str, Any]:
    workspace = workspace.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    known_daily = run_daily.run_daily(
        workspace,
        known_date,
        baseline_date=None,
        no_update_baseline=False,
        allow_existing=False,
        dry_run=True,
    )
    if known_daily.get("status") != "refused_existing_outputs":
        errors.append(f"expected known-date daily dry-run guard refusal, got {known_daily.get('status')}")
    if not known_daily.get("existing_outputs"):
        errors.append("known-date daily guard did not report existing outputs")

    future_daily = run_daily.run_daily(
        workspace,
        missing_date,
        baseline_date=known_date,
        no_update_baseline=True,
        allow_existing=False,
        dry_run=True,
    )
    if future_daily.get("status") != "dry_run_ok":
        errors.append(f"expected missing-date daily dry-run ok, got {future_daily.get('status')}")
    planned = set(future_daily.get("planned_steps") or [])
    expected_steps = {"fetch.fetch_nationals", "parse.normalize_snapshot", "diff.run_diff"}
    if planned != expected_steps:
        errors.append(f"future daily dry-run planned steps mismatch: {sorted(planned)}")

    known_bundle = create_bundle.build_bundle(workspace, known_date, allow_existing=False, dry_run=True)
    if known_bundle.get("status") != "refused_existing_outputs":
        errors.append(f"expected known-date bundle guard refusal, got {known_bundle.get('status')}")
    if not known_bundle.get("existing_outputs"):
        errors.append("known-date bundle guard did not report existing bundle outputs")

    future_bundle = create_bundle.build_bundle(workspace, missing_date, allow_existing=False, dry_run=True)
    if future_bundle.get("status") != "missing_inputs":
        errors.append(f"expected missing-date bundle preflight missing_inputs, got {future_bundle.get('status')}")
    missing_inputs = set(future_bundle.get("missing_inputs") or [])
    expected_missing = {
        f"snapshots/{missing_date}/manifest.json",
        f"normalized/{missing_date}/manifest.json",
        f"diffs/{missing_date}.json",
        f"baselines/{missing_date}.json",
    }
    if not expected_missing.issubset(missing_inputs):
        errors.append(f"future bundle missing-input set incomplete: {sorted(missing_inputs)}")

    try:
        alert_rollup.build_entry(workspace, missing_date)
    except FileNotFoundError as exc:
        future_alert = {"status": "missing_inputs", "message": str(exc)}
    else:
        future_alert = {"status": "unexpected_ok"}
        errors.append("expected missing-date alert entry build to fail before dated artifacts exist")

    known_alert = alert_rollup.append_or_replace_alert(workspace, known_date, dry_run=True)
    if known_alert.get("status") != "ok":
        errors.append(f"expected known-date alert dry-run status ok, got {known_alert.get('status')}")
    if known_alert.get("alerts_sha256") is not None:
        errors.append("alert dry-run unexpectedly reported a new alerts_sha256")
    if not known_alert.get("entry", {}).get("dedupe_key"):
        errors.append("known-date alert dry-run entry lacks dedupe_key")

    caveat_text = " ".join(
        str(item)
        for item in [
            RESEARCH_CAVEAT,
            known_daily.get("research_caveat"),
            future_daily.get("research_caveat"),
            known_bundle.get("research_caveat"),
            future_bundle.get("research_caveat"),
            known_alert.get("entry", {}).get("caveat"),
        ]
    ).lower()
    required_caveat_tokens = [
        "not legal-status determination",
        "supervision",
        "signature validation",
        "public alerting",
    ]
    for token in required_caveat_tokens:
        if token not in caveat_text:
            warnings.append(f"caveat token not found in combined orchestration outputs: {token}")

    return {
        "schema": "urn:tyche:cassandra:future-orchestration-validation:0.1",
        "created_at": now_z(),
        "workspace": str(workspace),
        "known_date": known_date,
        "missing_date": missing_date,
        "status": "ok" if not errors else "error",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "known_daily_guard": {
                "status": known_daily.get("status"),
                "existing_outputs": known_daily.get("existing_outputs"),
            },
            "future_daily_dry_run": {
                "status": future_daily.get("status"),
                "planned_steps": future_daily.get("planned_steps"),
            },
            "known_bundle_guard": {
                "status": known_bundle.get("status"),
                "existing_outputs": known_bundle.get("existing_outputs"),
            },
            "future_bundle_preflight": {
                "status": future_bundle.get("status"),
                "missing_inputs": future_bundle.get("missing_inputs"),
            },
            "future_alert_preflight": future_alert,
            "known_alert_dry_run": {
                "status": known_alert.get("status"),
                "dry_run": known_alert.get("dry_run"),
                "jsonl_entry_count": known_alert.get("jsonl_entry_count"),
                "dedupe_key_present": bool(known_alert.get("entry", {}).get("dedupe_key")),
            },
        },
        "research_caveat": RESEARCH_CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--known-date", default="2026-05-20")
    parser.add_argument("--missing-date", default="2099-12-31")
    parser.add_argument("--output", default="notes/future-orchestration-validation-output.json")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace, known_date=args.known_date, missing_date=args.missing_date)
    output = pathlib.Path(args.output)
    if not output.is_absolute():
        output = workspace / output
    write_json(output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
