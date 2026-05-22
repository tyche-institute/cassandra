#!/usr/bin/env python3
"""Validate paper and ARTIFACT_INDEX freshness for the release-readiness topology report.

This non-mutating helper checks that the paper checklist still references the
local topology report and that ARTIFACT_INDEX.md contains a current sha256 row
for that report. It is workflow-maintenance telemetry only: not legal review,
publication approval, trusted-list legal effect, signature validation,
supervision, public alerting, listed-entity status evidence, or regulated
trust-service output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

TOPOLOGY_REPORT = "notes/release-readiness-topology-report-output.json"
PAPER = "paper/draft.md"
ARTIFACT_INDEX = "ARTIFACT_INDEX.md"
REQUIRED_PAPER_FRAGMENTS = [
    TOPOLOGY_REPORT,
    "release-readiness topology report",
    "not an additional release gate",
    "not a release decision",
]
REQUIRED_CAVEAT_FRAGMENTS = [
    "not legal compliance",
    "trusted-list legal effect",
    "signature validation",
    "supervision",
    "public alerting",
    "regulated trust-service output",
    "publication approval",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact_index_hashes(index_text: str, rel_path: str) -> list[str]:
    pattern = rf"`{re.escape(rel_path)}`[^\n]*`sha256:([0-9a-f]{{64}})`"
    return re.findall(pattern, index_text)


def line_for(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    if idx < 0:
        return None
    return text.count("\n", 0, idx) + 1


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    report_path = workspace / TOPOLOGY_REPORT
    paper_path = workspace / PAPER
    index_path = workspace / ARTIFACT_INDEX

    report_exists = report_path.exists()
    paper_exists = paper_path.exists()
    index_exists = index_path.exists()

    report_data: dict[str, Any] = {}
    report_digest: str | None = None
    index_candidates: list[str] = []
    paper_line: int | None = None

    if not paper_exists:
        errors.append(f"missing paper file: {PAPER}")
        paper_text = ""
    else:
        paper_text = paper_path.read_text(encoding="utf-8")
        paper_line = line_for(paper_text, TOPOLOGY_REPORT)
        for fragment in REQUIRED_PAPER_FRAGMENTS:
            if fragment not in paper_text:
                errors.append(f"paper lacks required topology-report fragment: {fragment}")

    if not index_exists:
        errors.append(f"missing artifact index: {ARTIFACT_INDEX}")
        index_text = ""
    else:
        index_text = index_path.read_text(encoding="utf-8")

    if not report_exists:
        errors.append(f"missing topology report: {TOPOLOGY_REPORT}")
    else:
        report_digest = sha256_path(report_path)
        try:
            report_data = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"topology report is not JSON: {exc}")
            report_data = {}
        else:
            if report_data.get("status") != "ok":
                errors.append(f"topology report status is not ok: {report_data.get('status')}")
            if isinstance(report_data.get("error_count"), int) and report_data["error_count"] != 0:
                errors.append(f"topology report error_count is nonzero: {report_data['error_count']}")
            if isinstance(report_data.get("warning_count"), int) and report_data["warning_count"] > 0:
                warnings.append(
                    f"topology report warning_count={report_data['warning_count']} preserved as manual-review context"
                )
            caveat = str(report_data.get("research_caveat", "")).lower()
            for fragment in REQUIRED_CAVEAT_FRAGMENTS:
                if fragment not in caveat:
                    errors.append(f"topology report caveat lacks required fragment: {fragment}")
            if report_data.get("safe_to_auto_clear_warnings") is not False:
                errors.append("topology report does not explicitly refuse automatic warning clearance")
            if report_data.get("safe_to_auto_publish") is not False:
                errors.append("topology report does not explicitly refuse automatic publication")

    if index_text and report_digest:
        index_candidates = artifact_index_hashes(index_text, TOPOLOGY_REPORT)
        if not index_candidates:
            errors.append(f"ARTIFACT_INDEX.md lacks hash row for {TOPOLOGY_REPORT}")
        elif report_digest not in index_candidates:
            errors.append(
                f"ARTIFACT_INDEX.md hash mismatch for {TOPOLOGY_REPORT}: actual {report_digest}, candidates {index_candidates}"
            )
        elif len(index_candidates) > 1:
            warnings.append(
                f"ARTIFACT_INDEX.md has multiple rows for {TOPOLOGY_REPORT}; one row matches the current file hash"
            )

    return {
        "schema": "urn:tyche:cassandra:topology-report-reference-freshness:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "paper_reference": {
            "path": PAPER,
            "exists": paper_exists,
            "topology_report_path": TOPOLOGY_REPORT,
            "line": paper_line,
        },
        "topology_report": {
            "path": TOPOLOGY_REPORT,
            "exists": report_exists,
            "sha256": report_digest,
            "status": report_data.get("status"),
            "error_count": report_data.get("error_count"),
            "warning_count": report_data.get("warning_count"),
        },
        "artifact_index": {
            "path": ARTIFACT_INDEX,
            "exists": index_exists,
            "topology_report_sha256_candidates": index_candidates,
            "current_hash_indexed": bool(report_digest and report_digest in index_candidates),
        },
        "operator_review_gate": True,
        "safe_to_auto_clear_warnings": False,
        "safe_to_auto_publish": False,
        "research_caveat": "Local topology-report reference freshness validation only; not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, listed-entity status evidence, legal review, warning clearance, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/topology-report-reference-freshness-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    output_path = workspace / args.output
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
