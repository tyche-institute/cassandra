#!/usr/bin/env python3
"""Validate duplicate ARTIFACT_INDEX cleanup proposals against the live report.

This is local workflow-maintenance validation only. It checks that the
proposal-only helper remains consistent with the duplicate-row report, that it
retains at least one current matching row for every proposed cleanup path, and
that no state register is rewritten while validating. It does not apply cleanup
patches and makes no legal, supervisory, signature-validation, public-alerting,
or publication-readiness claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE / "notes") not in sys.path:
    sys.path.insert(0, str(WORKSPACE / "notes"))

import report_artifact_index_duplicates as duplicate_report  # noqa: E402
import propose_artifact_index_duplicate_cleanup as cleanup_proposal  # noqa: E402

CAVEAT = (
    "Validation-only workflow maintenance for local reproducibility: this helper "
    "does not rewrite ARTIFACT_INDEX.md, does not apply patches, does not delete "
    "historical rows, does not assert legal effect, does not perform signature "
    "validation, does not supervise trusted lists, does not provide public "
    "alerting, and does not assert publication readiness. Cleanup remains "
    "operator-reviewed only."
)

REQUIRED_CAVEAT_FRAGMENTS = [
    "does not rewrite",
    "does not apply patches",
    "does not assert legal effect",
    "does not perform signature validation",
    "does not supervise trusted lists",
    "does not provide public alerting",
    "does not assert publication readiness",
    "operator-reviewed",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def candidate_key(candidate: dict[str, Any]) -> tuple[str, int, str]:
    return (str(candidate["path"]), int(candidate["line"]), str(candidate["sha256"]))


def build_validation(workspace: Path) -> dict[str, Any]:
    index_path = workspace / "ARTIFACT_INDEX.md"
    before = index_path.read_bytes()
    before_sha = hashlib.sha256(before).hexdigest()

    report = duplicate_report.build_report(workspace)
    proposal = cleanup_proposal.build_proposal(workspace)

    after = index_path.read_bytes()
    after_sha = hashlib.sha256(after).hexdigest()

    errors: list[str] = []
    warnings: list[str] = []

    if before != after:
        errors.append("ARTIFACT_INDEX.md changed during validation")

    if report.get("status") != "ok":
        errors.append(f"duplicate report status is {report.get('status')!r}")
    if proposal.get("status") != "ok":
        errors.append(f"cleanup proposal status is {proposal.get('status')!r}")
    if proposal.get("mode") != "proposal_only_no_rewrite":
        errors.append("cleanup proposal mode is not proposal_only_no_rewrite")
    if proposal.get("duplicate_path_count") != report.get("duplicate_path_count"):
        errors.append("proposal duplicate_path_count does not match report")

    report_expected: set[tuple[str, int, str]] = set()
    report_current_rows_by_path: dict[str, list[dict[str, Any]]] = {}
    for duplicate in report.get("duplicate_paths", []):
        path = str(duplicate.get("path"))
        current_sha = duplicate.get("current_sha256")
        rows = duplicate.get("rows", [])
        current_rows = [row for row in rows if current_sha and row.get("sha256") == current_sha]
        stale_rows = [row for row in rows if not current_sha or row.get("sha256") != current_sha]
        report_current_rows_by_path[path] = current_rows
        if stale_rows and not current_rows:
            warnings.append(f"duplicate path has stale rows but no current matching row: {path}")
        for row in stale_rows:
            report_expected.add((path, int(row["line"]), str(row["sha256"])))

    proposal_candidates = proposal.get("cleanup_candidates", [])
    proposal_keys = {candidate_key(candidate) for candidate in proposal_candidates}
    if proposal_keys != report_expected:
        errors.append("cleanup candidate set does not match stale rows from duplicate report")

    if proposal.get("cleanup_candidate_count") != len(proposal_candidates):
        errors.append("cleanup_candidate_count does not match cleanup_candidates length")
    if proposal.get("cleanup_candidate_count") != len(report_expected):
        errors.append("cleanup_candidate_count does not match expected stale duplicate row count")

    for candidate in proposal_candidates:
        path = str(candidate.get("path"))
        if candidate.get("safe_to_auto_apply") is not False:
            errors.append(f"candidate missing safe_to_auto_apply false: {path}:{candidate.get('line')}")
        if path not in report_current_rows_by_path or not report_current_rows_by_path[path]:
            errors.append(f"candidate path lacks retained current row in report: {path}")
        if not candidate.get("current_sha256"):
            errors.append(f"candidate missing current_sha256: {path}:{candidate.get('line')}")

    retained_paths = {str(row.get("path")) for row in proposal.get("retained_current_rows", [])}
    for path, current_rows in report_current_rows_by_path.items():
        if current_rows and path not in retained_paths:
            errors.append(f"proposal does not list retained current row for duplicate path: {path}")

    patch_sketch = str(proposal.get("patch_sketch", ""))
    expected_patch_sha = hashlib.sha256(patch_sketch.encode("utf-8")).hexdigest()
    if proposal.get("patch_sketch_sha256") != expected_patch_sha:
        errors.append("patch_sketch_sha256 does not match patch_sketch content")
    if proposal_candidates and "candidate stale duplicate row" not in patch_sketch:
        errors.append("patch_sketch does not include stale duplicate row marker")

    for fragment in REQUIRED_CAVEAT_FRAGMENTS:
        if fragment not in str(proposal.get("caveat", "")).lower():
            errors.append(f"proposal caveat missing fragment: {fragment}")
        if fragment not in CAVEAT.lower():
            errors.append(f"validator caveat missing fragment: {fragment}")

    status = "ok" if not errors else "error"
    return {
        "status": status,
        "artifact": "ARTIFACT_INDEX.md",
        "mode": "validation_only_no_rewrite",
        "created": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "workspace": str(workspace),
        "artifact_index_sha256_before": before_sha,
        "artifact_index_sha256_after": after_sha,
        "duplicate_path_count": report.get("duplicate_path_count"),
        "expected_cleanup_candidate_count": len(report_expected),
        "cleanup_candidate_count": proposal.get("cleanup_candidate_count"),
        "retained_current_row_count": len(proposal.get("retained_current_rows", [])),
        "patch_sketch_sha256": proposal.get("patch_sketch_sha256"),
        "proposal_output_path": "notes/artifact-index-duplicate-cleanup-proposal-output.json",
        "report_output_path": "notes/artifact-index-duplicate-report-output.json",
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "caveat": CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="Cassandra workspace path")
    parser.add_argument("--output", default="notes/artifact-index-cleanup-proposal-validation-output.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = workspace / output
    validation = build_validation(workspace)
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(validation, indent=2, sort_keys=True) + "\n"
    output.write_text(text, encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0 if validation["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
