#!/usr/bin/env python3
"""Report status-only release-readiness gates and cycle-avoidance reasons.

This helper is intentionally non-mutating except for its requested output file.
It explains why selected release-readiness validators are recorded without
sha256 fields in the checklist: hashing them there would create recurring
checklist/reference/freshness churn. The report is operator-review workflow
telemetry only. It does not clear warnings, approve publication, perform legal
review, validate trusted-list signatures, supervise trusted lists, determine
listed-entity status, provide public alerting, or create regulated trust-service
output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

STATUS_ONLY_REASONS = {
    "release_gate_summary_freshness": {
        "expected_path": "notes/release-gate-summary-freshness-validation-output.json",
        "reason": "This validator reads the release-readiness gate summary, which embeds hashes of upstream checklist/warning/policy outputs. Recording its own sha256 in the checklist would induce recurring checklist/summary/freshness hash churn.",
        "policy": "status_only_to_avoid_release_checklist_gate_summary_hash_cycle",
    },
    "hash_cycle_policy_references": {
        "expected_path": "notes/hash-cycle-policy-reference-validation-output.json",
        "reason": "This validator reads paper and checklist-validator wiring for the hash-cycle policy report. Hashing it inside the checklist would create needless checklist/reference/policy hash churn while adding no new provenance authority.",
        "policy": "status_only_to_avoid_release_checklist_reference_hash_cycle",
    },
    "status_only_release_gates_report": {
        "expected_path": "notes/status-only-release-gates-report-output.json",
        "reason": "This report reads the release-readiness checklist it summarizes. Hashing the report inside that checklist would create recurring checklist/report hash churn while adding no new provenance authority beyond the report's own operator trace hashes.",
        "policy": "status_only_to_avoid_release_checklist_report_hash_cycle",
    },
}
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
    return json.loads(path.read_text(encoding="utf-8"))


def caveat_errors(label: str, caveat: str | None) -> list[str]:
    if not caveat:
        return [f"{label} lacks research_caveat"]
    lower = caveat.lower()
    return [f"{label} caveat lacks required fragment: {fragment}" for fragment in REQUIRED_CAVEAT_FRAGMENTS if fragment not in lower]


def report(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checklist_path = workspace / "notes" / "release-readiness-checklist-validation-output.json"
    checklist = load_json(checklist_path)
    validators = {record.get("name"): record for record in checklist.get("validators", [])}

    if checklist.get("status") != "ok":
        errors.append(f"release-readiness checklist status is not ok: {checklist.get('status')}")
    if checklist.get("error_count") not in (0, None):
        errors.append(f"release-readiness checklist error_count is nonzero: {checklist.get('error_count')}")
    errors.extend(caveat_errors("release_readiness_checklist", checklist.get("research_caveat")))

    status_only_records: list[dict[str, Any]] = []
    for name, config in STATUS_ONLY_REASONS.items():
        record = validators.get(name)
        if not record:
            errors.append(f"missing status-only validator record: {name}")
            continue
        expected_path = config["expected_path"]
        if record.get("path") != expected_path:
            errors.append(f"{name} path mismatch: {record.get('path')} != {expected_path}")
        if "sha256" in record:
            errors.append(f"{name} unexpectedly records sha256 in checklist")
        hash_policy = str(record.get("hash_policy", ""))
        if "status_only" not in hash_policy or "cycle" not in hash_policy:
            errors.append(f"{name} lacks explicit status-only cycle hash_policy")
        validator_path = workspace / expected_path
        if not validator_path.exists():
            errors.append(f"missing status-only validator output: {expected_path}")
            current_sha = None
            output_status = None
            output_warning_count = None
            output_error_count = None
        else:
            current_sha = sha256_path(validator_path)
            data = load_json(validator_path)
            output_status = data.get("status")
            output_warning_count = data.get("warning_count")
            output_error_count = data.get("error_count")
            if output_status != "ok":
                errors.append(f"{name} output status is not ok: {output_status}")
            if output_error_count not in (0, None):
                errors.append(f"{name} output error_count is nonzero: {output_error_count}")
            # Upstream status-only validators predate this report and do not all
            # use identical caveat wording. This report preserves their caveats
            # as operator-review context instead of rewriting or failing them.
            if not data.get("research_caveat"):
                warnings.append(f"{name} lacks research_caveat; preserve as manual-review context")
            if isinstance(output_warning_count, int) and output_warning_count > 0:
                warnings.append(f"{name} has warning_count={output_warning_count}; preserve as manual-review context")
        status_only_records.append(
            {
                "name": name,
                "path": expected_path,
                "checklist_status": record.get("status"),
                "checklist_warning_count": record.get("warning_count"),
                "checklist_hash_policy": record.get("hash_policy"),
                "current_output_sha256_for_operator_trace_only": current_sha,
                "output_status": output_status,
                "output_error_count": output_error_count,
                "output_warning_count": output_warning_count,
                "cycle_avoidance_reason": config["reason"],
                "expected_policy": config["policy"],
                "not_missing_provenance": True,
                "safe_to_add_checklist_sha256": False,
            }
        )

    non_status_only_with_hash = 0
    for name, record in validators.items():
        if name not in STATUS_ONLY_REASONS and record.get("exists") is True and "sha256" in record:
            non_status_only_with_hash += 1
    expected_non_status_only = max(0, len(validators) - len(STATUS_ONLY_REASONS))
    if non_status_only_with_hash != expected_non_status_only:
        errors.append(f"non-status-only hash coverage mismatch: {non_status_only_with_hash} != {expected_non_status_only}")

    return {
        "schema": "urn:tyche:cassandra:status-only-release-gates-report:0.2",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "source_checklist": {
            "path": str(checklist_path.relative_to(workspace)),
            "sha256": sha256_path(checklist_path),
            "status": checklist.get("status"),
            "validator_count": checklist.get("validator_count"),
            "warning_count": checklist.get("warning_count"),
        },
        "status_only_gate_count": len(status_only_records),
        "status_only_gates": status_only_records,
        "non_status_only_validator_hash_count": non_status_only_with_hash,
        "safe_to_auto_clear_warnings": False,
        "safe_to_auto_publish": False,
        "operator_review_context": True,
        "research_caveat": "Local status-only release-readiness gate report only; it is not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/status-only-release-gates-report-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = report(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
