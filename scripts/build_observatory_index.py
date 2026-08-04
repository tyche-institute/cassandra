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

EATF_VERIFIER_URL = "https://eatf.eu/verify"
CANONICAL_URL = "https://cassandra.eatf.eu/"
FALLBACK_URL = "https://cassandra-observatory.pages.dev/"
PUBLIC_EVIDENCE_FILES = {
    "package": "cassandra-observation.aep",
    "payload": "cassandra-observation.json",
    "receipt": "eatf-verification.json",
    "metadata": "eatf-metadata.json",
}


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


def public_file_record(path: pathlib.Path, public_dir: pathlib.Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(public_dir)),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def copy_public_evidence(workspace: pathlib.Path, public_dir: pathlib.Path, date: str) -> dict[str, Any]:
    records: dict[str, Any] = {}
    source_dir = workspace / "evidence" / date
    target_dir = public_dir / "evidence" / date
    for key, filename in PUBLIC_EVIDENCE_FILES.items():
        src = source_dir / filename
        if not src.exists():
            records[key] = None
            continue
        dst = target_dir / filename
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        records[key] = public_file_record(dst, public_dir)
    return records


def load_eatf_status(workspace: pathlib.Path, date: str, public_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
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
            "verifier_url": EATF_VERIFIER_URL,
        }
    receipt = read_json(receipt_path)
    verify = receipt.get("verify") if isinstance(receipt.get("verify"), dict) else {}
    valid = verify.get("valid") if isinstance(verify, dict) else None
    public_evidence = public_evidence or {}
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
        "verifier_url": EATF_VERIFIER_URL,
        "public_package": public_evidence.get("package"),
        "public_payload": public_evidence.get("payload"),
        "public_receipt": public_evidence.get("receipt"),
        "public_metadata": public_evidence.get("metadata"),
    }


def row_to_run(workspace: pathlib.Path, row: dict[str, Any], public_evidence: dict[str, Any] | None = None) -> dict[str, Any]:
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
        "eatf": load_eatf_status(workspace, date, public_evidence),
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


def card_base(card_id: str, title: str) -> dict[str, Any]:
    return {
        "schema": "urn:tyche:cassandra:observatory-card:0.1",
        "id": card_id,
        "project": "cassandra",
        "title": title,
        "case_study_sentence": "Cassandra: from governance infrastructure to evidence infrastructure.",
        "caveat": CAVEAT,
        "not_a": (
            "trusted-list validation; legal-status determination; signature validation; "
            "supervision; compliance judgment; relying-party processing; public alerting; "
            "publication approval"
        ),
    }


