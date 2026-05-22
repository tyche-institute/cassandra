#!/usr/bin/env python3
"""Validate Cassandra paper subsection word counts and risk-caveat coverage.

Local research-safety helper only. It checks public-facing draft sections for
bounded subsection size, required cautious caveat families, and absence of hard
compliance-rail tokens. It does not assert legal compliance, trusted-list legal
effect, supervision, signature validation, public alerting, regulated trust-
service output, or publication readiness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

RESEARCH_CAVEAT = (
    "Local paper subsection risk-coverage validation only; not legal compliance, "
    "trusted-list legal effect, supervision, signature validation, public "
    "alerting, regulated trust-service output, or publication readiness."
)

# Long sections are expected to carry most risk caveat families. The abstract,
# outline, and references sections are intentionally excluded from word-count
# range checks because they are scaffolding or bibliographic material.
SECTION_RULES: dict[str, dict[str, Any]] = {
    "## Background": {"min_words": 250, "max_words": 900, "required_families": ["research_only", "no_legal_effect", "no_relying_party"]},
    "## Dataset boundary and source handling": {"min_words": 250, "max_words": 400, "required_families": ["source_boundary", "no_authoritative_registry", "no_relying_party"]},
    "## Method and evidence-bundle design": {"min_words": 250, "max_words": 400, "required_families": ["evidence_bundle", "no_legal_effect", "no_supervision", "no_relying_party"]},
    "## Initial baseline telemetry (2026-05-20)": {"min_words": 60, "max_words": 500, "required_families": ["no_legal_effect", "baseline_only"]},
    "## Planned longitudinal aggregation and alert taxonomy": {"min_words": 250, "max_words": 400, "required_families": ["alerts_internal", "aggregate_only", "no_public_alerting", "no_legal_effect"]},
    "## Aggregate telemetry table interpretation": {"min_words": 250, "max_words": 400, "required_families": ["aggregate_only", "no_legal_effect", "no_signature_validation"]},
    "## Results presentation and figure design": {"min_words": 250, "max_words": 400, "required_families": ["aggregate_only", "figure_caution", "no_public_alerting"]},
    "## Figure reproducibility cross-references": {"min_words": 250, "max_words": 400, "required_families": ["figure_caution", "reproducibility", "no_publication_readiness"]},
    "## Limitations and reproducibility": {"min_words": 250, "max_words": 400, "required_families": ["limitations", "no_legal_effect", "no_relying_party"]},
    "### Threats to validity for early longitudinal interpretation": {"min_words": 250, "max_words": 400, "required_families": ["limitations", "aggregate_only", "no_ranking", "source_boundary"]},
}

CAVEAT_FAMILIES: dict[str, list[str]] = {
    "research_only": ["research", "structural-observation"],
    "aggregate_only": ["aggregate", "aggregate-only", "counts", "totals"],
    "source_boundary": ["source boundary", "LOTL-derived", "saved LOTL"],
    "evidence_bundle": ["evidence bundle", "MIRROR-style", "bundle"],
    "baseline_only": ["baseline", "calibration"],
    "alerts_internal": ["internal research telemetry", "local research telemetry", "internal and descriptive", "not public alerts"],
    "figure_caution": ["figure", "caption", "visual"],
    "reproducibility": ["reproducible", "hash", "local evidence"],
    "limitations": ["limitation", "limited by", "threat to validity", "cannot characterize"],
    "no_legal_effect": ["does not assert legal effect", "do not assert legal effect", "not assertions about legal status", "does not determine legal effect", "legal effect", "legal status"],
    "no_relying_party": ["does not describe relying-party validation", "not a relying-party process", "relying-party", "outside this lane"],
    "no_supervision": ["does not supervise", "not supervision", "supervisory", "supervision"],
    "no_signature_validation": ["does not validate signatures", "signature validity", "signature validation", "signature was verified", "relied upon"],
    "no_public_alerting": ["not public alerts", "public alerting", "public risk", "not a public alert"],
    "no_publication_readiness": ["publication readiness", "publication-readiness", "publication approval", "not publication", "operator approves"],
    "no_authoritative_registry": ["not as a complete or authoritative registry", "not a complete or authoritative registry", "authoritative registry"],
    "no_ranking": ["do not rank authorities", "do not rank", "not rank"],
}

FORBIDDEN_TOKENS = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees compliance",
    "qualifies as a QTSP",
    "we offer",
    "we provide eIDAS",
]

HEADING_RE = re.compile(r"^(#{1,3})\s+.+$", re.MULTILINE)
WORD_RE = re.compile(r"\b[\w'-]+\b")


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def line_for(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    if idx < 0:
        return None
    return text.count("\n", 0, idx) + 1


def extract_sections(paper: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(paper))
    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        heading = match.group(0).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(paper)
        sections[heading] = paper[start:end].strip()
    return sections


def family_present(section_text: str, family: str) -> bool:
    lowered = section_text.lower()
    return any(fragment.lower() in lowered for fragment in CAVEAT_FAMILIES[family])


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    paper_path = workspace / "paper" / "draft.md"
    paper = paper_path.read_text(encoding="utf-8")
    sections = extract_sections(paper)
    errors: list[str] = []
    warnings: list[str] = []
    section_results: list[dict[str, Any]] = []

    for heading, rule in SECTION_RULES.items():
        text = sections.get(heading)
        if text is None:
            errors.append(f"missing required checked section: {heading}")
            section_results.append({"heading": heading, "present": False})
            continue
        wc = word_count(text)
        missing_families = [family for family in rule["required_families"] if not family_present(text, family)]
        if wc < rule["min_words"] or wc > rule["max_words"]:
            errors.append(f"{heading} word count {wc} outside expected range {rule['min_words']}-{rule['max_words']}")
        if missing_families:
            errors.append(f"{heading} missing caveat families: {missing_families}")
        section_results.append({
            "heading": heading,
            "present": True,
            "line": line_for(paper, heading),
            "word_count": wc,
            "min_words": rule["min_words"],
            "max_words": rule["max_words"],
            "required_families": rule["required_families"],
            "missing_families": missing_families,
        })

    forbidden_hits = []
    for token in FORBIDDEN_TOKENS:
        if token.lower() in paper.lower():
            forbidden_hits.append({"token": token, "line": line_for(paper.lower(), token.lower())})
    if forbidden_hits:
        errors.append(f"paper contains forbidden/overclaiming tokens: {forbidden_hits}")

    # Warn if checked sections are too sparse on caveat diversity overall, even
    # when each configured section passes its family-specific checks.
    all_required_families = sorted({family for rule in SECTION_RULES.values() for family in rule["required_families"]})
    missing_global_families = [family for family in all_required_families if not family_present(paper, family)]
    if missing_global_families:
        warnings.append(f"paper missing global caveat family coverage: {missing_global_families}")

    return {
        "schema": "urn:tyche:cassandra:paper-subsection-risk-coverage-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "paper": str(paper_path.relative_to(workspace)),
        "paper_sha256": sha256_path(paper_path),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "checked_section_count": len(SECTION_RULES),
        "section_results": section_results,
        "forbidden_hits": forbidden_hits,
        "global_caveat_families": all_required_families,
        "research_caveat": RESEARCH_CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/paper-subsection-risk-coverage-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
