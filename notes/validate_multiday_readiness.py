#!/usr/bin/env python3
"""Validate Cassandra's multi-day readiness and interpretation boundary.

This is a local workflow/reproducibility check only. It does not assert legal
compliance, trusted-list legal effect, signature validity, supervision, public
alerting, regulated trust-service output, or publication readiness.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_SINGLE_DAY_PAPER_FRAGMENTS = [
    "single baseline row can verify that the workflow produces bounded artifacts, but it cannot characterize longitudinal behavior",
    "A missing second date should not be simulated with copied files or renamed directories",
    "Once Cassandra has more than one dated run",
    "Multi-day charts should keep this caveat visible",
]

FORBIDDEN_EARLY_LONGITUDINAL_CLAIMS = [
    "typical trusted-list churn",
    "recurring trusted-list pattern",
    "stable legal ecosystem",
    "public warning",
    "compliance risk score",
]

CAVEAT = (
    "Local workflow-readiness telemetry only: this check does not assert legal "
    "compliance, trusted-list legal effect, signature validity, supervision, "
    "public alerting, regulated trust-service output, or publication readiness."
)


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dated_children(base: Path) -> list[str]:
    if not base.exists():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir() and DATE_RE.match(p.name))


def dated_diff_files(base: Path) -> list[str]:
    if not base.exists():
        return []
    return sorted(p.stem for p in base.glob("*.json") if DATE_RE.match(p.stem))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def latest_aggregate_results(workspace: Path) -> Path | None:
    candidates = sorted(
        p
        for p in workspace.glob("notes/aggregate-results-*-output.json")
        if re.match(r"^aggregate-results-\d{4}-\d{2}-\d{2}-output\.json$", p.name)
    )
    if not candidates:
        return None
    return candidates[-1]


def validate(workspace: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    paper_path = workspace / "paper" / "draft.md"
    aggregate_path = latest_aggregate_results(workspace)
    alerts_path = workspace / "alerts.jsonl"

    snapshot_dates = dated_children(workspace / "snapshots")
    normalized_dates = dated_children(workspace / "normalized")
    bundle_dates = dated_children(workspace / "bundles")
    diff_dates = dated_diff_files(workspace / "diffs")

    completed_dates = sorted(
        set(snapshot_dates) & set(normalized_dates) & set(bundle_dates) & set(diff_dates)
    )

    if not completed_dates:
        errors.append("no completed dated snapshot/normalization/diff/bundle set found")

    synthetic_second_date_detected = False
    multi_day_mode = len(completed_dates) >= 2
    if not multi_day_mode:
        # With only one completed date, the paper must explicitly resist simulation
        # and early longitudinal overclaiming.
        if not paper_path.exists():
            errors.append("paper/draft.md missing")
            paper = ""
        else:
            paper = paper_path.read_text(encoding="utf-8")
            for fragment in REQUIRED_SINGLE_DAY_PAPER_FRAGMENTS:
                if fragment not in paper:
                    errors.append(f"missing single-day boundary fragment in paper: {fragment}")
            lower_paper = paper.lower()
            for phrase in FORBIDDEN_EARLY_LONGITUDINAL_CLAIMS:
                if phrase.lower() in lower_paper:
                    errors.append(f"forbidden early longitudinal overclaiming phrase found: {phrase}")
    else:
        # With two or more completed dates, this validator checks aggregate telemetry
        # linkage while keeping interpretation descriptive and local.
        pass

    # Smoke/preflight directories are allowed, but they must not match strict YYYY-MM-DD completed sets.
    snapshots_dir = workspace / "snapshots"
    non_completed_dated_snapshot_dirs = sorted(set(snapshot_dates) - set(completed_dates))
    if non_completed_dated_snapshot_dirs:
        warnings.append(
            "dated snapshot dirs without complete normalized/diff/bundle lineage: "
            + ", ".join(non_completed_dated_snapshot_dirs)
        )

    aggregate_summary: dict[str, Any] = {
        "path": None,
        "dates": [],
        "row_count": 0,
        "diff_change_count_total": None,
        "sha256": None,
    }
    if aggregate_path and aggregate_path.exists():
        aggregate = load_json(aggregate_path)
        rows = aggregate.get("rows", [])
        aggregate_dates = sorted(row.get("date") for row in rows if row.get("date"))
        aggregate_summary = {
            "path": str(aggregate_path.relative_to(workspace)),
            "dates": aggregate_dates,
            "row_count": aggregate.get("row_count", len(rows)),
            "diff_change_count_total": aggregate.get("totals", {}).get("diff_change_count"),
            "sha256": sha256_file(aggregate_path),
        }
        if not multi_day_mode and len(aggregate_dates) != 1:
            errors.append(f"expected one aggregate-results row before second completed date, found {len(aggregate_dates)}")
        if multi_day_mode and aggregate_dates != completed_dates:
            errors.append(
                "aggregate-results dates do not match completed local lineages: "
                f"aggregate={aggregate_dates}; completed={completed_dates}"
            )
        if multi_day_mode and aggregate.get("row_count", len(rows)) != len(completed_dates):
            errors.append(
                "aggregate-results row_count does not match completed lineage count: "
                f"row_count={aggregate.get('row_count', len(rows))}; completed={len(completed_dates)}"
            )
        caveat_text = json.dumps(aggregate, sort_keys=True)
        for required in [
            "structural-observation telemetry",
            "not trusted-list validation",
            "legal-status determination",
            "public alerting",
            "publication approval",
        ]:
            if required not in caveat_text:
                errors.append(f"aggregate-results output lacks visible caveat fragment: {required}")
        for d in aggregate_dates:
            if d not in completed_dates:
                errors.append(f"aggregate-results row date lacks completed local lineage: {d}")
    else:
        errors.append("missing aggregate-results JSON under notes/aggregate-results-*-output.json")

    alert_dates: list[str] = []
    if alerts_path.exists():
        with alerts_path.open("r", encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(f"alerts.jsonl line {i} is not valid JSON: {exc}")
                    continue
                d = obj.get("date")
                if d:
                    alert_dates.append(d)
                caveat_text = json.dumps(obj, sort_keys=True)
                for required in ["does not assert legal effect", "public alerting"]:
                    if required not in caveat_text:
                        warnings.append(f"alerts.jsonl line {i} lacks visible caveat fragment: {required}")
    else:
        errors.append("alerts.jsonl missing")

    if not multi_day_mode:
        extra_alert_dates = sorted(set(alert_dates) - set(completed_dates))
        if extra_alert_dates:
            errors.append(f"alert dates without completed local lineage before second date: {extra_alert_dates}")

    artifacts = []
    for rel in [
        "paper/draft.md",
        "alerts.jsonl",
    ]:
        p = workspace / rel
        if p.exists():
            artifacts.append({"path": rel, "sha256": sha256_file(p)})
    if aggregate_summary["path"]:
        artifacts.append({"path": aggregate_summary["path"], "sha256": aggregate_summary["sha256"]})

    return {
        "status": "ok" if not errors else "needs_review",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "completed_dates": completed_dates,
        "multi_day_mode": multi_day_mode,
        "aggregate_results": aggregate_summary,
        "date_counts": {
            "snapshots": len(snapshot_dates),
            "normalized": len(normalized_dates),
            "diffs": len(diff_dates),
            "bundles": len(bundle_dates),
            "completed": len(completed_dates),
        },
        "synthetic_second_date_detected": synthetic_second_date_detected,
        "errors": errors,
        "warnings": warnings,
        "checked_artifacts": artifacts,
        "caveat": CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/multiday-readiness-validation-output.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    result = validate(workspace)
    output = workspace / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
