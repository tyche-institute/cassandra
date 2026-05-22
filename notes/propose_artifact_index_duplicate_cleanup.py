#!/usr/bin/env python3
"""Propose an operator-reviewed cleanup patch for duplicate ARTIFACT_INDEX rows.

This helper is intentionally report-only. It reads ARTIFACT_INDEX.md and the
existing duplicate-row report, then emits a machine-readable proposal describing
which stale duplicate rows could be removed in a future manual/operator-reviewed
edit. It does not modify ARTIFACT_INDEX.md or any other state register.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import report_artifact_index_duplicates as duplicate_report

CAVEAT = (
    "Proposal-only workflow maintenance for local reproducibility: this helper "
    "does not rewrite ARTIFACT_INDEX.md, does not apply patches, does not delete "
    "historical rows, does not assert legal effect, does not perform signature "
    "validation, does not supervise trusted lists, does not provide public "
    "alerting, and does not assert publication readiness. Any cleanup must be "
    "operator-reviewed before application."
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_unified_diff_stub(index_path: Path, removable_rows: list[dict[str, Any]]) -> str:
    """Build a human-readable patch sketch without applying it.

    The sketch uses line-number comments plus exact row text so an operator can
    review intent. It is deliberately not a complete auto-applied patch because
    ARTIFACT_INDEX.md line numbers can shift as new rows are appended.
    """
    lines = index_path.read_text(encoding="utf-8").splitlines()
    out = [
        "# Proposed manual cleanup sketch for ARTIFACT_INDEX.md",
        "# Review before applying. This helper does not modify files.",
    ]
    for row in removable_rows:
        line_no = int(row["line"])
        line_text = lines[line_no - 1] if 0 < line_no <= len(lines) else "<line unavailable>"
        out.append(f"# candidate stale duplicate row at current line {line_no}")
        out.append(f"- {line_text}")
    return "\n".join(out) + "\n"


def build_proposal(workspace: Path) -> dict[str, Any]:
    index_path = workspace / "ARTIFACT_INDEX.md"
    report = duplicate_report.build_report(workspace)
    cleanup_candidates: list[dict[str, Any]] = []
    retained_current_rows: list[dict[str, Any]] = []

    for duplicate in report["duplicate_paths"]:
        path = duplicate["path"]
        current_sha = duplicate.get("current_sha256")
        current_rows = [row for row in duplicate["rows"] if current_sha and row["sha256"] == current_sha]
        stale_rows = [row for row in duplicate["rows"] if not current_sha or row["sha256"] != current_sha]
        for row in current_rows:
            retained_current_rows.append(
                {
                    "path": path,
                    "line": row["line"],
                    "sha256": row["sha256"],
                    "reason": "retains at least one row matching the current file hash",
                }
            )
        for row in stale_rows:
            cleanup_candidates.append(
                {
                    "path": path,
                    "line": row["line"],
                    "sha256": row["sha256"],
                    "current_sha256": current_sha,
                    "reason": (
                        "stale duplicate row: another row for the same path matches "
                        "the current file hash; remove only after operator review"
                    ),
                    "safe_to_auto_apply": False,
                }
            )

    patch_sketch = build_unified_diff_stub(index_path, cleanup_candidates)
    return {
        "status": "ok",
        "artifact": "ARTIFACT_INDEX.md",
        "mode": "proposal_only_no_rewrite",
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "workspace": str(workspace),
        "duplicate_path_count": report["duplicate_path_count"],
        "cleanup_candidate_count": len(cleanup_candidates),
        "cleanup_candidates": cleanup_candidates,
        "retained_current_rows": retained_current_rows,
        "patch_sketch": patch_sketch,
        "patch_sketch_sha256": sha256_text(patch_sketch),
        "caveat": CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="Cassandra workspace path")
    parser.add_argument("--output", default="notes/artifact-index-duplicate-cleanup-proposal-output.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = workspace / output
    proposal = build_proposal(workspace)
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(proposal, indent=2, sort_keys=True) + "\n"
    output.write_text(text, encoding="utf-8")
    print(json.dumps(proposal, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
