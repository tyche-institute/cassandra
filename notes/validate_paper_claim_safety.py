#!/usr/bin/env python3
"""Local claim-safety validator for Cassandra public-facing draft prose.

Research-only helper. This validator checks wording risk in public-facing
Cassandra prose; it does not determine legal compliance, signature validity,
trusted-list status, or publication readiness.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Iterable

WORKSPACE = Path(__file__).resolve().parents[1]
PUBLIC_TEXT_PATHS = [
    WORKSPACE / "paper" / "draft.md",
]

# Hard rails from the lane prompt and operator profile. These are deliberately
# conservative string/regex checks for public-facing prose, not legal analysis.
FORBIDDEN_PATTERNS = [
    ("zetes_mention", re.compile(r"\bZetes\b", re.IGNORECASE)),
    ("zetes_estonia_mention", re.compile(r"\bZetes\s+Estonia\b", re.IGNORECASE)),
    ("employee_identification", re.compile(r"\b(employee|employed)\b.{0,80}\bZetes\b", re.IGNORECASE | re.DOTALL)),
    ("trust_service_provider_claim", re.compile(r"\b(Tyche Institute|Anton Sokolov|Cassandra)\b.{0,120}\b(provides?|offers?|sells?|operates?)\b.{0,80}\b(trust services?|qualified certificates?|timestamps?|identity solutions?|border-control solutions?)\b", re.IGNORECASE | re.DOTALL)),
    ("qualified_tsp_claim", re.compile(r"\b(Tyche Institute|Anton Sokolov|Cassandra)\b.{0,120}\b(QTSP|qualified trust service provider)\b", re.IGNORECASE | re.DOTALL)),
]

RISKY_PHRASES = [
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "legal status determination",
    "public alerting",
    "relying-party validation",
]

REQUIRED_PHRASES = [
    "Tyche Institute, Tallinn, Estonia",
    "does not assert legal effect",
    "does not determine",
]

@dataclass
class Finding:
    path: str
    category: str
    pattern: str
    line: int
    snippet: str
    severity: str


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def snippet(text: str, start: int, end: int, width: int = 100) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return " ".join(text[left:right].split())


def scan_file(path: Path) -> tuple[list[Finding], dict]:
    text = path.read_text(encoding="utf-8")
    findings: list[Finding] = []

    for name, pattern in FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(Finding(
                path=str(path.relative_to(WORKSPACE)),
                category="forbidden_pattern",
                pattern=name,
                line=line_number(text, match.start()),
                snippet=snippet(text, match.start(), match.end()),
                severity="error",
            ))

    lowered = text.lower()
    for phrase in RISKY_PHRASES:
        if phrase.lower() in lowered:
            # These phrases can be allowed when negated/caveated. Record warnings,
            # not errors, for manual review.
            index = lowered.index(phrase.lower())
            findings.append(Finding(
                path=str(path.relative_to(WORKSPACE)),
                category="risky_phrase_review",
                pattern=phrase,
                line=line_number(text, index),
                snippet=snippet(text, index, index + len(phrase)),
                severity="warning",
            ))

    required_presence = {phrase: (phrase in text) for phrase in REQUIRED_PHRASES}
    stats = {
        "path": str(path.relative_to(WORKSPACE)),
        "sha256": file_sha256(path),
        "bytes": path.stat().st_size,
        "line_count": text.count("\n") + (1 if text else 0),
        "word_count": len(re.findall(r"\b\w+\b", text)),
        "required_presence": required_presence,
    }
    return findings, stats


def main() -> int:
    all_findings: list[Finding] = []
    file_stats: list[dict] = []
    missing_files: list[str] = []

    for path in PUBLIC_TEXT_PATHS:
        if not path.exists():
            missing_files.append(str(path.relative_to(WORKSPACE)))
            continue
        findings, stats = scan_file(path)
        all_findings.extend(findings)
        file_stats.append(stats)

    errors = [f for f in all_findings if f.severity == "error"]
    missing_required = []
    for stats in file_stats:
        for phrase, present in stats["required_presence"].items():
            if not present:
                missing_required.append({"path": stats["path"], "phrase": phrase})

    status = "ok"
    if missing_files or errors or missing_required:
        status = "needs_review"

    result = {
        "schema_version": "cassandra-claim-safety-validator-v0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "status": status,
        "scope": "public-facing Cassandra draft prose only; local wording check, not legal analysis or publication approval",
        "missing_files": missing_files,
        "file_stats": file_stats,
        "findings": [asdict(f) for f in all_findings],
        "error_count": len(errors),
        "warning_count": len([f for f in all_findings if f.severity == "warning"]),
        "missing_required": missing_required,
        "caveat": "Passing this check does not assert legal compliance, trusted-list legal effect, signature validity, supervision, or publication readiness.",
    }

    output_path = WORKSPACE / "notes" / "paper-claim-safety-validation-output.json"
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
