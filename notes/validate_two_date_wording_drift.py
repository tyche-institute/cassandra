#!/usr/bin/env python3
"""Review two-date aggregate prose and figure wording for interpretation drift.

This is a local wording and reproducibility check only. It does not assert legal
compliance, trusted-list legal effect, supervision, signature validation, public
alerting, regulated trust-service output, or publication readiness.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import xml.etree.ElementTree as ET
from hashlib import sha256
from typing import Any

FIGURE_PATHS = [
    pathlib.Path("figures/aggregate-run-telemetry.svg"),
    pathlib.Path("figures/aggregate-diff-classes.svg"),
]
PAPER_PATH = pathlib.Path("paper/draft.md")
LATEST_AGGREGATE_RE = re.compile(r"aggregate-results-(\d{4}-\d{2}-\d{2})-output\.json$")

# Phrases that would make two rows sound like legal/status/market evidence.
FORBIDDEN_DRIFT_PATTERNS = [
    ("ecosystem_stability_claim", re.compile(r"\b(?:shows?|proves?|demonstrates?|confirms?)\b.{0,80}\b(?:ecosystem|market|trusted-list|country|provider|service)\s+stabil", re.IGNORECASE | re.DOTALL)),
    ("legal_status_claim", re.compile(r"\b(?:shows?|proves?|demonstrates?|confirms?|means)\b.{0,80}\blegal\s+status\b", re.IGNORECASE | re.DOTALL)),
    ("supervisory_claim", re.compile(r"\b(?:supervisory significance|authority performance|provider status|service quality)\b", re.IGNORECASE)),
    ("public_alert_claim", re.compile(r"\bpublic\s+alert(?:s|ing)?\b(?![^.]{0,90}\bnot\b)", re.IGNORECASE)),
    ("publication_ready_claim", re.compile(r"\bpublication[- ]ready\b|\bready\s+for\s+publication\b", re.IGNORECASE)),
    ("named_entity_example_pressure", re.compile(r"\bnamed\s+(?:provider|service|authority|scheme|country)\s+example\b(?![^.]{0,120}\boperator\b)", re.IGNORECASE)),
]

REQUIRED_PAPER_FRAGMENTS = [
    "two dated rows",
    "2026-05-20",
    "2026-05-21",
    "does not support trend or status conclusions",
    "zero aggregate structural diff entries",
    "not enough to characterize churn rate",
    "clean validation output is not publication approval",
]
REQUIRED_FIGURE_CAVEATS = [
    "not trusted-list validation",
    "not legal-status determination",
    "not supervision",
    "not signature validation",
    "not public alerting",
    "not publication approval",
    "Listed names are intentionally absent",
]


def sha256_path(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def latest_aggregate_path(workspace: pathlib.Path) -> pathlib.Path | None:
    candidates = []
    for path in (workspace / "notes").glob("aggregate-results-????-??-??-output.json"):
        match = LATEST_AGGREGATE_RE.search(path.name)
        if match:
            candidates.append((match.group(1), path))
    if not candidates:
        return None
    return sorted(candidates)[-1][1].relative_to(workspace)


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"(^##\s+{re.escape(heading)}\s*$)(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(0) if match else ""


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def snippet(text: str, start: int, end: int, width: int = 120) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return " ".join(text[left:right].split())


def svg_text_and_metadata(path: pathlib.Path) -> tuple[str, dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    root = ET.fromstring(raw)
    combined = " ".join("".join(node.itertext()) for node in root.iter())
    metadata: dict[str, Any] = {}
    meta_match = re.search(r"<metadata[^>]*>(.*?)</metadata>", raw, re.DOTALL)
    if meta_match:
        try:
            metadata = json.loads(html.unescape(meta_match.group(1)))
        except json.JSONDecodeError:
            metadata = {"parse_error": True}
    return combined + " " + raw, metadata


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    findings: list[dict[str, Any]] = []

    paper_path = workspace / PAPER_PATH
    paper = paper_path.read_text(encoding="utf-8")
    latest_rel = latest_aggregate_path(workspace)
    aggregate: dict[str, Any] | None = None
    if latest_rel is None:
        errors.append("no dated aggregate-results output found")
        dates: list[str] = []
    else:
        aggregate = json.loads((workspace / latest_rel).read_text(encoding="utf-8"))
        dates = aggregate.get("dates", [])
        if len(dates) != 2:
            errors.append(f"expected exactly two aggregate dates for this validator, got {dates}")
        if aggregate.get("row_count") != len(dates):
            errors.append(f"aggregate row_count/date mismatch: {aggregate.get('row_count')} vs {dates}")
        if aggregate.get("totals", {}).get("diff_change_count") != 0:
            warnings.append("latest aggregate diff_change_count is nonzero; review wording manually for nonzero-diff framing")

    target_sections = {
        "Aggregate telemetry table interpretation": section(paper, "Aggregate telemetry table interpretation"),
        "Two-date aggregate-validation gate": section(paper, "Two-date aggregate-validation gate"),
        "Figure reproducibility cross-references": section(paper, "Figure reproducibility cross-references"),
    }
    missing_sections = [name for name, body in target_sections.items() if not body]
    if missing_sections:
        errors.append(f"missing target paper sections: {missing_sections}")
    review_text = "\n".join(target_sections.values())

    for fragment in REQUIRED_PAPER_FRAGMENTS:
        if fragment not in review_text:
            errors.append(f"two-date paper prose lacks required fragment: {fragment}")
    if latest_rel and str(latest_rel) not in review_text:
        errors.append(f"two-date prose does not reference latest aggregate output {latest_rel}")
    for date in dates:
        if date not in review_text:
            errors.append(f"two-date prose does not reference aggregate date {date}")

    for name, pattern in FORBIDDEN_DRIFT_PATTERNS:
        for match in pattern.finditer(review_text):
            # Allow explicitly negated/caveated status terms that are already part of the guard language.
            local = review_text[max(0, match.start() - 180): min(len(review_text), match.end() + 160)].lower()
            if any(token in local for token in ["not enough", "should not", "does not", "not publication", "operator-review"]):
                continue
            findings.append({
                "category": name,
                "line": line_number(paper, paper.find(match.group(0))) if match.group(0) in paper else None,
                "snippet": snippet(review_text, match.start(), match.end()),
            })
    if findings:
        errors.append(f"possible two-date wording drift findings: {len(findings)}")

    figure_results: list[dict[str, Any]] = []
    for rel in FIGURE_PATHS:
        path = workspace / rel
        if not path.exists():
            errors.append(f"missing figure {rel}")
            continue
        text, metadata = svg_text_and_metadata(path)
        missing_caveats = [fragment for fragment in REQUIRED_FIGURE_CAVEATS if fragment not in text]
        if missing_caveats:
            errors.append(f"figure {rel} lacks caveat fragments: {missing_caveats}")
        meta_dates = metadata.get("dates", []) if isinstance(metadata, dict) else []
        if dates and meta_dates != dates:
            errors.append(f"figure {rel} metadata dates {meta_dates} do not match aggregate dates {dates}")
        figure_results.append({
            "path": str(rel),
            "sha256": sha256_path(path),
            "metadata_dates": meta_dates,
            "missing_caveats": missing_caveats,
        })

    return {
        "schema": "urn:tyche:cassandra:two-date-wording-drift-validation:0.1",
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
        "paper": str(PAPER_PATH),
        "paper_sha256": sha256_path(paper_path),
        "reviewed_sections": list(target_sections),
        "aggregate_results": {
            "path": str(latest_rel) if latest_rel else None,
            "sha256": sha256_path(workspace / latest_rel) if latest_rel else None,
            "dates": dates,
            "row_count": aggregate.get("row_count") if aggregate else None,
            "diff_change_count_total": aggregate.get("totals", {}).get("diff_change_count") if aggregate else None,
        },
        "figures": figure_results,
        "research_caveat": "Local two-date wording drift review only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/two-date-wording-drift-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
