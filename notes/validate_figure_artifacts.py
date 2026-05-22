#!/usr/bin/env python3
"""Validate Cassandra SVG figure artifacts.

Local research-only validator for generated figure artifacts. It checks SVG
parseability, embedded metadata, source CSV hashes, required caveats, and
forbidden overclaiming strings. It does not assert legal effect, trusted-list
status, supervision, signature validity, public alerting, or publication
readiness.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_CAVEAT_FRAGMENTS = [
    "structural-observation telemetry",
    "not trusted-list validation",
    "not legal-status determination",
    "not supervision",
    "not signature validation",
    "not public alerting",
    "not publication approval",
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

EXPECTED_FIGURE_SCHEMAS = {
    "urn:tyche:cassandra:figure:aggregate-run-telemetry:0.1",
    "urn:tyche:cassandra:figure:aggregate-diff-classes:0.1",
}

SVG_NS = "{http://www.w3.org/2000/svg}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def add_error(errors: list[dict[str, Any]], code: str, detail: str) -> None:
    errors.append({"code": code, "detail": detail})


def add_warning(warnings: list[dict[str, Any]], code: str, detail: str) -> None:
    warnings.append({"code": code, "detail": detail})


def parse_svg_metadata(path: Path, errors: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        add_error(errors, "svg_parse_error", f"{path}: {exc}")
        return {}
    if root.tag != f"{SVG_NS}svg":
        add_error(errors, "not_svg", f"{path}: root tag is {root.tag!r}")
        return {}
    metadata_node = None
    for node in root:
        if node.tag == f"{SVG_NS}metadata" and node.attrib.get("id") == "cassandra-figure-metadata":
            metadata_node = node
            break
    if metadata_node is None or not metadata_node.text:
        add_error(errors, "missing_metadata", f"{path}: missing cassandra figure metadata")
        return {}
    try:
        return json.loads(html.unescape(metadata_node.text))
    except json.JSONDecodeError as exc:
        add_error(errors, "metadata_json_error", f"{path}: {exc}")
        return {}


def validate(workspace: Path, render_output: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checked_paths: list[str] = []

    if not render_output.exists():
        add_error(errors, "missing_render_output", f"Missing render output: {render_output}")
        render: dict[str, Any] = {}
    else:
        checked_paths.append(str(render_output.relative_to(workspace)))
        render = load_json(render_output)
        if render.get("schema") != "urn:tyche:cassandra:figure-render:0.1":
            add_error(errors, "render_schema_mismatch", f"Unexpected render schema: {render.get('schema')!r}")
        if render.get("status") != "ok":
            add_error(errors, "render_status_not_ok", f"Render status is {render.get('status')!r}")

    render_text = render_output.read_text(encoding="utf-8") if render_output.exists() else ""
    for needle in FORBIDDEN_STRINGS:
        if needle in render_text:
            add_error(errors, "forbidden_string", f"Forbidden string present in render output: {needle}")

    aggregate_csv_rel = render.get("aggregate_csv") if isinstance(render.get("aggregate_csv"), str) else ""
    aggregate_csv = (workspace / aggregate_csv_rel).resolve() if aggregate_csv_rel else None
    aggregate_csv_sha = render.get("aggregate_csv_sha256")
    if not aggregate_csv_rel or aggregate_csv is None or not aggregate_csv.exists():
        add_error(errors, "missing_aggregate_csv", f"Render output references missing aggregate CSV: {aggregate_csv_rel!r}")
    elif not str(aggregate_csv).startswith(str(workspace)):
        add_error(errors, "csv_outside_workspace", f"Aggregate CSV outside workspace: {aggregate_csv}")
    elif aggregate_csv_sha != sha256_file(aggregate_csv):
        add_error(errors, "csv_hash_mismatch", "Render output aggregate_csv_sha256 does not match current CSV")

    seen_schemas: set[str] = set()
    figures = render.get("figures") if isinstance(render.get("figures"), list) else []
    if len(figures) != 2:
        add_warning(warnings, "unexpected_figure_count", f"Expected 2 figures, observed {len(figures)}")
    for fig in figures:
        if not isinstance(fig, dict):
            add_error(errors, "figure_not_object", f"Figure entry is not an object: {fig!r}")
            continue
        rel = fig.get("path") if isinstance(fig.get("path"), str) else ""
        path = (workspace / rel).resolve() if rel else workspace
        if not rel or not str(path).startswith(str(workspace)):
            add_error(errors, "figure_path_invalid", f"Invalid figure path: {rel!r}")
            continue
        if not path.exists():
            add_error(errors, "figure_missing", f"Figure missing: {rel}")
            continue
        checked_paths.append(str(path.relative_to(workspace)))
        if fig.get("sha256") != sha256_file(path):
            add_error(errors, "figure_hash_mismatch", f"Figure sha256 mismatch: {rel}")
        text = path.read_text(encoding="utf-8")
        for needle in FORBIDDEN_STRINGS:
            if needle in text:
                add_error(errors, "forbidden_string", f"Forbidden string present in {rel}: {needle}")
        metadata = parse_svg_metadata(path, errors)
        if not metadata:
            continue
        schema = metadata.get("schema")
        seen_schemas.add(str(schema))
        if schema not in EXPECTED_FIGURE_SCHEMAS:
            add_error(errors, "figure_schema_mismatch", f"{rel}: unexpected schema {schema!r}")
        if metadata.get("lane") != "cassandra":
            add_error(errors, "lane_mismatch", f"{rel}: lane {metadata.get('lane')!r}")
        if metadata.get("source_csv") != aggregate_csv_rel:
            add_error(errors, "figure_source_csv_mismatch", f"{rel}: source_csv mismatch")
        if aggregate_csv is not None and aggregate_csv.exists() and metadata.get("source_csv_sha256") != sha256_file(aggregate_csv):
            add_error(errors, "figure_source_hash_mismatch", f"{rel}: source_csv_sha256 mismatch")
        if metadata.get("row_count") != render.get("row_count"):
            add_error(errors, "figure_row_count_mismatch", f"{rel}: row_count mismatch")
        caveat = metadata.get("caveat") if isinstance(metadata.get("caveat"), str) else ""
        for fragment in REQUIRED_CAVEAT_FRAGMENTS:
            if fragment not in caveat:
                add_error(errors, "missing_caveat_fragment", f"{rel}: caveat lacks fragment {fragment!r}")

    missing_schemas = EXPECTED_FIGURE_SCHEMAS - seen_schemas
    if missing_schemas:
        add_warning(warnings, "missing_expected_figure_schema", f"Missing expected schemas: {sorted(missing_schemas)!r}")

    return {
        "schema": "urn:tyche:cassandra:figure-artifact-validation:0.1",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "lane": "cassandra",
        "status": "ok" if not errors else "error",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "checked_paths": checked_paths,
        "caveat": "Local figure-artifact consistency and claim-safety validation only; not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, or publication readiness.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--render-output", default="notes/figure-render-output.json")
    parser.add_argument("--output", default="notes/figure-artifact-validation-output.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    render_output = (workspace / args.render_output).resolve()
    output = (workspace / args.output).resolve()
    for path in [render_output, output]:
        if not str(path).startswith(str(workspace)):
            raise SystemExit("All paths must stay inside workspace")
    result = validate(workspace, render_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
