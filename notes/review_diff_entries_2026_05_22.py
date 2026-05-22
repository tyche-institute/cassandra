#!/usr/bin/env python3
"""Aggregate-only review of the 2026-05-22 Cassandra diff entries.

This helper deliberately avoids dereferencing provider/service hashes into raw
listed names. It summarizes diff classes, country-code keys, service-count
movements, and signature-shape algorithm movements as local research telemetry.
It does not perform trusted-list validation, signature validation, supervision,
legal-status determination, public alerting, or publication approval.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
DIFF_PATH = WORKSPACE / "diffs" / "2026-05-22.json"
OUT_JSON = WORKSPACE / "notes" / "diff-review-2026-05-22-output.json"
OUT_MD = WORKSPACE / "notes" / "diff-review-2026-05-22.md"

CAVEAT = (
    "Aggregate structural-observation review only; not trusted-list validation, "
    "not signature validation, not supervision, not legal-status determination, "
    "not listed-entity status evidence, not public alerting, and not publication approval."
)


def _as_set(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(v) for v in value}
    return set()


def main() -> int:
    diff = json.loads(DIFF_PATH.read_text(encoding="utf-8"))
    changes = diff.get("changes", [])
    class_counts: Counter[str] = Counter(str(c.get("class", "<missing>")) for c in changes)
    key_counts: Counter[str] = Counter(str(c.get("key", "<missing>")) for c in changes)
    keys_by_class: dict[str, list[str]] = defaultdict(list)
    summary_field_counts: Counter[str] = Counter()
    service_inventory_movements = []
    provider_detail_movements = []
    signature_shape_movements = []
    caveat_missing = []

    for idx, change in enumerate(changes):
        cls = str(change.get("class", "<missing>"))
        key = str(change.get("key", "<missing>"))
        if key not in keys_by_class[cls]:
            keys_by_class[cls].append(key)
        if not change.get("caveat"):
            caveat_missing.append(idx)
        if cls == "summary_field_changed":
            field = str(change.get("field", "<missing>"))
            summary_field_counts[field] += 1
            if field == "signature_shape":
                old = change.get("old") or {}
                new = change.get("new") or {}
                signature_shape_movements.append(
                    {
                        "key": key,
                        "old_signature_methods": sorted(_as_set(old.get("signature_method_algorithms"))),
                        "new_signature_methods": sorted(_as_set(new.get("signature_method_algorithms"))),
                        "old_digest_methods": sorted(_as_set(old.get("digest_method_algorithms"))),
                        "new_digest_methods": sorted(_as_set(new.get("digest_method_algorithms"))),
                        "interpretation_caveat": "Signature-shape observation only; no cryptographic verification performed.",
                    }
                )
        elif cls == "service_inventory_changed":
            old_count = int(change.get("old_service_count", 0))
            new_count = int(change.get("new_service_count", 0))
            service_inventory_movements.append(
                {
                    "key": key,
                    "old_service_count": old_count,
                    "new_service_count": new_count,
                    "delta": new_count - old_count,
                    "added_hashed_service_key_count": len(change.get("added_service_keys") or []),
                    "removed_hashed_service_key_count": len(change.get("removed_service_keys") or []),
                    "raw_listed_names_omitted": True,
                }
            )
        elif cls == "provider_service_detail_changed":
            deltas = change.get("deltas") or {}
            service_count = deltas.get("service_count") or {}
            keys_delta = deltas.get("service_keys") or {}
            old_count = int(service_count.get("old", 0))
            new_count = int(service_count.get("new", 0))
            provider_detail_movements.append(
                {
                    "key": key,
                    "provider_key": change.get("provider_key"),
                    "old_service_count": old_count,
                    "new_service_count": new_count,
                    "delta": new_count - old_count,
                    "added_hashed_service_key_count": len(keys_delta.get("added") or []),
                    "removed_hashed_service_key_count": len(keys_delta.get("removed") or []),
                    "raw_listed_names_omitted": True,
                }
            )

    aggregate = {
        "status": "ok" if not caveat_missing else "warning",
        "created": datetime.now(timezone.utc).isoformat(),
        "date": diff.get("date"),
        "diff_path": str(DIFF_PATH.relative_to(WORKSPACE)),
        "change_count": len(changes),
        "reported_change_count": diff.get("change_count"),
        "class_counts": dict(sorted(class_counts.items())),
        "diff_summary": diff.get("summary"),
        "keys_with_changes": sorted(key_counts.keys()),
        "change_counts_by_key": dict(sorted(key_counts.items())),
        "keys_by_class": {k: sorted(v) for k, v in sorted(keys_by_class.items())},
        "summary_field_counts": dict(sorted(summary_field_counts.items())),
        "service_inventory_movements": service_inventory_movements,
        "provider_detail_movement_count": len(provider_detail_movements),
        "provider_detail_delta_total": sum(x["delta"] for x in provider_detail_movements),
        "provider_detail_movements": provider_detail_movements,
        "signature_shape_movement_count": len(signature_shape_movements),
        "signature_shape_movements": signature_shape_movements,
        "caveat_missing_indices": caveat_missing,
        "raw_listed_names_omitted": True,
        "review_decision": {
            "recommended_next_bounded_action": "Add or refine a semantic diff roll-up focused on signature-shape and service-inventory aggregate classes before adding named examples or public prose.",
            "rationale": "The first non-empty run is concentrated in three country-code keys with metadata/date fields, service-count additions, and two signature-method shape changes; aggregate roll-up will reduce overinterpretation risk.",
        },
        "claim_safety_caveat": CAVEAT,
    }

    OUT_JSON.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md_lines = [
        "# Diff review — 2026-05-22",
        "",
        CAVEAT,
        "",
        f"Reviewed diff: `{aggregate['diff_path']}`",
        f"Change entries: {aggregate['change_count']} (reported: {aggregate['reported_change_count']})",
        "",
        "## Aggregate class counts",
        "",
    ]
    for cls, count in aggregate["class_counts"].items():
        md_lines.append(f"- `{cls}`: {count}")
    md_lines.extend([
        "",
        "## Aggregate key coverage",
        "",
        f"- Country-code keys with observed structural entries: {', '.join(aggregate['keys_with_changes'])}",
        "- Raw listed names were not dereferenced or reproduced in this review.",
        "",
        "## Summary-field counts",
        "",
    ])
    for field, count in aggregate["summary_field_counts"].items():
        md_lines.append(f"- `{field}`: {count}")
    md_lines.extend([
        "",
        "## Service-inventory movements",
        "",
    ])
    for item in service_inventory_movements:
        md_lines.append(
            f"- `{item['key']}`: service count {item['old_service_count']} -> {item['new_service_count']} "
            f"(delta {item['delta']:+}); added hashed service keys {item['added_hashed_service_key_count']}; "
            f"removed hashed service keys {item['removed_hashed_service_key_count']}."
        )
    md_lines.extend([
        "",
        "## Signature-shape movements",
        "",
    ])
    for item in signature_shape_movements:
        md_lines.append(
            f"- `{item['key']}`: signature method shape {item['old_signature_methods']} -> "
            f"{item['new_signature_methods']}; no cryptographic verification performed."
        )
    md_lines.extend([
        "",
        "## Decision",
        "",
        aggregate["review_decision"]["recommended_next_bounded_action"],
        "",
        aggregate["review_decision"]["rationale"],
        "",
    ])
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
