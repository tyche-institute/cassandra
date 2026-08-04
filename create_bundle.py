#!/usr/bin/env python3
"""Create a MIRROR-style Cassandra snapshot-summary evidence bundle.

Research-only helper: summarizes local Cassandra fetch, normalization, diff, and
baseline artifacts for one dated run. It does not perform relying-party
validation, signature verification, supervision, legal-status determination,
regulated trust-service output, public alerting, or external publication.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import shutil
from typing import Any

RESEARCH_CAVEAT = (
    "Cassandra bundle for research-only structural observation; not legal-status "
    "determination, supervision, signature validation, relying-party processing, "
    "public alerting, regulated trust-service output, or publication readiness."
)


def now_z() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_path(path: pathlib.Path) -> str:
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


def required_inputs(workspace: pathlib.Path, date: str) -> dict[str, pathlib.Path]:
    return {
        "snapshot_manifest": workspace / "snapshots" / date / "manifest.json",
        "normalized_manifest": workspace / "normalized" / date / "manifest.json",
        "diff": workspace / "diffs" / f"{date}.json",
        "baseline": workspace / "baselines" / f"{date}.json",
        "pointers": workspace / "notes" / "pointers.json",
    }


def existing_outputs(workspace: pathlib.Path, date: str) -> list[str]:
    bundle_root = workspace / "bundles" / date
    candidates = [
        bundle_root / "snapshot-summary.json",
        bundle_root / "snapshot-summary.json.bundle",
    ]
    return [str(path.relative_to(workspace)) for path in candidates if path.exists()]


def summarize_counts(snapshot: dict[str, Any], normalized: dict[str, Any], diff_doc: dict[str, Any]) -> dict[str, Any]:
    summary = diff_doc.get("summary") or {}
    return {
        "pointer_attempts": snapshot.get("count"),
        "fetched_content_files": snapshot.get("ok_count"),
        "fetch_errors": snapshot.get("error_count"),
        "normalization_inputs": normalized.get("count"),
        "normalized_xml_artifacts": normalized.get("ok_count"),
        "normalization_skips": normalized.get("skipped_count"),
        "normalization_errors": normalized.get("error_count"),
        "diff_current_record_count": diff_doc.get("current_record_count"),
        "diff_change_count": diff_doc.get("change_count"),
        "baseline_created": diff_doc.get("baseline_created"),
        "provider_inventory_changed": summary.get("provider_inventory_changed", 0),
        "service_inventory_changed": summary.get("service_inventory_changed", 0),
        "provider_service_detail_changed": summary.get("provider_service_detail_changed", 0),
    }


def make_pointer_url_record(date: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "urn:tyche:cassandra:pointer-url-records:0.2",
        "created_at": now_z(),
        "source": f"snapshots/{date}/manifest.json",
        "urls": [
            {
                "territory": item.get("territory"),
                "url": item.get("url"),
                "http_status": item.get("http_status"),
                "sha256": item.get("sha256"),
                "destination": item.get("destination"),
                "error_type": item.get("error_type"),
            }
            for item in snapshot.get("items", [])
        ],
        "caveat": "URLs are public LOTL-derived fetch targets recorded for structural observation only; this record does not determine legal status or endpoint validity.",
    }


def build_bundle(workspace: pathlib.Path, date: str, *, allow_existing: bool, dry_run: bool) -> dict[str, Any]:
    workspace = workspace.resolve()
    inputs = required_inputs(workspace, date)
    missing = [str(path.relative_to(workspace)) for path in inputs.values() if not path.exists()]
    existing = existing_outputs(workspace, date)

    preflight = {
        "schema": "urn:tyche:cassandra:bundle-run:0.2",
        "created_at": now_z(),
        "date": date,
        "workspace": str(workspace),
        "dry_run": dry_run,
        "existing_outputs": existing,
        "missing_inputs": missing,
        "research_caveat": RESEARCH_CAVEAT,
    }
    if missing:
        return {**preflight, "status": "missing_inputs", "message": "Required dated local inputs are absent; run daily fetch/normalize/diff first."}
    if existing and not allow_existing:
        return {**preflight, "status": "refused_existing_outputs", "message": "Refusing to overwrite existing bundle outputs without --allow-existing."}
    if dry_run:
        return {**preflight, "status": "dry_run_ok", "planned_outputs": [f"bundles/{date}/snapshot-summary.json", f"bundles/{date}/snapshot-summary.json.bundle/"]}

    snapshot = read_json(inputs["snapshot_manifest"])
    normalized = read_json(inputs["normalized_manifest"])
    diff_doc = read_json(inputs["diff"])

    bundle_root = workspace / "bundles" / date
    bundle_dir = bundle_root / "snapshot-summary.json.bundle"
    sources_dir = bundle_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "schema": "urn:tyche:cassandra:snapshot-summary:0.2",
        "created_at": now_z(),
        "date": date,
        "workspace": str(workspace),
        "scope": "Research-only structural observation of public LOTL-derived trusted-list snapshots.",
        "caveats": [
            "This artifact does not perform relying-party validation, signature verification, supervision, legal-status determination, public alerting, or publication readiness assessment.",
            "Fetch failures, parser results, and diffs are operational or structural observations only.",
            "Listed names are intentionally not reproduced in prose; detailed machine-readable snapshot files remain local workspace artifacts.",
        ],
        "inputs": {
            "lotl_url": "https://ec.europa.eu/tools/lotl/eu-lotl.xml",
            "pointers_file": "notes/pointers.json",
        },
        "counts": summarize_counts(snapshot, normalized, diff_doc),
        "artifact_paths": {
            "snapshot_manifest": f"snapshots/{date}/manifest.json",
            "normalized_manifest": f"normalized/{date}/manifest.json",
            "diff": f"diffs/{date}.json",
            "baseline": f"baselines/{date}.json",
        },
        "hashes": {name + "_sha256": sha256_path(path) for name, path in inputs.items()},
    }
    artifact_path = bundle_root / "snapshot-summary.json"
    write_json(artifact_path, artifact)
    artifact_sha = sha256_path(artifact_path)

    source_specs: list[tuple[str, str, pathlib.Path, str, str]] = [
        ("src-001", "local_file", inputs["snapshot_manifest"], "sources/snapshot-manifest.json", "local-run-manifest"),
        ("src-002", "local_file", inputs["normalized_manifest"], "sources/normalized-manifest.json", "local-run-manifest"),
        ("src-003", "local_file", inputs["diff"], f"sources/diff-{date}.json", "local-run-diff"),
        ("src-004", "local_file", inputs["baseline"], f"sources/baseline-{date}.json", "local-run-baseline"),
        ("src-005", "local_file", inputs["pointers"], "sources/pointers.json", "local-derived"),
    ]
    lotl_meta = workspace / "sources" / "eu-lotl.xml.meta.json"
    if lotl_meta.exists():
        source_specs.append(("src-006", "local_file", lotl_meta, "sources/eu-lotl.xml.meta.json", "primary-metadata"))

    sources: list[dict[str, Any]] = []
    for sid, kind, src, rel, reliability in source_specs:
        dst = bundle_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        sources.append({
            "id": sid,
            "kind": kind,
            "path": rel,
            "sha256": {"algorithm": "SHA-256", "value": sha256_path(dst)},
            "accessed_at": now_z(),
            "reliability": reliability,
        })

    pointer_record_path = sources_dir / "pointer-url-records.json"
    write_json(pointer_record_path, make_pointer_url_record(date, snapshot))
    sources.append({
        "id": "src-007",
        "kind": "url_record",
        "path": "sources/pointer-url-records.json",
        "sha256": {"algorithm": "SHA-256", "value": sha256_path(pointer_record_path)},
        "accessed_at": now_z(),
        "reliability": "primary-url-record",
    })

    bundle_id = "urn:tyche:mirror:bundle:" + artifact_sha[:32]
    manifest = {
        "schema": "urn:tyche:mirror:bundle:0.1",
        "schema_version": "0.1.0",
        "bundle_version": "0.2.0",
        "bundle_id": bundle_id,
        "bundle_created_at": now_z(),
        "created_at": now_z(),
        "canonicalization": "mirror-bundle-json-v0.1",
        "created_by": {"name": "Anton Sokolov", "affiliation": "Tyche Institute, Tallinn, Estonia"},
        "producer": {"lane": "cassandra", "project": "Project Zeus", "mode": "research-only structural observation"},
        "attestation": {"signed": False, "timestamped": False, "caveat": "No regulated trust-service output is created by this bundle."},
        "artifact": {"path": "../snapshot-summary.json", "sha256": {"algorithm": "SHA-256", "value": artifact_sha}, "media_type": "application/json"},
        "sources": sources,
        "claims_file": "claims.json",
        "notes_file": "notes.md",
        "assumptions": [
            "The bundle summarizes local run artifacts already present in the Cassandra workspace.",
            "Counts are parser and fetcher telemetry, not legal or supervisory findings.",
            "Diff entries are structural observations and do not assert legally relevant change or absence of such change.",
        ],
        "dependencies": [
            {"name": "python", "path": ".venv/bin/python"},
            {"name": "lxml", "purpose": "XML parsing and canonicalization"},
            {"name": "requests-cache", "purpose": "HTTP retrieval support"},
        ],
    }
    write_json(bundle_dir / "manifest.json", manifest)

    counts = artifact["counts"]
    claims = {
        "schema": "urn:tyche:mirror:claims:0.1",
        "bundle_id": bundle_id,
        "claims": [
            {
                "id": "claim-001",
                "text": f"The {date} Cassandra run recorded {counts['pointer_attempts']} LOTL-derived pointer attempts, {counts['fetched_content_files']} fetched content files, and {counts['fetch_errors']} fetch errors.",
                "evidence": [{"source_id": "src-001", "pointer": "sources/snapshot-manifest.json", "locator": "$.count,$.ok_count,$.error_count"}],
                "risk": "low",
                "safe_wording": f"The {date} structural-observation run recorded fetched snapshot-file and fetch-error counts among LOTL-derived pointers; these are operational observations only.",
                "notes": "No trusted-list legal status is inferred.",
            },
            {
                "id": "claim-002",
                "text": f"The {date} normalizer recorded {counts['normalized_xml_artifacts']} normalized XML artifacts, {counts['normalization_skips']} skips, and {counts['normalization_errors']} parser errors.",
                "evidence": [{"source_id": "src-002", "pointer": "sources/normalized-manifest.json", "locator": "$.ok_count,$.skipped_count,$.error_count"}],
                "risk": "low",
                "safe_wording": f"The {date} normalizer recorded aggregate parser telemetry only.",
                "notes": "No signature validity, relying-party validation, or legal effect is asserted.",
            },
            {
                "id": "claim-003",
                "text": f"The {date} diff recorded {counts['diff_change_count']} machine-readable structural diff entries over {counts['diff_current_record_count']} comparable records.",
                "evidence": [{"source_id": "src-003", "pointer": f"sources/diff-{date}.json", "locator": "$.current_record_count,$.change_count,$.summary"}],
                "risk": "medium",
                "safe_wording": f"The {date} diff records machine-readable structural observations against the configured baseline only.",
                "notes": "Diff counts do not assert legal effect, supervision, listed-entity status, or absence of legally relevant change.",
            },
        ],
    }
    write_json(bundle_dir / "claims.json", claims)

    notes = f"""# Cassandra {date} snapshot summary bundle

