#!/usr/bin/env python3
"""Validate Cassandra's local release-readiness checklist.

This is an abstention-oriented local workflow check. It verifies that the paper
contains a compact operator-review checklist and that the currently configured
validation outputs exist and report ok status where applicable. It does not
assert legal compliance, trusted-list legal effect, supervision, signature
validation, public alerting, regulated trust-service output, or publication
readiness.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

CHECKLIST_HEADING = "## Release-readiness checklist for operator review"
VALIDATION_OUTPUTS = [
    ("snapshot_metadata", pathlib.Path("notes/snapshot-metadata-linkage-2026-05-21-output.json")),
    ("lineage", pathlib.Path("notes/lineage-consistency-2026-05-21-output.json")),
    ("aggregate_results", pathlib.Path("notes/aggregate-results-validation-output.json")),
    ("figure_artifacts", pathlib.Path("notes/figure-artifact-validation-output.json")),
    ("public_artifact_safety", pathlib.Path("notes/public-artifact-safety-validation-output.json")),
    ("paper_claim_safety", pathlib.Path("notes/paper-claim-safety-validation-output.json")),
    ("paper_evidence_refs", pathlib.Path("notes/paper-evidence-reference-validation-output.json")),
    ("paper_figure_refs", pathlib.Path("notes/paper-figure-reference-validation-output.json")),
    ("two_date_wording_drift", pathlib.Path("notes/two-date-wording-drift-validation-output.json")),
    ("multiday_readiness", pathlib.Path("notes/multiday-readiness-validation-output.json")),
    ("source_coverage_policy_note", pathlib.Path("notes/source-coverage-policy-note-validation-output.json")),
    ("persistent_warning_policy", pathlib.Path("notes/release-readiness-persistent-warning-policy-validation-output.json")),
    ("release_gate_summary_freshness", pathlib.Path("notes/release-gate-summary-freshness-validation-output.json")),
    ("hash_cycle_policy_references", pathlib.Path("notes/hash-cycle-policy-reference-validation-output.json")),
    ("status_only_release_gates_report", pathlib.Path("notes/status-only-release-gates-report-output.json")),
    ("artifact_index_current_hashes", pathlib.Path("notes/artifact-index-current-hash-validation-output.json")),
]
# These validators read the release-readiness checklist output or validator
# source as upstream context. Hashing their outputs from this validator would
# create needless checklist/summary/reference hash churn. The checklist still
# requires their status to be ok, but records that the relevant hashes are
# deliberately omitted for explicit cycle-avoidance reasons.
STATUS_ONLY_OUTPUTS = {"release_gate_summary_freshness", "hash_cycle_policy_references", "status_only_release_gates_report"}
REQUIRED_SECTION_FRAGMENTS = [
    "snapshot metadata linkage validator",
    "lineage validator",
    "aggregate-results validator",
    "figure-artifact validator",
    "public-artifact safety validator",
    "paper claim-safety validator",
    "paper evidence-reference validator",
    "paper/figure reference validator",
    "two-date wording-drift validator",
    "multi-day readiness validator",
    "source-coverage policy-note validator",
    "persistent-warning policy validator",
    "release gate-summary freshness validator",
    "hash-cycle policy reference validator",
    "notes/hash-cycle-policy-reference-validation-output.json",
    "status-only release gate report",
    "notes/status-only-release-gates-report-output.json",
    "dependency-context status-only gate",
    "ARTIFACT_INDEX current-hash validator",
    "release-readiness warning report",
    "notes/release-readiness-warning-report-output.json",
    "not a clearance mechanism",
    "release-readiness gate summary",
    "notes/release-readiness-gate-summary-output.json",
    "not a release decision",
    "release gate hash-cycle policy report",
    "notes/release-gate-hash-cycle-policy-report-output.json",
    "status-only inside the checklist",
    "not as missing-hash repair",
    "release-readiness topology report",
    "notes/release-readiness-topology-report-output.json",
    "not an additional release gate",
    "Passing the checklist is therefore a gate for manual review, not a substitute for it.",
    "Cassandra outputs remain research-only working artifacts",
]
FORBIDDEN_UNCAVEATED = [
    "publication ready",
    "ready for publication",
    "legal compliance evidence",
    "supervisory findings",
    "endpoint certification",
]


def sha256_path(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    paper_path = workspace / "paper" / "draft.md"
    paper = paper_path.read_text(encoding="utf-8")
    checklist = section(paper, CHECKLIST_HEADING)
    if not checklist:
        errors.append("paper lacks release-readiness checklist section")
    for fragment in REQUIRED_SECTION_FRAGMENTS:
        if fragment not in checklist:
            errors.append(f"checklist section lacks required fragment: {fragment}")
    for phrase in FORBIDDEN_UNCAVEATED:
        for match in re.finditer(re.escape(phrase), checklist, re.IGNORECASE):
            local = checklist[max(0, match.start() - 140): match.end() + 140].lower()
            if not any(token in local for token in ["not ", "should not", "does not", "not a substitute", "not legal"]):
                errors.append(f"uncaveated release-readiness phrase: {phrase}")

    validation_records: list[dict[str, Any]] = []
    ok_statuses = {"ok"}
    for name, rel in VALIDATION_OUTPUTS:
        path = workspace / rel
        record: dict[str, Any] = {"name": name, "path": str(rel), "exists": path.exists()}
        if not path.exists():
            errors.append(f"missing validator output: {rel}")
            validation_records.append(record)
            continue
        if name in STATUS_ONLY_OUTPUTS:
            record["hash_policy"] = "status_only_to_avoid_release_checklist_gate_summary_hash_cycle"
        else:
            record["sha256"] = sha256_path(path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"validator output is not JSON: {rel}: {exc}")
            validation_records.append(record)
            continue
        status = status_from_json(data)
        record["status"] = status
        record["error_count"] = data.get("error_count")
        record["warning_count"] = data.get("warning_count")
        if status not in ok_statuses:
            errors.append(f"validator output status is not ok for {rel}: {status}")
        if isinstance(data.get("warning_count"), int) and data["warning_count"] > 0:
            warnings.append(f"{rel} has warning_count={data['warning_count']}; preserve as manual-review context")
        validation_records.append(record)

    return {
        "schema": "urn:tyche:cassandra:release-readiness-checklist-validation:0.6",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "paper": str(paper_path.relative_to(workspace)),
        "paper_sha256": sha256_path(paper_path),
        "checklist_heading": CHECKLIST_HEADING,
        "validator_count": len(VALIDATION_OUTPUTS),
        "validators": validation_records,
        "research_caveat": "Local release-readiness checklist validation only; clean status is a manual-review gate and not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/release-readiness-checklist-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
