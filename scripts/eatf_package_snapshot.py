#!/usr/bin/env python3
"""Create an EATF/AEP evidence package for a dated Cassandra snapshot.

This wrapper is intentionally conservative. It packages hashes, paths, and
bounded claim text for an already-created Cassandra observation. If EATF signing
inputs are present, it signs and verifies the package through the local EATF
CLI. If signing inputs are absent, it writes an explicit skipped receipt so the
automation remains reproducible without silently inventing trust.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any

SCHEMA = "urn:tyche:cassandra:eatf-observation-package:0.1"
PAYLOAD_SCHEMA = "urn:tyche:cassandra:eatf-observation-payload:0.1"
RECEIPT_SCHEMA = "urn:tyche:cassandra:eatf-verification-receipt:0.1"
CAVEAT = (
    "EATF/AEP receipt for Cassandra structural observation only; it verifies "
    "the evidence package bytes and declared hashes, not trusted-list legal "
    "status, supervision, signature validity, relying-party validation, or "
    "public alerting."
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


def rel(workspace: pathlib.Path, path: pathlib.Path) -> str:
    return str(path.resolve().relative_to(workspace.resolve()))


def artifact_record(workspace: pathlib.Path, name: str, path: pathlib.Path, *, required: bool = True) -> dict[str, Any] | None:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"missing required artifact: {rel(workspace, path)}")
        return None
    return {
        "name": name,
        "path": rel(workspace, path),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def load_counts(workspace: pathlib.Path, date: str) -> dict[str, Any]:
    snapshot = read_json(workspace / "snapshots" / date / "manifest.json")
    normalized = read_json(workspace / "normalized" / date / "manifest.json")
    diff_doc = read_json(workspace / "diffs" / f"{date}.json")
    bundle_path = workspace / "bundles" / date / "snapshot-summary.json"
    bundle = read_json(bundle_path) if bundle_path.exists() else {}
    diff_summary = diff_doc.get("summary") if isinstance(diff_doc.get("summary"), dict) else {}
    bundle_counts = bundle.get("counts") if isinstance(bundle.get("counts"), dict) else {}
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
        "diff_summary": {
            "listed_document_added": diff_summary.get("listed_document_added", 0),
            "listed_document_removed": diff_summary.get("listed_document_removed", 0),
            "normalized_hash_changed": diff_summary.get("normalized_hash_changed", 0),
            "summary_field_changed": diff_summary.get("summary_field_changed", 0),
            "provider_inventory_changed": diff_summary.get("provider_inventory_changed", 0),
            "service_inventory_changed": diff_summary.get("service_inventory_changed", 0),
            "provider_service_detail_changed": diff_summary.get("provider_service_detail_changed", 0),
        },
        "bundle_counts": bundle_counts,
    }


def build_payload(workspace: pathlib.Path, date: str, output_dir: pathlib.Path) -> dict[str, Any]:
    paths = [
        ("snapshot_manifest", workspace / "snapshots" / date / "manifest.json", True),
        ("normalized_manifest", workspace / "normalized" / date / "manifest.json", True),
        ("diff", workspace / "diffs" / f"{date}.json", True),
        ("baseline", workspace / "baselines" / f"{date}.json", False),
        ("bundle_summary", workspace / "bundles" / date / "snapshot-summary.json", False),
        ("bundle_manifest", workspace / "bundles" / date / "snapshot-summary.json.bundle" / "manifest.json", False),
        ("alert_rollup", workspace / "notes" / f"alert-rollup-{date}-output.json", False),
    ]
    artifacts = []
    for name, path, required in paths:
        record = artifact_record(workspace, name, path, required=required)
        if record is not None:
            artifacts.append(record)

    payload = {
        "schema": PAYLOAD_SCHEMA,
        "created_at": now_z(),
        "lane": "cassandra",
        "observation_date": date,
        "case_study_sentence": "Cassandra: from governance infrastructure to evidence infrastructure.",
        "subject": {
            "type": "public_trust_list_structural_observation",
            "scope": "Public LOTL-derived trusted-list snapshot telemetry",
            "workspace": "tyche-institute/cassandra",
        },
        "counts": load_counts(workspace, date),
        "artifacts": artifacts,
        "claim_boundary": {
            "asserts": [
                "The listed local files existed at package time.",
                "The package payload records SHA-256 hashes and bounded telemetry for the dated run.",
                "The AEP verification receipt, when present, verifies the package envelope and payload bytes.",
            ],
            "does_not_assert": [
                "trusted-list legal status",
                "signature validity",
                "supervisory decision",
                "relying-party validation",
                "public alerting or publication approval",
            ],
        },
        "caveat": CAVEAT,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    payload_path = output_dir / "cassandra-observation.json"
    write_json(payload_path, payload)
    payload["payload_path"] = rel(workspace, payload_path)
    payload["payload_sha256"] = sha256_file(payload_path)
    write_json(payload_path, payload)
    return payload


def build_metadata(workspace: pathlib.Path, date: str, output_dir: pathlib.Path, signing_profile: str) -> dict[str, Any]:
    metadata = {
        "schema": SCHEMA,
        "created_at": now_z(),
        "attestation_id": f"att_cassandra_{date.replace('-', '_')}",
        "agent_id": "urn:eatf:tenant:tyche:agent:cassandra-observatory",
        "tenant_id": "tyche-research",
        "action_type": "cassandra.public-trust-list-observation",
        "policy": {
            "purpose": "research evidence packaging",
            "retention": "commit history and public observatory artifact",
            "disclosure": "hashes, counts, paths, and cautious claim boundary only",
        },
        "case_study": "Cassandra: from governance infrastructure to evidence infrastructure.",
        "signing_profile": signing_profile,
        "caveat": CAVEAT,
    }
    path = output_dir / "eatf-metadata.json"
    write_json(path, metadata)
    return metadata


def command_output(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr


def parse_verify_output(text: str) -> dict[str, Any] | None:
    for line in reversed([line.strip() for line in text.splitlines() if line.strip()]):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def sign_and_verify(
    *,
    workspace: pathlib.Path,
    payload_path: pathlib.Path,
    metadata_path: pathlib.Path,
    aep_path: pathlib.Path,
    eatf_root: pathlib.Path,
    key_path: pathlib.Path,
    public_key_path: pathlib.Path,
    timestamp: str,
    timestamp_label: str,
    scope: str,
    signing_profile: str,
) -> dict[str, Any]:
    sign_cli = eatf_root / "cli" / "eatf-sign" / "bin" / "eatf-sign.js"
    verify_cli = eatf_root / "cli" / "eatf-verify" / "bin" / "eatf-verify.js"
    for path in [sign_cli, verify_cli, key_path, public_key_path]:
        if not path.exists():
            raise FileNotFoundError(str(path))

    sign_cmd = [
        "node",
        str(sign_cli),
        "--payload",
        str(payload_path),
        "--key",
        str(key_path),
        "--public-key",
        str(public_key_path),
        "--metadata",
        str(metadata_path),
        "--scope",
        scope,
        "--timestamp",
        timestamp,
        "--out",
        str(aep_path),
    ]
    sign_code, sign_stdout, sign_stderr = command_output(sign_cmd)
    if sign_code != 0:
        return {
            "schema": RECEIPT_SCHEMA,
            "status": "sign_failed",
            "created_at": now_z(),
            "aep_package": rel(workspace, aep_path) if aep_path.exists() else None,
            "sign_exit_code": sign_code,
            "sign_stdout": sign_stdout,
            "sign_stderr": sign_stderr,
            "caveat": CAVEAT,
        }

    verify_cmd = ["node", str(verify_cli), str(aep_path), "--json"]
    verify_code, verify_stdout, verify_stderr = command_output(verify_cmd)
    parsed = parse_verify_output(verify_stdout)
    if isinstance(parsed, dict):
        parsed["path"] = rel(workspace, aep_path)
    valid = bool(parsed.get("valid")) if isinstance(parsed, dict) else verify_code == 0
    status = "ok" if verify_code == 0 and valid else "verify_failed"
    failure_logs = {} if status == "ok" else {"verify_stdout": verify_stdout, "verify_stderr": verify_stderr}
    return {
        "schema": RECEIPT_SCHEMA,
        "status": status,
        "created_at": now_z(),
        "aep_package": rel(workspace, aep_path),
        "aep_sha256": sha256_file(aep_path) if aep_path.exists() else None,
        "payload": rel(workspace, payload_path),
        "payload_sha256": sha256_file(payload_path),
        "metadata": rel(workspace, metadata_path),
        "metadata_sha256": sha256_file(metadata_path),
        "scope": scope,
        "signing_profile": signing_profile,
        "timestamp": timestamp_label,
        "verify_exit_code": verify_code,
        "verify": parsed,
        **failure_logs,
        "caveat": CAVEAT,
    }


def skipped_receipt(
    missing: list[str],
    *,
    workspace: pathlib.Path,
    payload_path: pathlib.Path,
    metadata_path: pathlib.Path,
    signing_profile: str,
    timestamp_label: str | None,
) -> dict[str, Any]:
    return {
        "schema": RECEIPT_SCHEMA,
        "status": "skipped_missing_signing_inputs",
        "created_at": now_z(),
        "missing_inputs": missing,
        "aep_package": None,
        "payload": rel(workspace, payload_path),
        "payload_sha256": sha256_file(payload_path),
        "metadata": rel(workspace, metadata_path),
        "metadata_sha256": sha256_file(metadata_path),
        "signing_profile": signing_profile,
        "timestamp": timestamp_label,
        "caveat": CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--out-dir", default="evidence")
    parser.add_argument("--eatf-root")
    parser.add_argument("--key")
    parser.add_argument("--public-key")
    parser.add_argument("--timestamp")
    parser.add_argument("--timestamp-label", help="Human-readable timestamp source to store in receipts.")
    parser.add_argument("--scope", default="foundational:public-trust-list-observation")
    parser.add_argument("--signing-profile", default="operator-supplied", help="Receipt label for the signing key/profile.")
    parser.add_argument("--require-signing", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    output_dir = (workspace / args.out_dir / args.date).resolve()
    if not str(output_dir).startswith(str(workspace)):
        raise SystemExit("Output directory must stay inside workspace")

    payload = build_payload(workspace, args.date, output_dir)
    build_metadata(workspace, args.date, output_dir, args.signing_profile)
    payload_path = output_dir / "cassandra-observation.json"
    metadata_path = output_dir / "eatf-metadata.json"
    aep_path = output_dir / "cassandra-observation.aep"
    receipt_path = output_dir / "eatf-verification.json"
    timestamp_label = args.timestamp_label or args.timestamp

    missing: list[str] = []
    eatf_root = pathlib.Path(args.eatf_root).resolve() if args.eatf_root else None
    key_path = pathlib.Path(args.key).resolve() if args.key else None
    public_key_path = pathlib.Path(args.public_key).resolve() if args.public_key else None
    if eatf_root is None or not eatf_root.exists():
        missing.append("eatf_root")
    if key_path is None or not key_path.exists():
        missing.append("private_key")
    if public_key_path is None or not public_key_path.exists():
        missing.append("public_key")
    if not args.timestamp:
        missing.append("timestamp")

    if missing:
        receipt = skipped_receipt(
            missing,
            workspace=workspace,
            payload_path=payload_path,
            metadata_path=metadata_path,
            signing_profile=args.signing_profile,
            timestamp_label=timestamp_label,
        )
        write_json(receipt_path, receipt)
        if args.output:
            write_json(workspace / args.output, {"status": receipt["status"], "payload": payload, "receipt": receipt})
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 1 if args.require_signing else 0

    try:
        receipt = sign_and_verify(
            workspace=workspace,
            payload_path=payload_path,
            metadata_path=metadata_path,
            aep_path=aep_path,
            eatf_root=eatf_root,  # type: ignore[arg-type]
            key_path=key_path,  # type: ignore[arg-type]
            public_key_path=public_key_path,  # type: ignore[arg-type]
            timestamp=args.timestamp,
            timestamp_label=timestamp_label,
            scope=args.scope,
            signing_profile=args.signing_profile,
        )
    except FileNotFoundError as exc:
        receipt = skipped_receipt(
            [str(exc)],
            workspace=workspace,
            payload_path=payload_path,
            metadata_path=metadata_path,
            signing_profile=args.signing_profile,
            timestamp_label=timestamp_label,
        )
        if args.require_signing:
            receipt["status"] = "failed_missing_signing_inputs"

    write_json(receipt_path, receipt)
    if args.output:
        write_json(workspace / args.output, {"status": receipt["status"], "payload": payload, "receipt": receipt})
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if args.require_signing and receipt.get("status") != "ok":
        return 1
    return 0 if receipt.get("status") in {"ok", "skipped_missing_signing_inputs"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
