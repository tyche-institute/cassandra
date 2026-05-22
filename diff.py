#!/usr/bin/env python3
"""Compare normalized trusted-list snapshots for structural research observation.

This script emits cautious, machine-readable diffs over normalized public XML
snapshots. It does not validate signatures, supervise trust services, determine
legal status, or assert legal effect from any observed change.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
from typing import Any

RESEARCH_CAVEAT = (
    "Structural diff observation only; not signature validation, supervision, "
    "legal-status determination, or relying-party processing. Observed changes "
    "should be treated as XML snapshot churn until independently reviewed."
)
SUMMARY_FIELDS = [
    "root_name",
    "root_namespace",
    "scheme_territory",
    "sequence_number",
    "issue_date_time",
    "next_update",
    "trust_service_provider_count",
    "tsp_service_count",
    "signature_shape",
]
INVENTORY_CAVEAT = (
    "Hashed provider/service inventory diff for structural observation only; "
    "raw listed names are omitted and keys are not legal-status identifiers."
)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(workspace: pathlib.Path, date: str) -> dict[str, Any]:
    manifest_path = workspace / "normalized" / date / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"normalized manifest not found: {manifest_path}")
    manifest = load_json(manifest_path)
    manifest["_manifest_path"] = str(manifest_path.relative_to(workspace))
    manifest["_manifest_sha256"] = sha256_file(manifest_path)
    return manifest


def item_key(item: dict[str, Any]) -> str:
    summary = item.get("summary") or {}
    territory = summary.get("scheme_territory")
    if territory:
        return str(territory)
    source = item.get("source") or item.get("normalized_path") or "unknown"
    return pathlib.Path(str(source)).name


def comparable_records(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for item in manifest.get("items", []):
        if item.get("status") != "ok":
            continue
        key = item_key(item)
        records[key] = {
            "key": key,
            "source": item.get("source"),
            "normalized_path": item.get("normalized_path"),
            "source_sha256": item.get("source_sha256"),
            "normalized_sha256": item.get("normalized_sha256"),
            "summary": item.get("summary") or {},
        }
    return records


def baseline_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "created": now_iso(),
        "date": manifest.get("date"),
        "manifest": manifest.get("_manifest_path"),
        "manifest_sha256": manifest.get("_manifest_sha256"),
        "record_count": len(comparable_records(manifest)),
        "records": comparable_records(manifest),
        "research_caveat": RESEARCH_CAVEAT,
    }


def summary_changes(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    old_summary = old.get("summary") or {}
    new_summary = new.get("summary") or {}
    for field in SUMMARY_FIELDS:
        old_value = old_summary.get(field)
        new_value = new_summary.get(field)
        if old_value != new_value:
            changes.append({
                "class": "summary_field_changed",
                "field": field,
                "old": old_value,
                "new": new_value,
                "caveat": "Field-level structural observation only; no legal-status inference.",
            })
    return changes


def provider_records_by_key(inventory: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(provider.get("provider_key")): provider
        for provider in inventory.get("providers", [])
        if provider.get("provider_key")
    }


def inventory_changes(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare hashed provider/service inventories without raw listed names."""
    changes: list[dict[str, Any]] = []
    old_inventory = (old.get("summary") or {}).get("provider_service_inventory") or {}
    new_inventory = (new.get("summary") or {}).get("provider_service_inventory") or {}
    if not old_inventory and not new_inventory:
        return changes

    old_provider_keys = set(old_inventory.get("provider_keys") or [])
    new_provider_keys = set(new_inventory.get("provider_keys") or [])
    old_service_keys = set(old_inventory.get("service_keys") or [])
    new_service_keys = set(new_inventory.get("service_keys") or [])

    if old_provider_keys != new_provider_keys:
        changes.append({
            "class": "provider_inventory_changed",
            "old_provider_count": old_inventory.get("provider_count"),
            "new_provider_count": new_inventory.get("provider_count"),
            "added_provider_keys": sorted(new_provider_keys - old_provider_keys),
            "removed_provider_keys": sorted(old_provider_keys - new_provider_keys),
            "caveat": INVENTORY_CAVEAT,
        })
    if old_service_keys != new_service_keys:
        changes.append({
            "class": "service_inventory_changed",
            "old_service_count": old_inventory.get("service_count"),
            "new_service_count": new_inventory.get("service_count"),
            "added_service_keys": sorted(new_service_keys - old_service_keys),
            "removed_service_keys": sorted(old_service_keys - new_service_keys),
            "caveat": INVENTORY_CAVEAT,
        })

    old_providers = provider_records_by_key(old_inventory)
    new_providers = provider_records_by_key(new_inventory)
    for provider_key in sorted(set(old_providers) & set(new_providers)):
        old_provider = old_providers[provider_key]
        new_provider = new_providers[provider_key]
        provider_deltas: dict[str, Any] = {}
        for field in ["service_count", "service_status_counts", "service_type_counts"]:
            if old_provider.get(field) != new_provider.get(field):
                provider_deltas[field] = {
                    "old": old_provider.get(field),
                    "new": new_provider.get(field),
                }
        old_provider_services = set(old_provider.get("service_keys") or [])
        new_provider_services = set(new_provider.get("service_keys") or [])
        if old_provider_services != new_provider_services:
            provider_deltas["service_keys"] = {
                "added": sorted(new_provider_services - old_provider_services),
                "removed": sorted(old_provider_services - new_provider_services),
            }
        if provider_deltas:
            changes.append({
                "class": "provider_service_detail_changed",
                "provider_key": provider_key,
                "deltas": provider_deltas,
                "caveat": INVENTORY_CAVEAT,
            })
    return changes


