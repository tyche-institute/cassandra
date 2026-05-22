#!/usr/bin/env python3
"""Validate SOURCES.md coverage for Cassandra dated runs and bundles.

This local validator checks whether SOURCES.md covers the public LOTL-derived
URLs used by dated snapshot manifests and whether MIRROR-style bundle source
lists are internally hash-consistent. It is a provenance/readiness check only:
it does not perform trusted-list validation, signature validation, supervision,
legal-status determination, public alerting, regulated trust-service output, or
publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_CAVEATS = [
    "structural observation",
]
FORBIDDEN_SOURCE_PHRASES = [
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(workspace: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(workspace.resolve()))
    except ValueError:
        return str(path)


def parse_sources_table(sources_md: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in sources_md.splitlines():
        raw = line.strip()
        if not raw.startswith("|") or raw.startswith("|---") or raw.startswith("| Title "):
            continue
        cells = [c.strip() for c in raw.strip("|").split("|")]
        if len(cells) < 5:
            continue
        rows.append({
            "title": cells[0],
            "url_or_path": cells[1],
            "access_date": cells[2],
            "reliability": cells[3],
            "local_copy_or_hash": cells[4],
            "notes": cells[4],
            "raw": raw,
        })
    return rows


def normalize_hash(value: str) -> str:
    m = re.search(r"sha256[:=]([0-9a-fA-F]{64})", value)
    if m:
        return m.group(1).lower()
    m = re.search(r"`?([0-9a-fA-F]{64})`?", value)
    return m.group(1).lower() if m else ""


def row_has_caveat(row: dict[str, str]) -> bool:
    hay = (row["notes"] + " " + row["reliability"] + " " + row["title"]).lower()
    return all(fragment in hay for fragment in REQUIRED_CAVEATS)


def validate_snapshot_manifest(workspace: Path, date: str, rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    records: list[dict[str, Any]] = []
    manifest_path = workspace / "snapshots" / date / "manifest.json"
    if not manifest_path.exists():
        return [], [f"missing snapshot manifest for {date}: {rel(workspace, manifest_path)}"], []
    manifest = load_json(manifest_path)
    for idx, item in enumerate(manifest.get("items", [])):
        if not isinstance(item, dict):
            errors.append(f"{date} manifest item {idx} is not an object")
            continue
        url = str(item.get("url") or "")
        sha = str(item.get("sha256") or "")
        destination = str(item.get("destination") or "")
        territory = str(item.get("territory") or "")
        dest_rel = str(Path(destination).relative_to(workspace)) if destination and Path(destination).is_absolute() and str(Path(destination)).startswith(str(workspace)) else destination
        matches = [r for r in rows if url and url in r["url_or_path"]]
        hash_matches = [r for r in matches if sha and sha in r["local_copy_or_hash"]]
        dest_matches = [r for r in rows if dest_rel and (dest_rel in r["url_or_path"] or dest_rel in r["local_copy_or_hash"] or Path(dest_rel).name in r["title"])]
        record = {
            "date": date,
            "index": idx,
            "territory": territory,
            "url": url,
            "sha256": sha or None,
            "destination": destination,
            "source_row_count": len(matches),
            "hash_row_count": len(hash_matches),
            "destination_row_count": len(dest_matches),
            "covered": bool(matches) and bool(dest_matches),
        }
        if not matches:
            errors.append(f"SOURCES.md lacks URL row for {date} item {idx} {territory}: {url}")
        if not dest_matches:
            errors.append(f"SOURCES.md lacks local path coverage for {date} item {idx} {territory}: {dest_rel}")
        if matches and not any(row_has_caveat(r) for r in matches):
            warnings.append(f"SOURCES.md row for {date} item {idx} {territory} lacks explicit full caveat fragments")
        records.append(record)
    return records, errors, warnings


def validate_bundle(workspace: Path, date: str, rows: list[dict[str, str]]) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    bundle_dir = workspace / "bundles" / date / "snapshot-summary.json.bundle"
    manifest_path = bundle_dir / "manifest.json"
    record: dict[str, Any] = {"date": date, "bundle_manifest": rel(workspace, manifest_path), "source_records": []}
    if not manifest_path.exists():
        errors.append(f"missing bundle manifest for {date}: {rel(workspace, manifest_path)}")
        return record, errors, warnings
    manifest = load_json(manifest_path)
    manifest_sources = manifest.get("sources", [])
    if not isinstance(manifest_sources, list):
        errors.append(f"bundle manifest sources is not a list for {date}")
        manifest_sources = []
    for src in manifest_sources:
        if not isinstance(src, dict):
            errors.append(f"bundle source entry is not object for {date}")
            continue
        src_path = str(src.get("path") or "")
        source_path = bundle_dir / src_path
        expected = ((src.get("sha256") or {}).get("value") if isinstance(src.get("sha256"), dict) else None) or ""
        source_record: dict[str, Any] = {
            "id": src.get("id"),
            "kind": src.get("kind"),
            "path": src_path,
            "exists": source_path.exists(),
            "expected_sha256": expected or None,
        }
        if not source_path.exists():
            errors.append(f"bundle source file missing for {date}: {rel(workspace, source_path)}")
        else:
            actual = sha256_file(source_path)
            source_record["actual_sha256"] = actual
            source_record["hash_matches"] = (not expected) or actual == expected
            if expected and actual != expected:
                errors.append(f"bundle source hash mismatch for {date}: {rel(workspace, source_path)} expected {expected} actual {actual}")
            if src_path.endswith("pointer-url-records.json"):
                pointer = load_json(source_path)
                caveat = str(pointer.get("caveat", "")).lower()
                has_legal_caveat = "does not determine legal status" in caveat or "no legal-status inference" in caveat
                if "structural observation" not in caveat or not has_legal_caveat:
                    warnings.append(f"pointer-url-records caveat is legacy/incomplete for {date}; accepted as a warning for historical bundle validation")
                urls = pointer.get("urls", [])
                covered = 0
                for entry in urls if isinstance(urls, list) else []:
                    u = str(entry.get("url") or "") if isinstance(entry, dict) else ""
                    sh = str(entry.get("sha256") or "") if isinstance(entry, dict) else ""
                    if any(u in r["url_or_path"] for r in rows):
                        covered += 1
                source_record["pointer_url_count"] = len(urls) if isinstance(urls, list) else None
                source_record["pointer_url_sources_md_covered"] = covered
                if isinstance(urls, list) and covered != len(urls):
                    errors.append(f"SOURCES.md does not cover all pointer-url-record URLs for {date}: {covered}/{len(urls)}")
        record["source_records"].append(source_record)
    bundle_title_matches = [r for r in rows if f"{date}" in r["title"] and "bundle" in (r["title"] + r["notes"]).lower()]
    record["bundle_source_rows"] = len(bundle_title_matches)
    if not bundle_title_matches:
        warnings.append(f"SOURCES.md has no date-specific bundle row for {date}; bundle source files were checked directly")
    return record, errors, warnings


def validate(workspace: Path, dates: list[str]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    sources_path = workspace / "SOURCES.md"
    sources_text = sources_path.read_text(encoding="utf-8")
    rows = parse_sources_table(sources_text)
    lower_sources = sources_text.lower()
    for phrase in FORBIDDEN_SOURCE_PHRASES:
        if phrase.lower() in lower_sources:
            errors.append(f"SOURCES.md contains forbidden overclaiming phrase: {phrase}")
    snapshot_records: list[dict[str, Any]] = []
    bundle_records: list[dict[str, Any]] = []
    for date in dates:
        sr, se, sw = validate_snapshot_manifest(workspace, date, rows)
        snapshot_records.extend(sr)
        errors.extend(se)
        warnings.extend(sw)
        br, be, bw = validate_bundle(workspace, date, rows)
        bundle_records.append(br)
        errors.extend(be)
        warnings.extend(bw)
    covered = sum(1 for r in snapshot_records if r.get("covered"))
    return {
        "schema": "urn:tyche:cassandra:sources-coverage-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "dates": dates,
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "sources_md": "SOURCES.md",
        "sources_md_sha256": sha256_file(sources_path),
        "sources_row_count": len(rows),
        "snapshot_item_count": len(snapshot_records),
        "snapshot_item_covered_count": covered,
        "snapshot_records": snapshot_records,
        "bundle_records": bundle_records,
        "research_caveat": "Local provenance coverage check only; this does not perform trusted-list validation, signature validation, supervision, legal-status determination, public alerting, regulated trust-service output, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", action="append", dest="dates", required=True)
    parser.add_argument("--output", default="notes/sources-coverage-validation-output.json")
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    result = validate(workspace, args.dates)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
