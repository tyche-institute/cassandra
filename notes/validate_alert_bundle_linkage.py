#!/usr/bin/env python3
"""Validate linkage between Cassandra alert entries and evidence bundles.

Local research-only workflow check. It verifies that alert JSONL artifact pointers
exist, that recorded hashes match current local files, and that dated bundle
manifests point to the expected snapshot-summary artifact. It is not legal
analysis, trusted-list validation, supervision, signature verification, public
alerting, or publication approval.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

RESEARCH_CAVEAT = (
    "Alert/bundle linkage validation is local structural-observation telemetry only; "
    "it does not assert legal effect, trusted-list status, signature validity, "
    "supervision, public alerting, regulated trust-service output, or publication readiness."
)

HASH_KEY_TO_ARTIFACT = {
    "bundle_manifest_sha256": "bundle_manifest",
    "bundle_summary_sha256": "bundle_summary",
    "diff_sha256": "diff",
    "normalized_manifest_sha256": "normalized_manifest",
    "snapshot_manifest_sha256": "snapshot_manifest",
}

OPTIONAL_HASH_KEY_TO_ARTIFACT = {
    "semantic_diff_rollup_sha256": "semantic_diff_rollup",
}


def file_sha256(path: Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(workspace: Path) -> dict[str, Any]:
    alerts_path = workspace / "alerts.jsonl"
    errors: list[str] = []
    warnings: list[str] = []
    entries: list[dict[str, Any]] = []

    if not alerts_path.exists():
        errors.append("missing alerts.jsonl")
    else:
        for idx, line in enumerate(alerts_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"alerts.jsonl line {idx} is not valid JSON: {exc}")
                continue
            entry["__line__"] = idx
            entries.append(entry)

    checked: list[dict[str, Any]] = []
    dates = sorted({str(e.get("date")) for e in entries if e.get("date")})

    for entry in entries:
        line = entry.get("__line__")
        date = str(entry.get("date", ""))
        artifacts = entry.get("artifacts") or {}
        hashes = entry.get("hashes") or {}
        caveat_text = " ".join(str(entry.get(k, "")) for k in ("caveat", "summary"))
        claim_safety = entry.get("claim_safety") or {}
        caveat_text += " " + " ".join(str(v) for v in claim_safety.values())
        for required in ["research telemetry", "not asserted", "not performed"]:
            if required not in caveat_text:
                warnings.append(f"alert line {line} missing caveat fragment {required!r}")

        entry_result = {"line": line, "date": date, "event_type": entry.get("event_type"), "artifacts": []}
        for hash_key, artifact_key in HASH_KEY_TO_ARTIFACT.items():
            rel = artifacts.get(artifact_key)
            recorded_hash = hashes.get(hash_key)
            if not rel:
                errors.append(f"alert line {line} missing artifact pointer {artifact_key}")
                continue
            path = workspace / rel
            if not path.exists():
                errors.append(f"alert line {line} artifact {rel} does not exist")
                continue
            actual = file_sha256(path)
            matches = bool(recorded_hash and actual == recorded_hash)
            if not recorded_hash:
                errors.append(f"alert line {line} missing hash {hash_key}")
            elif not matches:
                warnings.append(
                    f"alert line {line} historical hash mismatch for {rel}: "
                    f"recorded {recorded_hash}, current {actual}; treat as append-only legacy telemetry unless no newer matching entry exists"
                )
            entry_result["artifacts"].append({"path": rel, "recorded_sha256": recorded_hash, "actual_sha256": actual, "matches": matches})

        for hash_key, artifact_key in OPTIONAL_HASH_KEY_TO_ARTIFACT.items():
            rel = artifacts.get(artifact_key)
            recorded_hash = hashes.get(hash_key)
            if not rel and not recorded_hash:
                continue
            if not rel or not recorded_hash:
                errors.append(f"alert line {line} incomplete optional artifact/hash pair {artifact_key}/{hash_key}")
                continue
            path = workspace / rel
            if not path.exists():
                errors.append(f"alert line {line} optional artifact {rel} does not exist")
                continue
            actual = file_sha256(path)
            matches = actual == recorded_hash
            if not matches:
                warnings.append(
                    f"alert line {line} historical hash mismatch for optional {rel}: "
                    f"recorded {recorded_hash}, current {actual}; treat as append-only legacy telemetry unless no newer matching entry exists"
                )
            entry_result["artifacts"].append({"path": rel, "recorded_sha256": recorded_hash, "actual_sha256": actual, "matches": matches, "optional": True})

        semantic_rollup = entry.get("semantic_diff_rollup") or {}
        if semantic_rollup:
            if semantic_rollup.get("raw_listed_names_omitted") is not True:
                errors.append(f"alert line {line} semantic_diff_rollup missing raw-listed-names omission marker")
            if semantic_rollup.get("source_diff_sha256") != hashes.get("diff_sha256"):
                warnings.append(f"alert line {line} semantic_diff_rollup source diff hash does not match alert diff hash")
            if "legal effect" not in str(semantic_rollup.get("claim_safety_caveat", "")):
                warnings.append(f"alert line {line} semantic_diff_rollup caveat missing legal-effect wording")

        bundle_manifest_rel = artifacts.get("bundle_manifest")
        bundle_summary_rel = artifacts.get("bundle_summary")
        if bundle_manifest_rel and (workspace / bundle_manifest_rel).exists():
            manifest = load_json(workspace / bundle_manifest_rel)
            if manifest.get("schema") != "urn:tyche:mirror:bundle:0.1":
                warnings.append(f"alert line {line} bundle manifest has unexpected schema {manifest.get('schema')!r}")
            producer_mode = str((manifest.get("producer") or {}).get("mode", ""))
            if "research-only" not in producer_mode:
                errors.append(f"alert line {line} bundle manifest missing research-only producer mode")
            artifact = manifest.get("artifact") or {}
            artifact_hash = ((artifact.get("sha256") or {}).get("value"))
            if bundle_summary_rel and artifact_hash:
                summary_path = workspace / bundle_summary_rel
                if summary_path.exists() and file_sha256(summary_path) != artifact_hash:
                    errors.append(f"alert line {line} bundle manifest artifact hash does not match {bundle_summary_rel}")
        checked.append(entry_result)

    return {
        "schema": "urn:tyche:cassandra:alert-bundle-linkage-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "dates": dates,
        "entry_count": len(entries),
        "checked_entries": checked,
        "research_caveat": RESEARCH_CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/alert-bundle-linkage-validation-output.json")
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    result = validate(workspace)
    output = (workspace / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "error_count": result["error_count"], "warning_count": result["warning_count"], "output": str(output)}, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
