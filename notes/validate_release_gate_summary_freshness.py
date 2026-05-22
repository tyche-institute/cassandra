#!/usr/bin/env python3
"""Validate freshness of Cassandra's release-readiness gate summary.

The check is intentionally local and non-mutating except for its own requested
output file. It verifies that the gate-summary output embeds current hashes for
its upstream release-readiness checklist, warning report, and persistent-warning
policy validation outputs. A clean result is workflow telemetry only; it is not
publication approval, legal review, signature validation, trusted-list
supervision, listed-entity status evidence, public alerting, or regulated
trust-service output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

UPSTREAM_SOURCES = {
    "release_readiness_checklist": "notes/release-readiness-checklist-validation-output.json",
    "warning_report": "notes/release-readiness-warning-report-output.json",
    "persistent_warning_policy": "notes/release-readiness-persistent-warning-policy-validation-output.json",
}
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
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate(workspace: pathlib.Path, summary_rel: str) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    summary_path = workspace / summary_rel
    if not summary_path.exists():
        errors.append(f"missing gate summary: {summary_rel}")
        summary: dict[str, Any] = {}
    else:
        summary = load_json(summary_path)

    if summary.get("schema") != "urn:tyche:cassandra:release-readiness-gate-summary:0.1":
        errors.append(f"unexpected gate summary schema: {summary.get('schema')}")
    if summary.get("status") != "ok":
        errors.append(f"gate summary status is not ok: {summary.get('status')}")
    if summary.get("error_count") != 0:
        errors.append(f"gate summary error_count is not zero: {summary.get('error_count')}")
    if summary.get("safe_to_auto_clear_warnings") is not False:
        errors.append("gate summary does not refuse automatic warning clearing")
    if summary.get("safe_to_auto_publish") is not False:
        errors.append("gate summary does not refuse automatic publication")

    caveat = str(summary.get("research_caveat") or "").lower()
    for fragment in REQUIRED_CAVEAT_FRAGMENTS:
        if fragment not in caveat:
            errors.append(f"gate summary caveat lacks required fragment: {fragment}")

    source_checks: dict[str, dict[str, Any]] = {}
    embedded_sources = summary.get("sources") if isinstance(summary.get("sources"), dict) else {}
    for label, rel in UPSTREAM_SOURCES.items():
        path = workspace / rel
        check: dict[str, Any] = {"path": rel, "exists": path.exists()}
        if not path.exists():
            errors.append(f"missing upstream source: {rel}")
            source_checks[label] = check
            continue
        current_hash = sha256_path(path)
        check["current_sha256"] = current_hash
        embedded = embedded_sources.get(label) if isinstance(embedded_sources, dict) else None
        if not isinstance(embedded, dict):
            errors.append(f"gate summary lacks embedded source record for {label}")
            check["embedded_present"] = False
        else:
            embedded_path = embedded.get("path")
            embedded_hash = embedded.get("sha256")
            check.update({
                "embedded_present": True,
                "embedded_path": embedded_path,
                "embedded_sha256": embedded_hash,
                "matches_current_hash": embedded_hash == current_hash,
            })
            if embedded_path != rel:
                errors.append(f"embedded path mismatch for {label}: {embedded_path} != {rel}")
            if embedded_hash != current_hash:
                errors.append(f"stale embedded hash for {label}: {embedded_hash} != {current_hash}")
        source_checks[label] = check

    # Created timestamps are informative only: regenerated files may share a
    # second-level timestamp in scripted runs, while hash matching is the hard
    # freshness property.
    created = summary.get("created")
    if not created:
        warnings.append("gate summary lacks created timestamp")

    return {
        "schema": "urn:tyche:cassandra:release-gate-summary-freshness-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "summary_path": summary_rel,
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "source_checks": source_checks,
        "research_caveat": "Local freshness check for release-readiness gate-summary telemetry only; it is not publication approval, legal review, signature validation, trusted-list supervision, listed-entity status evidence, public alerting, or regulated trust-service output.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--summary", default="notes/release-readiness-gate-summary-output.json")
    parser.add_argument("--output", default="notes/release-gate-summary-freshness-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace, args.summary)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
