#!/usr/bin/env python3
"""Append a compact operator-review release-readiness checklist section.

This helper edits the local working paper only. It does not publish anything and
it does not assert legal compliance, trusted-list legal effect, supervision,
signature validation, public alerting, regulated trust-service output, or
publication readiness.
"""
from __future__ import annotations

import json
import pathlib
import re
from datetime import datetime, timezone
from hashlib import sha256

WORKSPACE = pathlib.Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-release-readiness-checklist-section-check-output.json"
HEADING = "## Release-readiness checklist for operator review"
SECTION = """## Release-readiness checklist for operator review

A compact release-readiness check is useful only if it remains an abstention mechanism. Before any external circulation, the operator should be able to inspect a fresh local run of the snapshot metadata linkage validator, lineage validator, aggregate-results validator, figure-artifact validator, public-artifact safety validator, paper claim-safety validator, paper evidence-reference validator, paper/figure reference validator, two-date wording-drift validator, multi-day readiness validator, and ARTIFACT_INDEX current-hash validator. A clean set means that configured files exist, hashes are current, internal links resolve, and caveat text is present; it does not mean that publication is approved, that legal review has occurred, that signatures were validated for relying-party purposes, or that any trusted-list change has legal effect.

The checklist should also record abstentions explicitly. If a validator warns about legacy append-only hash drift, duplicate index rows, missing bundle inputs, or nonzero future structural diffs, the default response is to preserve the warning with local evidence pointers rather than repair the narrative from memory. If external circulation is considered, the operator must review whether named examples are necessary, whether every cited source is a saved local artifact rather than a live reinterpretation, and whether the prose still avoids service-provision language. Passing the checklist is therefore a gate for manual review, not a substitute for it.

For the current two-date corpus, the checklist remains local workflow telemetry over `notes/aggregate-results-2026-05-21-output.json`, `figures/aggregate-run-telemetry.svg`, `figures/aggregate-diff-classes.svg`, and the dated 2026-05-20/2026-05-21 snapshot, normalization, diff, alert, and bundle records. It should be refreshed after any new dated fetch or paper rewrite. Until the operator approves an external package, Cassandra outputs remain research-only working artifacts and should not be presented as public alerts, endpoint certification, supervisory findings, listed-entity status evidence, legal compliance evidence, regulated trust-service output, or publication approval.
"""

FORBIDDEN = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
]
REQUIRED = [
    "operator should be able to inspect",
    "does not mean that publication is approved",
    "not a substitute for it",
    "research-only working artifacts",
    "should not be presented as public alerts",
]


def sha256_path(path: pathlib.Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def replace_or_insert(text: str) -> tuple[str, str]:
    pattern = re.compile(rf"^{re.escape(HEADING)}\n.*?(?=^## References and local evidence\n|\Z)", re.MULTILINE | re.DOTALL)
    if pattern.search(text):
        return pattern.sub(SECTION + "\n", text), "replaced"
    marker = "## References and local evidence\n"
    if marker not in text:
        raise RuntimeError("paper lacks references section marker")
    return text.replace(marker, SECTION + "\n" + marker, 1), "inserted"


def validate_section(text: str) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if text.count(HEADING) != 1:
        errors.append(f"expected one checklist heading, found {text.count(HEADING)}")
    section_match = re.search(rf"^{re.escape(HEADING)}\n(.*?)(?=^## References and local evidence\n|\Z)", text, re.MULTILINE | re.DOTALL)
    section = section_match.group(0) if section_match else ""
    for fragment in REQUIRED:
        if fragment not in section:
            errors.append(f"missing required checklist fragment: {fragment}")
    for token in FORBIDDEN:
        if token.lower() in section.lower():
            errors.append(f"forbidden token in checklist section: {token}")
    risky = ["public alerting", "relying-party validation"]
    for phrase in risky:
        if phrase in section and not re.search(rf"(?:not|does not|should not).{{0,90}}{re.escape(phrase)}", section, re.IGNORECASE | re.DOTALL):
            warnings.append(f"risky phrase needs manual review context: {phrase}")
    words = len(re.findall(r"\b[\w'-]+\b", section))
    if words < 200 or words > 450:
        errors.append(f"checklist section word count {words} outside 200-450")
    return {"errors": errors, "warnings": warnings, "word_count": words}


def main() -> int:
    before = PAPER.read_text(encoding="utf-8")
    after, action = replace_or_insert(before)
    PAPER.write_text(after, encoding="utf-8")
    check = validate_section(after)
    result = {
        "schema": "urn:tyche:cassandra:paper-release-readiness-checklist-section:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if not check["errors"] else "needs_review",
        "action": action,
        "paper": str(PAPER.relative_to(WORKSPACE)),
        "paper_sha256": sha256_path(PAPER),
        "heading": HEADING,
        "word_count": check["word_count"],
        "error_count": len(check["errors"]),
        "warning_count": len(check["warnings"]),
        "errors": check["errors"],
        "warnings": check["warnings"],
        "research_caveat": "Local checklist prose update only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
