#!/usr/bin/env python3
"""Validate the Cassandra preprint candidate shape and claim boundaries.

Research-only helper. This does not approve publication, perform legal
review, validate trusted lists, validate source signatures, supervise any
actor, or determine legal/provider/service status.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
PREPRINT = WORKSPACE / "paper" / "preprint" / "cassandra-preprint-v0.1.md"
OUTPUT = WORKSPACE / "notes" / "preprint-candidate-validation-output.json"

REQUIRED_SECTIONS = [
    "# Cassandra: From Governance Infrastructure to Evidence Infrastructure",
    "## Abstract",
    "## Claim-Safety Note",
    "## 1. Introduction",
    "## 2. Background: Trusted Lists as Governance Artifacts",
    "## 3. Related Work and Positioning",
    "## 4. System Overview",
    "## 5. Evidence Package Design",
    "## 6. Dataset and Current Results",
    "## 7. Fixture-Backed Behavior",
    "## 8. Discussion: From PKI Governance to AI Evidence",
    "## 9. Limitations",
    "## 10. Conclusion",
    "## Artifact Availability",
    "## References",
]

REQUIRED_STRINGS = [
    "does not assert legal effect",
    "does not determine whether any listed entity has gained or lost status",
    "does not validate source signatures for relying-party purposes",
    "does not provide public alerting",
    "https://cassandra-observatory.pages.dev/data/index.json",
    "notes/cassandra-checked-reference-ledger-2026-05-27.md",
    "notes/fixture-to-claim-map.md",
    "Regulation (EU) No 910/2014",
    "ETSI TS 119 612",
    "RFC 5280",
    "NIST. FIPS 203",
]

FORBIDDEN_PATTERNS = [
    ("legal_status_oracle_positive", re.compile(r"\bCassandra\s+is\s+a\s+legal status oracle\b", re.IGNORECASE)),
    ("certifies_compliance", re.compile(r"\bcertifies compliance\b", re.IGNORECASE)),
    ("validates_source_signatures_positive", re.compile(r"\bCassandra\s+validates\s+source signatures\b", re.IGNORECASE)),
    ("supervisory_tool_positive", re.compile(r"\bCassandra\s+is\s+a\s+supervisory tool\b", re.IGNORECASE)),
]


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def main() -> int:
    errors: list[dict] = []
    warnings: list[dict] = []

    if not PREPRINT.exists():
        errors.append({"type": "missing_preprint", "path": str(PREPRINT.relative_to(WORKSPACE))})
        text = ""
    else:
        text = PREPRINT.read_text(encoding="utf-8")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append({"type": "missing_section", "section": section})

    normalized_text = " ".join(text.split())

    for value in REQUIRED_STRINGS:
        if value not in normalized_text:
            errors.append({"type": "missing_required_string", "value": value})

    for name, pattern in FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            errors.append({
                "type": "forbidden_pattern",
                "pattern": name,
                "line": line_number(text, match.start()),
                "snippet": " ".join(text[max(0, match.start() - 80):match.end() + 80].split()),
            })

    if "operator-review required before external submission" not in text:
        warnings.append({"type": "operator_review_marker_missing"})

    stats = {
        "path": str(PREPRINT.relative_to(WORKSPACE)),
        "sha256": sha256_file(PREPRINT) if PREPRINT.exists() else None,
        "bytes": PREPRINT.stat().st_size if PREPRINT.exists() else 0,
        "line_count": text.count("\n") + (1 if text else 0),
        "word_count": len(re.findall(r"\b\w+\b", text)),
    }

    output = {
        "status": "ok" if not errors else "error",
        "created": datetime.now(timezone.utc).isoformat(),
        "scope": "Cassandra preprint candidate shape and claim-boundary check only",
        "stats": stats,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "non_claims": "This validation does not approve publication, perform legal review, validate trusted lists, validate source signatures, supervise any actor, issue public alerts, or determine legal/provider/service status.",
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
