#!/usr/bin/env python3
"""Validate the Cassandra source-coverage policy note.

This validator is local provenance/readiness telemetry only. It does not
perform trusted-list validation, signature validation, supervision,
legal-status determination, public alerting, regulated trust-service output,
or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_NOTE = Path("notes/source-coverage-policy-note.md")

REQUIRED_FRAGMENTS = [
    "frozen bundle manifests",
    "SOURCES.md is a provenance register",
    "does not duplicate every bundle-source hash",
    "without rewriting historical bundles",
    "does not assert legal effect",
    "does not perform trusted-list validation",
    "publication approval",
]
FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(workspace: Path, note_path: Path) -> dict:
    path = note_path if note_path.is_absolute() else workspace / note_path
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        errors.append(f"missing policy note: {path}")
        text = ""
    else:
        text = path.read_text(encoding="utf-8")
    for fragment in REQUIRED_FRAGMENTS:
        if fragment not in text:
            errors.append(f"missing required fragment: {fragment}")
    for token in FORBIDDEN:
        if token.lower() in text.lower():
            errors.append(f"forbidden token: {token}")
    if "safe_to_rewrite_historical_bundles: false" not in text:
        errors.append("missing explicit historical-bundle non-rewrite policy")
    if "named listed entities" in text and "operator review" not in text:
        warnings.append("named-entity reference lacks operator-review context")
    word_count = len(text.split())
    if word_count < 180 or word_count > 450:
        errors.append(f"word count outside 180-450: {word_count}")
    rel = str(path.relative_to(workspace)) if path.exists() and path.is_relative_to(workspace) else str(path)
    return {
        "schema": "urn:tyche:cassandra:source-coverage-policy-note-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if not errors else "needs_review",
        "note": rel,
        "note_sha256": sha256_file(path) if path.exists() else None,
        "word_count": word_count,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "research_caveat": "Local provenance-policy validation only; not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--note", default=str(DEFAULT_NOTE))
    parser.add_argument("--output", default="notes/source-coverage-policy-note-validation-output.json")
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    result = validate(workspace, Path(args.note))
    output = Path(args.output)
    if not output.is_absolute():
        output = workspace / output
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
