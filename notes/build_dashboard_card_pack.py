#!/usr/bin/env python3
"""Build a reviewer-readable dashboard card pack from public observatory JSON cards.

This helper is intentionally narrow. It renders existing public dashboard cards into
Markdown and checks card-index hashes so a reviewer can inspect the dashboard
boundary without treating it as trusted-list validation, source-signature
validation, legal-status determination, supervision, compliance judgment, public
alerting, endorsement, legal review, or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

RESEARCH_CAVEAT = (
    "Reviewer dashboard-card rendering only; it summarizes public observatory "
    "JSON cards and hash checks. It is not trusted-list validation, "
    "source-signature validation, legal-status determination, supervision, "
    "compliance judgment, public alerting, endorsement, legal review, or "
    "publication approval."
)

FORBIDDEN_RENDER_TOKENS = [
    "certifies compliance",
    "proves legal compliance",
    "supervisory approval granted",
    "signature validity is confirmed",
    "legal status changed",
    "public alert issued",
]

CARD_ORDER = [
    "claim-boundary",
    "latest-run",
    "eatf-receipt",
    "aggregate-diffs",
    "caveat",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def bulletize(value: Any, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        rows: list[str] = []
        for key in sorted(value):
            item = value[key]
            if isinstance(item, (dict, list)):
                rows.append(f"{prefix}- {key}:")
                rows.extend(bulletize(item, prefix + "  "))
            else:
                rows.append(f"{prefix}- {key}: `{item}`")
        return rows
    if isinstance(value, list):
        rows = []
        for item in value:
            if isinstance(item, (dict, list)):
                rows.extend(bulletize(item, prefix))
            else:
                rows.append(f"{prefix}- {item}")
        return rows
    return [f"{prefix}- `{value}`"]


def render_card(card: dict[str, Any]) -> str:
    title = card.get("title") or card.get("id") or "Untitled card"
    lines = [f"## {title}", ""]
    for field in ["id", "summary", "interpretation", "caveat", "not_a"]:
        if field in card:
            lines.append(f"- {field}: {card[field]}")
    data = card.get("data")
    if data is not None:
        lines.append("")
        lines.append("Data:")
        lines.extend(bulletize(data))
    lines.append("")
    return "\n".join(lines)


def build(workspace: pathlib.Path, output: pathlib.Path, validation_output: pathlib.Path) -> dict[str, Any]:
    card_dir = workspace / "observatory" / "public" / "data" / "cards"
    index_path = card_dir / "index.json"
    public_index_path = workspace / "observatory" / "public" / "data" / "index.json"
    card_index = load_json(index_path)
    public_index = load_json(public_index_path)

    errors: list[str] = []
    warnings: list[str] = []
    card_records: list[dict[str, Any]] = []
    cards_by_id: dict[str, dict[str, Any]] = {}

    for entry in card_index.get("cards", []):
        rel = entry.get("path", "")
        card_path = workspace / "observatory" / "public" / rel
        record = {"path": rel, "exists": card_path.exists()}
        if not card_path.exists():
            errors.append(f"card path missing: {rel}")
            card_records.append(record)
            continue
        actual_sha = sha256_path(card_path)
        record["sha256"] = actual_sha
        record["index_sha256"] = entry.get("sha256")
        record["size_bytes"] = card_path.stat().st_size
        if entry.get("sha256") != actual_sha:
            errors.append(f"card hash mismatch for {rel}: index={entry.get('sha256')} actual={actual_sha}")
        card = load_json(card_path)
        card_id = card.get("id")
        if not card_id:
            errors.append(f"card has no id: {rel}")
        else:
            cards_by_id[card_id] = card
        if "not_a" not in card and "caveat" not in card:
            warnings.append(f"card lacks explicit not_a/caveat field: {rel}")
        card_records.append(record)

    missing_ordered_cards = [card_id for card_id in CARD_ORDER if card_id not in cards_by_id]
    if missing_ordered_cards:
        errors.append(f"missing expected dashboard cards: {missing_ordered_cards}")

    rendered_parts = [
        "# Cassandra dashboard card pack",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Purpose: reviewer-readable rendering of the public dashboard card JSON pack.",
        "",
        f"Case sentence: {public_index.get('case_study_sentence')}",
        "",
        f"Public index: `observatory/public/data/index.json` (`sha256:{sha256_path(public_index_path)}`)",
        f"Card index: `observatory/public/data/cards/index.json` (`sha256:{sha256_path(index_path)}`)",
        "",
        f"Boundary: {RESEARCH_CAVEAT}",
        "",
        "## Dashboard telemetry snapshot",
        "",
        f"- latest_date: `{public_index.get('latest_date')}`",
        f"- run_count: `{public_index.get('run_count')}`",
        f"- packaged_evidence_count: `{public_index.get('packaged_evidence_count')}`",
        f"- eatf_verified_count: `{public_index.get('eatf_verified_count')}`",
        f"- caveat: {public_index.get('caveat')}",
        "",
        "## Card index hash checks",
        "",
    ]
    for record in card_records:
        rendered_parts.append(
            f"- `{record.get('path')}`: exists=`{record.get('exists')}`, "
            f"sha256=`{record.get('sha256')}`, index_sha256=`{record.get('index_sha256')}`"
        )
    rendered_parts.append("")

    for card_id in CARD_ORDER:
        if card_id in cards_by_id:
            rendered_parts.append(render_card(cards_by_id[card_id]))

    rendered_parts.extend([
        "## Reviewer use",
        "",
        "Use this pack to check whether dashboard prose keeps the Cassandra boundary visible: structural observation, local hashes, bundles, receipts, schemas, and caveats are in scope; legal interpretation, provider/service status, source-signature validation, supervision, compliance judgment, public alerting, endorsement, legal review, and publication approval are out of scope.",
        "",
    ])

    rendered = "\n".join(rendered_parts)
    forbidden_hits = [token for token in FORBIDDEN_RENDER_TOKENS if token in rendered]
    if forbidden_hits:
        errors.append(f"rendered pack contains forbidden overclaiming tokens: {forbidden_hits}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")

    result = {
        "schema": "urn:tyche:cassandra:dashboard-card-pack-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "output": str(output.relative_to(workspace)),
        "output_sha256": sha256_path(output),
        "card_index": str(index_path.relative_to(workspace)),
        "card_index_sha256": sha256_path(index_path),
        "public_index": str(public_index_path.relative_to(workspace)),
        "public_index_sha256": sha256_path(public_index_path),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "card_records": card_records,
        "research_caveat": RESEARCH_CAVEAT,
    }
    validation_output.parent.mkdir(parents=True, exist_ok=True)
    validation_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/dashboard-card-pack-2026-05-27.md")
    parser.add_argument("--validation-output", default="notes/dashboard-card-pack-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = build(workspace, workspace / args.output, workspace / args.validation_output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
