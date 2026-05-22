#!/usr/bin/env python3
"""Bootstrap step 10 consistency check for Cassandra lane state.

Research-only local verifier. It reads existing local manifests and writes a
small JSON note. It does not fetch, publish, validate signatures, determine
legal status, or supervise any trusted list.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
DATE = "2026-05-20"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: pathlib.Path):
    if not path.exists():
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            rows.append({"line": line_no, "record": json.loads(line)})
    return rows


def main() -> int:
    required = [
        "PLAN.md",
        "HERMES_PROGRESS.md",
        "ARTIFACT_INDEX.md",
        "SOURCES.md",
        "CLAIMS.md",
        "fetch.py",
        "parse.py",
        "diff.py",
        f"snapshots/{DATE}/manifest.json",
        f"normalized/{DATE}/manifest.json",
        f"diffs/{DATE}.json",
        f"bundles/{DATE}/snapshot-summary.json",
        f"bundles/{DATE}/snapshot-summary.json.bundle/manifest.json",
        "alerts.jsonl",
    ]
    presence = {rel: (WORKSPACE / rel).exists() for rel in required}
    missing = [rel for rel, ok in presence.items() if not ok]

    snapshot_manifest = load_json(WORKSPACE / "snapshots" / DATE / "manifest.json")
    normalized_manifest = load_json(WORKSPACE / "normalized" / DATE / "manifest.json")
    diff = load_json(WORKSPACE / "diffs" / f"{DATE}.json")
    bundle_manifest = load_json(WORKSPACE / "bundles" / DATE / "snapshot-summary.json.bundle" / "manifest.json")
    alerts = read_jsonl(WORKSPACE / "alerts.jsonl")

    expected_counts = {
        "snapshot_pointer_attempts": snapshot_manifest.get("count"),
        "snapshot_ok_count": snapshot_manifest.get("ok_count"),
        "snapshot_error_count": snapshot_manifest.get("error_count"),
        "normalized_count": normalized_manifest.get("count"),
        "normalized_ok_count": normalized_manifest.get("ok_count"),
        "normalized_skipped_count": normalized_manifest.get("skipped_count"),
        "normalized_error_count": normalized_manifest.get("error_count"),
        "diff_record_count": diff.get("current_record_count"),
        "diff_change_count": diff.get("change_count"),
        "alert_entries": len(alerts),
    }

    errors = []
    if missing:
        errors.append({"class": "missing_required_file", "paths": missing})
    if expected_counts["snapshot_pointer_attempts"] != 43:
        errors.append({"class": "unexpected_snapshot_count", "value": expected_counts["snapshot_pointer_attempts"]})
    if expected_counts["snapshot_ok_count"] != 41 or expected_counts["snapshot_error_count"] != 2:
        errors.append({"class": "unexpected_fetch_counts", "counts": expected_counts})
    if expected_counts["normalized_ok_count"] != 31 or expected_counts["normalized_skipped_count"] != 9 or expected_counts["normalized_error_count"] != 1:
        errors.append({"class": "unexpected_normalization_counts", "counts": expected_counts})
    if not diff.get("baseline_created") or diff.get("change_count") != 0:
        errors.append({"class": "unexpected_baseline_diff", "baseline_created": diff.get("baseline_created"), "change_count": diff.get("change_count")})
    if not alerts or alerts[-1]["record"].get("event_type") != "baseline_initialized":
        errors.append({"class": "unexpected_alert_tail", "tail": alerts[-1]["record"] if alerts else None})
    # The MIRROR-style manifest stores the artifact path relative to the bundle
    # directory (`../snapshot-summary.json`), which resolves to the expected
    # workspace artifact. Accept both the resolved and already-normalized forms.
    artifact_path = bundle_manifest.get("artifact", {}).get("path")
    artifact_resolved = None
    if artifact_path:
        artifact_resolved = (WORKSPACE / "bundles" / DATE / "snapshot-summary.json.bundle" / artifact_path).resolve()
    expected_artifact = (WORKSPACE / "bundles" / DATE / "snapshot-summary.json").resolve()
    if artifact_resolved != expected_artifact and artifact_path not in {"bundles/2026-05-20/snapshot-summary.json", "snapshot-summary.json"}:
        errors.append({"class": "unexpected_bundle_artifact", "artifact": bundle_manifest.get("artifact"), "resolved": str(artifact_resolved) if artifact_resolved else None})

    output = {
        "created": dt.datetime.now(dt.timezone.utc).isoformat(),
        "date": DATE,
        "workspace": str(WORKSPACE),
        "status": "ok" if not errors else "error",
        "errors": errors,
        "presence": presence,
        "counts": expected_counts,
        "hashes": {
            rel: sha256_file(WORKSPACE / rel)
            for rel, ok in presence.items()
            if ok and rel not in {"HERMES_PROGRESS.md", "ARTIFACT_INDEX.md", "CLAIMS.md", "SOURCES.md"}
        },
        "next_semantic_diff_class": "trust_service_provider_count_change drill-down into listed-entity additions/removals using hashed provider/service keys, with listed names kept only in machine-readable records unless explicitly approved.",
        "research_caveat": "Local consistency check only; not signature validation, supervision, legal-status determination, public alerting, or relying-party processing.",
    }
    output_path = WORKSPACE / "notes" / "bootstrap-step10-consistency.json"
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "errors": errors, "output": str(output_path.relative_to(WORKSPACE)), "counts": expected_counts}, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
