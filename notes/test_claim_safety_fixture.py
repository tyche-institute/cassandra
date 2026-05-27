#!/usr/bin/env python3
"""Validate synthetic Cassandra claim-safety wording fixture.

This scanner fixture catches forbidden overclaiming examples and allows bounded
method/evidence-integrity wording. It is a local heuristic guard only; it is not
legal review, publication approval, trusted-list validation, signature
validation, supervision, compliance judgment, or public alerting.
"""
from __future__ import annotations

import json
import pathlib

FIXTURE_PATH = pathlib.Path(__file__).parent / "fixtures" / "claim-safety-wording-fixtures.json"


def scan_text(text: str, patterns: list[dict[str, str]]) -> list[dict[str, str]]:
    lowered = text.lower()
    hits = []
    for pattern in patterns:
        needle = pattern["pattern"].lower()
        if needle in lowered:
            hits.append({
                "id": pattern["id"],
                "pattern": pattern["pattern"],
                "reason": pattern["reason"],
            })
    return hits


def main() -> int:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    patterns = fixture["forbidden_patterns"]
    results = {}
    for case in fixture["cases"]:
        hits = scan_text(case["text"], patterns)
        hit_ids = [hit["id"] for hit in hits]
        expected = case["expected"]
        if expected == "pass" and hits:
            raise AssertionError(f"{case['name']} expected pass, got {hit_ids}")
        if expected == "fail":
            expected_ids = case["expected_ids"]
            if hit_ids != expected_ids:
                raise AssertionError(f"{case['name']} expected {expected_ids}, got {hit_ids}")
        results[case["name"]] = {"expected": expected, "hit_ids": hit_ids}

    print(json.dumps({
        "status": "ok",
        "fixture_path": str(FIXTURE_PATH),
        "tested_cases": results,
        "scanner_boundary": "Heuristic wording scanner only; not legal review, publication approval, trusted-list validation, signature validation, supervision, compliance judgment, or public alerting.",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
