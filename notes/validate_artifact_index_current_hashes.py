#!/usr/bin/env python3
"""Validate Cassandra ARTIFACT_INDEX.md hash freshness without rewriting state.

This is a local workflow-maintenance helper. It checks whether each indexed
workspace path that still exists has at least one ARTIFACT_INDEX row whose
sha256 matches the current file content. Duplicate rows are reported as
maintenance warnings rather than errors when a current matching row exists,
because append-only artifacts and repeated verifier outputs may have historical
rows.

Research caveat: this is local reproducibility telemetry only. It does not
assert legal compliance, trusted-list legal effect, signature validity,
supervision, public alerting, regulated trust-service output, or publication
readiness.
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

ROW_RE = re.compile(r"^\| `(?P<path>[^`]+)` \| (?P<purpose>.*?) \| `sha256:(?P<hash>[0-9a-f]{64})` \| (?P<verified>.*?) \|$")

CAVEAT = (
    "Local artifact-index hash freshness telemetry only; not legal compliance, "
    "trusted-list legal effect, signature validation, supervision, public "
    "alerting, regulated trust-service output, or publication readiness."
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_index(index_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(index_path.read_text(encoding="utf-8").splitlines(), start=1):
        m = ROW_RE.match(line)
        if not m:
            continue
        d = m.groupdict()
        d["line"] = line_no
        rows.append(d)
    return rows


def validate(workspace: Path) -> dict[str, Any]:
    index_path = workspace / "ARTIFACT_INDEX.md"
    rows = parse_index(index_path)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["path"]].append(row)

    missing_paths: list[dict[str, Any]] = []
    stale_paths: list[dict[str, Any]] = []
    duplicate_paths: list[dict[str, Any]] = []
    current_matches: list[dict[str, Any]] = []

    ignored_self_output_reasons = {
        "ARTIFACT_INDEX.md": "artifact index is append-only and self-referential; adding its current hash changes the file, so freshness is covered by non-indexed local sha256 computation and progress notes",
        "notes/artifact-index-current-hash-validation-output.json": "validator output is rewritten by this command and cannot be self-validated against a pre-run index row",
        "notes/artifact-index-current-hash-validation-run.json": "validator output is rewritten by this command and cannot be self-validated against a pre-run index row",
    }
    ignored_paths: list[dict[str, Any]] = []

    for rel_path in sorted(grouped):
        file_path = workspace / rel_path
        entries = grouped[rel_path]
        hashes = [e["hash"] for e in entries]
        if rel_path in ignored_self_output_reasons:
            ignored_paths.append({
                "path": rel_path,
                "reason": ignored_self_output_reasons[rel_path],
                "lines": [e["line"] for e in entries],
            })
            continue
        if not file_path.exists():
            missing_paths.append({
                "path": rel_path,
                "lines": [e["line"] for e in entries],
                "recorded_hashes": sorted(set(hashes)),
            })
            continue
        if not file_path.is_file():
            stale_paths.append({
                "path": rel_path,
                "reason": "indexed path exists but is not a regular file",
                "lines": [e["line"] for e in entries],
            })
            continue
        current_hash = sha256_file(file_path)
        matching_lines = [e["line"] for e in entries if e["hash"] == current_hash]
        stale_lines = [e["line"] for e in entries if e["hash"] != current_hash]
        if matching_lines:
            current_matches.append({
                "path": rel_path,
                "current_hash": f"sha256:{current_hash}",
                "matching_lines": matching_lines,
                "stale_line_count": len(stale_lines),
                "row_count": len(entries),
            })
            if len(entries) > 1:
                duplicate_paths.append({
                    "path": rel_path,
                    "current_hash": f"sha256:{current_hash}",
                    "matching_lines": matching_lines,
                    "stale_lines": stale_lines,
                    "row_count": len(entries),
                })
        else:
            stale_paths.append({
                "path": rel_path,
                "current_hash": f"sha256:{current_hash}",
                "recorded_hashes": [f"sha256:{h}" for h in sorted(set(hashes))],
                "lines": [e["line"] for e in entries],
            })

    errors: list[str] = []
    if missing_paths:
        errors.append(f"{len(missing_paths)} indexed paths are missing")
    if stale_paths:
        errors.append(f"{len(stale_paths)} existing indexed paths lack a current matching hash row")

    warnings: list[str] = []
    if duplicate_paths:
        warnings.append(f"{len(duplicate_paths)} paths have duplicate ARTIFACT_INDEX rows; each reported duplicate has at least one current matching hash row")

    return {
        "status": "ok" if not errors else "needs_review",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "index_path": "ARTIFACT_INDEX.md",
        "research_caveat": CAVEAT,
        "row_count": len(rows),
        "unique_path_count": len(grouped),
        "current_match_count": len(current_matches),
        "ignored_self_output_count": len(ignored_paths),
        "duplicate_path_count": len(duplicate_paths),
        "missing_path_count": len(missing_paths),
        "stale_path_count": len(stale_paths),
        "errors": errors,
        "warnings": warnings,
        "ignored_self_output_paths": ignored_paths,
        "duplicate_paths": duplicate_paths,
        "missing_paths": missing_paths,
        "stale_paths": stale_paths,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", default=".")
    ap.add_argument("--output", default="notes/artifact-index-current-hash-validation-output.json")
    args = ap.parse_args()

    workspace = Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
