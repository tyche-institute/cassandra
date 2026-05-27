#!/usr/bin/env python3
"""Validate the Cassandra preprint operator-review packet.

This is a mechanical completeness/boundary check only. It does not approve
publication, perform legal review, validate trusted-list signatures, determine
trusted-list/provider/service status, or issue public alerts.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_SECTIONS = [
    "# Cassandra preprint operator-review packet",
    "## Review decision boundary",
    "## Reading order",
    "## Operator checklist",
    "## Committee/reviewer checklist",
    "## Release blockers to resolve before any external deposit",
    "## Safe next actions",
]

REQUIRED_PATHS = [
    "paper/preprint/cassandra-preprint-v0.1.md",
    "paper/preprint/cassandra-preprint-v0.1.pdf",
    "paper/preprint/cassandra-preprint-v0.1.docx",
    "notes/validate_preprint_candidate.py",
    "notes/preprint-candidate-validation-output.json",
    "notes/cassandra-checked-reference-ledger-2026-05-27.md",
    "notes/fixture-to-claim-map.md",
    "notes/publication-status-discipline.md",
    "notes/publication-case-kit-readiness-output.json",
]

REQUIRED_BOUNDARY_PHRASES = [
    "not publication approval",
    "not legal review",
    "not trusted-list validation",
    "not source-signature validation",
    "not supervision",
    "not public alerting",
    "operator-review required",
]

FORBIDDEN_POSITIVE_PATTERNS = [
    r"\bpublication approved\b",
    r"\blegal review complete\b",
    r"\bready to submit\b",
    r"\btrusted-list validation complete\b",
    r"\bsource-signature validation complete\b",
    r"\bsupervisory approval\b",
    r"\bpublic alert issued\b",
]


def validate(workspace: Path) -> dict:
    packet = workspace / "notes" / "preprint-review-packet-2026-05-27.md"
    errors: list[str] = []
    warnings: list[str] = []

    if not packet.exists():
        errors.append(f"missing review packet: {packet.relative_to(workspace)}")
        text = ""
    else:
        text = packet.read_text(encoding="utf-8")

    lower = text.lower()
    for section in REQUIRED_SECTIONS:
        if section.lower() not in lower:
            errors.append(f"missing required section: {section}")

    for phrase in REQUIRED_BOUNDARY_PHRASES:
        if phrase not in lower:
            errors.append(f"missing boundary phrase: {phrase}")

    for pattern in FORBIDDEN_POSITIVE_PATTERNS:
        if re.search(pattern, lower):
            errors.append(f"forbidden positive publication/status wording: {pattern}")

    missing_paths = []
    for rel in REQUIRED_PATHS:
        if rel not in text:
            errors.append(f"packet does not reference required path: {rel}")
        if not (workspace / rel).exists():
            missing_paths.append(rel)
    if missing_paths:
        errors.append("missing referenced repository paths: " + ", ".join(missing_paths))

    checkbox_count = len(re.findall(r"^- \[ \] ", text, flags=re.MULTILINE))
    if checkbox_count < 14:
        errors.append(f"expected at least 14 open review checkboxes, found {checkbox_count}")

    blocker_count = len(re.findall(r"^- BLOCKER:", text, flags=re.MULTILINE))
    if blocker_count < 5:
        errors.append(f"expected at least 5 explicit blockers, found {blocker_count}")

    return {
        "status": "ok" if not errors else "fail",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "packet": "notes/preprint-review-packet-2026-05-27.md",
        "checkbox_count": checkbox_count,
        "blocker_count": blocker_count,
        "required_path_count": len(REQUIRED_PATHS),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": "mechanical review-packet validation only; not publication approval, not legal review, not trusted-list validation, not source-signature validation, not supervision, and not public alerting",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/preprint-review-packet-validation-output.json")
    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()
    result = validate(workspace)
    output = workspace / args.output
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
