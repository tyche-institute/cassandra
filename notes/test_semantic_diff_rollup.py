#!/usr/bin/env python3
"""Smoke test semantic diff roll-up helper.

Synthetic fixture only; no real trusted-list names or legal-status claims.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "notes"))

import rollup_semantic_diff_classes as rollup  # noqa: E402


def test_rollup() -> None:
    diff_doc = {
        "date": "2099-01-01",
        "change_count": 4,
        "summary": {
            "service_inventory_changed": 1,
            "provider_service_detail_changed": 1,
            "summary_field_changed": 1,
        },
        "changes": [
            {
                "class": "service_inventory_changed",
                "key": "ZZ",
                "old_service_count": 1,
                "new_service_count": 3,
                "added_service_keys": ["hash-service-2", "hash-service-3"],
                "removed_service_keys": [],
            },
            {
                "class": "provider_service_detail_changed",
                "key": "ZZ",
                "provider_key": "hash-provider",
                "deltas": {"service_keys": {"added": ["hash-service-2"], "removed": []}},
            },
            {
                "class": "summary_field_changed",
                "key": "ZZ",
                "field": "signature_shape",
                "old": {
                    "signature_method_algorithms": ["urn:old-signature-method"],
                    "digest_method_algorithms": ["urn:old-digest-method"],
                },
                "new": {
                    "signature_method_algorithms": ["urn:new-signature-method"],
                    "digest_method_algorithms": ["urn:new-digest-method"],
                },
            },
            {"class": "summary_field_changed", "key": "ZZ", "field": "issue_date_time", "old": "a", "new": "b"},
        ],
    }
    out = rollup.build_rollup(diff_doc, "diffs/synthetic.json", "0" * 64)
    assert out["status"] == "ok"
    assert out["service_inventory"]["movement_count"] == 1
    assert out["service_inventory"]["added_hashed_service_key_total"] == 2
    assert out["provider_service_detail"]["movement_count"] == 1
    assert out["provider_service_detail"]["added_hashed_service_key_total"] == 1
    assert out["signature_shape"]["movement_count"] == 1
    assert out["signature_shape"]["old_signature_method_counts"] == {"urn:old-signature-method": 1}
    assert out["signature_shape"]["new_signature_method_counts"] == {"urn:new-signature-method": 1}
    assert out["raw_listed_names_omitted"] is True
    assert "legal effect" in out["claim_safety_caveat"]
    assert "publication approval" in out["claim_safety_caveat"]


if __name__ == "__main__":
    test_rollup()
    print('{"status":"ok","test":"semantic_diff_rollup"}')