## Purpose

This MIRROR-style bundle records reproducible local provenance for the Cassandra lane's {date} snapshot, normalization, baseline, and diff summary. It is a research-only evidence bundle for structural observation.

## Methodology

The lane used the locally pinned Python environment to fetch public LOTL-derived inputs, normalize XML-like artifacts, and compare normalized records against the configured structural-observation baseline. This bundle summarizes local manifests rather than reproducing every raw XML/PDF file.

## Known gaps

- The bundle does not perform cryptographic signature verification.
- The bundle does not determine or assert legal status for any listed entity or service.
- Endpoint fetches and parser outcomes are operational telemetry only.
- Diff entries are structural observations, not legal or supervisory findings.

## Assumptions

- Local workspace files referenced by hashes remain available for deeper replay.
- Counts are tool telemetry and should be reviewed before public use.
- Prose should remain aggregate-only unless Anton explicitly approves named-entity discussion.
"""
    (bundle_dir / "notes.md").write_text(notes, encoding="utf-8")

    errors: list[str] = []
    for rel in ["manifest.json", "claims.json", "notes.md"]:
        if not (bundle_dir / rel).exists():
            errors.append(f"missing {rel}")
    if sha256_path(artifact_path) != manifest["artifact"]["sha256"]["value"]:
        errors.append("artifact hash mismatch")
    for src in manifest["sources"]:
        p = bundle_dir / src["path"]
        if not p.exists():
            errors.append(f"missing source {src['path']}")
        elif sha256_path(p) != src["sha256"]["value"]:
            errors.append(f"source hash mismatch {src['path']}")
    verification = {"status": "ok" if not errors else "fail", "errors": errors, "bundle_dir": str(bundle_dir), "artifact": str(artifact_path), "research_caveat": RESEARCH_CAVEAT}
    verify_path = bundle_dir / "verification.json"
    write_json(verify_path, verification)

    files = [artifact_path, bundle_dir / "manifest.json", bundle_dir / "claims.json", bundle_dir / "notes.md", verify_path] + [bundle_dir / src["path"] for src in sources]
    hashes = {str(path.relative_to(workspace)): sha256_path(path) for path in files}
    return {**preflight, "status": "ok" if not errors else "fail", "verification": verification, "hashes": hashes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--allow-existing", action="store_true", help="Permit replacing existing bundle outputs for the same date.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", help="Optional JSON output path relative to workspace unless absolute.")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    result = build_bundle(workspace, args.date, allow_existing=args.allow_existing, dry_run=args.dry_run)
    if args.output:
        out = pathlib.Path(args.output)
        if not out.is_absolute():
            out = workspace / out
        write_json(out, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") in {"ok", "dry_run_ok", "refused_existing_outputs", "missing_inputs"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
