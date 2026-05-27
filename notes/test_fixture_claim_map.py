#!/usr/bin/env python3
"""Validate the Cassandra fixture-to-claim reviewer map."""

from __future__ import annotations

import json
import pathlib
import re

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
MAP_PATH = WORKSPACE / "notes" / "fixture-to-claim-map.md"
MATRIX_PATH = WORKSPACE / "notes" / "fixture-matrix.md"
TRANSCRIPT_PATH = WORKSPACE / "notes" / "cassandra-full-stack-usable-transcript-2026-05-27.md"
OUTPUT_PATH = WORKSPACE / "notes" / "fixture-claim-map-validation-output.json"

REQUIRED_FIXTURES = [
    "stable no-change",
    "normalized hash change",
    "provider inventory",
    "service inventory",
    "provider-service detail",
    "fetch failure",
    "non-xml",
    "eatf success",
    "eatf tamper",
    "missing signing input",
    "dashboard multistate",
    "claim safety",
]

REQUIRED_COLUMNS = [
    "Fixture class",
    "Paper claim supported",
    "Reviewer question answered",
    "Primary evidence artifacts",
    "Boundary / non-claim",
]

FORBIDDEN_PATTERNS = [
    r"legal status (is|was|verified|validated)",
    r"signature validity (is|was|verified|validated)",
    r"supervisory (approval|finding|determination)",
    r"proves no legally relevant change",
    r"provider status (is|was|verified|validated)",
]


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    if not MAP_PATH.exists():
        errors.append(f"missing {MAP_PATH.relative_to(WORKSPACE)}")
        text = ""
    else:
        text = MAP_PATH.read_text(encoding="utf-8")

    lowered = text.lower()
    for fixture in REQUIRED_FIXTURES:
        if fixture not in lowered:
            errors.append(f"missing fixture row or wording: {fixture}")

    for column in REQUIRED_COLUMNS:
        if column not in text:
            errors.append(f"missing table column: {column}")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, lowered):
            errors.append(f"forbidden overclaim pattern present: {pattern}")

    required_paths = [
        "notes/fixture-matrix.md",
        "notes/test_synthetic_diff_fixtures.py",
        "notes/test_fetch_and_non_xml_fixtures.py",
        "notes/test_eatf_success_tamper_fixture.py",
        "notes/test_eatf_missing_signing_fixture.py",
        "notes/test_dashboard_public_index_fixture.py",
        "notes/test_claim_safety_fixture.py",
    ]
    for path in required_paths:
        if path not in text:
            errors.append(f"missing evidence path reference: {path}")

    if "fixtures prove expected software behavior on synthetic inputs" not in lowered:
        errors.append("missing synthetic-fixture boundary sentence")
    if "not trusted-list validation" not in lowered:
        errors.append("missing trusted-list validation abstention")

    matrix_text = MATRIX_PATH.read_text(encoding="utf-8") if MATRIX_PATH.exists() else ""
    transcript_text = TRANSCRIPT_PATH.read_text(encoding="utf-8") if TRANSCRIPT_PATH.exists() else ""
    if "fixture-to-claim-map.md" not in matrix_text:
        warnings.append("fixture matrix does not yet cross-reference fixture-to-claim-map.md")
    if "fixture-to-claim-map.md" not in transcript_text:
        warnings.append("full-stack transcript does not yet cross-reference fixture-to-claim-map.md")

    result = {
        "status": "ok" if not errors else "error",
        "errors": errors,
        "warnings": warnings,
        "required_fixture_count": len(REQUIRED_FIXTURES),
        "map_path": str(MAP_PATH.relative_to(WORKSPACE)),
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
