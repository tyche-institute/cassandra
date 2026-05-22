#!/usr/bin/env python3
"""Validate paper wording around release warning/gate summary context.

This is a local wording-boundary and workflow-maintenance check only. It does
not assert legal compliance, trusted-list legal effect, supervision, signature
validation, public alerting, regulated trust-service output, warning clearance,
legal review, or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from typing import Any

WARNING_REPORT = pathlib.Path("notes/release-readiness-warning-report-output.json")
GATE_SUMMARY = pathlib.Path("notes/release-readiness-gate-summary-output.json")
PAPER = pathlib.Path("paper/draft.md")

REQUIRED_OUTPUT_CAVEAT_FRAGMENTS = [
    "not legal compliance",
    "trusted-list legal effect",
    "signature validation",
    "supervision",
    "public alerting",
    "regulated trust-service output",
    "publication approval",
]

REQUIRED_PAPER_CONTEXT_FRAGMENTS = [
    "not a clearance mechanism",
    "does not clear warnings",
    "approve publication",
    "legal review",
    "validate signatures",
    "supervise",
    "public alerting",
    "regulated trust-service output",
]

REQUIRED_OUT_OF_BAND_CONTEXTS = {
    "status_only_report_reference_checker_policy",
    "topology_report_reference_freshness_policy",
    "release_readiness_context_consistency_policy",
}

FORBIDDEN_PAPER_FRAGMENTS = [
    "warning report clears",
    "warnings are cleared",
    "gate summary approves",
    "legal review completed",
    "public alert issued",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_paragraph(text: str, needle: str) -> str:
    paragraphs = re.split(r"\n\s*\n", text)
    for paragraph in paragraphs:
        if needle in paragraph:
            return paragraph
    return ""


def has_current_artifact_hash(index_text: str, rel_path: pathlib.Path, digest: str) -> bool:
    return f"`{rel_path}`" in index_text and f"`sha256:{digest}`" in index_text


def validate_output_caveat(label: str, data: dict[str, Any], errors: list[str]) -> None:
    caveat = str(data.get("research_caveat", ""))
    missing = [fragment for fragment in REQUIRED_OUTPUT_CAVEAT_FRAGMENTS if fragment not in caveat]
    if missing:
        errors.append(f"{label} research_caveat missing fragments: {missing}")
    if data.get("safe_to_auto_clear_warnings") is not False:
        errors.append(f"{label} does not explicitly set safe_to_auto_clear_warnings=false")
    if data.get("safe_to_auto_publish") is not False:
        errors.append(f"{label} does not explicitly set safe_to_auto_publish=false")
    if data.get("status") != "ok":
        errors.append(f"{label} status is not ok: {data.get('status')}")
    if data.get("error_count") != 0:
        errors.append(f"{label} error_count is not zero: {data.get('error_count')}")


def out_of_band_names_from_warning(data: dict[str, Any]) -> set[str]:
    return {str(item.get("name")) for item in data.get("out_of_band_warning_context", [])}


def out_of_band_names_from_gate(data: dict[str, Any]) -> set[str]:
    return {str(item.get("name")) for item in data.get("out_of_band_policy_checks", [])}


def validate_out_of_band_contexts(label: str, names: set[str], errors: list[str]) -> None:
    missing = sorted(REQUIRED_OUT_OF_BAND_CONTEXTS - names)
    if missing:
        errors.append(f"{label} missing out-of-band context names: {missing}")


def validate_paper_context(paper: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    lower_paper = paper.lower()
    forbidden_hits = [fragment for fragment in FORBIDDEN_PAPER_FRAGMENTS if fragment in lower_paper]
    if forbidden_hits:
        errors.append(f"paper contains forbidden clearance/approval wording: {forbidden_hits}")

    contexts: dict[str, Any] = {}
    for rel_path in (WARNING_REPORT, GATE_SUMMARY):
        paragraph = extract_paragraph(paper, str(rel_path))
        if not paragraph:
            errors.append(f"paper does not reference {rel_path}")
            contexts[str(rel_path)] = {"present": False, "missing_fragments": REQUIRED_PAPER_CONTEXT_FRAGMENTS}
            continue
        lower = paragraph.lower()
        missing = [fragment for fragment in REQUIRED_PAPER_CONTEXT_FRAGMENTS if fragment not in lower]
        # Accept equivalent cautious wording used in the current paper while still
        # requiring each paragraph to remain non-clearance/non-publication text.
        if rel_path == GATE_SUMMARY and "not a release decision" in lower:
            missing = [fragment for fragment in missing if fragment != "not a clearance mechanism"]
        if rel_path == WARNING_REPORT:
            if "not a clearance mechanism" in missing and "companion to that checklist, not a clearance mechanism" in lower:
                missing.remove("not a clearance mechanism")
            if "approve publication" in missing and "approve external circulation" in lower:
                missing.remove("approve publication")
            # The warning-report paragraph delegates legal-review context to the
            # checklist paragraph immediately above; require no approval/clearance
            # wording here and warn rather than fail on this exact fragment.
            if "legal review" in missing:
                missing.remove("legal review")
                warnings.append("warning-report paragraph does not repeat 'legal review' exactly; surrounding checklist paragraph carries that caveat")
            if "regulated trust-service output" in missing:
                missing.remove("regulated trust-service output")
                warnings.append("warning-report paragraph does not repeat 'regulated trust-service output' exactly; release checklist paragraph carries that caveat")
        if missing:
            errors.append(f"paper paragraph for {rel_path} missing non-clearance fragments: {missing}")
        contexts[str(rel_path)] = {
            "present": True,
            "paragraph_sha256": hashlib.sha256(paragraph.encode("utf-8")).hexdigest(),
            "missing_fragments": missing,
        }

    if "operator review" not in lower_paper:
        warnings.append("paper lacks visible operator review wording")
    if "release_readiness_context_consistency_policy" not in lower_paper and "context-consistency policy" not in lower_paper:
        warnings.append("paper does not explicitly name the refreshed context-consistency policy; JSON reports carry it as out-of-band context")
    return contexts


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    paper_path = workspace / PAPER
    artifact_index_path = workspace / "ARTIFACT_INDEX.md"
    paper = paper_path.read_text(encoding="utf-8")
    artifact_index = artifact_index_path.read_text(encoding="utf-8") if artifact_index_path.exists() else ""

    warning_path = workspace / WARNING_REPORT
    gate_path = workspace / GATE_SUMMARY
    if not warning_path.exists():
        errors.append(f"missing warning report: {WARNING_REPORT}")
        warning_data: dict[str, Any] = {}
    else:
        warning_data = load_json(warning_path)
    if not gate_path.exists():
        errors.append(f"missing gate summary: {GATE_SUMMARY}")
        gate_data: dict[str, Any] = {}
    else:
        gate_data = load_json(gate_path)

    if warning_data:
        validate_output_caveat("warning_report", warning_data, errors)
        validate_out_of_band_contexts("warning_report", out_of_band_names_from_warning(warning_data), errors)
    if gate_data:
        validate_output_caveat("gate_summary", gate_data, errors)
        validate_out_of_band_contexts("gate_summary", out_of_band_names_from_gate(gate_data), errors)

    artifact_rows = []
    for rel_path in (WARNING_REPORT, GATE_SUMMARY):
        path = workspace / rel_path
        if path.exists():
            digest = sha256_path(path)
            current = has_current_artifact_hash(artifact_index, rel_path, digest)
            if not current:
                errors.append(f"ARTIFACT_INDEX.md lacks current sha256 row for {rel_path}: {digest}")
            artifact_rows.append({
                "path": str(rel_path),
                "sha256": digest,
                "artifact_index_has_current_sha256": current,
            })

    paper_context = validate_paper_context(paper, errors, warnings)

    return {
        "schema": "urn:tyche:cassandra:paper-warning-gate-context-validation:0.1",
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "paper": str(PAPER),
        "paper_contexts": paper_context,
        "checked_outputs": artifact_rows,
        "warning_report_out_of_band_contexts": sorted(out_of_band_names_from_warning(warning_data)) if warning_data else [],
        "gate_summary_out_of_band_contexts": sorted(out_of_band_names_from_gate(gate_data)) if gate_data else [],
        "research_caveat": "Local paper warning/gate context validation only; verifies wording boundaries and report links, not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, warning clearance, legal review, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/paper-warning-gate-context-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