def build_dashboard_cards(index: dict[str, Any], cards_dir: pathlib.Path) -> dict[str, Any]:
    """Write compact, caveated dashboard cards derived from the public index."""
    latest_run = index["runs"][-1]
    cards: dict[str, dict[str, Any]] = {}

    claim_boundary = card_base("claim-boundary", "Claim boundary")
    claim_boundary.update(
        {
            "summary": "Cassandra observes and packages structural telemetry over saved LOTL-derived public artifacts.",
            "data": index["claim_boundary"],
            "interpretation": "Evidence integrity and aggregate method telemetry are in scope; legal interpretation is out of scope.",
        }
    )
    cards["claim-boundary.json"] = claim_boundary

    latest = card_base("latest-run", "Latest Cassandra run")
    latest.update(
        {
            "summary": "Latest dated structural-observation run exposed through the public index.",
            "data": {
                "date": latest_run["date"],
                "pointer_attempts": latest_run["counts"].get("pointer_attempts"),
                "fetched_content_files": latest_run["counts"].get("fetched_content_files"),
                "fetch_errors": latest_run["counts"].get("fetch_errors"),
                "normalized_xml_artifacts": latest_run["counts"].get("normalized_xml_artifacts"),
                "diff_change_count": latest_run["counts"].get("diff_change_count"),
                "eatf_status": latest_run["eatf"].get("status"),
            },
            "interpretation": "Run counts describe Cassandra's saved workflow telemetry for the date, not external legal state.",
        }
    )
    cards["latest-run.json"] = latest

    eatf = card_base("eatf-receipt", "EATF receipt boundary")
    eatf.update(
        {
            "summary": "Latest EATF/AEP receipt status for the Cassandra evidence package.",
            "data": {
                "date": latest_run["date"],
                "status": latest_run["eatf"].get("status"),
                "valid": latest_run["eatf"].get("valid"),
                "package_path": latest_run["eatf"].get("package_path"),
                "package_sha256": latest_run["eatf"].get("package_sha256"),
                "receipt_path": latest_run["eatf"].get("receipt_path"),
                "receipt_sha256": latest_run["eatf"].get("receipt_sha256"),
                "public_package": latest_run["eatf"].get("public_package"),
                "public_receipt": latest_run["eatf"].get("public_receipt"),
                "verifier_url": latest_run["eatf"].get("verifier_url"),
                "signing_profile": latest_run["eatf"].get("signing_profile"),
            },
            "interpretation": "A status of ok verifies package bytes, envelope structure, and declared hashes only.",
        }
    )
    cards["eatf-receipt.json"] = eatf

    aggregate = card_base("aggregate-diffs", "Aggregate structural diffs")
    aggregate.update(
        {
            "summary": "Diff-class totals across public Cassandra runs.",
            "data": {
                "run_count": index["run_count"],
                "latest_date": index["latest_date"],
                "diff_change_count": index["aggregate"]["totals"].get("diff_change_count"),
                "diff_class_totals": index["aggregate"].get("diff_class_totals") or {},
            },
            "interpretation": "Diff classes are local structural-observation buckets against Cassandra baselines, not compliance or legal-effect classes.",
        }
    )
    cards["aggregate-diffs.json"] = aggregate

    caveat = card_base("caveat", "Dashboard caveat")
    caveat.update(
        {
            "summary": "Reusable public caveat for dashboard panels and downstream cards.",
            "data": {"caveat": CAVEAT, "source": "observatory public index"},
            "interpretation": "Keep this caveat attached to dashboard cards, figures, and public-index excerpts.",
        }
    )
    cards["caveat.json"] = caveat

    card_records = []
    for name in sorted(cards):
        path = cards_dir / name
        write_json(path, cards[name])
        card_records.append({"path": f"data/cards/{name}", "sha256": sha256_file(path), "size_bytes": path.stat().st_size})

    cards_index = {
        "schema": "urn:tyche:cassandra:observatory-card-index:0.1",
        "project": "cassandra",
        "card_count": len(card_records),
        "cards": card_records,
        "caveat": CAVEAT,
        "not_a": "trusted-list validation; legal-status determination; signature validation; supervision; compliance judgment; public alerting; publication approval",
    }
    cards_index["sha256"] = hashlib.sha256(json.dumps(cards_index, sort_keys=True).encode("utf-8")).hexdigest()
    write_json(cards_dir / "index.json", cards_index)
    return {
        "index": "data/cards/index.json",
        "index_sha256": cards_index["sha256"],
        "card_count": len(card_records),
        "cards": card_records,
    }


def build_index(workspace: pathlib.Path, public_dir: pathlib.Path, aggregate_json: pathlib.Path | None) -> dict[str, Any]:
    aggregate_path = aggregate_json or find_latest_aggregate(workspace)
    aggregate = read_json(aggregate_path)
    rows = aggregate.get("rows") if isinstance(aggregate.get("rows"), list) else []
    if not rows:
        raise SystemExit("Aggregate output has no rows")

    data_dir = public_dir / "data"
    figures_dir = data_dir / "figures"
    evidence_dir = public_dir / "evidence"
    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    if evidence_dir.exists():
        shutil.rmtree(evidence_dir)

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

    public_evidence_by_date = {
        str(row["date"]): copy_public_evidence(workspace, public_dir, str(row["date"]))
        for row in rows
    }
    runs = [row_to_run(workspace, row, public_evidence_by_date.get(str(row["date"]))) for row in rows]
    latest = runs[-1]
    eatf_ok = sum(1 for run in runs if run["eatf"].get("status") == "ok")
    packaged = sum(1 for run in runs if run["eatf"].get("status") not in {"not_packaged", None})
    index = {
        "schema": "urn:tyche:cassandra:observatory-public-index:0.1",
        "created_at": now_z(),
        "project": "cassandra",
        "case_study_sentence": "Cassandra: from governance infrastructure to evidence infrastructure.",
        "ai_governance_bridge": {
            "boundary": "Cassandra is not an AI monitor and does not inspect models.",
            "role": (
                "Sample public governance-artifact case study for the evidence "
                "discipline that AI governance will need."
            ),
            "future_case_studies": [
                "agent attestations",
                "agent cards",
                "evaluation receipts",
                "incident records",
                "lifecycle-monitoring snapshots",
                "decision-transcript packages",
            ],
        },
        "repo": "https://github.com/tyche-institute/cassandra",
        "canonical_url": CANONICAL_URL,
        "fallback_url": FALLBACK_URL,
        "eatf": {
            "name": "Agent Trust Framework",
            "home": "https://eatf.eu/",
            "verifier": EATF_VERIFIER_URL,
        },
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
    index["dashboard_cards"] = build_dashboard_cards(index, data_dir / "cards")
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
