#!/usr/bin/env python3
"""Create the 2026-05-20 Cassandra structural-observation alert entry.

Research-only: this script emits machine-readable operational/diff telemetry only.
It does not perform relying-party validation, supervision, signature verification, or
legal-status determination.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
DATE = "2026-05-20"
ALERTS = WORKSPACE / "alerts.jsonl"
OUTPUT = WORKSPACE / "notes" / "alerts-2026-05-20-output.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(rel: str) -> dict:
    return json.loads((WORKSPACE / rel).read_text(encoding="utf-8"))


def main() -> None:
    snapshot = load_json(f"snapshots/{DATE}/manifest.json")
    normalized = load_json(f"normalized/{DATE}/manifest.json")
    diff = load_json(f"diffs/{DATE}.json")
    bundle = load_json(f"bundles/{DATE}/snapshot-summary.json")

    entry = {
        "schema": "urn:tyche:cassandra:structural-observation-alert:0.1",
        "lane": "cassandra",
        "date": DATE,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "event_type": "baseline_initialized" if diff.get("baseline_created") else "structural_diff_observed",
        "severity": "info",
        "summary": "Baseline structural-observation run recorded with no observed diff entries because no previous baseline was available.",
        "counts": {
            "pointer_attempts": snapshot.get("count"),
            "fetched_content_files": snapshot.get("ok_count"),
            "fetch_errors": snapshot.get("error_count"),
            "normalization_inputs": normalized.get("count"),
            "normalized_xml_artifacts": normalized.get("ok_count"),
            "normalization_skips": normalized.get("skipped_count"),
            "normalization_errors": normalized.get("error_count"),
            "diff_current_record_count": diff.get("current_record_count"),
            "diff_change_count": diff.get("change_count"),
            "listed_document_added": diff.get("summary", {}).get("listed_document_added"),
            "listed_document_removed": diff.get("summary", {}).get("listed_document_removed"),
            "normalized_hash_changed": diff.get("summary", {}).get("normalized_hash_changed"),
            "summary_field_changed": diff.get("summary", {}).get("summary_field_changed"),
        },
        "artifacts": {
            "snapshot_manifest": f"snapshots/{DATE}/manifest.json",
            "normalized_manifest": f"normalized/{DATE}/manifest.json",
            "diff": f"diffs/{DATE}.json",
            "bundle_summary": f"bundles/{DATE}/snapshot-summary.json",
            "bundle_manifest": f"bundles/{DATE}/snapshot-summary.json.bundle/manifest.json",
        },
        "hashes": {
            "snapshot_manifest_sha256": sha256(WORKSPACE / f"snapshots/{DATE}/manifest.json"),
            "normalized_manifest_sha256": sha256(WORKSPACE / f"normalized/{DATE}/manifest.json"),
            "diff_sha256": sha256(WORKSPACE / f"diffs/{DATE}.json"),
            "bundle_summary_sha256": sha256(WORKSPACE / f"bundles/{DATE}/snapshot-summary.json"),
            "bundle_manifest_sha256": sha256(WORKSPACE / f"bundles/{DATE}/snapshot-summary.json.bundle/manifest.json"),
        },
        "claim_safety": {
            "legal_effect": "not asserted",
            "signature_validation": "not performed",
            "supervision_or_operation": "not performed",
            "safe_wording": "The 2026-05-20 structural-observation run initialized a baseline and recorded no diff entries against a prior baseline because no prior baseline was available.",
        },
        "caveat": "Machine-readable research telemetry only; do not treat as trusted-list validation, supervisory finding, legal-status determination, or publication approval.",
    }

    existing = []
    if ALERTS.exists():
        for line in ALERTS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing.append(json.loads(line))

    replaced = False
    for i, old in enumerate(existing):
        if old.get("schema") == entry["schema"] and old.get("date") == DATE and old.get("event_type") == entry["event_type"]:
            existing[i] = entry
            replaced = True
            break
    if not replaced:
        existing.append(entry)

    ALERTS.write_text("\n".join(json.dumps(item, sort_keys=True, separators=(",", ":")) for item in existing) + "\n", encoding="utf-8")

    # Verify JSONL and consistency with source counts.
    parsed = [json.loads(line) for line in ALERTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    matching = [item for item in parsed if item.get("date") == DATE and item.get("event_type") == entry["event_type"]]
    errors = []
    if len(matching) != 1:
        errors.append(f"expected exactly one matching alert entry, found {len(matching)}")
    if entry["counts"]["diff_change_count"] != 0:
        errors.append("expected day-one baseline diff_change_count to remain 0")
    if entry["counts"]["diff_current_record_count"] != 31:
        errors.append("expected 31 comparable normalized XML records")

    output = {
        "status": "ok" if not errors else "error",
        "errors": errors,
        "alerts_path": "alerts.jsonl",
        "alerts_sha256": sha256(ALERTS),
        "entry": entry,
        "source_bundle_counts": bundle.get("counts", {}),
        "jsonl_entry_count": len(parsed),
        "replaced_existing_entry": replaced,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
