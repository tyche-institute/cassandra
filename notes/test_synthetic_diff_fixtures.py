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
    for name in [
        "stable_no_change",
        "normalized_hash_change",
        "provider_inventory_change",
        "provider_inventory_removal",
        "service_inventory_change",
        "service_inventory_removal",
        "provider_service_detail_change",
        "provider_service_reassignment",
    ]:
        case = fixtures[name]
        changes = diff.compare_baselines(
            {"records": {case["old"]["key"]: case["old"]}},
            {"records": {case["new"]["key"]: case["new"]}},
        )
        classes = [change["class"] for change in changes]
        expected = case["expected_classes"]
        if classes != expected:
            raise AssertionError(f"{name}: expected {expected}, got {classes}")
        results[name] = {"status": "ok", "classes": classes, "expected_classes": expected}

        if name == "provider_inventory_change":
            provider_change = next(change for change in changes if change["class"] == "provider_inventory_changed")
            assert provider_change["added_provider_keys"] == ["hash-provider-2"]
            assert provider_change["removed_provider_keys"] == []
        if name == "provider_inventory_removal":
            provider_change = next(change for change in changes if change["class"] == "provider_inventory_changed")
            assert provider_change["added_provider_keys"] == []
            assert provider_change["removed_provider_keys"] == ["hash-provider-2"]
        if name == "service_inventory_change":
            service_change = next(change for change in changes if change["class"] == "service_inventory_changed")
            assert service_change["added_service_keys"] == ["hash-service-3"]
            assert service_change["removed_service_keys"] == []
        if name == "service_inventory_removal":
            service_change = next(change for change in changes if change["class"] == "service_inventory_changed")
            assert service_change["added_service_keys"] == []
            assert service_change["removed_service_keys"] == ["hash-service-3"]
        if name == "provider_service_detail_change":
            detail_change = next(change for change in changes if change["class"] == "provider_service_detail_changed")
            assert detail_change["provider_key"] == "hash-provider-1"
            assert set(detail_change["deltas"]) == {"service_status_counts", "service_type_counts"}
        if name == "provider_service_reassignment":
            detail_changes = [change for change in changes if change["class"] == "provider_service_detail_changed"]
            assert [change["provider_key"] for change in detail_changes] == ["hash-provider-1", "hash-provider-2"]
            assert detail_changes[0]["deltas"]["service_keys"]["removed"] == ["hash-service-2"]
            assert detail_changes[1]["deltas"]["service_keys"]["added"] == ["hash-service-2"]

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
