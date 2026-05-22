#!/usr/bin/env python3
"""Validate Cassandra aggregate-results JSON/CSV consistency.

Local research-only validator. It checks figure-ready aggregate telemetry files
for internal consistency and claim-safety caveats. It does not assert legal
effect, trusted-list status, supervision, signature validity, public alerting,
or publication readiness.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_CAVEAT_FRAGMENTS = [
    "structural-observation telemetry",
    "not trusted-list validation",
    "supervision",
    "legal-status determination",
    "signature verification",
    "public alerting",
    "publication approval",
]

FORBIDDEN_STRINGS = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer eIDAS-aligned trust services",
]

CSV_FIELDS = [
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
    "listed_document_added",
    "listed_document_removed",
    "normalized_hash_changed",
    "summary_field_changed",
    "provider_inventory_changed",
    "service_inventory_changed",
    "provider_service_detail_changed",
]

NUMERIC_FIELDS = [field for field in CSV_FIELDS if field != "date"]
DIFF_CLASS_FIELDS = [
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


def add_error(errors: list[dict[str, Any]], code: str, detail: str) -> None:
    errors.append({"code": code, "detail": detail})


def add_warning(warnings: list[dict[str, Any]], code: str, detail: str) -> None:
    warnings.append({"code": code, "detail": detail})


def parse_int(value: Any, field: str, date: str, errors: list[dict[str, Any]]) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        add_error(errors, "non_numeric_field", f"{date}: field {field!r} is not an integer: {value!r}")
        return 0
    if parsed < 0:
        add_error(errors, "negative_field", f"{date}: field {field!r} is negative: {parsed}")
    return parsed


def validate(workspace: Path, aggregate_json: Path, aggregate_csv: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checked: list[str] = []

    if not aggregate_json.exists():
        add_error(errors, "missing_json", f"Missing aggregate JSON: {aggregate_json}")
        data: dict[str, Any] = {}
    else:
        checked.append(str(aggregate_json.relative_to(workspace)))
        data = load_json(aggregate_json)

    if not aggregate_csv.exists():
        add_error(errors, "missing_csv", f"Missing aggregate CSV: {aggregate_csv}")
        csv_rows: list[dict[str, str]] = []
    else:
        checked.append(str(aggregate_csv.relative_to(workspace)))
        with aggregate_csv.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != CSV_FIELDS:
                add_error(errors, "csv_header_mismatch", f"CSV header {reader.fieldnames!r} != expected {CSV_FIELDS!r}")
            csv_rows = list(reader)

    json_text = aggregate_json.read_text(encoding="utf-8") if aggregate_json.exists() else ""
    csv_text = aggregate_csv.read_text(encoding="utf-8") if aggregate_csv.exists() else ""
    for needle in FORBIDDEN_STRINGS:
        if needle in json_text or needle in csv_text:
            add_error(errors, "forbidden_string", f"Forbidden string present in aggregate outputs: {needle}")

    if data:
        if data.get("schema") != "urn:tyche:cassandra:aggregate-results:0.1":
            add_error(errors, "schema_mismatch", f"Unexpected schema: {data.get('schema')!r}")
        if data.get("status") != "ok":
            add_error(errors, "json_status_not_ok", f"Aggregate status is {data.get('status')!r}")
        if data.get("lane") != "cassandra":
            add_error(errors, "lane_mismatch", f"Unexpected lane: {data.get('lane')!r}")

        caveat = data.get("caveat") if isinstance(data.get("caveat"), str) else ""
        for fragment in REQUIRED_CAVEAT_FRAGMENTS:
            if fragment not in caveat:
                add_error(errors, "missing_caveat_fragment", f"Aggregate caveat lacks fragment: {fragment}")

        rows = data.get("rows") if isinstance(data.get("rows"), list) else []
        if data.get("row_count") != len(rows):
            add_error(errors, "row_count_mismatch", f"row_count {data.get('row_count')!r} != len(rows) {len(rows)}")
        if len(csv_rows) != len(rows):
            add_error(errors, "csv_row_count_mismatch", f"CSV rows {len(csv_rows)} != JSON rows {len(rows)}")

        dates = [row.get("date") for row in rows if isinstance(row, dict)]
        if data.get("dates") != dates:
            add_error(errors, "dates_mismatch", f"top-level dates {data.get('dates')!r} != row dates {dates!r}")
        if dates != sorted(dates):
            add_warning(warnings, "dates_not_sorted", f"Dates are not sorted: {dates!r}")

        csv_by_date = {row.get("date"): row for row in csv_rows}
        for row in rows:
            if not isinstance(row, dict):
                add_error(errors, "row_not_object", f"Row is not an object: {row!r}")
                continue
            date = str(row.get("date"))
            if row.get("caveat") != caveat:
                add_error(errors, "row_caveat_mismatch", f"{date}: row caveat does not match top-level caveat")
            csv_row = csv_by_date.get(date)
            if not csv_row:
                add_error(errors, "missing_csv_row", f"{date}: missing CSV row")
                continue
            for field in NUMERIC_FIELDS:
                json_value = parse_int(row.get(field), field, date, errors)
                csv_value = parse_int(csv_row.get(field), field, date, errors)
                if json_value != csv_value:
                    add_error(errors, "json_csv_value_mismatch", f"{date}: {field} JSON {json_value} != CSV {csv_value}")
            if parse_int(row.get("pointer_attempts"), "pointer_attempts", date, errors) < parse_int(row.get("fetched_content_files"), "fetched_content_files", date, errors):
                add_error(errors, "fetch_count_invariant", f"{date}: fetched_content_files exceeds pointer_attempts")
            if parse_int(row.get("normalization_inputs"), "normalization_inputs", date, errors) < parse_int(row.get("normalized_xml_artifacts"), "normalized_xml_artifacts", date, errors):
                add_error(errors, "normalization_count_invariant", f"{date}: normalized_xml_artifacts exceeds normalization_inputs")

        totals = data.get("totals") if isinstance(data.get("totals"), dict) else {}
        for field in [
            "pointer_attempts",
            "fetched_content_files",
            "fetch_errors",
            "normalized_xml_artifacts",
            "normalization_skips",
            "normalization_errors",
            "diff_change_count",
            "provider_count_total",
            "service_count_total",
            "alert_entry_count",
        ]:
            expected = sum(parse_int(row.get(field), field, str(row.get("date")), errors) for row in rows if isinstance(row, dict))
            observed = parse_int(totals.get(field), f"totals.{field}", "totals", errors)
            if expected != observed:
                add_error(errors, "totals_mismatch", f"{field}: expected {expected}, observed {observed}")

        diff_totals = data.get("diff_class_totals") if isinstance(data.get("diff_class_totals"), dict) else {}
        for field in DIFF_CLASS_FIELDS:
            expected = sum(parse_int(row.get(field), field, str(row.get("date")), errors) for row in rows if isinstance(row, dict))
            observed = parse_int(diff_totals.get(field), f"diff_class_totals.{field}", "diff_totals", errors)
            if expected != observed:
                add_error(errors, "diff_totals_mismatch", f"{field}: expected {expected}, observed {observed}")

        recorded_csv = data.get("csv")
        recorded_hash = data.get("csv_sha256")
        if recorded_csv != str(aggregate_csv.relative_to(workspace)):
            add_error(errors, "csv_path_mismatch", f"Recorded csv path {recorded_csv!r} != {str(aggregate_csv.relative_to(workspace))!r}")
        if aggregate_csv.exists() and recorded_hash != sha256_file(aggregate_csv):
            add_error(errors, "csv_hash_mismatch", "Recorded csv_sha256 does not match current CSV file")

    return {
        "schema": "urn:tyche:cassandra:aggregate-results-validation:0.1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "lane": "cassandra",
        "status": "ok" if not errors else "error",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "checked_paths": checked,
        "caveat": "Local consistency and claim-safety validation only; not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, or publication readiness.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--aggregate-json", default="notes/aggregate-results-2026-05-20-output.json")
    parser.add_argument("--aggregate-csv", default="notes/aggregate-results-table.csv")
    parser.add_argument("--output", default="notes/aggregate-results-validation-output.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    aggregate_json = (workspace / args.aggregate_json).resolve()
    aggregate_csv = (workspace / args.aggregate_csv).resolve()
    output = (workspace / args.output).resolve()
    for path in [aggregate_json, aggregate_csv, output]:
        if not str(path).startswith(str(workspace)):
            raise SystemExit("All paths must stay inside workspace")

    result = validate(workspace, aggregate_json, aggregate_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
