#!/usr/bin/env python3
"""Validate Cassandra synthetic diff fixtures.

Fixtures are synthetic structural-observation examples only. They do not validate
trusted lists, signatures, legal status, supervision, compliance, public alerts,
or publication readiness.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import diff  # noqa: E402

FIXTURE_PATH = pathlib.Path(__file__).parent / "fixtures" / "synthetic-diff-fixtures.json"
FORBIDDEN_DIRECT_ASSERTIONS = [
    "legally valid",
    "signature valid",
    "supervisory approval",
    "compliance passed",
    "public alert issued",
]


def classes_for_case(case: dict) -> list[str]:
    changes = diff.compare_baselines(
        {"records": {case["old"]["key"]: case["old"]}},
        {"records": {case["new"]["key"]: case["new"]}},
    )
    return [change["class"] for change in changes]


def main() -> int:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    serialized = json.dumps(fixtures).lower()
    leaked = [phrase for phrase in FORBIDDEN_DIRECT_ASSERTIONS if phrase in serialized]
    if leaked:
        raise AssertionError(f"forbidden direct assertions in fixture file: {leaked}")

    results = {}
    for name in ["stable_no_change", "normalized_hash_change"]:
        case = fixtures[name]
        classes = classes_for_case(case)
        expected = case["expected_classes"]
        if classes != expected:
            raise AssertionError(f"{name}: expected {expected}, got {classes}")
        results[name] = {"status": "ok", "classes": classes, "expected_classes": expected}

    hash_case = fixtures["normalized_hash_change"]
    hash_changes = diff.compare_baselines(
        {"records": {hash_case["old"]["key"]: hash_case["old"]}},
        {"records": {hash_case["new"]["key"]: hash_case["new"]}},
    )
    assert len(hash_changes) == 1
    assert "Canonical XML bytes differ" in hash_changes[0]["caveat"]

    print(json.dumps({
        "status": "ok",
        "fixture_path": str(FIXTURE_PATH),
        "tested_cases": results,
        "caveat": fixtures["caveat"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
