#!/usr/bin/env python3
"""Smoke test hashed provider/service inventory diff classes.

Research-only test fixture: no real trusted-list names or legal-status claims.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import diff  # noqa: E402


def record(provider_keys, service_keys, provider_service_counts, digest):
    providers = []
    for provider_key, service_count in provider_service_counts.items():
        provider_services = sorted(key for key in service_keys if key.startswith(provider_key[-1]))
        providers.append({
            "provider_key": provider_key,
            "service_count": service_count,
            "service_keys": provider_services,
            "service_status_counts": {"observed-status": service_count},
            "service_type_counts": {"observed-type": service_count},
        })
    return {
        "key": "ZZ",
        "source": "synthetic/zz.xml",
        "normalized_path": "synthetic/zz.xml.normalized.xml",
        "normalized_sha256": digest,
        "summary": {
            "scheme_territory": "ZZ",
            "trust_service_provider_count": len(provider_keys),
            "tsp_service_count": len(service_keys),
            "provider_service_inventory": {
                "provider_count": len(provider_keys),
                "provider_keys": sorted(provider_keys),
                "providers": providers,
                "service_count": len(service_keys),
                "service_keys": sorted(service_keys),
            },
        },
    }


old_record = record(["provider-a"], ["a-service-1"], {"provider-a": 1}, "old")
new_record = record(["provider-a", "provider-b"], ["a-service-1", "b-service-1"], {"provider-a": 1, "provider-b": 1}, "new")
changes = diff.compare_baselines({"records": {"ZZ": old_record}}, {"records": {"ZZ": new_record}})
classes = [change["class"] for change in changes]
expected = {"normalized_hash_changed", "summary_field_changed", "provider_inventory_changed", "service_inventory_changed"}
missing = sorted(expected - set(classes))
assert not missing, f"missing expected classes: {missing}; classes={classes}"
assert all("provider-a" not in json.dumps(change) for change in changes), "test fixture names leaked unexpectedly"
print(json.dumps({"status": "ok", "classes": classes, "change_count": len(changes)}, indent=2, sort_keys=True))
