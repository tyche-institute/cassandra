#!/usr/bin/env python3
"""Report Cassandra release-readiness warning classes without mutating state.

This helper explains validator warnings that are intentionally preserved as
manual-review context. It does not downgrade warnings to approval, rewrite
historical artifacts, or assert legal compliance, trusted-list legal effect,
signature validity, supervision, public alerting, regulated trust-service
output, or publication readiness.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

SCHEMA = "urn:tyche:cassandra:release-readiness-warning-report:0.1"
OUT_OF_BAND_WARNING_CONTEXT_PATHS = [
    pathlib.Path("notes/status-only-report-reference-checker-policy-validation-output.json"),
    pathlib.Path("notes/topology-report-reference-freshness-policy-validation-output.json"),
    pathlib.Path("notes/release-readiness-context-consistency-policy-validation-output.json"),
]
RESEARCH_CAVEAT = (
    "Local release-readiness warning report only; warnings are manual-review "
    "context, not legal compliance, trusted-list legal effect, signature "
    "validation, supervision, public alerting, regulated trust-service output, "
    "or publication approval."
)


def sha256_path(path: pathlib.Path) -> str:
    h = sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_public_artifact_warning(finding: dict[str, Any]) -> str:
    path = str(finding.get("path", ""))
    snippet = str(finding.get("snippet", "")).lower()
    pattern = str(finding.get("pattern", "")).lower()
    if "not " in snippet or "does not" in snippet:
        if path.endswith(".svg"):
            return "caveated_svg_risky_phrase"
        if "bundle-generic" in path:
            return "caveated_bundle_helper_risky_phrase"
        if "alerts.jsonl" in path:
            return "caveated_alert_risky_phrase"
        if "bundle" in path:
            return "caveated_bundle_risky_phrase"
        return "caveated_risky_phrase"
    if "legacy" in snippet or "dedupe" in snippet or "dedupe" in pattern:
        return "legacy_append_only_alert_context"
    return "manual_review_warning"


def classify_paper_claim_warning(finding: dict[str, Any]) -> str:
    snippet = str(finding.get("snippet", "")).lower()
    pattern = str(finding.get("pattern", "")).lower()
    if "not " in snippet or "does not" in snippet:
        if "public alerting" in pattern:
            return "caveated_public_alerting_phrase"
        if "relying-party validation" in pattern:
            return "caveated_relying_party_validation_phrase"
        return "caveated_risky_phrase"
    return "manual_review_warning"


def classify_evidence_warning(warning: str) -> str:
    lowered = warning.lower()
    if "multiple rows" in lowered and "one row matches" in lowered:
        return "artifact_index_duplicate_row_current_hash_present"
    return "manual_review_warning"


def summarize_validation(name: str, path: pathlib.Path, data: dict[str, Any]) -> dict[str, Any]:
    classes: Counter[str] = Counter()
    examples: dict[str, list[str]] = defaultdict(list)
    if name == "public_artifact_safety":
        for finding in data.get("findings", []):
            cls = classify_public_artifact_warning(finding)
            classes[cls] += 1
            if len(examples[cls]) < 3:
                examples[cls].append(f"{finding.get('path')}:{finding.get('line')} {finding.get('pattern')}")
    elif name == "paper_claim_safety":
        for finding in data.get("findings", []):
            cls = classify_paper_claim_warning(finding)
            classes[cls] += 1
            if len(examples[cls]) < 3:
                examples[cls].append(f"line {finding.get('line')} {finding.get('pattern')}")
    elif name == "paper_evidence_refs":
        for warning in data.get("warnings", []):
            cls = classify_evidence_warning(str(warning))
            classes[cls] += 1
            if len(examples[cls]) < 3:
                examples[cls].append(str(warning))
    else:
        for warning in data.get("warnings", []):
            classes["manual_review_warning"] += 1
            if len(examples["manual_review_warning"]) < 3:
                examples["manual_review_warning"].append(str(warning))

    return {
        "name": name,
        "path": str(path),
        "status": data.get("status"),
        "error_count": data.get("error_count"),
        "warning_count": data.get("warning_count", len(data.get("warnings", []))),
        "warning_class_counts": dict(sorted(classes.items())),
        "examples": {key: value for key, value in sorted(examples.items())},
        "sha256": sha256_path(path),
    }


def report(workspace: pathlib.Path, validation_output: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    validation_path = workspace / validation_output
    before_hashes = {str(validation_output): sha256_path(validation_path)}
    release = load_json(validation_path)
    warning_validators = [item for item in release.get("validators", []) if isinstance(item.get("warning_count"), int) and item["warning_count"] > 0]

    summaries = []
    aggregate_classes: Counter[str] = Counter()
    for item in warning_validators:
        rel = pathlib.Path(item["path"])
        path = workspace / rel
        if not path.exists():
            errors.append(f"missing warning source: {rel}")
            continue
        data = load_json(path)
        summary = summarize_validation(item["name"], rel, data)
        summaries.append(summary)
        aggregate_classes.update(summary["warning_class_counts"])
        before_hashes[str(rel)] = sha256_path(path)
        if data.get("status") != "ok":
            errors.append(f"warning source is not ok: {rel}: {data.get('status')}")
        if isinstance(data.get("error_count"), int) and data["error_count"] != 0:
            errors.append(f"warning source has hard errors: {rel}: {data['error_count']}")

    after_hashes = {rel: sha256_path(workspace / rel) for rel in before_hashes}
    mutated = [rel for rel, old_hash in before_hashes.items() if after_hashes.get(rel) != old_hash]
    if mutated:
        errors.append(f"unexpected mutation while reporting warnings: {mutated}")

    if release.get("status") != "ok" or release.get("error_count") != 0:
        warnings.append("release-readiness validation is not currently ok/zero-error; preserved as refresh-order context")
    if release.get("warning_count") != len(warning_validators):
        warnings.append("release-readiness warning_count differs from positive-warning validator count")

    out_of_band_warning_context: list[dict[str, Any]] = []
    out_of_band_names = {
        "notes/status-only-report-reference-checker-policy-validation-output.json": "status_only_report_reference_checker_policy",
        "notes/topology-report-reference-freshness-policy-validation-output.json": "topology_report_reference_freshness_policy",
        "notes/release-readiness-context-consistency-policy-validation-output.json": "release_readiness_context_consistency_policy",
    }
    for out_of_band_rel in OUT_OF_BAND_WARNING_CONTEXT_PATHS:
        out_of_band_path = workspace / out_of_band_rel
        if not out_of_band_path.exists():
            errors.append(f"missing out-of-band warning context: {out_of_band_rel}")
            continue
        out_of_band_data = load_json(out_of_band_path)
        decision = out_of_band_data.get("decision", {})
        out_of_band_warning_context.append(
            {
                "name": out_of_band_names[str(out_of_band_rel)],
                "path": str(out_of_band_rel),
                "sha256": sha256_path(out_of_band_path),
                "status": out_of_band_data.get("status"),
                "error_count": out_of_band_data.get("error_count"),
                "warning_count": out_of_band_data.get("warning_count"),
                "warnings": out_of_band_data.get("warnings", []),
                "checker_kept_out_of_band": decision.get("checker_kept_out_of_band"),
                "safe_to_wire_into_checklist_without_operator_review": decision.get("safe_to_wire_into_checklist_without_operator_review"),
                "cycle_avoidance_reason": decision.get("cycle_avoidance_reason"),
                "safe_to_wire_into_topology_without_operator_review": decision.get("safe_to_wire_into_topology_without_operator_review"),
                "counted_in_release_warning_count": False,
            }
        )
        if out_of_band_data.get("status") != "ok" or out_of_band_data.get("error_count") != 0:
            errors.append(f"out-of-band warning context is not ok: {out_of_band_rel}")
        if decision.get("checker_kept_out_of_band") is not True:
            errors.append(f"out-of-band warning context does not preserve checker_kept_out_of_band=true: {out_of_band_rel}")
        if decision.get("safe_to_wire_into_checklist_without_operator_review") is not False:
            errors.append(f"out-of-band warning context does not refuse checklist wiring without operator review: {out_of_band_rel}")
        if str(out_of_band_rel) == "notes/release-readiness-context-consistency-policy-validation-output.json" and decision.get("safe_to_wire_into_topology_without_operator_review") is not False:
            errors.append(f"context-consistency policy does not refuse topology wiring without operator review: {out_of_band_rel}")

    return {
        "schema": SCHEMA,
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "release_validation": str(validation_output),
        "release_validation_sha256": before_hashes[str(validation_output)],
        "release_warning_count": release.get("warning_count"),
        "warning_validator_count": len(warning_validators),
        "warning_sources": summaries,
        "out_of_band_warning_context": out_of_band_warning_context,
        "aggregate_warning_class_counts": dict(sorted(aggregate_classes.items())),
        "non_mutation_hashes": after_hashes,
        "safe_to_auto_clear_warnings": False,
        "safe_to_auto_publish": False,
        "research_caveat": RESEARCH_CAVEAT,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--validation-output", default="notes/release-readiness-checklist-validation-output.json")
    parser.add_argument("--output", default="notes/release-readiness-warning-report-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = report(workspace, pathlib.Path(args.validation_output))
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
