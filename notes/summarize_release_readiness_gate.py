#!/usr/bin/env python3
"""Summarize Cassandra's local release-readiness gate for operator review.

This helper is intentionally non-mutating except for its own requested output
file. It does not clear warnings, approve publication, perform legal review,
validate trusted-list signatures, supervise trusted lists, determine listed-
entity status, provide public alerting, or create regulated trust-service
output.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

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


def load_json(workspace: pathlib.Path, rel: str) -> tuple[pathlib.Path, dict[str, Any]]:
    path = workspace / rel
    with path.open("r", encoding="utf-8") as fh:
        return path, json.load(fh)


def caveat_errors(label: str, caveat: str | None) -> list[str]:
    if not caveat:
        return [f"{label} lacks research_caveat"]
    lower = caveat.lower()
    missing = [fragment for fragment in REQUIRED_CAVEAT_FRAGMENTS if fragment not in lower]
    return [f"{label} caveat lacks required fragment: {fragment}" for fragment in missing]


def summarize(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checklist_path, checklist = load_json(workspace, "notes/release-readiness-checklist-validation-output.json")
    warning_path, warning_report = load_json(workspace, "notes/release-readiness-warning-report-output.json")
    policy_path, policy = load_json(workspace, "notes/release-readiness-persistent-warning-policy-validation-output.json")
    out_of_band_policy_path, out_of_band_policy = load_json(workspace, "notes/status-only-report-reference-checker-policy-validation-output.json")
    topology_policy_path, topology_policy = load_json(workspace, "notes/topology-report-reference-freshness-policy-validation-output.json")
    context_policy_path, context_policy = load_json(workspace, "notes/release-readiness-context-consistency-policy-validation-output.json")

    sources = {
        "release_readiness_checklist": {
            "path": str(checklist_path.relative_to(workspace)),
            "sha256": sha256_path(checklist_path),
            "status": checklist.get("status"),
            "error_count": checklist.get("error_count"),
            "warning_count": checklist.get("warning_count"),
        },
        "warning_report": {
            "path": str(warning_path.relative_to(workspace)),
            "sha256": sha256_path(warning_path),
            "status": warning_report.get("status"),
            "error_count": warning_report.get("error_count"),
            "warning_count": warning_report.get("warning_count"),
        },
        "persistent_warning_policy": {
            "path": str(policy_path.relative_to(workspace)),
            "sha256": sha256_path(policy_path),
            "status": policy.get("status"),
            "error_count": policy.get("error_count"),
            "warning_count": policy.get("warning_count"),
        },
        "out_of_band_status_only_report_reference_checker_policy": {
            "path": str(out_of_band_policy_path.relative_to(workspace)),
            "sha256": sha256_path(out_of_band_policy_path),
            "status": out_of_band_policy.get("status"),
            "error_count": out_of_band_policy.get("error_count"),
            "warning_count": out_of_band_policy.get("warning_count"),
            "checker_kept_out_of_band": out_of_band_policy.get("decision", {}).get("checker_kept_out_of_band"),
            "safe_to_wire_into_checklist_without_operator_review": out_of_band_policy.get("decision", {}).get("safe_to_wire_into_checklist_without_operator_review"),
        },
        "out_of_band_topology_report_reference_freshness_policy": {
            "path": str(topology_policy_path.relative_to(workspace)),
            "sha256": sha256_path(topology_policy_path),
            "status": topology_policy.get("status"),
            "error_count": topology_policy.get("error_count"),
            "warning_count": topology_policy.get("warning_count"),
            "checker_kept_out_of_band": topology_policy.get("decision", {}).get("checker_kept_out_of_band"),
            "safe_to_wire_into_checklist_without_operator_review": topology_policy.get("decision", {}).get("safe_to_wire_into_checklist_without_operator_review"),
        },
        "out_of_band_release_readiness_context_consistency_policy": {
            "path": str(context_policy_path.relative_to(workspace)),
            "sha256": sha256_path(context_policy_path),
            "status": context_policy.get("status"),
            "error_count": context_policy.get("error_count"),
            "warning_count": context_policy.get("warning_count"),
            "checker_kept_out_of_band": context_policy.get("decision", {}).get("checker_kept_out_of_band"),
            "safe_to_wire_into_checklist_without_operator_review": context_policy.get("decision", {}).get("safe_to_wire_into_checklist_without_operator_review"),
            "safe_to_wire_into_topology_without_operator_review": context_policy.get("decision", {}).get("safe_to_wire_into_topology_without_operator_review"),
        },
    }

    for label, data in [
        ("release_readiness_checklist", checklist),
        ("warning_report", warning_report),
        ("persistent_warning_policy", policy),
    ]:
        if data.get("status") != "ok":
            if label == "release_readiness_checklist":
                # The checklist includes a status-only freshness record for this
                # gate summary; during a bounded refresh the checklist may be
                # stale until this summary and its freshness output are rewritten.
                warnings.append(f"{label} status is refresh-order context: {data.get('status')}")
            else:
                errors.append(f"{label} status is not ok: {data.get('status')}")
        if isinstance(data.get("error_count"), int) and data.get("error_count") != 0:
            if label == "release_readiness_checklist":
                warnings.append(f"{label} error_count is refresh-order context: {data.get('error_count')}")
            else:
                errors.append(f"{label} error_count is nonzero: {data.get('error_count')}")
        errors.extend(caveat_errors(label, data.get("research_caveat")))

    for label, out_of_band_data in [
        ("out_of_band_status_only_report_reference_checker_policy", out_of_band_policy),
        ("out_of_band_topology_report_reference_freshness_policy", topology_policy),
        ("out_of_band_release_readiness_context_consistency_policy", context_policy),
    ]:
        if out_of_band_data.get("status") != "ok":
            errors.append(f"{label} status is not ok: {out_of_band_data.get('status')}")
        if isinstance(out_of_band_data.get("error_count"), int) and out_of_band_data.get("error_count") != 0:
            errors.append(f"{label} error_count is nonzero: {out_of_band_data.get('error_count')}")
        out_of_band_caveat = str(out_of_band_data.get("research_caveat", "")).lower()
        for fragment in ["does not clear warnings", "approve publication", "legal review", "trusted-list legal effect", "regulated trust-service output"]:
            if fragment not in out_of_band_caveat:
                errors.append(f"{label} caveat lacks required fragment: {fragment}")

    validators = checklist.get("validators", [])
    if checklist.get("validator_count") != len(validators):
        errors.append("checklist validator_count does not match validators length")
    validator_status_counts: dict[str, int] = {}
    warning_validator_names: list[str] = []
    for record in validators:
        status = str(record.get("status"))
        validator_status_counts[status] = validator_status_counts.get(status, 0) + 1
        warning_count = record.get("warning_count")
        if isinstance(warning_count, int) and warning_count > 0:
            warning_validator_names.append(str(record.get("name")))
    if validator_status_counts.get("ok", 0) != len(validators):
        warnings.append(f"not all checklist validators report ok during refresh-order check: {validator_status_counts}")

    aggregate_warning_classes = warning_report.get("aggregate_warning_class_counts", {})
    policy_classes = set(policy.get("warning_classes", []))
    report_classes = set(aggregate_warning_classes.keys())
    if policy_classes != report_classes:
        errors.append("persistent-warning policy classes do not match warning-report classes")
    if warning_report.get("safe_to_auto_clear_warnings") is not False:
        errors.append("warning report does not explicitly refuse automatic warning clearing")
    if warning_report.get("safe_to_auto_publish") is not False:
        errors.append("warning report does not explicitly refuse automatic publication")

    out_of_band_decisions = [
        ("status-only report reference checker", out_of_band_policy.get("decision", {}), str(out_of_band_policy_path.relative_to(workspace))),
        ("topology-report reference freshness", topology_policy.get("decision", {}), str(topology_policy_path.relative_to(workspace))),
        ("release-readiness context consistency", context_policy.get("decision", {}), str(context_policy_path.relative_to(workspace))),
    ]
    for label, out_of_band_decision, _path in out_of_band_decisions:
        if out_of_band_decision.get("checker_kept_out_of_band") is not True:
            errors.append(f"out-of-band {label} policy does not preserve checker_kept_out_of_band=true")
        if out_of_band_decision.get("safe_to_wire_into_checklist_without_operator_review") is not False:
            errors.append(f"out-of-band {label} policy does not refuse checklist wiring without operator review")
        if label == "release-readiness context consistency" and out_of_band_decision.get("safe_to_wire_into_topology_without_operator_review") is not False:
            errors.append("out-of-band release-readiness context consistency policy does not refuse topology wiring without operator review")

    return {
        "schema": "urn:tyche:cassandra:release-readiness-gate-summary:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "sources": sources,
        "validator_count": checklist.get("validator_count"),
        "validator_status_counts": validator_status_counts,
        "warning_validator_count": warning_report.get("warning_validator_count"),
        "warning_validator_names": warning_validator_names,
        "release_warning_count": warning_report.get("release_warning_count"),
        "aggregate_warning_class_counts": aggregate_warning_classes,
        "persistent_warning_class_count": policy.get("warning_class_count"),
        "persistent_warning_classes": sorted(policy_classes),
        "out_of_band_policy_checks": [
            {
                "name": name,
                "path": path,
                "status": data.get("status"),
                "warning_count": data.get("warning_count"),
                "checker_kept_out_of_band": decision.get("checker_kept_out_of_band"),
                "safe_to_wire_into_checklist_without_operator_review": decision.get("safe_to_wire_into_checklist_without_operator_review"),
                "safe_to_wire_into_topology_without_operator_review": decision.get("safe_to_wire_into_topology_without_operator_review"),
                "cycle_avoidance_reason": decision.get("cycle_avoidance_reason"),
            }
            for name, data, decision, path in [
                ("status_only_report_reference_checker_policy", out_of_band_policy, out_of_band_policy.get("decision", {}), str(out_of_band_policy_path.relative_to(workspace))),
                ("topology_report_reference_freshness_policy", topology_policy, topology_policy.get("decision", {}), str(topology_policy_path.relative_to(workspace))),
                ("release_readiness_context_consistency_policy", context_policy, context_policy.get("decision", {}), str(context_policy_path.relative_to(workspace))),
            ]
        ],
        "safe_to_auto_clear_warnings": False,
        "safe_to_auto_publish": False,
        "operator_review_gate": True,
        "research_caveat": "Local release-readiness gate summary only; it is not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/release-readiness-gate-summary-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = summarize(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
