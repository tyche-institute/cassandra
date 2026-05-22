#!/usr/bin/env python3
"""Validate the local release-readiness persistent-warning policy note."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOTE_PATH = Path("notes/release-readiness-persistent-warning-policy.md")
REPORT_PATH = Path("notes/release-readiness-warning-report-output.json")
REQUIRED_FRAGMENTS = [
    "expected to persist across append-only Cassandra history",
    "manual-review context only",
    "should not automatically delete historical rows",
    "rewrite frozen bundles",
    "not autonomous worker cleanup",
    "does not clear warnings",
    "approve publication",
    "perform legal review",
    "validate signatures",
    "supervise trusted lists",
    "determine listed-entity status",
    "provide public alerting",
    "regulated trust-service output",
]
FORBIDDEN_UNCAVEATED = [
    "safe to publish",
    "approved for publication",
    "legal compliance achieved",
    "trusted-list validation complete",
    "signature validation complete",
]
CAVEAT = (
    "Local persistent-warning policy validation only; warning persistence is "
    "manual-review context, not legal compliance, trusted-list legal effect, "
    "signature validation, supervision, public alerting, regulated "
    "trust-service output, or publication approval."
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(workspace: Path) -> dict[str, Any]:
    note_path = workspace / NOTE_PATH
    report_path = workspace / REPORT_PATH
    errors: list[str] = []
    warnings: list[str] = []

    if not note_path.exists():
        errors.append(f"missing note: {NOTE_PATH.as_posix()}")
        note = ""
    else:
        note = note_path.read_text(encoding="utf-8")

    if not report_path.exists():
        errors.append(f"missing source report: {REPORT_PATH.as_posix()}")
        report: dict[str, Any] = {}
    else:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("status") != "ok":
            errors.append(f"source report status is not ok: {report.get('status')}")
        if report.get("safe_to_auto_clear_warnings") is not False:
            errors.append("source report does not preserve safe_to_auto_clear_warnings=false")
        if report.get("safe_to_auto_publish") is not False:
            errors.append("source report does not preserve safe_to_auto_publish=false")

    for fragment in REQUIRED_FRAGMENTS:
        if fragment not in note:
            errors.append(f"missing required note fragment: {fragment}")

    lower = note.lower()
    for phrase in FORBIDDEN_UNCAVEATED:
        if phrase in lower:
            errors.append(f"forbidden uncaveated phrase present: {phrase}")

    classes = report.get("aggregate_warning_class_counts", {}) if isinstance(report, dict) else {}
    for klass in classes:
        if f"`{klass}`" not in note:
            errors.append(f"warning class not mentioned in note: {klass}")

    release_warning_count = report.get("release_warning_count")
    if not isinstance(release_warning_count, int) or release_warning_count < 1:
        errors.append(f"source report lacks positive release_warning_count: {release_warning_count}")

    result: dict[str, Any] = {
        "schema": "urn:tyche:cassandra:release-readiness-persistent-warning-policy-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "error",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "note": NOTE_PATH.as_posix(),
        "note_sha256": sha256_file(note_path) if note_path.exists() else None,
        "source_report": REPORT_PATH.as_posix(),
        "source_report_sha256": sha256_file(report_path) if report_path.exists() else None,
        "warning_class_count": len(classes),
        "warning_classes": sorted(classes),
        "research_caveat": CAVEAT,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/release-readiness-persistent-warning-policy-validation-output.json")
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    result = validate(workspace)
    output = workspace / args.output
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
