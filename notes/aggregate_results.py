#!/usr/bin/env python3
"""Build aggregate, figure-ready Cassandra telemetry tables.

Research-only helper. It summarizes local structural-observation manifests,
diffs, and alert JSONL entries without exposing listed entity names and without
asserting legal effect, supervision, relying-party validation, or publication
readiness.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAVEAT = (
    "Aggregate structural-observation telemetry only; not trusted-list "
    "validation, supervision, legal-status determination, signature "
    "verification, public alerting, or publication approval."
)

DIFF_CLASSES = [
    "listed_document_added",
    "listed_document_removed",
    "normalized_hash_changed",
    "summary_field_changed",
    "provider_inventory_changed",
    "service_inventory_changed",
    "provider_service_detail_changed",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_alerts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSONL at {path}:{idx}: {exc}") from exc
    return rows


def count_alerts_by_date(alerts: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    out: dict[str, Counter[str]] = {}
    for row in alerts:
        date = row.get("date")
        if not isinstance(date, str):
            continue
        event_type = row.get("event_type") if isinstance(row.get("event_type"), str) else "unknown"
        out.setdefault(date, Counter())[event_type] += 1
    return out


def build_rows(workspace: Path) -> list[dict[str, Any]]:
    snapshot_root = workspace / "snapshots"
    dates = sorted(
        p.name
        for p in snapshot_root.iterdir()
        if p.is_dir() and (p / "manifest.json").exists() and not p.name.endswith("smoke") and "smoke" not in p.name
    ) if snapshot_root.exists() else []

    alerts_by_date = count_alerts_by_date(load_alerts(workspace / "alerts.jsonl"))
    rows: list[dict[str, Any]] = []
    for date in dates:
        snapshot_manifest_path = workspace / "snapshots" / date / "manifest.json"
        normalized_manifest_path = workspace / "normalized" / date / "manifest.json"
        diff_path = workspace / "diffs" / f"{date}.json"

        snapshot = load_json(snapshot_manifest_path)
        normalized = load_json(normalized_manifest_path) if normalized_manifest_path.exists() else {}
        diff = load_json(diff_path) if diff_path.exists() else {}
        diff_summary = diff.get("summary") if isinstance(diff.get("summary"), dict) else {}

        normalized_items = normalized.get("items") if isinstance(normalized.get("items"), list) else []
        ok_items = [item for item in normalized_items if item.get("status") == "ok"]
        provider_counts = []
        service_counts = []
        signature_counts = []
        for item in ok_items:
            summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
            provider_counts.append(int(summary.get("trust_service_provider_count") or 0))
            service_counts.append(int(summary.get("tsp_service_count") or 0))
            sig = summary.get("signature_shape") if isinstance(summary.get("signature_shape"), dict) else {}
            signature_counts.append(int(sig.get("signature_count") or 0))

        alert_counter = alerts_by_date.get(date, Counter())
        row: dict[str, Any] = {
            "date": date,
            "snapshot_manifest": str(snapshot_manifest_path.relative_to(workspace)),
            "snapshot_manifest_sha256": sha256_file(snapshot_manifest_path),
            "pointer_attempts": int(snapshot.get("count") or len(snapshot.get("items", []))),
            "fetched_content_files": int(snapshot.get("ok_count") or 0),
            "fetch_errors": int(snapshot.get("error_count") or 0),
            "normalized_manifest": str(normalized_manifest_path.relative_to(workspace)) if normalized_manifest_path.exists() else None,
            "normalized_manifest_sha256": sha256_file(normalized_manifest_path) if normalized_manifest_path.exists() else None,
            "normalization_inputs": int(normalized.get("count") or 0),
            "normalized_xml_artifacts": int(normalized.get("ok_count") or len(ok_items)),
            "normalization_skips": int(normalized.get("skipped_count") or 0),
            "normalization_errors": int(normalized.get("error_count") or 0),
            "diff": str(diff_path.relative_to(workspace)) if diff_path.exists() else None,
            "diff_sha256": sha256_file(diff_path) if diff_path.exists() else None,
            "diff_change_count": int(diff.get("change_count") or 0),
            "diff_current_record_count": int(diff.get("current_record_count") or 0),
            "baseline_created": bool(diff.get("baseline_created")) if diff else None,
            "provider_count_total": sum(provider_counts),
            "service_count_total": sum(service_counts),
            "signature_shape_records": sum(1 for value in signature_counts if value > 0),
            "alert_entry_count": sum(alert_counter.values()),
            "alert_event_types": dict(sorted(alert_counter.items())),
            "caveat": CAVEAT,
        }
        for cls in DIFF_CLASSES:
            row[cls] = int(diff_summary.get(cls) or 0)
        rows.append(row)
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "date",
        "pointer_attempts",
        "fetched_content_files",
        "fetch_errors",
        "normalization_inputs",
        "normalized_xml_artifacts",
        "normalization_skips",
        "normalization_errors",
        "diff_current_record_count",
        "diff_change_count",
        "provider_count_total",
        "service_count_total",
        "signature_shape_records",
        "alert_entry_count",
        *DIFF_CLASSES,
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/aggregate-results-output.json")
    parser.add_argument("--csv", default="notes/aggregate-results-table.csv")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    rows = build_rows(workspace)
    if not rows:
        raise SystemExit("No dated snapshot manifests found")

    csv_path = (workspace / args.csv).resolve()
    if not str(csv_path).startswith(str(workspace)):
        raise SystemExit("CSV output must stay inside workspace")
    write_csv(rows, csv_path)

    summary = {
        "schema": "urn:tyche:cassandra:aggregate-results:0.1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "lane": "cassandra",
        "row_count": len(rows),
        "dates": [row["date"] for row in rows],
        "totals": {
            "pointer_attempts": sum(row["pointer_attempts"] for row in rows),
            "fetched_content_files": sum(row["fetched_content_files"] for row in rows),
            "fetch_errors": sum(row["fetch_errors"] for row in rows),
            "normalized_xml_artifacts": sum(row["normalized_xml_artifacts"] for row in rows),
            "normalization_skips": sum(row["normalization_skips"] for row in rows),
            "normalization_errors": sum(row["normalization_errors"] for row in rows),
            "diff_change_count": sum(row["diff_change_count"] for row in rows),
            "provider_count_total": sum(row["provider_count_total"] for row in rows),
            "service_count_total": sum(row["service_count_total"] for row in rows),
            "alert_entry_count": sum(row["alert_entry_count"] for row in rows),
        },
        "diff_class_totals": {cls: sum(row[cls] for row in rows) for cls in DIFF_CLASSES},
        "csv": str(csv_path.relative_to(workspace)),
        "csv_sha256": sha256_file(csv_path),
        "rows": rows,
        "caveat": CAVEAT,
        "status": "ok",
    }

    output_path = (workspace / args.output).resolve()
    if not str(output_path).startswith(str(workspace)):
        raise SystemExit("JSON output must stay inside workspace")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
