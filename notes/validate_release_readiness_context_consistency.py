#!/usr/bin/env python3
"""Validate release-readiness context-name consistency across local reports.

This non-mutating checker compares the names and counts used by the release-
readiness topology report, warning report, and gate summary for checklist gates,
status-only gates, warning-context validators, and out-of-band policy checks.
It is workflow-maintenance telemetry only: it does not clear warnings, approve
publication, perform legal review, validate trusted-list signatures, supervise
trusted lists, determine listed-entity status, provide public alerting, assert
trusted-list legal effect, or create regulated trust-service output.
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

TOPOLOGY_REL = "notes/release-readiness-topology-report-output.json"
WARNING_REL = "notes/release-readiness-warning-report-output.json"
GATE_REL = "notes/release-readiness-gate-summary-output.json"
STATUS_ONLY_REL = "notes/status-only-release-gates-report-output.json"

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


def load_json(workspace: pathlib.Path, rel: str) -> dict[str, Any]:
    with (workspace / rel).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def source_summary(workspace: pathlib.Path, rel: str, data: dict[str, Any]) -> dict[str, Any]:
    path = workspace / rel
    return {
        "path": rel,
        "sha256": sha256_path(path),
        "status": data.get("status"),
        "error_count": data.get("error_count"),
        "warning_count": data.get("warning_count"),
    }


def caveat_errors(label: str, data: dict[str, Any]) -> list[str]:
    caveat = str(data.get("research_caveat", "")).lower()
    if not caveat:
        return [f"{label} lacks research_caveat"]
    return [
        f"{label} caveat lacks required fragment: {fragment}"
        for fragment in REQUIRED_CAVEAT_FRAGMENTS
        if fragment not in caveat
    ]


def sorted_strings(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []
    return sorted(str(item) for item in items)


def context_names_from_records(records: Any) -> list[str]:
    if not isinstance(records, list):
        return []
    return sorted(str(record.get("name")) for record in records if isinstance(record, dict))


def validate_data(workspace: pathlib.Path, data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    topology = data["topology"]
    warning = data["warning"]
    gate = data["gate"]
    status_only = data["status_only"]

    for label, item in data.items():
        if item.get("status") != "ok":
            errors.append(f"{label} status is not ok: {item.get('status')}")
        if isinstance(item.get("error_count"), int) and item.get("error_count") != 0:
            errors.append(f"{label} error_count is nonzero: {item.get('error_count')}")
        errors.extend(caveat_errors(label, item))
        if isinstance(item.get("warning_count"), int) and item["warning_count"] > 0:
            warnings.append(f"{label} warning_count={item['warning_count']} preserved as manual-review context")

    topo = topology.get("topology", {}) if isinstance(topology.get("topology"), dict) else {}

    topology_out_of_band = sorted_strings(topo.get("out_of_band_check_names"))
    warning_out_of_band = context_names_from_records(warning.get("out_of_band_warning_context"))
    gate_out_of_band = context_names_from_records(gate.get("out_of_band_policy_checks"))
    expected_topology_out_of_band = sorted([
        "status_only_report_reference_checker_policy",
        "topology_report_reference_freshness_policy",
    ])
    expected_report_out_of_band = sorted([
        "release_readiness_context_consistency_policy",
        "status_only_report_reference_checker_policy",
        "topology_report_reference_freshness_policy",
    ])
    for label, names, expected in [
        ("topology out-of-band", topology_out_of_band, expected_topology_out_of_band),
        ("warning out-of-band", warning_out_of_band, expected_report_out_of_band),
        ("gate-summary out-of-band", gate_out_of_band, expected_report_out_of_band),
    ]:
        if names != expected:
            errors.append(f"{label} names mismatch: {names}")

    topology_status_only = sorted_strings(topo.get("status_only_gate_names"))
    status_only_names = context_names_from_records(status_only.get("status_only_gates"))
    if not status_only_names:
        status_only_names = sorted_strings(status_only.get("status_only_gate_names"))
    expected_status_only = sorted([
        "hash_cycle_policy_references",
        "release_gate_summary_freshness",
        "status_only_release_gates_report",
    ])
    if topology_status_only != expected_status_only:
        errors.append(f"topology status-only gate names mismatch: {topology_status_only}")
    if status_only_names and status_only_names != expected_status_only:
        errors.append(f"status-only report gate names mismatch: {status_only_names}")

    topology_warning_names = sorted_strings(topo.get("warning_context_validator_names"))
    warning_source_names = context_names_from_records(warning.get("warning_sources"))
    gate_warning_names = sorted_strings(gate.get("warning_validator_names"))
    for label, names in [
        ("topology warning-context", topology_warning_names),
        ("warning-report warning-source", warning_source_names),
        ("gate-summary warning-validator", gate_warning_names),
    ]:
        if names != warning_source_names:
            errors.append(f"{label} names do not match warning report sources: {names} vs {warning_source_names}")

    if topo.get("out_of_band_check_count") != len(expected_topology_out_of_band):
        errors.append("topology out_of_band_check_count does not match expected out-of-band names")
    if len(warning_out_of_band) != len(expected_report_out_of_band):
        errors.append("warning report out-of-band context count does not match expected names")
    if len(gate_out_of_band) != len(expected_report_out_of_band):
        errors.append("gate summary out-of-band policy count does not match expected names")

    if topo.get("warning_context_validator_count") != warning.get("warning_validator_count"):
        errors.append("topology warning_context_validator_count does not match warning report warning_validator_count")
    if gate.get("warning_validator_count") != warning.get("warning_validator_count"):
        errors.append("gate summary warning_validator_count does not match warning report warning_validator_count")
    if gate.get("validator_count") != topo.get("checklist_validator_count"):
        errors.append("gate summary validator_count does not match topology checklist_validator_count")
    if status_only.get("status_only_gate_count") != topo.get("status_only_gate_count"):
        errors.append("status-only report gate count does not match topology status_only_gate_count")

    aggregate_warning_classes = set(warning.get("aggregate_warning_class_counts", {}).keys())
    gate_warning_classes = set(gate.get("aggregate_warning_class_counts", {}).keys())
    if aggregate_warning_classes != gate_warning_classes:
        errors.append("warning report aggregate warning classes do not match gate summary aggregate warning classes")

    for label, item in [("topology", topology), ("warning", warning), ("gate", gate), ("status_only", status_only)]:
        if item.get("safe_to_auto_clear_warnings") is not False:
            errors.append(f"{label} does not refuse automatic warning clearing")
        if item.get("safe_to_auto_publish") is not False:
            errors.append(f"{label} does not refuse automatic publication")

    return {
        "schema": "urn:tyche:cassandra:release-readiness-context-consistency-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "sources": {
            "topology": source_summary(workspace, TOPOLOGY_REL, topology),
            "warning_report": source_summary(workspace, WARNING_REL, warning),
            "gate_summary": source_summary(workspace, GATE_REL, gate),
            "status_only_report": source_summary(workspace, STATUS_ONLY_REL, status_only),
        },
        "checked_context": {
            "topology_out_of_band_names": expected_topology_out_of_band,
            "report_out_of_band_names": expected_report_out_of_band,
            "out_of_band_names": expected_topology_out_of_band,
            "status_only_gate_names": expected_status_only,
            "warning_context_validator_names": warning_source_names,
            "aggregate_warning_class_count": len(aggregate_warning_classes),
        },
        "safe_to_auto_clear_warnings": False,
        "safe_to_auto_publish": False,
        "operator_review_gate": True,
        "research_caveat": "Local release-readiness context consistency validation only; it is not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, or publication approval.",
    }


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    data = {
        "topology": load_json(workspace, TOPOLOGY_REL),
        "warning": load_json(workspace, WARNING_REL),
        "gate": load_json(workspace, GATE_REL),
        "status_only": load_json(workspace, STATUS_ONLY_REL),
    }
    return validate_data(workspace, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/release-readiness-context-consistency-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    output = workspace / args.output
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