def compare_baselines(old: dict[str, Any], new: dict[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    old_records = old.get("records", {})
    new_records = new.get("records", {})
    for key in sorted(set(new_records) - set(old_records)):
        record = new_records[key]
        changes.append({
            "class": "listed_document_added",
            "key": key,
            "source": record.get("source"),
            "normalized_path": record.get("normalized_path"),
            "new_normalized_sha256": record.get("normalized_sha256"),
            "caveat": "Added comparable XML document in snapshot set; not a trust-status claim.",
        })
    for key in sorted(set(old_records) - set(new_records)):
        record = old_records[key]
        changes.append({
            "class": "listed_document_removed",
            "key": key,
            "source": record.get("source"),
            "normalized_path": record.get("normalized_path"),
            "old_normalized_sha256": record.get("normalized_sha256"),
            "caveat": "Removed comparable XML document from snapshot set; not a trust-status claim.",
        })
    for key in sorted(set(old_records) & set(new_records)):
        old_record = old_records[key]
        new_record = new_records[key]
        if old_record.get("normalized_sha256") != new_record.get("normalized_sha256"):
            changes.append({
                "class": "normalized_hash_changed",
                "key": key,
                "source": new_record.get("source"),
                "normalized_path": new_record.get("normalized_path"),
                "old_normalized_sha256": old_record.get("normalized_sha256"),
                "new_normalized_sha256": new_record.get("normalized_sha256"),
                "caveat": "Canonical XML bytes differ; inspect field-level entries before interpretation.",
            })
            for field_change in summary_changes(old_record, new_record):
                field_change["key"] = key
                field_change["source"] = new_record.get("source")
                field_change["normalized_path"] = new_record.get("normalized_path")
                changes.append(field_change)
            for inventory_change in inventory_changes(old_record, new_record):
                inventory_change["key"] = key
                inventory_change["source"] = new_record.get("source")
                inventory_change["normalized_path"] = new_record.get("normalized_path")
                changes.append(inventory_change)
    return changes


def resolve_baseline(workspace: pathlib.Path, baseline_date: str | None) -> tuple[dict[str, Any] | None, pathlib.Path | None]:
    if baseline_date:
        manifest = load_manifest(workspace, baseline_date)
        return baseline_from_manifest(manifest), workspace / "normalized" / baseline_date / "manifest.json"
    current = workspace / "baselines" / "current.json"
    if current.exists():
        return load_json(current), current
    return None, None


def run_diff(workspace: pathlib.Path, date: str, baseline_date: str | None = None, update_baseline: bool = True) -> dict[str, Any]:
    current_manifest = load_manifest(workspace, date)
    current_baseline = baseline_from_manifest(current_manifest)
    previous_baseline, previous_path = resolve_baseline(workspace, baseline_date)
    baseline_created = previous_baseline is None
    changes = [] if baseline_created else compare_baselines(previous_baseline, current_baseline)

    diff = {
        "created": now_iso(),
        "date": date,
        "baseline_created": baseline_created,
        "baseline_source": None if previous_path is None else str(previous_path.relative_to(workspace)),
        "current_manifest": current_manifest.get("_manifest_path"),
        "current_manifest_sha256": current_manifest.get("_manifest_sha256"),
        "current_record_count": current_baseline["record_count"],
        "change_count": len(changes),
        "changes": changes,
        "summary": {
            "listed_document_added": sum(1 for c in changes if c.get("class") == "listed_document_added"),
            "listed_document_removed": sum(1 for c in changes if c.get("class") == "listed_document_removed"),
            "normalized_hash_changed": sum(1 for c in changes if c.get("class") == "normalized_hash_changed"),
            "summary_field_changed": sum(1 for c in changes if c.get("class") == "summary_field_changed"),
            "provider_inventory_changed": sum(1 for c in changes if c.get("class") == "provider_inventory_changed"),
            "service_inventory_changed": sum(1 for c in changes if c.get("class") == "service_inventory_changed"),
            "provider_service_detail_changed": sum(1 for c in changes if c.get("class") == "provider_service_detail_changed"),
        },
        "research_caveat": RESEARCH_CAVEAT,
    }
    output_path = workspace / "diffs" / f"{date}.json"
    write_json(output_path, diff)

    baseline_snapshot_path = workspace / "baselines" / f"{date}.json"
    write_json(baseline_snapshot_path, current_baseline)
    if update_baseline:
        write_json(workspace / "baselines" / "current.json", current_baseline)

    return diff


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["diff"])
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--baseline-date", help="Optional normalized snapshot date to compare against instead of baselines/current.json")
    parser.add_argument("--no-update-baseline", action="store_true")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    diff = run_diff(
        workspace=workspace,
        date=args.date,
        baseline_date=args.baseline_date,
        update_baseline=not args.no_update_baseline,
    )
    print(json.dumps({
        "date": diff["date"],
        "baseline_created": diff["baseline_created"],
        "baseline_source": diff["baseline_source"],
        "current_record_count": diff["current_record_count"],
        "change_count": diff["change_count"],
        "diff": f"diffs/{args.date}.json",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
