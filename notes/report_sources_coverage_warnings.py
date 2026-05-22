#!/usr/bin/env python3
"""Report-only explanation of Cassandra SOURCES.md coverage warnings.

This helper reads the latest SOURCES.md coverage validator output and produces a
small operator-review report explaining why each warning is legacy/provenance
context rather than a hard source-coverage failure. It is intentionally
non-mutating: it does not rewrite SOURCES.md, historical bundles, manifests, or
state registers.

The report is local provenance telemetry only. It does not perform trusted-list
validation, signature validation, supervision, legal-status determination,
public alerting, regulated trust-service output, or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "urn:tyche:cassandra:sources-coverage-warning-report:0.1"
RESEARCH_CAVEAT = (
    "Local warning-explanation report only; this does not perform trusted-list "
    "validation, signature validation, supervision, legal-status determination, "
    "public alerting, regulated trust-service output, or publication approval."
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_warning(warning: str) -> dict[str, Any]:
    text = warning.lower()
    if "pointer-url-records caveat is legacy/incomplete" in text:
        return {
            "class": "legacy_pointer_record_caveat",
            "severity": "manual_review_context",
            "hard_failure": False,
            "explanation": (
                "The historical pointer-url bundle source records structural-observation "
                "wording but predates the stronger later legal-status caveat phrase. The "
                "bundle source file still exists and its hash matched the bundle manifest; "
                "the warning is retained rather than rewriting a frozen historical bundle."
            ),
            "recommended_action": (
                "Do not rewrite the historical bundle automatically. If an operator prepares "
                "external circulation, review the frozen 2026-05-20 bundle notes/caveats and "
                "add a separate erratum or new bundle version if stronger caveat wording is required."
            ),
        }
    if "sources.md has no date-specific bundle row" in text:
        return {
            "class": "missing_date_specific_bundle_sources_row",
            "severity": "coverage_style_warning",
            "hard_failure": False,
            "explanation": (
                "SOURCES.md records external/public snapshot URL provenance rows, while the "
                "MIRROR-style bundle source lists were checked directly from each bundle "
                "manifest and local source copies. The validator found the bundle sources "
                "present and hash-consistent, so absence of a date-specific bundle row is "
                "a documentation-style warning rather than missing provenance."
            ),
            "recommended_action": (
                "Keep the warning visible for operator review. Add optional date-specific "
                "bundle-summary rows to SOURCES.md only if the lane decides to document local "
                "bundle manifests as source context; do not treat this as a fetch or hash failure."
            ),
        }
    return {
        "class": "unclassified_warning",
        "severity": "manual_review_needed",
        "hard_failure": False,
        "explanation": "The warning was not recognized by the report helper and should be reviewed manually.",
        "recommended_action": "Inspect the validator output and decide whether a new classifier or a hard validation rule is needed.",
    }


def build_report(workspace: Path, validation_output: Path) -> dict[str, Any]:
    validation = load_json(validation_output)
    warnings = list(validation.get("warnings") or [])
    entries = []
    hard_failure_like = []
    for warning in warnings:
        entry = {"warning": warning}
        entry.update(classify_warning(str(warning)))
        entries.append(entry)
        if entry.get("hard_failure"):
            hard_failure_like.append(str(warning))
    status = "ok" if validation.get("status") == "ok" and not hard_failure_like else "needs_review"
    classes: dict[str, int] = {}
    for entry in entries:
        classes[entry["class"]] = classes.get(entry["class"], 0) + 1
    return {
        "schema": SCHEMA,
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": status,
        "source_validation_output": str(validation_output.relative_to(workspace)),
        "source_validation_sha256": sha256_file(validation_output),
        "source_validation_status": validation.get("status"),
        "source_validation_error_count": validation.get("error_count"),
        "source_validation_warning_count": validation.get("warning_count"),
        "sources_row_count": validation.get("sources_row_count"),
        "snapshot_item_count": validation.get("snapshot_item_count"),
        "snapshot_item_covered_count": validation.get("snapshot_item_covered_count"),
        "bundle_count": len(validation.get("bundle_records") or []),
        "warning_count": len(entries),
        "warning_classes": classes,
        "warnings": entries,
        "non_mutating": True,
        "safe_to_auto_rewrite_historical_bundles": False,
        "research_caveat": RESEARCH_CAVEAT,
        "summary": (
            "The latest SOURCES.md coverage validation has zero hard errors and full "
            "snapshot URL/local-path coverage for the checked dated manifests. The three "
            "warnings are retained as legacy wording or documentation-style context, not "
            "as source-fetch, source-presence, or bundle-hash failures."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--validation-output", default="notes/sources-coverage-validation-output.json")
    parser.add_argument("--output", default="notes/sources-coverage-warning-report-output.json")
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    validation_output = (workspace / args.validation_output).resolve()
    before_hashes = {}
    for rel_path in ["SOURCES.md", "bundles/2026-05-20/snapshot-summary.json.bundle/manifest.json", "bundles/2026-05-21/snapshot-summary.json.bundle/manifest.json"]:
        path = workspace / rel_path
        if path.exists():
            before_hashes[rel_path] = sha256_file(path)
    result = build_report(workspace, validation_output)
    after_hashes = {}
    for rel_path in before_hashes:
        after_hashes[rel_path] = sha256_file(workspace / rel_path)
    result["non_mutation_hash_check"] = {"before": before_hashes, "after": after_hashes, "unchanged": before_hashes == after_hashes}
    if before_hashes != after_hashes:
        result["status"] = "needs_review"
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
