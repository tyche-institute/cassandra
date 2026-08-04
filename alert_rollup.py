#!/usr/bin/env python3
"""Append a cautious Cassandra structural-observation alert roll-up entry.

Research-only helper: reads local snapshot, normalization, and diff artifacts and
emits machine-readable telemetry. It does not perform relying-party validation,
supervision, signature verification, legal-status determination, public alerting,
or external publication.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
from typing import Any

SCHEMA = "urn:tyche:cassandra:structural-observation-alert:0.2"
RESEARCH_CAVEAT = (
    "Machine-readable research telemetry only; do not treat as trusted-list "
    "validation, supervisory finding, legal-status determination, signature "
    "verification, public alerting, or publication approval."
)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(workspace: pathlib.Path, path: pathlib.Path) -> str:
    return str(path.resolve().relative_to(workspace.resolve()))


def event_type(diff_doc: dict[str, Any]) -> str:
    if diff_doc.get("baseline_created"):
        return "baseline_initialized"
    if int(diff_doc.get("change_count") or 0) == 0:
        return "no_structural_diff_observed"
    return "structural_diff_observed"


def severity(diff_doc: dict[str, Any]) -> str:
    return "info" if int(diff_doc.get("change_count") or 0) == 0 else "review"


def safe_summary(date: str, diff_doc: dict[str, Any]) -> str:
    changes = int(diff_doc.get("change_count") or 0)
    if diff_doc.get("baseline_created"):
        return (
            f"The {date} structural-observation run initialized a local baseline; "
            "diff entries are empty because no prior baseline was available."
        )
    if changes == 0:
        return (
            f"The {date} structural-observation diff recorded zero machine-readable "
            "structural diff entries against the configured baseline."
        )
    return (
        f"The {date} structural-observation diff recorded {changes} machine-readable "
        "structural diff entries for local research review."
    )


def build_entry(workspace: pathlib.Path, date: str) -> dict[str, Any]:
    snapshot_path = workspace / "snapshots" / date / "manifest.json"
    normalized_path = workspace / "normalized" / date / "manifest.json"
    diff_path = workspace / "diffs" / f"{date}.json"
    missing = [rel(workspace, p) for p in [snapshot_path, normalized_path, diff_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"required local artifacts missing for {date}: {missing}")

    snapshot = load_json(snapshot_path)
    normalized = load_json(normalized_path)
    diff_doc = load_json(diff_path)
    diff_summary = diff_doc.get("summary") or {}

    artifacts: dict[str, str] = {
        "snapshot_manifest": rel(workspace, snapshot_path),
        "normalized_manifest": rel(workspace, normalized_path),
        "diff": rel(workspace, diff_path),
    }
    hashes: dict[str, str] = {
        "snapshot_manifest_sha256": sha256_file(snapshot_path),
        "normalized_manifest_sha256": sha256_file(normalized_path),
        "diff_sha256": sha256_file(diff_path),
    }

    bundle_summary = workspace / "bundles" / date / "snapshot-summary.json"
    bundle_manifest = workspace / "bundles" / date / "snapshot-summary.json.bundle" / "manifest.json"
    if bundle_summary.exists():
        artifacts["bundle_summary"] = rel(workspace, bundle_summary)
        hashes["bundle_summary_sha256"] = sha256_file(bundle_summary)
    if bundle_manifest.exists():
        artifacts["bundle_manifest"] = rel(workspace, bundle_manifest)
        hashes["bundle_manifest_sha256"] = sha256_file(bundle_manifest)

    semantic_rollup_path = workspace / "notes" / f"semantic-diff-rollup-{date}-output.json"
    semantic_rollup_summary: dict[str, Any] | None = None
    if semantic_rollup_path.exists():
        semantic_rollup = load_json(semantic_rollup_path)
        artifacts["semantic_diff_rollup"] = rel(workspace, semantic_rollup_path)
        hashes["semantic_diff_rollup_sha256"] = sha256_file(semantic_rollup_path)
        semantic_rollup_summary = {
            "status": semantic_rollup.get("status"),
            "source_diff_sha256": semantic_rollup.get("diff_sha256"),
            "raw_listed_names_omitted": semantic_rollup.get("raw_listed_names_omitted"),
            "keys_with_selected_movements": semantic_rollup.get("keys_with_selected_movements") or [],
            "service_inventory": {
                "movement_count": (semantic_rollup.get("service_inventory") or {}).get("movement_count"),
                "added_hashed_service_key_total": (semantic_rollup.get("service_inventory") or {}).get("added_hashed_service_key_total"),
                "removed_hashed_service_key_total": (semantic_rollup.get("service_inventory") or {}).get("removed_hashed_service_key_total"),
            },
            "provider_service_detail": {
                "movement_count": (semantic_rollup.get("provider_service_detail") or {}).get("movement_count"),
                "added_hashed_service_key_total": (semantic_rollup.get("provider_service_detail") or {}).get("added_hashed_service_key_total"),
                "removed_hashed_service_key_total": (semantic_rollup.get("provider_service_detail") or {}).get("removed_hashed_service_key_total"),
            },
            "signature_shape": {
                "movement_count": (semantic_rollup.get("signature_shape") or {}).get("movement_count"),
                "old_signature_method_counts": (semantic_rollup.get("signature_shape") or {}).get("old_signature_method_counts") or {},
                "new_signature_method_counts": (semantic_rollup.get("signature_shape") or {}).get("new_signature_method_counts") or {},
                "old_digest_method_counts": (semantic_rollup.get("signature_shape") or {}).get("old_digest_method_counts") or {},
                "new_digest_method_counts": (semantic_rollup.get("signature_shape") or {}).get("new_digest_method_counts") or {},
            },
            "claim_safety_caveat": semantic_rollup.get("claim_safety_caveat"),
        }

    entry_type = event_type(diff_doc)
    entry = {
        "schema": SCHEMA,
        "lane": "cassandra",
        "date": date,
        "created_at": now_iso(),
        "event_type": entry_type,
        "severity": severity(diff_doc),
        "summary": safe_summary(date, diff_doc),
        "counts": {
            "pointer_attempts": snapshot.get("count"),
            "fetched_content_files": snapshot.get("ok_count"),
            "fetch_errors": snapshot.get("error_count"),
            "normalization_inputs": normalized.get("count"),
            "normalized_xml_artifacts": normalized.get("ok_count"),
            "normalization_skips": normalized.get("skipped_count"),
            "normalization_errors": normalized.get("error_count"),
            "diff_current_record_count": diff_doc.get("current_record_count"),
            "diff_change_count": diff_doc.get("change_count"),
            "listed_document_added": diff_summary.get("listed_document_added"),
            "listed_document_removed": diff_summary.get("listed_document_removed"),
            "normalized_hash_changed": diff_summary.get("normalized_hash_changed"),
            "summary_field_changed": diff_summary.get("summary_field_changed"),
            "provider_inventory_changed": diff_summary.get("provider_inventory_changed"),
            "service_inventory_changed": diff_summary.get("service_inventory_changed"),
            "provider_service_detail_changed": diff_summary.get("provider_service_detail_changed"),
        },
        "artifacts": artifacts,
        "hashes": hashes,
        "dedupe_key": f"{SCHEMA}:{date}:{entry_type}:{hashes['diff_sha256']}",
        "claim_safety": {
            "legal_effect": "not asserted",
            "signature_validation": "not performed",
            "supervision_or_operation": "not performed",
            "safe_wording": safe_summary(date, diff_doc),
        },
        "caveat": RESEARCH_CAVEAT,
    }
    if semantic_rollup_summary is not None:
        entry["semantic_diff_rollup"] = semantic_rollup_summary
    return entry


def read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: pathlib.Path, items: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(item, sort_keys=True, separators=(",", ":")) for item in items) + "\n", encoding="utf-8")


def append_or_replace_alert(workspace: pathlib.Path, date: str, *, output: pathlib.Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    alerts_path = workspace / "alerts.jsonl"
    entry = build_entry(workspace, date)
    existing = read_jsonl(alerts_path)
    replaced = False
    for idx, old in enumerate(existing):
        if old.get("dedupe_key") == entry["dedupe_key"]:
            existing[idx] = entry
            replaced = True
            break
    if not replaced:
        existing.append(entry)

    if not dry_run:
        write_jsonl(alerts_path, existing)

    parsed = existing if dry_run else read_jsonl(alerts_path)
    matching = [item for item in parsed if item.get("dedupe_key") == entry["dedupe_key"]]
    errors: list[str] = []
    if len(matching) != 1:
        errors.append(f"expected exactly one matching alert entry, found {len(matching)}")
    if entry["counts"]["diff_change_count"] is None:
        errors.append("diff_change_count is missing")
    if entry["counts"]["diff_current_record_count"] is None:
        errors.append("diff_current_record_count is missing")

    result = {
        "status": "ok" if not errors else "error",
        "errors": errors,
        "dry_run": dry_run,
        "alerts_path": "alerts.jsonl",
        "alerts_sha256": None if dry_run or not alerts_path.exists() else sha256_file(alerts_path),
        "jsonl_entry_count": len(parsed),
        "replaced_existing_entry": replaced,
        "entry": entry,
    }
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        raise RuntimeError("; ".join(errors))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", help="Optional JSON path for verification output, relative to workspace unless absolute.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    output = None
    if args.output:
        candidate = pathlib.Path(args.output)
        output = candidate if candidate.is_absolute() else workspace / candidate
    result = append_or_replace_alert(workspace, args.date, output=output, dry_run=args.dry_run)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
