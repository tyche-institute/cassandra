#!/usr/bin/env python3
"""Build public dashboard data for the Cassandra observatory."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import shutil
from typing import Any

CAVEAT = (
    "Public observatory data for Cassandra structural observation only; not "
    "trusted-list validation, legal-status determination, supervision, "
    "signature validation, relying-party processing, or public alerting."
)


def now_z() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def find_latest_aggregate(workspace: pathlib.Path) -> pathlib.Path:
    paths = sorted((workspace / "notes").glob("aggregate-results-*-output.json"))
    if not paths:
        raise SystemExit("No aggregate results output found")
    return paths[-1]


def load_eatf_status(workspace: pathlib.Path, date: str) -> dict[str, Any]:
    receipt_path = workspace / "evidence" / date / "eatf-verification.json"
    package_path = workspace / "evidence" / date / "cassandra-observation.aep"
    payload_path = workspace / "evidence" / date / "cassandra-observation.json"
    if not receipt_path.exists():
        return {
            "status": "not_packaged",
            "valid": None,
            "receipt_path": None,
            "receipt_sha256": None,
            "package_path": None,
            "package_sha256": None,
            "payload_path": None,
            "payload_sha256": None,
        }
    receipt = read_json(receipt_path)
    verify = receipt.get("verify") if isinstance(receipt.get("verify"), dict) else {}
    valid = verify.get("valid") if isinstance(verify, dict) else None
    return {
        "status": receipt.get("status"),
        "valid": valid,
        "receipt_path": str(receipt_path.relative_to(workspace)),
        "receipt_sha256": sha256_file(receipt_path),
        "package_path": str(package_path.relative_to(workspace)) if package_path.exists() else None,
        "package_sha256": sha256_file(package_path) if package_path.exists() else None,
        "payload_path": str(payload_path.relative_to(workspace)) if payload_path.exists() else None,
        "payload_sha256": sha256_file(payload_path) if payload_path.exists() else None,
        "signing_profile": receipt.get("signing_profile"),
        "timestamp": receipt.get("timestamp"),
        "caveat": receipt.get("caveat"),
    }


def row_to_run(workspace: pathlib.Path, row: dict[str, Any]) -> dict[str, Any]:
    date = str(row["date"])
    bundle_manifest = workspace / "bundles" / date / "snapshot-summary.json.bundle" / "manifest.json"
    bundle_summary = workspace / "bundles" / date / "snapshot-summary.json"
    return {
        "date": date,
        "counts": {
            "pointer_attempts": row.get("pointer_attempts"),
            "fetched_content_files": row.get("fetched_content_files"),
            "fetch_errors": row.get("fetch_errors"),
            "normalized_xml_artifacts": row.get("normalized_xml_artifacts"),
            "normalization_errors": row.get("normalization_errors"),
            "diff_current_record_count": row.get("diff_current_record_count"),
            "diff_change_count": row.get("diff_change_count"),
            "provider_count_total": row.get("provider_count_total"),
            "service_count_total": row.get("service_count_total"),
            "alert_entry_count": row.get("alert_entry_count"),
        },
        "diff_classes": {
            "listed_document_added": row.get("listed_document_added"),
            "listed_document_removed": row.get("listed_document_removed"),
            "normalized_hash_changed": row.get("normalized_hash_changed"),
            "summary_field_changed": row.get("summary_field_changed"),
            "provider_inventory_changed": row.get("provider_inventory_changed"),
            "service_inventory_changed": row.get("service_inventory_changed"),
            "provider_service_detail_changed": row.get("provider_service_detail_changed"),
        },
        "artifacts": {
            "snapshot_manifest": row.get("snapshot_manifest"),
            "snapshot_manifest_sha256": row.get("snapshot_manifest_sha256"),
            "normalized_manifest": row.get("normalized_manifest"),
            "normalized_manifest_sha256": row.get("normalized_manifest_sha256"),
            "diff": row.get("diff"),
            "diff_sha256": row.get("diff_sha256"),
            "bundle_summary": str(bundle_summary.relative_to(workspace)) if bundle_summary.exists() else None,
            "bundle_summary_sha256": sha256_file(bundle_summary) if bundle_summary.exists() else None,
            "bundle_manifest": str(bundle_manifest.relative_to(workspace)) if bundle_manifest.exists() else None,
            "bundle_manifest_sha256": sha256_file(bundle_manifest) if bundle_manifest.exists() else None,
        },
        "eatf": load_eatf_status(workspace, date),
        "alert_event_types": row.get("alert_event_types") or {},
        "caveat": row.get("caveat") or CAVEAT,
    }


def copy_if_exists(src: pathlib.Path, dst: pathlib.Path) -> dict[str, Any] | None:
    if not src.exists():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return {
        "path": str(dst.name),
        "sha256": sha256_file(dst),
        "size_bytes": dst.stat().st_size,
    }


def copy_text_lf_if_exists(src: pathlib.Path, dst: pathlib.Path) -> dict[str, Any] | None:
    if not src.exists():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(src.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    return {
        "path": str(dst.name),
        "sha256": sha256_file(dst),
        "size_bytes": dst.stat().st_size,
    }


def build_index(workspace: pathlib.Path, public_dir: pathlib.Path, aggregate_json: pathlib.Path | None) -> dict[str, Any]:
    aggregate_path = aggregate_json or find_latest_aggregate(workspace)
    aggregate = read_json(aggregate_path)
    rows = aggregate.get("rows") if isinstance(aggregate.get("rows"), list) else []
    if not rows:
        raise SystemExit("Aggregate output has no rows")

    data_dir = public_dir / "data"
    figures_dir = data_dir / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    aggregate_copy = data_dir / "aggregate-results.json"
    write_json(aggregate_copy, aggregate)
    csv_src = workspace / (aggregate.get("csv") or "notes/aggregate-results-table.csv")
    csv_record = copy_text_lf_if_exists(csv_src, data_dir / "aggregate-results-table.csv")

    figure_records = []
    for src in sorted((workspace / "figures").glob("*.svg")):
        copied = copy_if_exists(src, figures_dir / src.name)
        if copied:
            copied["source"] = str(src.relative_to(workspace))
            figure_records.append(copied)

    runs = [row_to_run(workspace, row) for row in rows]
    latest = runs[-1]
    eatf_ok = sum(1 for run in runs if run["eatf"].get("status") == "ok")
    packaged = sum(1 for run in runs if run["eatf"].get("status") not in {"not_packaged", None})
    index = {
        "schema": "urn:tyche:cassandra:observatory-public-index:0.1",
        "created_at": now_z(),
        "project": "cassandra",
        "case_study_sentence": "Cassandra: from governance infrastructure to evidence infrastructure.",
        "repo": "https://github.com/sapsan14/cassandra",
        "latest_date": latest["date"],
        "run_count": len(runs),
        "packaged_evidence_count": packaged,
        "eatf_verified_count": eatf_ok,
        "aggregate": {
            "source": str(aggregate_path.relative_to(workspace)),
            "source_sha256": sha256_file(aggregate_path),
            "public_json": "data/aggregate-results.json",
            "public_json_sha256": sha256_file(aggregate_copy),
            "public_csv": "data/aggregate-results-table.csv" if csv_record else None,
            "public_csv_sha256": csv_record["sha256"] if csv_record else None,
            "totals": aggregate.get("totals") or {},
            "diff_class_totals": aggregate.get("diff_class_totals") or {},
        },
        "figures": figure_records,
        "runs": runs,
        "claim_boundary": {
            "asserts": [
                "Cassandra records dated structural observation telemetry over local LOTL-derived artifacts.",
                "EATF receipts, when status is ok, verify the corresponding package envelope and payload bytes.",
            ],
            "does_not_assert": [
                "legal effect of any trusted list",
                "signature or certificate validity",
                "supervisory approval",
                "absence of legally relevant change",
            ],
        },
        "caveat": CAVEAT,
    }
    write_json(data_dir / "index.json", index)
    write_json(data_dir / "latest.json", latest)
    return index


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--public-dir", default="observatory/public")
    parser.add_argument("--aggregate-json")
    parser.add_argument("--output")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    public_dir = (workspace / args.public_dir).resolve()
    if not str(public_dir).startswith(str(workspace)):
        raise SystemExit("Public directory must stay inside workspace")
    aggregate_json = (workspace / args.aggregate_json).resolve() if args.aggregate_json else None
    index = build_index(workspace, public_dir, aggregate_json)
    if args.output:
        write_json(workspace / args.output, index)
    print(json.dumps({"status": "ok", "public_index": str((public_dir / "data" / "index.json").relative_to(workspace)), "run_count": index["run_count"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
