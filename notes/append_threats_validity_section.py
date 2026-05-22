#!/usr/bin/env python3
"""Append a cautious threats-to-validity subsection to the Cassandra paper draft.

Local drafting helper only. It produces aggregate-only public-facing prose and
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

SECTION_HEADING = "### Threats to validity for early longitudinal interpretation"
INSERT_BEFORE = "## References and local evidence"
SECTION_BODY = """### Threats to validity for early longitudinal interpretation

The main threat to validity in the current draft is temporal shallowness. A single baseline row can verify that the workflow produces bounded artifacts, but it cannot characterize longitudinal behavior. Until several dated runs exist, Cassandra should not describe any pattern as typical, recurring, or stable. The first row is best understood as a calibration record: it fixes count definitions, demonstrates that endpoint and parser anomalies are retained, and gives the paper a reproducible place to attach future rows.

A second threat is parser perspective. The normalizer and structural parser observe XML shape, selected summary fields, signature-shaped elements, and hashed provider/service inventory keys. They do not implement the full semantics of any trusted-list processing stack. A parser omission, namespace edge case, or non-XML pointer can affect local comparison counts without saying anything about the public document's legal meaning. For that reason, future result tables should keep parser-success counts next to diff counts rather than treating the comparable subset as the whole corpus.

A third threat is presentation pressure. Once multiple dates are available, visual diffs and alert entries may invite readers to infer importance from count size, territory code, or chart shape. The paper should resist that inference. Counts can motivate manual research review, but they do not rank authorities, providers, services, schemes, or countries. If a future revision needs named examples, they should be introduced only after operator approval and should be framed as document-structure examples with local artifact paths, not as assertions about legal status, service quality, compliance, or trustworthiness.

Finally, Cassandra's source boundary is intentionally LOTL-derived. That makes the dataset reproducible, but it also means the monitor does not answer questions that require alternative endpoints, official supervisory interpretation, or relying-party validation. Those questions belong outside this lane.
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
    "do not rank authorities, providers, services, schemes, or countries",
    "not as assertions about legal status",
    "outside this lane",
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
        re.escape(SECTION_HEADING) + r"\n\n(?P<body>.*?)(?=\n## References and local evidence)",
        paper,
        flags=re.S,
    )
    errors: list[str] = []
    warnings: list[str] = []
    if not section_match:
        errors.append("threats-to-validity section not found in expected location")
        section_text = ""
    else:
        section_text = section_match.group(0)
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
        "schema": "urn:tyche:cassandra:paper-threats-validity-section:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if not errors else "needs_review",
        "inserted": inserted,
        "section_heading": SECTION_HEADING,
        "section_word_count": word_count(section_match.group("body")) if section_match else 0,
        "paper": str(paper_path.relative_to(workspace)),
        "paper_sha256": sha256_path(paper_path),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "research_caveat": "Local paper drafting helper only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }
    out = workspace / "notes" / "paper-threats-validity-section-check-output.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
