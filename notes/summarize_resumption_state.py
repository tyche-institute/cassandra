#!/usr/bin/env python3
"""Build a compact, aggregate-only resumption summary for Cassandra workers.

The output intentionally avoids trusted-list entity names and endpoint-level
interpretation. It summarizes local workflow state so repeated pre-gate wakeups
can resume without scanning the full append-only registers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_FILES = [
    "PLAN.md",
    "HERMES_PROGRESS.md",
    "ARTIFACT_INDEX.md",
    "SOURCES.md",
    "CLAIMS.md",
    "BLOCKED.md",
]
OUTPUT_DEFAULT = Path("notes/resumption-state-summary-output.json")
MD_DEFAULT = Path("notes/resumption-state-summary.md")


def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text_stats(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"present": False}
    if not path.is_file():
        return {"present": True, "is_file": False}
    data = path.read_text(encoding="utf-8", errors="replace")
    lines = data.splitlines()
    return {
        "present": True,
        "is_file": True,
        "bytes": path.stat().st_size,
        "line_count": len(lines),
        "sha256": sha256_path(path),
    }


def latest_progress_entry(progress_text: str) -> dict[str, Any]:
    headings = list(re.finditer(r"^##\s+(\d{4}-\d{2}-\d{2}T[^\s]+)\s+—\s+(.+)$", progress_text, re.M))
    if not headings:
        return {"found": False}
    last = headings[-1]
    end = headings[-0].start() if False else len(progress_text)
    body = progress_text[last.end() : end].strip()
    next_action = None
    for line in reversed(body.splitlines()):
        if line.startswith("Next action:"):
            next_action = line.strip()
            break
    return {
        "found": True,
        "heading_timestamp": last.group(1),
        "heading_title": last.group(2),
        "next_action": next_action,
        "body_line_count": len(body.splitlines()),
    }


def dated_dirs(root: Path, name: str) -> list[str]:
    base = root / name
    if not base.exists():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name))


def count_files(path: Path, suffixes: tuple[str, ...] | None = None) -> int:
    if not path.exists():
        return 0
    count = 0
    for p in path.rglob("*"):
        if p.is_file() and (suffixes is None or p.name.endswith(suffixes)):
            count += 1
    return count


def build_summary(root: Path) -> dict[str, Any]:
    progress_path = root / "HERMES_PROGRESS.md"
    progress_text = progress_path.read_text(encoding="utf-8", errors="replace") if progress_path.exists() else ""
    snapshot_dates = dated_dirs(root, "snapshots")
    normalized_dates = dated_dirs(root, "normalized")
    bundle_dates = dated_dirs(root, "bundles")
    diff_files = sorted((root / "diffs").glob("*.json")) if (root / "diffs").exists() else []
    latest_date = max(snapshot_dates) if snapshot_dates else None

    latest_counts: dict[str, Any] = {}
    if latest_date:
        latest_counts = {
            "snapshot_files": count_files(root / "snapshots" / latest_date),
            "snapshot_content_files": count_files(root / "snapshots" / latest_date, (".xml", ".XML", ".xtsl", ".pdf")),
            "snapshot_meta_files": count_files(root / "snapshots" / latest_date, (".meta.json",)),
            "normalized_files": count_files(root / "normalized" / latest_date),
            "bundle_files": count_files(root / "bundles" / latest_date),
            "diff_present": (root / "diffs" / f"{latest_date}.json").exists(),
        }

    return {
        "schema": "cassandra.resumption_state_summary.v1",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "workspace": str(root),
        "claim_boundary": "Local workflow resumption telemetry only; not endpoint stability evidence, legal effect, signature validation, supervision, listed-entity status evidence, public alerting, regulated trust-service output, warning clearance, legal review, or publication approval.",
        "state_files": {name: text_stats(root / name) for name in STATE_FILES},
        "latest_progress_entry": latest_progress_entry(progress_text),
        # Compatibility aliases for lightweight shell/Python resumption helpers.
        # The canonical location remains dated_lineages.latest_snapshot_date, but
        # previous diary entries show that workers sometimes probe legacy top-level
        # keys and then report `None`. Keeping read-only aliases avoids misleading
        # cadence-gate telemetry without changing the bundle/diff/snapshot model.
        "status": "ok",
        "latest_snapshot_date": latest_date,
        "latest_date": latest_date,
        "latest_completed_date": latest_date,
        "latest_dated_lineage": latest_date,
        "latest_counts": latest_counts,
        "dated_lineages": {
            "snapshots": snapshot_dates,
            "normalized": normalized_dates,
            "bundles": bundle_dates,
            "diffs": [p.stem for p in diff_files],
            "latest_snapshot_date": latest_date,
            "latest_date": latest_date,
            "latest_counts": latest_counts,
        },
        "resumption_hint": "If the latest progress next action says the UTC gate is closed and latest_snapshot_date is already complete for today, do not refresh validators merely for churn; either make one bounded aggregate-only improvement or append a gate-state exit.",
    }


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    latest = summary["dated_lineages"]["latest_snapshot_date"] or "none"
    latest_entry = summary["latest_progress_entry"]
    lines = [
        "# Cassandra resumption state summary",
        "",
        f"Created UTC: {summary['created_utc']}",
        "",
        "Boundary: local workflow resumption telemetry only. This file does not assert endpoint stability, trusted-list legal effect, signature validity, supervision, listed-entity status, public alerting, regulated trust-service output, warning clearance, legal review, or publication approval.",
        "",
        f"Latest snapshot date: {latest}",
        "",
        "## Latest counts",
        "",
    ]
    for key, value in summary["dated_lineages"].get("latest_counts", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Latest progress entry", ""])
    if latest_entry.get("found"):
        lines.append(f"- timestamp: {latest_entry.get('heading_timestamp')}")
        lines.append(f"- title: {latest_entry.get('heading_title')}")
        lines.append(f"- next action: {latest_entry.get('next_action')}")
    else:
        lines.append("- no progress heading found")
    lines.extend(["", "## State file sizes", ""])
    for name, stats in summary["state_files"].items():
        if stats.get("present") and stats.get("is_file"):
            lines.append(f"- {name}: {stats['line_count']} lines, {stats['bytes']} bytes, sha256:{stats['sha256']}")
        else:
            lines.append(f"- {name}: {'present' if stats.get('present') else 'absent'}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default=str(OUTPUT_DEFAULT))
    parser.add_argument("--markdown", default=str(MD_DEFAULT))
    args = parser.parse_args()
    root = Path(args.workspace).resolve()
    summary = build_summary(root)
    output = root / args.output
    markdown = root / args.markdown
    output.parent.mkdir(parents=True, exist_ok=True)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, markdown)
    print(json.dumps({"status": "ok", "output": str(output), "markdown": str(markdown), "latest_snapshot_date": summary["dated_lineages"]["latest_snapshot_date"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
