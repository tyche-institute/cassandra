#!/usr/bin/env python3
"""Append an operator-review-gates subsection to the Cassandra paper draft.

Local drafting helper only. It creates aggregate-only public-facing prose and
checks basic claim-safety constraints. It does not assert legal compliance,
trusted-list legal effect, supervision, signature validation, public alerting,
regulated trust-service output, or publication readiness.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone

SECTION_HEADING = "## Operator review gates and non-publication status"
INSERT_BEFORE = "## Limitations and reproducibility"
SECTION_BODY = """## Operator review gates and non-publication status

Cassandra's artifacts are useful only if they remain visibly separated from publication and service-provision decisions. The lane can collect public documents, preserve hashes, normalize XML, compare local records, render aggregate figures, and draft cautious explanatory prose. It should not decide whether a result is publishable, whether a named example is acceptable, or whether a structural observation has legal, supervisory, or reliance significance. Those decisions require operator review outside the autonomous worker loop.

The first review gate is named-entity use. Machine-readable records may contain names or source strings that appear in public XML, but narrative prose should stay aggregate-only unless the operator explicitly approves a case study and its wording. A proposed case study should identify the local artifact path, the exact diff class, the evidence bundle, and the reason the example is necessary. Even then, the text should describe document structure rather than the status, compliance, quality, or trustworthiness of any provider, service, authority, or scheme.

The second gate is external circulation. A clean validator run, a matching hash, or a complete evidence bundle is not publication approval. Before any draft, figure, bundle, alert extract, or dataset slice leaves the workspace, the operator should review affiliation, source boundaries, claim wording, named examples, and whether the item could be mistaken for regulated trust-service output or public alerting. If that review is not available, the safe state is to keep the artifact local.

The third gate is method expansion. Adding alternative endpoints, manual source substitutions, signature-validation logic, or legally framed labels would change the study boundary. Such changes should be proposed as research-method revisions with assumptions and risks, not silently folded into the daily monitor. This preserves Cassandra as a longitudinal observation lane rather than a supervisory, relying-party, or trust-service process.
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
    "operator review",
    "not publication approval",
    "not decide whether a result is publishable",
    "not silently folded into the daily monitor",
    "rather than a supervisory, relying-party, or trust-service process",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def main() -> int:
    workspace = pathlib.Path(__file__).resolve().parents[1]
    paper_path = workspace / "paper" / "draft.md"
    paper = paper_path.read_text(encoding="utf-8")

    inserted = False
    if SECTION_HEADING not in paper:
        if INSERT_BEFORE not in paper:
            raise SystemExit(f"insert marker missing: {INSERT_BEFORE}")
        paper = paper.replace(INSERT_BEFORE, SECTION_BODY + "\n" + INSERT_BEFORE, 1)
        paper_path.write_text(paper, encoding="utf-8")
        inserted = True

    paper = paper_path.read_text(encoding="utf-8")
    section_match = re.search(
        re.escape(SECTION_HEADING) + r"\n\n(?P<body>.*?)(?=\n## Limitations and reproducibility)",
        paper,
        flags=re.S,
    )
    errors: list[str] = []
    warnings: list[str] = []
    if not section_match:
        errors.append("operator-review-gates section not found in expected location")
        wc = 0
    else:
        wc = word_count(section_match.group("body"))
        if not (250 <= wc <= 400):
            errors.append(f"section word count outside 250-400: {wc}")

    forbidden_hits = [token for token in FORBIDDEN if token in paper]
    if forbidden_hits:
        errors.append(f"forbidden/overclaiming tokens present: {forbidden_hits}")
    missing_required = [fragment for fragment in REQUIRED if fragment not in paper]
    if missing_required:
        errors.append(f"missing required cautious fragments: {missing_required}")
    if paper.count(SECTION_HEADING) != 1:
        errors.append(f"expected exactly one section heading, found {paper.count(SECTION_HEADING)}")
    if "Tyche Institute, Tallinn, Estonia" not in paper:
        errors.append("expected Tyche affiliation missing")

    result = {
        "schema": "urn:tyche:cassandra:paper-operator-review-gates-section:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if not errors else "needs_review",
        "inserted": inserted,
        "section_heading": SECTION_HEADING,
        "section_word_count": wc,
        "paper": str(paper_path.relative_to(workspace)),
        "paper_sha256": sha256_path(paper_path),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "research_caveat": "Local paper drafting helper only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }
    out = workspace / "notes" / "paper-operator-review-gates-section-check-output.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
