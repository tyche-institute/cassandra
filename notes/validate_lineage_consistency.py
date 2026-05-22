#!/usr/bin/env python3
"""Validate Cassandra snapshot-to-normalization-to-diff lineage consistency.

This local reproducibility helper checks that a dated raw snapshot manifest,
normalization manifest, diff JSON, and optional baseline JSON line up by local
paths, hashes, counts, and cautious research-only caveats. It does not perform
trusted-list validation, signature validation, supervision, legal-status
determination, public alerting, regulated trust-service output, or publication
approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAVEAT = (
    "Local snapshot-to-normalization-to-diff lineage telemetry only; not legal "
    "compliance, trusted-list legal effect, signature validation, supervision, "
    "public alerting, regulated trust-service output, or publication readiness."
)

REQUIRED_DIFF_CAVEATS = [
    "Structural diff observation only",
    "not signature validation",
    "legal-status determination",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def rel(workspace: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(workspace.resolve()))
    except ValueError:
        return str(path)


def resolve_workspace_path(workspace: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return workspace / path


def validate_date(workspace: Path, date: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    snapshot_manifest_path = workspace / "snapshots" / date / "manifest.json"
    normalized_manifest_path = workspace / "normalized" / date / "manifest.json"
    diff_path = workspace / "diffs" / f"{date}.json"
    baseline_path = workspace / "baselines" / f"{date}.json"
    current_baseline_path = workspace / "baselines" / "current.json"

    required_paths = {
        "snapshot_manifest": snapshot_manifest_path,
        "normalized_manifest": normalized_manifest_path,
        "diff": diff_path,
    }
    for label, path in required_paths.items():
        if not path.exists():
            errors.append(f"missing {label}: {rel(workspace, path)}")
    if errors:
        return {
            "status": "error",
            "date": date,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "research_caveat": CAVEAT,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
        }

    snapshot_manifest = load_json(snapshot_manifest_path)
    normalized_manifest = load_json(normalized_manifest_path)
    diff = load_json(diff_path)
    baseline = load_json(baseline_path) if baseline_path.exists() else None
    current_baseline = load_json(current_baseline_path) if current_baseline_path.exists() else None

    snapshot_items = snapshot_manifest.get("items", [])
    normalized_items = normalized_manifest.get("items", [])
    if not isinstance(snapshot_items, list):
        errors.append("snapshot manifest items is not a list")
        snapshot_items = []
    if not isinstance(normalized_items, list):
        errors.append("normalized manifest items is not a list")
        normalized_items = []

    snapshot_by_path: dict[str, dict[str, Any]] = {}
    snapshot_success_paths: set[str] = set()
    for idx, item in enumerate(snapshot_items):
        if not isinstance(item, dict):
            errors.append(f"snapshot item {idx} is not an object")
            continue
        dest_value = item.get("destination")
        if not dest_value:
            errors.append(f"snapshot item {idx} missing destination")
            continue
        dest_path = resolve_workspace_path(workspace, str(dest_value))
        dest_rel = rel(workspace, dest_path)
        snapshot_by_path[dest_rel] = item
        if item.get("http_status") is not None and not item.get("error"):
            snapshot_success_paths.add(dest_rel)
            if not dest_path.exists():
                errors.append(f"snapshot success file missing: {dest_rel}")
            elif item.get("sha256") != sha256_file(dest_path):
                errors.append(f"snapshot success hash mismatch: {dest_rel}")

    normalized_ok_paths: set[str] = set()
    normalized_error_sources: set[str] = set()
    normalized_skipped_sources: set[str] = set()
    comparable_keys: set[str] = set()
    status_counts: dict[str, int] = {}
    checked_normalized_sample: list[dict[str, Any]] = []

    for idx, item in enumerate(normalized_items):
        if not isinstance(item, dict):
            errors.append(f"normalized item {idx} is not an object")
            continue
        status = str(item.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        source_value = item.get("source")
        if not source_value:
            errors.append(f"normalized item {idx} missing source")
            continue
        source_path = resolve_workspace_path(workspace, str(source_value))
        source_rel = rel(workspace, source_path)
        if source_rel not in snapshot_success_paths:
            errors.append(f"normalized item source not found among successful snapshot files: {source_rel}")
        if source_path.exists() and item.get("source_sha256") and item.get("source_sha256") != sha256_file(source_path):
            errors.append(f"normalized item source hash mismatch: {source_rel}")

        if status == "ok":
            normalized_path_value = item.get("normalized_path")
            if not normalized_path_value:
                errors.append(f"normalized ok item missing normalized_path for source {source_rel}")
                continue
            normalized_path = resolve_workspace_path(workspace, str(normalized_path_value))
            normalized_rel = rel(workspace, normalized_path)
            normalized_ok_paths.add(normalized_rel)
            if not normalized_path.exists():
                errors.append(f"normalized file missing: {normalized_rel}")
            else:
                actual_norm_hash = sha256_file(normalized_path)
                if item.get("normalized_sha256") != actual_norm_hash:
                    errors.append(f"normalized hash mismatch: {normalized_rel}")
                actual_size = normalized_path.stat().st_size
                if item.get("normalized_bytes") != actual_size:
                    errors.append(f"normalized byte-size mismatch: {normalized_rel}")
            summary = item.get("summary") or {}
            key = str(summary.get("scheme_territory") or source_rel)
            comparable_keys.add(key)
            inventory = summary.get("provider_service_inventory") or {}
            if inventory:
                if inventory.get("provider_count") != summary.get("trust_service_provider_count"):
                    errors.append(f"provider inventory count mismatch for {source_rel}")
                if inventory.get("service_count") != summary.get("tsp_service_count"):
                    errors.append(f"service inventory count mismatch for {source_rel}")
                caveat = str(inventory.get("caveat", ""))
                if "not a legal-status" not in caveat:
                    errors.append(f"inventory caveat missing for {source_rel}")
            checked_normalized_sample.append({
                "source": source_rel,
                "normalized_path": normalized_rel,
                "scheme_territory": summary.get("scheme_territory"),
                "normalized_sha256": item.get("normalized_sha256"),
            })
        elif status in {"skipped", "skipped_non_xml"}:
            normalized_skipped_sources.add(source_rel)
        elif status in {"error", "xml_parse_error"}:
            normalized_error_sources.add(source_rel)
        else:
            warnings.append(f"unknown normalization status {status!r} for {source_rel}")

    snapshot_ok_count = int(snapshot_manifest.get("ok_count") or 0)
    norm_count = int(normalized_manifest.get("count") or 0)
    norm_ok_count = int(normalized_manifest.get("ok_count") or 0)
    norm_skip_count = int(normalized_manifest.get("skipped_count") or 0)
    norm_error_count = int(normalized_manifest.get("error_count") or 0)
    if snapshot_ok_count != len(snapshot_success_paths):
        errors.append(f"snapshot ok_count {snapshot_ok_count} does not match checked successful paths {len(snapshot_success_paths)}")
    if norm_count != len(normalized_items):
        errors.append(f"normalized count {norm_count} does not match item length {len(normalized_items)}")
    if norm_count != snapshot_ok_count:
        errors.append(f"normalized count {norm_count} does not match snapshot ok_count {snapshot_ok_count}")
    if norm_ok_count != len(normalized_ok_paths):
        errors.append(f"normalized ok_count {norm_ok_count} does not match checked ok paths {len(normalized_ok_paths)}")
    if norm_skip_count != len(normalized_skipped_sources):
        errors.append(f"normalized skipped_count {norm_skip_count} does not match checked skipped sources {len(normalized_skipped_sources)}")
    if norm_error_count != len(normalized_error_sources):
        errors.append(f"normalized error_count {norm_error_count} does not match checked error sources {len(normalized_error_sources)}")

    missing_from_normalization = sorted(snapshot_success_paths - {rel(workspace, resolve_workspace_path(workspace, str(i.get("source")))) for i in normalized_items if isinstance(i, dict) and i.get("source")})
    if missing_from_normalization:
        errors.append(f"{len(missing_from_normalization)} successful snapshot files are absent from normalization manifest")

    current_manifest_value = diff.get("current_manifest")
    current_manifest_path = resolve_workspace_path(workspace, str(current_manifest_value)) if current_manifest_value else None
    if current_manifest_path is None or current_manifest_path.resolve() != normalized_manifest_path.resolve():
        errors.append(f"diff current_manifest does not point to normalized manifest for {date}: {current_manifest_value!r}")
    if diff.get("current_manifest_sha256") != sha256_file(normalized_manifest_path):
        errors.append("diff current_manifest_sha256 does not match normalized manifest")
    if diff.get("current_record_count") != norm_ok_count:
        errors.append(f"diff current_record_count {diff.get('current_record_count')} does not match normalized ok_count {norm_ok_count}")
    if diff.get("change_count") != len(diff.get("changes", []) or []):
        errors.append("diff change_count does not match changes length")
    diff_caveat = str(diff.get("research_caveat", ""))
    for fragment in REQUIRED_DIFF_CAVEATS:
        if fragment not in diff_caveat:
            errors.append(f"diff research caveat missing fragment: {fragment}")

    summary = diff.get("summary") or {}
    if not isinstance(summary, dict):
        errors.append("diff summary is not an object")
        summary = {}
    for key, value in summary.items():
        if not isinstance(value, int) or value < 0:
            errors.append(f"diff summary field {key} is not a non-negative integer")

    baseline_sha256 = None
    current_baseline_sha256 = None
    if baseline is None:
        warnings.append(f"baseline file missing for date: {rel(workspace, baseline_path)}")
    else:
        baseline_sha256 = sha256_file(baseline_path)
        baseline_source = baseline.get("baseline_source") or baseline.get("source_manifest") or baseline.get("manifest")
        if baseline_source and resolve_workspace_path(workspace, str(baseline_source)).resolve() != normalized_manifest_path.resolve():
            errors.append(f"date baseline source does not point to normalized manifest: {baseline_source!r}")
        baseline_records = baseline.get("records") or baseline.get("items")
        if isinstance(baseline_records, list) and len(baseline_records) != norm_ok_count:
            errors.append(f"date baseline record count {len(baseline_records)} does not match normalized ok_count {norm_ok_count}")
    if current_baseline is None:
        warnings.append(f"current baseline file missing: {rel(workspace, current_baseline_path)}")
    else:
        current_baseline_sha256 = sha256_file(current_baseline_path)
        current_records = current_baseline.get("records") or current_baseline.get("items")
        if isinstance(current_records, list) and len(current_records) != norm_ok_count:
            warnings.append(f"current baseline record count {len(current_records)} differs from normalized ok_count {norm_ok_count}")

    return {
        "status": "ok" if not errors else "error",
        "date": date,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "research_caveat": CAVEAT,
        "paths": {
            "snapshot_manifest": rel(workspace, snapshot_manifest_path),
            "normalized_manifest": rel(workspace, normalized_manifest_path),
            "diff": rel(workspace, diff_path),
            "baseline": rel(workspace, baseline_path) if baseline_path.exists() else None,
            "current_baseline": rel(workspace, current_baseline_path) if current_baseline_path.exists() else None,
        },
        "hashes": {
            "snapshot_manifest_sha256": sha256_file(snapshot_manifest_path),
            "normalized_manifest_sha256": sha256_file(normalized_manifest_path),
            "diff_sha256": sha256_file(diff_path),
            "baseline_sha256": baseline_sha256,
            "current_baseline_sha256": current_baseline_sha256,
        },
        "counts": {
            "snapshot_item_count": len(snapshot_items),
            "snapshot_ok_count": snapshot_ok_count,
            "normalized_count": norm_count,
            "normalized_ok_count": norm_ok_count,
            "normalized_skipped_count": norm_skip_count,
            "normalized_error_count": norm_error_count,
            "diff_current_record_count": diff.get("current_record_count"),
            "diff_change_count": diff.get("change_count"),
            "comparable_key_count": len(comparable_keys),
        },
        "normalization_status_counts": dict(sorted(status_counts.items())),
        "checked_normalized_sample": checked_normalized_sample[:5],
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--date", required=True)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    workspace = Path(args.workspace).resolve()
    result = validate_date(workspace, args.date)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = workspace / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
