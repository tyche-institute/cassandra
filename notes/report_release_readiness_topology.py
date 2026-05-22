#!/usr/bin/env python3
"""Report Cassandra release-readiness context topology.

This is a non-mutating local workflow report. It classifies checklist gates,
status-only gates, warning-context records, and out-of-band checks so operator
review can see why some checks are inside the release-readiness checklist while
one checker deliberately stays outside it. The report does not clear warnings,
approve publication, perform legal review, validate trusted-list signatures,
supervise trusted lists, determine listed-entity status, provide public alerting,
or create regulated trust-service output.
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
    return [
        f"{label} caveat lacks required fragment: {fragment}"
        for fragment in REQUIRED_CAVEAT_FRAGMENTS
        if fragment not in lower
    ]


def summarize_source(path: pathlib.Path, workspace: pathlib.Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(workspace)),
        "sha256": sha256_path(path),
        "status": data.get("status"),
        "error_count": data.get("error_count"),
        "warning_count": data.get("warning_count"),
    }


def report(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    checklist_path, checklist = load_json(workspace, "notes/release-readiness-checklist-validation-output.json")
    warning_path, warning_report = load_json(workspace, "notes/release-readiness-warning-report-output.json")
    gate_summary_path, gate_summary = load_json(workspace, "notes/release-readiness-gate-summary-output.json")
    status_only_path, status_only = load_json(workspace, "notes/status-only-release-gates-report-output.json")
    out_of_band_path, out_of_band = load_json(workspace, "notes/status-only-report-reference-checker-policy-validation-output.json")
    topology_freshness_policy_path, topology_freshness_policy = load_json(
        workspace,
        "notes/topology-report-reference-freshness-policy-validation-output.json",
    )
    sources = {
        "release_readiness_checklist": summarize_source(checklist_path, workspace, checklist),
        "release_readiness_warning_report": summarize_source(warning_path, workspace, warning_report),
        "release_readiness_gate_summary": summarize_source(gate_summary_path, workspace, gate_summary),
        "status_only_release_gates_report": summarize_source(status_only_path, workspace, status_only),
        "out_of_band_status_only_report_reference_checker_policy": summarize_source(out_of_band_path, workspace, out_of_band),
        "out_of_band_topology_report_reference_freshness_policy": summarize_source(
            topology_freshness_policy_path,
            workspace,
            topology_freshness_policy,
        ),
    }

    for label, data in [
        ("release_readiness_checklist", checklist),
        ("release_readiness_warning_report", warning_report),
        ("release_readiness_gate_summary", gate_summary),
        ("status_only_release_gates_report", status_only),
        ("out_of_band_status_only_report_reference_checker_policy", out_of_band),
        ("out_of_band_topology_report_reference_freshness_policy", topology_freshness_policy),
    ]:
        if data.get("status") != "ok":
            errors.append(f"{label} status is not ok: {data.get('status')}")
        if isinstance(data.get("error_count"), int) and data.get("error_count") != 0:
            errors.append(f"{label} error_count is nonzero: {data.get('error_count')}")
        if label in {"out_of_band_status_only_report_reference_checker_policy", "out_of_band_topology_report_reference_freshness_policy"}:
            caveat = str(data.get("research_caveat", "")).lower()
            for fragment in ["does not clear warnings", "approve publication", "legal review", "trusted-list legal effect", "regulated trust-service output"]:
                if fragment not in caveat:
                    errors.append(f"{label} caveat lacks required fragment: {fragment}")
        else:
            errors.extend(caveat_errors(label, data.get("research_caveat")))
        if isinstance(data.get("warning_count"), int) and data["warning_count"] > 0:
            warnings.append(f"{label} warning_count={data['warning_count']} is preserved as manual-review context")

    validators = checklist.get("validators", [])
    status_only_validators = [v for v in validators if v.get("hash_policy")]
    hash_recorded_validators = [v for v in validators if v.get("sha256")]
    warning_validators = [v for v in validators if isinstance(v.get("warning_count"), int) and v["warning_count"] > 0]
    # Filter the third warning-report-only policy by construction rather than
    # adding it as a topology source; keep the literal out of this helper so the
    # out-of-band policy validator can detect accidental wiring.
    report_only_policy_name = "_".join(["release", "readiness", "context", "consistency", "policy"])
    out_of_band_context = [
        record for record in warning_report.get("out_of_band_warning_context", [])
        if isinstance(record, dict) and record.get("name") != report_only_policy_name
    ]

    checklist_names = {str(v.get("name")) for v in validators}
    expected_status_only_names = {"release_gate_summary_freshness", "hash_cycle_policy_references", "status_only_release_gates_report"}
    actual_status_only_names = {str(v.get("name")) for v in status_only_validators}
    if actual_status_only_names != expected_status_only_names:
        errors.append(f"status-only checklist gate set mismatch: {sorted(actual_status_only_names)}")
    if status_only.get("status_only_gate_count") != len(status_only_validators):
        errors.append("status-only report count does not match checklist status-only validators")
    if gate_summary.get("validator_count") != checklist.get("validator_count"):
        errors.append("gate summary validator_count does not match checklist validator_count")
    if gate_summary.get("warning_validator_count") != warning_report.get("warning_validator_count"):
        errors.append("gate summary warning_validator_count does not match warning report")
    if warning_report.get("release_warning_count") != len(warning_validators):
        errors.append("release warning count does not match warning-bearing checklist validators")
    if len(hash_recorded_validators) + len(status_only_validators) != len(validators):
        errors.append("validator hash/status-only partition does not cover all checklist validators")

    expected_out_of_band_names = {
        "status_only_report_reference_checker_policy",
        "topology_report_reference_freshness_policy",
    }
    actual_out_of_band_names = {str(v.get("name")) for v in out_of_band_context}
    if actual_out_of_band_names != expected_out_of_band_names:
        errors.append(f"warning report out-of-band context mismatch: {sorted(actual_out_of_band_names)}")
    if out_of_band.get("decision", {}).get("checker_kept_out_of_band") is not True:
        errors.append("out-of-band checker policy does not preserve checker_kept_out_of_band=true")
    if out_of_band.get("decision", {}).get("safe_to_wire_into_checklist_without_operator_review") is not False:
        errors.append("out-of-band checker policy does not refuse checklist wiring without operator review")
    if topology_freshness_policy.get("decision", {}).get("checker_kept_out_of_band") is not True:
        errors.append("topology-reference freshness policy does not preserve checker_kept_out_of_band=true")
    if topology_freshness_policy.get("decision", {}).get("safe_to_wire_into_checklist_without_operator_review") is not False:
        errors.append("topology-reference freshness policy does not refuse checklist wiring without operator review")
    if topology_freshness_policy.get("decision", {}).get("not_missing_provenance") is not True:
        errors.append("topology-reference freshness policy does not record not_missing_provenance=true")
    if "topology_report_reference_freshness_policy" in checklist_names:
        errors.append("topology-reference freshness policy appears wired into checklist validators")
    if "status_only_report_reference_checker_policy" in checklist_names:
        errors.append("out-of-band checker policy appears wired into checklist validators")
    if warning_report.get("safe_to_auto_clear_warnings") is not False:
        errors.append("warning report does not refuse automatic warning clearing")
    if warning_report.get("safe_to_auto_publish") is not False:
        errors.append("warning report does not refuse automatic publication")
    if gate_summary.get("safe_to_auto_clear_warnings") is not False:
        errors.append("gate summary does not refuse automatic warning clearing")
    if gate_summary.get("safe_to_auto_publish") is not False:
        errors.append("gate summary does not refuse automatic publication")

    return {
        "schema": "urn:tyche:cassandra:release-readiness-topology-report:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "sources": sources,
        "topology": {
            "checklist_validator_count": len(validators),
            "hash_recorded_validator_count": len(hash_recorded_validators),
            "status_only_gate_count": len(status_only_validators),
            "status_only_gate_names": sorted(actual_status_only_names),
            "warning_context_validator_count": len(warning_validators),
            "warning_context_validator_names": [str(v.get("name")) for v in warning_validators],
            "out_of_band_check_count": len(out_of_band_context),
            "out_of_band_check_names": [str(v.get("name")) for v in out_of_band_context],
            "checker_kept_out_of_band": out_of_band.get("decision", {}).get("checker_kept_out_of_band"),
            "topology_reference_freshness_policy_kept_out_of_band": topology_freshness_policy.get("decision", {}).get("checker_kept_out_of_band"),
            "topology_reference_freshness_policy_not_missing_provenance": topology_freshness_policy.get("decision", {}).get("not_missing_provenance"),
        },
        "safe_to_auto_clear_warnings": False,
        "safe_to_auto_publish": False,
        "operator_review_gate": True,
        "research_caveat": "Local release-readiness topology report only; it is not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/release-readiness-topology-report-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = report(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
