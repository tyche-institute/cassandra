#!/usr/bin/env python3
"""Validate the Cassandra preprint deposit-metadata draft.

Mechanical completeness check only. It does not upload, submit, reserve DOI,
approve publication, perform legal review, validate trusted lists, validate
source signatures, supervise any actor, or issue public alerts.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_SECTIONS = [
    "# Cassandra preprint deposit metadata draft",
    "## Boundary",
    "## Candidate metadata",
    "## Suggested abstract",
    "## Keywords",
    "## Related identifiers to verify before deposit",
    "## Files to attach only after operator approval",
    "## Pre-deposit checklist",
]

REQUIRED_PHRASES = [
    "operator-review required",
    "draft only",
    "no upload action",
    "not publication approval",
    "not legal review",
    "not trusted-list validation",
    "not source-signature validation",
    "not supervision",
    "not public alerting",
]

REQUIRED_PATHS = [
    "paper/preprint/cassandra-preprint-v0.1.md",
    "paper/preprint/cassandra-preprint-v0.1.pdf",
    "paper/preprint/cassandra-preprint-v0.1.docx",
    "notes/preprint-review-packet-2026-05-27.md",
    "notes/cassandra-checked-reference-ledger-2026-05-27.md",
    "notes/publication-status-discipline.md",
]

FORBIDDEN = [
    r"\buploaded\b",
    r"\bsubmitted\b",
    r"\bdoi reserved\b",
    r"\bpublication approved\b",
    r"\blegal review complete\b",
    r"\bready to publish\b",
]


def validate(workspace: Path) -> dict:
    rel = "notes/preprint-deposit-metadata-draft-2026-05-27.md"
    path = workspace / rel
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lower = text.lower()

    if not path.exists():
        errors.append(f"missing metadata draft: {rel}")
    for section in REQUIRED_SECTIONS:
        if section.lower() not in lower:
            errors.append(f"missing required section: {section}")
    for phrase in REQUIRED_PHRASES:
        if phrase not in lower:
            errors.append(f"missing required boundary phrase: {phrase}")
    for rel_path in REQUIRED_PATHS:
        if rel_path not in text:
            errors.append(f"metadata draft does not reference required path: {rel_path}")
        if not (workspace / rel_path).exists():
            errors.append(f"referenced path missing from repository: {rel_path}")
    for pattern in FORBIDDEN:
        if re.search(pattern, lower):
            errors.append(f"forbidden deposit/publication-positive wording: {pattern}")

    checklist_count = len(re.findall(r"^- \[ \] ", text, flags=re.MULTILINE))
    if checklist_count < 8:
        errors.append(f"expected at least 8 pre-deposit checklist items, found {checklist_count}")

    keyword_line = next((line for line in text.splitlines() if line.startswith("Keywords:")), "")
    keywords = [k.strip() for k in keyword_line.removeprefix("Keywords:").split(";") if k.strip()]
    if len(keywords) < 8:
        errors.append(f"expected at least 8 semicolon-separated keywords, found {len(keywords)}")

    return {
        "status": "ok" if not errors else "fail",
        "created": datetime.now(timezone.utc).isoformat(),
        "metadata_draft": rel,
        "checklist_count": checklist_count,
        "keyword_count": len(keywords),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": "deposit metadata draft validation only; draft only, no upload action, not publication approval, not legal review, not trusted-list validation, not source-signature validation, not supervision, and not public alerting",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/preprint-deposit-metadata-validation-output.json")
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    result = validate(workspace)
    output = workspace / args.output
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1

if __name__ == "__main__":
    raise SystemExit(main())
