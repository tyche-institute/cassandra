#!/usr/bin/env python3
"""Report duplicate path rows in ARTIFACT_INDEX.md without rewriting history.

This is a local workflow-maintenance helper for Cassandra state registers. It
reports duplicate artifact-index rows and whether at least one row matches the
current file hash. It does not delete, consolidate, or rewrite historical rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROW_RE = re.compile(
    r"^\| `(?P<path>[^`]+)` \| (?P<purpose>.*?) \| `sha256:(?P<sha256>[0-9a-f]{64})` \| (?P<verified>.*?) \|$"
)

CAVEAT = (
    "Report-only workflow maintenance for local reproducibility: this helper "
    "does not rewrite ARTIFACT_INDEX.md, does not assert legal effect, does not "
    "perform signature validation, does not supervise trusted lists, does not "
    "provide public alerting, and does not assert publication readiness."
)


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_rows(index_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), 1):
        match = ROW_RE.match(line)
        if not match:
            continue
        data = match.groupdict()
        rows.append(
            {
                "line": line_number,
                "path": data["path"],
                "sha256": data["sha256"],
                "purpose": data["purpose"],
                "verified": data["verified"],
            }
        )
    return rows


def build_report(workspace: Path) -> dict[str, Any]:
    index_path = workspace / "ARTIFACT_INDEX.md"
    rows = parse_rows(index_path)
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_path[row["path"]].append(row)

    duplicate_paths: list[dict[str, Any]] = []
    for rel_path, path_rows in sorted(by_path.items()):
        if len(path_rows) < 2:
            continue
        current_hash = sha256_file(workspace / rel_path)
        matching_rows = [row for row in path_rows if current_hash and row["sha256"] == current_hash]
        stale_rows = [row for row in path_rows if not current_hash or row["sha256"] != current_hash]
        duplicate_paths.append(
            {
                "path": rel_path,
                "row_occurrences": len(path_rows),
                "current_sha256": current_hash,
                "current_matching_row_count": len(matching_rows),
                "stale_row_count": len(stale_rows),
                "rows": path_rows,
                "maintenance_note": (
                    "Duplicate rows are preserved by this report. A current matching row "
                    "is sufficient for reproducibility checks; any cleanup should be a "
                    "separate operator-reviewed edit."
                ),
            }
        )

    return {
        "status": "ok",
        "artifact": "ARTIFACT_INDEX.md",
        "mode": "report_only_no_rewrite",
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "workspace": str(workspace),
        "row_count": len(rows),
        "unique_path_count": len(by_path),
        "duplicate_path_count": len(duplicate_paths),
        "duplicate_paths": duplicate_paths,
        "caveat": CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="Cassandra workspace path")
    parser.add_argument("--output", default="notes/artifact-index-duplicate-report-output.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = workspace / output
    report = build_report(workspace)
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    output.write_text(text, encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
