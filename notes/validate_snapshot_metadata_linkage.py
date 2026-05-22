#!/usr/bin/env python3
"""Validate Cassandra snapshot manifest and adjacent metadata linkage.

This is a local reproducibility check only. It verifies that dated raw snapshot
manifests point to local files/metadata whose hashes and endpoint metadata are
internally consistent. It does not perform trusted-list validation, signature
validation, supervision, legal-status determination, public alerting, regulated
trust-service output, or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_CAVEAT_FRAGMENTS = [
    "structural observation",
    "not relying-party validation",
    "legal-status",
]
ERROR_CAVEAT_FRAGMENTS = [
    "no legal-status inference",
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


def validate_date(workspace: Path, date: str) -> dict[str, Any]:
    snapshot_dir = workspace / "snapshots" / date
    manifest_path = snapshot_dir / "manifest.json"
    errors: list[str] = []
    warnings: list[str] = []
    checked_items: list[dict[str, Any]] = []

    if not manifest_path.exists():
        return {
            "status": "error",
            "date": date,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "error_count": 1,
            "warning_count": 0,
            "errors": [f"missing snapshot manifest: {rel(workspace, manifest_path)}"],
            "warnings": [],
            "checked_items": [],
            "research_caveat": "Local snapshot metadata linkage check only; not trusted-list validation, legal-status determination, supervision, signature validation, public alerting, regulated trust-service output, or publication approval.",
        }

    manifest = load_json(manifest_path)
    items = manifest.get("items", [])
    if not isinstance(items, list):
        errors.append("manifest items is not a list")
        items = []

    ok_count = 0
    error_count = 0
    content_type_counts: dict[str, int] = {}
    territory_counts: dict[str, int] = {}

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"item {idx} is not an object")
            continue
        destination_value = item.get("destination")
        if not destination_value:
            errors.append(f"item {idx} missing destination")
            continue
        destination = Path(destination_value)
        if not destination.is_absolute():
            destination = workspace / destination
        try:
            destination.resolve().relative_to(workspace.resolve())
        except ValueError:
            errors.append(f"item {idx} destination outside workspace: {destination}")
            continue

        meta_path = Path(str(destination) + ".meta.json")
        item_result: dict[str, Any] = {
            "index": idx,
            "territory": item.get("territory"),
            "destination": rel(workspace, destination),
            "meta": rel(workspace, meta_path),
            "http_status": item.get("http_status"),
            "has_content": False,
            "metadata_hash_matches": None,
        }
        checked_items.append(item_result)

        if not meta_path.exists():
            errors.append(f"missing adjacent metadata for {rel(workspace, destination)}")
            continue
        meta = load_json(meta_path)

        for field in ("url", "http_status", "sha256", "destination"):
            if meta.get(field) != item.get(field):
                errors.append(
                    f"metadata mismatch for {rel(workspace, destination)} field {field}: manifest={item.get(field)!r} meta={meta.get(field)!r}"
                )

        caveat = str(item.get("research_caveat", "")) + " " + str(meta.get("research_caveat", ""))
        if item.get("error") or item.get("http_status") is None:
            error_count += 1
            if destination.exists():
                errors.append(f"error item unexpectedly has content file: {rel(workspace, destination)}")
            if item.get("sha256") is not None or meta.get("sha256") is not None:
                errors.append(f"error item has non-null sha256: {rel(workspace, destination)}")
            if not all(fragment in caveat for fragment in ERROR_CAVEAT_FRAGMENTS):
                errors.append(f"error item lacks no-legal-status-inference caveat: {rel(workspace, destination)}")
            if not item.get("error"):
                warnings.append(f"error item lacks error type: {rel(workspace, destination)}")
        else:
            ok_count += 1
            if not destination.exists():
                errors.append(f"successful item missing content file: {rel(workspace, destination)}")
                continue
            actual_hash = sha256_file(destination)
            expected_hash = item.get("sha256")
            item_result["has_content"] = True
            item_result["metadata_hash_matches"] = actual_hash == expected_hash
            item_result["actual_sha256"] = actual_hash
            if actual_hash != expected_hash:
                errors.append(f"hash mismatch for {rel(workspace, destination)}: expected {expected_hash}, actual {actual_hash}")
            actual_size = destination.stat().st_size
            if item.get("bytes") != actual_size or meta.get("bytes") != actual_size:
                errors.append(f"byte-size mismatch for {rel(workspace, destination)}")
            if not all(fragment in caveat for fragment in REQUIRED_CAVEAT_FRAGMENTS):
                errors.append(f"successful item lacks required structural-observation caveat fragments: {rel(workspace, destination)}")
            content_type = str(item.get("content_type") or "unknown")
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1

        territory = str(item.get("territory") or "unknown")
        territory_counts[territory] = territory_counts.get(territory, 0) + 1

    if manifest.get("count") != len(items):
        errors.append(f"manifest count {manifest.get('count')} does not match item length {len(items)}")
    if manifest.get("ok_count") != ok_count:
        errors.append(f"manifest ok_count {manifest.get('ok_count')} does not match checked ok_count {ok_count}")
    if manifest.get("error_count") != error_count:
        errors.append(f"manifest error_count {manifest.get('error_count')} does not match checked error_count {error_count}")
    if len(territory_counts) < 20:
        warnings.append(f"low territory diversity in snapshot manifest: {len(territory_counts)} distinct territory codes")

    output = {
        "status": "ok" if not errors else "error",
        "date": date,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "manifest": rel(workspace, manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "item_count": len(items),
        "ok_count": ok_count,
        "error_count_manifest": manifest.get("error_count"),
        "error_count_checked": error_count,
        "content_type_counts": dict(sorted(content_type_counts.items())),
        "territory_count": len(territory_counts),
        "checked_items_sample": checked_items[:5],
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "research_caveat": "Local snapshot metadata linkage check only; not trusted-list validation, legal-status determination, supervision, signature validation, public alerting, regulated trust-service output, or publication approval.",
    }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

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
