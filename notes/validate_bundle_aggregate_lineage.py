#!/usr/bin/env python3
"""Validate local bundle-to-aggregate-results lineage for Cassandra.

This is a reproducibility/claim-safety helper only. It does not validate trusted
lists, signatures, legal status, supervision, public alerting, or publication
readiness.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RESEARCH_CAVEAT = (
    "Bundle-to-aggregate lineage validation for local structural-observation "
    "telemetry only; not trusted-list validation, legal-status determination, "
    "signature verification, supervision, public alerting, regulated trust-service "
    "output, or publication readiness."
)

COUNT_MAP = {
    "pointer_attempts": "pointer_attempts",
    "fetched_content_files": "fetched_content_files",
    "fetch_errors": "fetch_errors",
    "normalization_inputs": "normalization_inputs",
    "normalization_skips": "normalization_skips",
    "normalization_errors": "normalization_errors",
    "normalized_xml_artifacts": "normalized_xml_artifacts",
    "diff_change_count": "diff_change_count",
    "diff_current_record_count": "diff_current_record_count",
}

REQUIRED_CAVEAT_TOKENS = [
    "not trusted-list validation",
    "legal-status determination",
    "signature verification",
    "supervision",
    "public alerting",
    "publication readiness",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_row(path: Path, date: str) -> dict[str, str] | None:
    with path.open("r", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("date") == date:
                return row
    return None


def as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def validate(workspace: Path, date: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: dict[str, Any] = {}

    bundle_summary_path = workspace / "bundles" / date / "snapshot-summary.json"
    bundle_manifest_path = workspace / "bundles" / date / "snapshot-summary.json.bundle" / "manifest.json"
    aggregate_json_path = workspace / "notes" / f"aggregate-results-{date}-output.json"
    aggregate_csv_path = workspace / "notes" / "aggregate-results-table.csv"

    required_paths = {
        "bundle_summary": bundle_summary_path,
        "bundle_manifest": bundle_manifest_path,
        "aggregate_json": aggregate_json_path,
        "aggregate_csv": aggregate_csv_path,
    }
    for label, path in required_paths.items():
        if not path.exists():
            errors.append(f"missing required {label}: {path.relative_to(workspace)}")
    if errors:
        return {
            "schema": "urn:tyche:cassandra:bundle-aggregate-lineage-validation:0.1",
            "status": "error",
            "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "date": date,
            "research_caveat": RESEARCH_CAVEAT,
            "errors": errors,
            "warnings": warnings,
            "checked": checked,
        }

    bundle_summary = load_json(bundle_summary_path)
    bundle_manifest = load_json(bundle_manifest_path)
    aggregate_json = load_json(aggregate_json_path)
    aggregate_row = next((row for row in aggregate_json.get("rows", []) if row.get("date") == date), None)
    csv_row = load_csv_row(aggregate_csv_path, date)

    checked["paths"] = {k: str(v.relative_to(workspace)) for k, v in required_paths.items()}
    checked["bundle_summary_sha256"] = sha256_file(bundle_summary_path)
    checked["aggregate_json_sha256"] = sha256_file(aggregate_json_path)
    checked["aggregate_csv_sha256"] = sha256_file(aggregate_csv_path)

    if bundle_summary.get("schema") != "urn:tyche:cassandra:snapshot-summary:0.1":
        errors.append("unexpected snapshot-summary schema")
    if aggregate_json.get("schema") != "urn:tyche:cassandra:aggregate-results:0.1":
        errors.append("unexpected aggregate-results schema")
    if bundle_summary.get("date") != date:
        errors.append("bundle summary date does not match requested date")
    if not aggregate_row:
        errors.append("aggregate JSON has no row for requested date")
    if not csv_row:
        errors.append("aggregate CSV has no row for requested date")

    caveat_text = "\n".join(
        [RESEARCH_CAVEAT, str(aggregate_json.get("caveat", "")), *map(str, bundle_summary.get("caveats", []))]
    ).lower()
    missing_tokens = [token for token in REQUIRED_CAVEAT_TOKENS if token not in caveat_text]
    if missing_tokens:
        errors.append(f"missing caveat tokens: {missing_tokens}")

    artifact = bundle_manifest.get("artifact", {})
    manifest_artifact_hash = artifact.get("sha256", {}).get("value")
    if manifest_artifact_hash != checked["bundle_summary_sha256"]:
        errors.append("bundle manifest artifact hash does not match snapshot-summary.json")

    count_checks: dict[str, dict[str, Any]] = {}
    if aggregate_row:
        bundle_counts = bundle_summary.get("counts", {})
        for bundle_key, aggregate_key in COUNT_MAP.items():
            bundle_value = as_int(bundle_counts.get(bundle_key))
            aggregate_value = as_int(aggregate_row.get(aggregate_key))
            count_checks[bundle_key] = {
                "bundle": bundle_value,
                "aggregate": aggregate_value,
                "matches": bundle_value == aggregate_value,
            }
            if bundle_value != aggregate_value:
                errors.append(f"count mismatch for {bundle_key}: bundle={bundle_value} aggregate={aggregate_value}")
        if csv_row:
            for _, aggregate_key in COUNT_MAP.items():
                json_value = as_int(aggregate_row.get(aggregate_key))
                csv_value = as_int(csv_row.get(aggregate_key))
                if json_value != csv_value:
                    errors.append(f"CSV mismatch for {aggregate_key}: json={json_value} csv={csv_value}")
        # Baseline flag may differ because the bundle is a frozen first-day summary
        # while aggregate rows are generated from the latest refreshed diff. Track it
        # as lineage context rather than a hard error.
        if bool(bundle_summary.get("counts", {}).get("baseline_created")) != bool(aggregate_row.get("baseline_created")):
            warnings.append(
                "baseline_created differs between frozen bundle summary and refreshed aggregate row; "
                "this is expected after same-date baseline refreshes and is not a legal/status claim"
            )
    checked["count_checks"] = count_checks

    hash_checks: dict[str, Any] = {}
    hash_sources = {
        "snapshot_manifest_sha256": workspace / bundle_summary.get("artifact_paths", {}).get("snapshot_manifest", ""),
        "normalized_manifest_sha256": workspace / bundle_summary.get("artifact_paths", {}).get("normalized_manifest", ""),
        "diff_sha256": workspace / bundle_summary.get("artifact_paths", {}).get("diff", ""),
        "baseline_sha256": workspace / bundle_summary.get("artifact_paths", {}).get("baseline", ""),
    }
    for key, path in hash_sources.items():
        recorded = bundle_summary.get("hashes", {}).get(key)
        if not path.exists():
            errors.append(f"bundle path missing for {key}: {path}")
            continue
        current = sha256_file(path)
        hash_checks[key] = {"bundle_recorded": recorded, "current": current, "matches_current": recorded == current}
        if recorded != current:
            warnings.append(
                f"frozen bundle hash for {key} differs from current workspace file; "
                "treat as post-bundle artifact refresh lineage, not as legal/status evidence"
            )
    checked["hash_checks"] = hash_checks

    status = "ok" if not errors else "error"
    return {
        "schema": "urn:tyche:cassandra:bundle-aggregate-lineage-validation:0.1",
        "status": status,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "date": date,
        "research_caveat": RESEARCH_CAVEAT,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "checked": checked,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", default="2026-05-20")
    parser.add_argument("--output", default="notes/bundle-aggregate-lineage-validation-output.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    result = validate(workspace, args.date)
    output_path = (workspace / args.output).resolve()
    if not output_path.is_relative_to(workspace):
        raise SystemExit("output path must remain inside workspace")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(output_path.relative_to(workspace)), "error_count": result.get("error_count", len(result.get("errors", []))), "warning_count": result.get("warning_count", len(result.get("warnings", [])))}, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
