#!/usr/bin/env python3
"""Roll up selected Cassandra semantic diff classes without raw listed names.

Research-only helper: summarizes service-inventory and signature-shape changes
from a local diff document. It does not validate signatures, supervise trusted
lists, determine legal status, provide public alerting, or approve publication.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
from collections import Counter, defaultdict
from typing import Any

CAVEAT = (
    "Aggregate semantic-diff roll-up for local research observation only; raw "
    "listed names are omitted. Counts and signature-shape fields do not assert "
    "legal effect, trusted-list validation, signature validity, supervision, "
    "listed-entity status, public alerting, regulated trust-service output, legal "
    "review, or publication approval."
)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_markdown(path: pathlib.Path, rollup: dict[str, Any]) -> None:
    lines = [
        f"# Semantic Diff Roll-up — {rollup['date']}",
        "",
        rollup["claim_safety_caveat"],
        "",
        "## Scope",
        "",
        "This local note summarizes service-inventory and signature-shape diff classes at aggregate level only. Raw listed names are intentionally omitted.",
        "",
        "## Counts",
        "",
        f"- Source diff: `{rollup['diff_path']}`",
        f"- Source diff sha256: `{rollup['diff_sha256']}`",
        f"- Total source diff entries: {rollup['source_change_count']}",
        f"- Service-inventory movement count: {rollup['service_inventory']['movement_count']}",
        f"- Service-inventory added hashed-service-key total: {rollup['service_inventory']['added_hashed_service_key_total']}",
        f"- Service-inventory removed hashed-service-key total: {rollup['service_inventory']['removed_hashed_service_key_total']}",
        f"- Provider-detail movement count: {rollup['provider_service_detail']['movement_count']}",
        f"- Provider-detail added hashed-service-key total: {rollup['provider_service_detail']['added_hashed_service_key_total']}",
        f"- Provider-detail removed hashed-service-key total: {rollup['provider_service_detail']['removed_hashed_service_key_total']}",
        f"- Signature-shape movement count: {rollup['signature_shape']['movement_count']}",
        "",
        "## Country-code keys with selected class movements",
        "",
    ]
    for key in rollup["keys_with_selected_movements"]:
        kc = rollup["per_key_counts"].get(key, {})
        lines.append(f"- `{key}`: service_inventory={kc.get('service_inventory_changed', 0)}, provider_service_detail={kc.get('provider_service_detail_changed', 0)}, signature_shape={kc.get('signature_shape_changed', 0)}")
    lines += [
        "",
        "## Signature-shape methods observed in changed fields",
        "",
        "These are method identifiers found in changed XML signature-shape summaries. They are not cryptographic verification results.",
        "",
        "### Old signature methods",
        "",
    ]
    for method, count in rollup["signature_shape"]["old_signature_method_counts"].items():
        lines.append(f"- `{method}`: {count}")
    lines += ["", "### New signature methods", ""]
    for method, count in rollup["signature_shape"]["new_signature_method_counts"].items():
        lines.append(f"- `{method}`: {count}")
    lines += ["", "## Caveat", "", rollup["claim_safety_caveat"], ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def signature_methods(shape: Any, field: str) -> list[str]:
    if not isinstance(shape, dict):
        return []
    # Parser versions have used both short keys (signature_methods) and
    # explicit algorithm keys (signature_method_algorithms). Preserve backward
    # compatibility so roll-ups do not silently drop signature-shape telemetry.
    aliases = {
        "signature_methods": ["signature_methods", "signature_method_algorithms"],
        "digest_methods": ["digest_methods", "digest_method_algorithms"],
    }.get(field, [field])
    values: list[str] = []
    for alias in aliases:
        values.extend(str(v) for v in as_list(shape.get(alias)))
    return values


def service_key_delta(change: dict[str, Any]) -> tuple[int, int]:
    added = len(as_list(change.get("added_service_keys")))
    removed = len(as_list(change.get("removed_service_keys")))
    return added, removed


def provider_service_key_delta(change: dict[str, Any]) -> tuple[int, int]:
    service_keys = ((change.get("deltas") or {}).get("service_keys") or {})
    return len(as_list(service_keys.get("added"))), len(as_list(service_keys.get("removed")))


def build_rollup(diff_doc: dict[str, Any], diff_path: str, diff_sha256: str) -> dict[str, Any]:
    changes = diff_doc.get("changes") or []
    per_key_counts: dict[str, Counter[str]] = defaultdict(Counter)
    service_movements: list[dict[str, Any]] = []
    provider_movements: list[dict[str, Any]] = []
    signature_movements: list[dict[str, Any]] = []
    old_sig_counter: Counter[str] = Counter()
    new_sig_counter: Counter[str] = Counter()
    old_digest_counter: Counter[str] = Counter()
    new_digest_counter: Counter[str] = Counter()

    for change in changes:
        cls = str(change.get("class") or "")
        key = str(change.get("key") or "unknown")
        if cls == "service_inventory_changed":
            added, removed = service_key_delta(change)
            per_key_counts[key][cls] += 1
            service_movements.append({
                "key": key,
                "old_service_count": change.get("old_service_count"),
                "new_service_count": change.get("new_service_count"),
                "added_hashed_service_key_count": added,
                "removed_hashed_service_key_count": removed,
                "raw_listed_names_omitted": True,
            })
        elif cls == "provider_service_detail_changed":
            added, removed = provider_service_key_delta(change)
            per_key_counts[key][cls] += 1
            provider_movements.append({
                "key": key,
                "provider_key": change.get("provider_key"),
                "added_hashed_service_key_count": added,
                "removed_hashed_service_key_count": removed,
                "raw_listed_names_omitted": True,
            })
        elif cls == "summary_field_changed" and change.get("field") == "signature_shape":
            old_shape = change.get("old")
            new_shape = change.get("new")
            old_sigs = signature_methods(old_shape, "signature_methods")
            new_sigs = signature_methods(new_shape, "signature_methods")
            old_digests = signature_methods(old_shape, "digest_methods")
            new_digests = signature_methods(new_shape, "digest_methods")
            old_sig_counter.update(old_sigs)
            new_sig_counter.update(new_sigs)
            old_digest_counter.update(old_digests)
            new_digest_counter.update(new_digests)
            per_key_counts[key]["signature_shape_changed"] += 1
            signature_movements.append({
                "key": key,
                "old_signature_methods": sorted(old_sigs),
                "new_signature_methods": sorted(new_sigs),
                "old_digest_methods": sorted(old_digests),
                "new_digest_methods": sorted(new_digests),
                "interpretation_caveat": "Signature-shape observation only; no cryptographic verification performed.",
            })

    selected_keys = sorted(per_key_counts)
    return {
        "status": "ok",
        "created": now_iso(),
        "date": diff_doc.get("date"),
        "diff_path": diff_path,
        "diff_sha256": diff_sha256,
        "source_change_count": diff_doc.get("change_count"),
        "source_diff_summary": diff_doc.get("summary") or {},
        "keys_with_selected_movements": selected_keys,
        "per_key_counts": {key: dict(counter) for key, counter in sorted(per_key_counts.items())},
        "service_inventory": {
            "movement_count": len(service_movements),
            "added_hashed_service_key_total": sum(m["added_hashed_service_key_count"] for m in service_movements),
            "removed_hashed_service_key_total": sum(m["removed_hashed_service_key_count"] for m in service_movements),
            "movements": service_movements,
        },
        "provider_service_detail": {
            "movement_count": len(provider_movements),
            "added_hashed_service_key_total": sum(m["added_hashed_service_key_count"] for m in provider_movements),
            "removed_hashed_service_key_total": sum(m["removed_hashed_service_key_count"] for m in provider_movements),
            "movements": provider_movements,
        },
        "signature_shape": {
            "movement_count": len(signature_movements),
            "old_signature_method_counts": dict(sorted(old_sig_counter.items())),
            "new_signature_method_counts": dict(sorted(new_sig_counter.items())),
            "old_digest_method_counts": dict(sorted(old_digest_counter.items())),
            "new_digest_method_counts": dict(sorted(new_digest_counter.items())),
            "movements": signature_movements,
        },
        "raw_listed_names_omitted": True,
        "claim_safety_caveat": CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()

    workspace = pathlib.Path(args.workspace).resolve()
    diff_path = workspace / "diffs" / f"{args.date}.json"
    output_path = pathlib.Path(args.output)
    if not output_path.is_absolute():
        output_path = workspace / output_path
    markdown_path = pathlib.Path(args.markdown_output)
    if not markdown_path.is_absolute():
        markdown_path = workspace / markdown_path
    diff_doc = load_json(diff_path)
    rollup = build_rollup(diff_doc, str(diff_path.relative_to(workspace)), sha256_file(diff_path))
    write_json(output_path, rollup)
    write_markdown(markdown_path, rollup)
    print(json.dumps({
        "status": rollup["status"],
        "date": rollup["date"],
        "output": str(output_path.relative_to(workspace)),
        "markdown_output": str(markdown_path.relative_to(workspace)),
        "service_inventory_movement_count": rollup["service_inventory"]["movement_count"],
        "provider_service_detail_movement_count": rollup["provider_service_detail"]["movement_count"],
        "signature_shape_movement_count": rollup["signature_shape"]["movement_count"],
        "raw_listed_names_omitted": rollup["raw_listed_names_omitted"],
        "claim_safety_caveat": rollup["claim_safety_caveat"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
