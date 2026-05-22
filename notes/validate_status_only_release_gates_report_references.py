#!/usr/bin/env python3
"""Validate status-only release gate report references and freshness.

This checker is local workflow-maintenance telemetry. It verifies that the
status-only release gate report stays referenced by the paper operator-review
checklist and release-readiness checklist validator, and that the report embeds
the current release-readiness checklist hash. It avoids adding a new cyclic
checklist/report/checker hash dependency. It does not clear warnings, approve
publication, perform legal review, validate trusted-list signatures, supervise
trusted lists, determine listed-entity status, provide public alerting, or create
regulated trust-service output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

PAPER_REL = pathlib.Path("paper/draft.md")
CHECKLIST_VALIDATOR_REL = pathlib.Path("notes/validate_release_readiness_checklist.py")
CHECKLIST_OUTPUT_REL = pathlib.Path("notes/release-readiness-checklist-validation-output.json")
STATUS_REPORT_REL = pathlib.Path("notes/status-only-release-gates-report-output.json")
CHECKLIST_HEADING = "## Release-readiness checklist for operator review"

PAPER_REQUIRED_FRAGMENTS = [
    "status-only release gate report",
    "notes/status-only-release-gates-report-output.json",
    "warning clearance",
    "legal review",
    "publication approval",
    "signature validation",
    "trusted-list supervision",
    "listed-entity status evidence",
    "public alerting",
    "regulated trust-service output",
]

VALIDATOR_REQUIRED_FRAGMENTS = [
    "status_only_release_gates_report",
    "notes/status-only-release-gates-report-output.json",
    "status-only release gate report",
]

REQUIRED_CAVEAT_FRAGMENTS = [
    "not legal compliance",
    "trusted-list legal effect",
    "signature validation",
    "supervision",
    "public alerting",
    "regulated trust-service output",
    "publication approval",
]


def sha256_path(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^{re.escape(heading)}\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(0) if match else ""


def status_from_json(data: dict[str, Any]) -> str | None:
    if isinstance(data.get("status"), str):
        return data["status"]
    if isinstance(data.get("result"), dict) and isinstance(data["result"].get("status"), str):
        return data["result"]["status"]
    return None


def caveat_errors(label: str, caveat: str | None) -> list[str]:
    if not caveat:
        return [f"{label} lacks research_caveat"]
    lower = caveat.lower()
    return [f"{label} caveat lacks required fragment: {fragment}" for fragment in REQUIRED_CAVEAT_FRAGMENTS if fragment not in lower]


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    paper_path = workspace / PAPER_REL
    validator_path = workspace / CHECKLIST_VALIDATOR_REL
    checklist_path = workspace / CHECKLIST_OUTPUT_REL
    report_path = workspace / STATUS_REPORT_REL

    for rel, path in [
        (PAPER_REL, paper_path),
        (CHECKLIST_VALIDATOR_REL, validator_path),
        (CHECKLIST_OUTPUT_REL, checklist_path),
        (STATUS_REPORT_REL, report_path),
    ]:
        if not path.exists():
            errors.append(f"missing required input: {rel}")

    paper_text = paper_path.read_text(encoding="utf-8") if paper_path.exists() else ""
    validator_text = validator_path.read_text(encoding="utf-8") if validator_path.exists() else ""
    checklist_section = section(paper_text, CHECKLIST_HEADING)
    if not checklist_section:
        errors.append("paper lacks release-readiness checklist section")
    for fragment in PAPER_REQUIRED_FRAGMENTS:
        if fragment not in checklist_section:
            errors.append(f"paper checklist lacks status-only report fragment: {fragment}")
    for fragment in VALIDATOR_REQUIRED_FRAGMENTS:
        if fragment not in validator_text:
            errors.append(f"release-readiness checklist validator source lacks status-only report fragment: {fragment}")

    checklist: dict[str, Any] = {}
    report: dict[str, Any] = {}
    if checklist_path.exists():
        try:
            checklist = load_json(checklist_path)
        except json.JSONDecodeError as exc:
            errors.append(f"release-readiness checklist output is not JSON: {exc}")
    if report_path.exists():
        try:
            report = load_json(report_path)
        except json.JSONDecodeError as exc:
            errors.append(f"status-only release gate report output is not JSON: {exc}")

    checklist_status = status_from_json(checklist)
    if checklist_status != "ok":
        errors.append(f"release-readiness checklist output status is not ok: {checklist_status}")
    if isinstance(checklist.get("warning_count"), int) and checklist["warning_count"] > 0:
        warnings.append(
            f"release-readiness checklist retains warning_count={checklist['warning_count']} as manual-review context"
        )

    if report.get("schema") != "urn:tyche:cassandra:status-only-release-gates-report:0.2":
        errors.append(f"unexpected status-only report schema: {report.get('schema')}")
    if report.get("status") != "ok":
        errors.append(f"status-only release gate report status is not ok: {report.get('status')}")
    if report.get("error_count") not in (0, None):
        errors.append(f"status-only release gate report error_count is nonzero: {report.get('error_count')}")
    if report.get("safe_to_auto_clear_warnings") is not False:
        errors.append("status-only release gate report does not refuse automatic warning clearing")
    if report.get("safe_to_auto_publish") is not False:
        errors.append("status-only release gate report does not refuse automatic publication")
    if report.get("operator_review_context") is not True:
        errors.append("status-only release gate report does not mark operator_review_context true")
    errors.extend(caveat_errors("status_only_release_gate_report", report.get("research_caveat")))

    source_checklist = report.get("source_checklist") if isinstance(report.get("source_checklist"), dict) else {}
    current_checklist_sha = sha256_path(checklist_path) if checklist_path.exists() else None
    embedded_path = source_checklist.get("path")
    embedded_sha = source_checklist.get("sha256")
    if embedded_path != str(CHECKLIST_OUTPUT_REL):
        errors.append(f"status-only report source_checklist path mismatch: {embedded_path} != {CHECKLIST_OUTPUT_REL}")
    if current_checklist_sha and embedded_sha != current_checklist_sha:
        errors.append(f"status-only report embeds stale checklist hash: {embedded_sha} != {current_checklist_sha}")
    if source_checklist.get("status") != "ok":
        errors.append(f"status-only report source_checklist status is not ok: {source_checklist.get('status')}")
    if source_checklist.get("validator_count") != checklist.get("validator_count"):
        errors.append(
            f"status-only report validator_count mismatch: {source_checklist.get('validator_count')} != {checklist.get('validator_count')}"
        )

    status_gates = report.get("status_only_gates") if isinstance(report.get("status_only_gates"), list) else []
    expected_gate_names = {"release_gate_summary_freshness", "hash_cycle_policy_references", "status_only_release_gates_report"}
    observed_gate_names = {record.get("name") for record in status_gates if isinstance(record, dict)}
    if observed_gate_names != expected_gate_names:
        errors.append(f"status-only gate set mismatch: {sorted(observed_gate_names)} != {sorted(expected_gate_names)}")
    for record in status_gates:
        if not isinstance(record, dict):
            errors.append("status_only_gates contains non-object record")
            continue
        name = record.get("name")
        if record.get("not_missing_provenance") is not True:
            errors.append(f"{name} does not mark not_missing_provenance true")
        if record.get("safe_to_add_checklist_sha256") is not False:
            errors.append(f"{name} does not refuse checklist sha256 insertion")
        if record.get("output_status") != "ok":
            errors.append(f"{name} output_status is not ok: {record.get('output_status')}")
        if not record.get("current_output_sha256_for_operator_trace_only"):
            errors.append(f"{name} lacks current output sha256 for operator trace")

    return {
        "schema": "urn:tyche:cassandra:status-only-release-gates-report-reference-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "inputs": {
            "paper": {"path": str(PAPER_REL), "sha256": sha256_path(paper_path) if paper_path.exists() else None},
            "release_readiness_checklist_validator": {
                "path": str(CHECKLIST_VALIDATOR_REL),
                "sha256": sha256_path(validator_path) if validator_path.exists() else None,
            },
            "release_readiness_checklist_output": {
                "path": str(CHECKLIST_OUTPUT_REL),
                "sha256": current_checklist_sha,
                "status": checklist_status,
                "warning_count": checklist.get("warning_count"),
                "validator_count": checklist.get("validator_count"),
            },
            "status_only_release_gate_report": {
                "path": str(STATUS_REPORT_REL),
                "sha256": sha256_path(report_path) if report_path.exists() else None,
                "status": report.get("status"),
                "embedded_checklist_sha256": embedded_sha,
                "embedded_checklist_matches_current": bool(current_checklist_sha and embedded_sha == current_checklist_sha),
                "status_only_gate_count": report.get("status_only_gate_count"),
            },
        },
        "reference_check": {
            "paper_section": CHECKLIST_HEADING,
            "paper_required_fragment_count": len(PAPER_REQUIRED_FRAGMENTS),
            "validator_required_fragment_count": len(VALIDATOR_REQUIRED_FRAGMENTS),
            "manual_review_only": True,
            "safe_to_clear_warnings": False,
            "safe_to_publish": False,
            "hash_cycle_note": "This checker deliberately remains outside the release-readiness checklist until operator review to avoid adding a new checklist/report/checker hash cycle.",
        },
        "research_caveat": "Local status-only release gate report reference/freshness validation only; it does not clear warnings, approve publication, perform legal review, validate signatures, supervise trusted lists, determine listed-entity status, provide public alerting, or create regulated trust-service output.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/status-only-release-gates-report-reference-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
