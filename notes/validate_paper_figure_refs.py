#!/usr/bin/env python3
"""Validate that paper figure references match local aggregate figure artifacts.

This is a local research-safety and reproducibility check only. It does not
assert legal compliance, trusted-list legal effect, supervision, signature
validation, public alerting, regulated trust-service output, or publication
readiness.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import xml.etree.ElementTree as ET
from typing import Any

FIGURE_PATHS = [
    pathlib.Path("figures/aggregate-run-telemetry.svg"),
    pathlib.Path("figures/aggregate-diff-classes.svg"),
]
REQUIRED_CAVEAT_FRAGMENTS = [
    "legal-status",
    "signature-validation",
    "supervisory",
    "public-alerting",
    "publication-readiness",
]
FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_artifact_index_hashes(index_text: str, rel_path: pathlib.Path) -> list[str]:
    pattern = rf"`{re.escape(str(rel_path))}`[^\n]*`sha256:([0-9a-f]{{64}})`"
    return re.findall(pattern, index_text)


def latest_aggregate_result(workspace: pathlib.Path) -> pathlib.Path | None:
    candidates = sorted((workspace / "notes").glob("aggregate-results-????-??-??-output.json"))
    if not candidates:
        return None
    return candidates[-1].relative_to(workspace)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    paper_path = workspace / "paper" / "draft.md"
    artifact_index_path = workspace / "ARTIFACT_INDEX.md"
    paper = paper_path.read_text(encoding="utf-8")
    artifact_index = artifact_index_path.read_text(encoding="utf-8")

    forbidden_hits = [token for token in FORBIDDEN if token in paper]
    if forbidden_hits:
        errors.append(f"paper contains forbidden tokens: {forbidden_hits}")

    latest_aggregate = latest_aggregate_result(workspace)
    aggregate_summary: dict[str, Any] | None = None
    data_paths = [pathlib.Path("notes/aggregate-results-table.csv")]
    if latest_aggregate is None:
        errors.append("no dated aggregate-results output found")
    else:
        data_paths.append(latest_aggregate)
        aggregate = load_json(workspace / latest_aggregate)
        dates = aggregate.get("dates", [])
        row_count = aggregate.get("row_count")
        csv_rel = pathlib.Path(aggregate.get("csv", "notes/aggregate-results-table.csv"))
        if csv_rel not in data_paths:
            data_paths.insert(0, csv_rel)
        if str(latest_aggregate) not in paper:
            errors.append(f"paper does not reference latest aggregate output: {latest_aggregate}")
        if row_count != len(dates):
            errors.append(f"latest aggregate row_count/date mismatch: row_count={row_count}, dates={dates}")
        if len(dates) >= 2 and "two dated" not in paper and "two-row" not in paper:
            warnings.append("paper does not visibly describe the current aggregate as two-date/two-row telemetry")
        missing_dates = [date for date in dates if date not in paper]
        if missing_dates:
            errors.append(f"paper does not reference aggregate dates: {missing_dates}")
        if "legal-status determination" not in aggregate.get("caveat", ""):
            errors.append("latest aggregate caveat lacks legal-status determination boundary")
        aggregate_summary = {
            "path": str(latest_aggregate),
            "sha256": sha256_path(workspace / latest_aggregate),
            "dates": dates,
            "row_count": row_count,
            "diff_change_count_total": aggregate.get("totals", {}).get("diff_change_count"),
            "csv": str(csv_rel),
        }

    figure_results = []
    for rel_path in FIGURE_PATHS:
        path = workspace / rel_path
        if not path.exists():
            errors.append(f"missing figure: {rel_path}")
            continue
        if str(rel_path) not in paper:
            errors.append(f"paper does not reference figure path: {rel_path}")
        digest = sha256_path(path)
        index_digests = extract_artifact_index_hashes(artifact_index, rel_path)
        if not index_digests:
            errors.append(f"artifact index lacks sha256 row for {rel_path}")
        elif digest not in index_digests:
            errors.append(f"artifact index lacks current sha256 for {rel_path}: actual {digest}")
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"SVG parse error for {rel_path}: {exc}")
            continue
        text = path.read_text(encoding="utf-8")
        missing_caveats = [fragment for fragment in REQUIRED_CAVEAT_FRAGMENTS if fragment not in text and fragment not in paper]
        if missing_caveats:
            errors.append(f"missing required caveat fragments for {rel_path}: {missing_caveats}")
        figure_results.append({
            "path": str(rel_path),
            "sha256": digest,
            "svg_root": root.tag,
            "artifact_index_has_current_sha256": digest in index_digests,
            "artifact_index_sha256_rows": index_digests,
        })

    data_results = []
    seen_data_paths: set[pathlib.Path] = set()
    for rel_path in data_paths:
        if rel_path in seen_data_paths:
            continue
        seen_data_paths.add(rel_path)
        path = workspace / rel_path
        if not path.exists():
            errors.append(f"missing data source: {rel_path}")
            continue
        if str(rel_path) not in paper:
            errors.append(f"paper does not reference figure data path: {rel_path}")
        digest = sha256_path(path)
        index_digests = extract_artifact_index_hashes(artifact_index, rel_path)
        if digest not in index_digests:
            errors.append(f"artifact index lacks current sha256 for data source {rel_path}: actual {digest}")
        data_results.append({
            "path": str(rel_path),
            "sha256": digest,
            "artifact_index_has_current_sha256": digest in index_digests,
        })

    if aggregate_summary:
        csv_path = workspace / pathlib.Path(aggregate_summary["csv"])
        if csv_path.exists():
            with csv_path.open("r", encoding="utf-8", newline="") as fh:
                csv_rows = list(csv.DictReader(fh))
            csv_dates = [row.get("date") for row in csv_rows]
            if csv_dates != aggregate_summary["dates"]:
                errors.append(f"aggregate CSV dates {csv_dates} do not match JSON dates {aggregate_summary['dates']}")
            if len(csv_rows) != aggregate_summary["row_count"]:
                errors.append(f"aggregate CSV row count {len(csv_rows)} does not match JSON row_count {aggregate_summary['row_count']}")

    if "listed names out of narrative" not in paper and "keeps listed names out of narrative" not in paper:
        warnings.append("paper does not contain expected listed-name narrative caveat wording")

    return {
        "schema": "urn:tyche:cassandra:paper-figure-reference-validation:0.2",
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "paper": str(paper_path.relative_to(workspace)),
        "aggregate_results": aggregate_summary,
        "figures": figure_results,
        "data_sources": data_results,
        "research_caveat": "Local paper/figure cross-reference validation only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/paper-figure-reference-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
