#!/usr/bin/env python3
"""Render cautious SVG figures from Cassandra aggregate telemetry.

Research-only helper. Figures summarize local structural-observation counts
from aggregate JSON/CSV outputs. They do not assert legal effect, trusted-list
status, supervision, signature validity, public alerting, or publication
readiness.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CAVEAT = (
    "Local structural-observation telemetry only; not trusted-list validation, "
    "not legal-status determination, not supervision, not signature validation, "
    "not public alerting, and not publication approval."
)

RUN_FIELDS = [
    ("pointer_attempts", "Pointer attempts", "#5B8DEF"),
    ("fetched_content_files", "Fetched files", "#39A275"),
    ("fetch_errors", "Fetch errors", "#D97706"),
    ("normalized_xml_artifacts", "Normalized XML", "#7C3AED"),
    ("normalization_skips", "Non-XML skips", "#64748B"),
    ("normalization_errors", "Parser errors", "#DC2626"),
    ("diff_current_record_count", "Comparable records", "#0891B2"),
    ("diff_change_count", "Diff entries", "#BE123C"),
]

DIFF_FIELDS = [
    ("listed_document_added", "Documents added", "#2563EB"),
    ("listed_document_removed", "Documents removed", "#9333EA"),
    ("normalized_hash_changed", "Normalized hash", "#0F766E"),
    ("summary_field_changed", "Summary field", "#EA580C"),
    ("provider_inventory_changed", "Provider inventory", "#4F46E5"),
    ("service_inventory_changed", "Service inventory", "#16A34A"),
    ("provider_service_detail_changed", "Provider/service detail", "#DB2777"),
]

FORBIDDEN_STRINGS = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer eIDAS-aligned trust services",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def int_value(row: dict[str, Any], field: str) -> int:
    value = row.get(field, 0)
    if value in (None, ""):
        return 0
    return int(value)


def svg_bar_chart(
    *,
    title: str,
    subtitle: str,
    fields: list[tuple[str, str, str]],
    rows: list[dict[str, Any]],
    source_csv: str,
    source_csv_sha256: str,
    schema: str,
) -> str:
    dates = [str(row.get("date", "unknown")) for row in rows]
    totals = {field: sum(int_value(row, field) for row in rows) for field, _, _ in fields}
    max_value = max([1, *totals.values()])
    width = 960
    left = 260
    top = 150
    row_height = 40
    bar_max = 560
    height = top + len(fields) * row_height + 130
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    metadata = {
        "schema": schema,
        "created_at": created_at,
        "lane": "cassandra",
        "title": title,
        "dates": dates,
        "source_csv": source_csv,
        "source_csv_sha256": source_csv_sha256,
        "row_count": len(rows),
        "fields": [field for field, _, _ in fields],
        "caveat": CAVEAT,
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<metadata id="cassandra-figure-metadata">{html.escape(json.dumps(metadata, sort_keys=True))}</metadata>',
        f'<title id="title">{html.escape(title)}</title>',
        f'<desc id="desc">{html.escape(subtitle + " " + CAVEAT)}</desc>',
        '<rect width="100%" height="100%" fill="#0f172a"/>',
        f'<text x="40" y="52" fill="#e2e8f0" font-family="Inter, Arial, sans-serif" font-size="24" font-weight="700">{html.escape(title)}</text>',
        f'<text x="40" y="84" fill="#94a3b8" font-family="Inter, Arial, sans-serif" font-size="14">{html.escape(subtitle)}</text>',
        f'<text x="40" y="108" fill="#fbbf24" font-family="Inter, Arial, sans-serif" font-size="12">{html.escape(CAVEAT)}</text>',
    ]
    for idx, (field, label, color) in enumerate(fields):
        value = totals[field]
        y = top + idx * row_height
        bar_width = 0 if value == 0 else max(3, round((value / max_value) * bar_max))
        lines.extend([
            f'<text x="40" y="{y + 18}" fill="#cbd5e1" font-family="Inter, Arial, sans-serif" font-size="13">{html.escape(label)}</text>',
            f'<rect x="{left}" y="{y}" width="{bar_width}" height="22" rx="4" fill="{color}"/>',
            f'<text x="{left + bar_width + 12}" y="{y + 17}" fill="#e2e8f0" font-family="Inter, Arial, sans-serif" font-size="13">{value}</text>',
        ])
    footer_y = height - 48
    lines.extend([
        f'<text x="40" y="{footer_y}" fill="#94a3b8" font-family="Inter, Arial, sans-serif" font-size="12">Source: {html.escape(source_csv)} (sha256:{html.escape(source_csv_sha256)})</text>',
        f'<text x="40" y="{footer_y + 22}" fill="#64748b" font-family="Inter, Arial, sans-serif" font-size="11">Dates summarized: {html.escape(", ".join(dates))}. Listed names are intentionally absent from this figure.</text>',
        "</svg>",
    ])
    return "\n".join(lines) + "\n"


def ensure_safe_text(text: str) -> None:
    for needle in FORBIDDEN_STRINGS:
        if needle in text:
            raise SystemExit(f"Forbidden string present in figure output: {needle}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--aggregate-json", default="notes/aggregate-results-2026-05-20-output.json")
    parser.add_argument("--aggregate-csv", default="notes/aggregate-results-table.csv")
    parser.add_argument("--output", default="notes/figure-render-output.json")
    parser.add_argument("--figures-dir", default="figures")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    aggregate_json = (workspace / args.aggregate_json).resolve()
    aggregate_csv = (workspace / args.aggregate_csv).resolve()
    output_path = (workspace / args.output).resolve()
    figures_dir = (workspace / args.figures_dir).resolve()
    for path in [aggregate_json, aggregate_csv, output_path, figures_dir]:
        if not str(path).startswith(str(workspace)):
            raise SystemExit("All paths must stay inside workspace")
    if not aggregate_json.exists() or not aggregate_csv.exists():
        raise SystemExit("Aggregate JSON and CSV must exist before rendering figures")

    aggregate = load_json(aggregate_json)
    rows = aggregate.get("rows") if isinstance(aggregate.get("rows"), list) else []
    csv_rows = load_csv_rows(aggregate_csv)
    if not rows or len(rows) != len(csv_rows):
        raise SystemExit("Aggregate rows must be non-empty and match CSV row count")

    figures_dir.mkdir(parents=True, exist_ok=True)
    source_csv_rel = str(aggregate_csv.relative_to(workspace))
    source_csv_sha = sha256_file(aggregate_csv)
    outputs = []
    figure_specs = [
        (
            "aggregate-run-telemetry.svg",
            "Cassandra aggregate run telemetry",
            "Counts from local dated snapshot, normalization, diff, and alert manifests.",
            RUN_FIELDS,
            "urn:tyche:cassandra:figure:aggregate-run-telemetry:0.1",
        ),
        (
            "aggregate-diff-classes.svg",
            "Cassandra aggregate diff-class telemetry",
            "Machine-readable structural diff classes summarized as local counts.",
            DIFF_FIELDS,
            "urn:tyche:cassandra:figure:aggregate-diff-classes:0.1",
        ),
    ]
    for filename, title, subtitle, fields, schema in figure_specs:
        svg = svg_bar_chart(
            title=title,
            subtitle=subtitle,
            fields=fields,
            rows=rows,
            source_csv=source_csv_rel,
            source_csv_sha256=source_csv_sha,
            schema=schema,
        )
        ensure_safe_text(svg)
        path = figures_dir / filename
        path.write_text(svg, encoding="utf-8")
        outputs.append({
            "path": str(path.relative_to(workspace)),
            "sha256": sha256_file(path),
            "schema": schema,
            "title": title,
        })

    result = {
        "schema": "urn:tyche:cassandra:figure-render:0.1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "lane": "cassandra",
        "status": "ok",
        "aggregate_json": str(aggregate_json.relative_to(workspace)),
        "aggregate_json_sha256": sha256_file(aggregate_json),
        "aggregate_csv": source_csv_rel,
        "aggregate_csv_sha256": source_csv_sha,
        "row_count": len(rows),
        "figures": outputs,
        "caveat": CAVEAT,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
