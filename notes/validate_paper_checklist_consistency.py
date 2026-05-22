#!/usr/bin/env python3
"""Validate paper/checklist consistency for Cassandra release-readiness gates.

This is a local workflow-boundary check. It verifies that the paper's
release-readiness checklist remains aligned with the configured checklist
validator outputs and that out-of-band context-consistency policy material is
not accidentally promoted into a new release gate. It does not assert legal
compliance, trusted-list legal effect, supervision, signature validation,
public alerting, regulated trust-service output, warning clearance, legal
review, or publication approval.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

PAPER = pathlib.Path("paper/draft.md")
CHECKLIST_VALIDATOR = pathlib.Path("notes/validate_release_readiness_checklist.py")
CHECKLIST_OUTPUT = pathlib.Path("notes/release-readiness-checklist-validation-output.json")
CONTEXT_POLICY_OUTPUT = pathlib.Path("notes/release-readiness-context-consistency-policy-validation-output.json")
CONTEXT_CONSISTENCY_VALIDATOR = "release_readiness_context_consistency"
CHECKLIST_HEADING = "## Release-readiness checklist for operator review"

REQUIRED_NON_CLEARANCE_FRAGMENTS = [
    "not a substitute",
    "not a clearance",
    "does not clear warnings",
    "approve publication",
    "legal review",
    "validate signatures",
    "supervise",
    "public alerting",
    "regulated trust-service output",
]


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^{re.escape(heading)}\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(0) if match else ""


def literal_value(node: ast.AST) -> Any:
    """Evaluate literals plus pathlib.Path('...') used in local validators."""
    if isinstance(node, ast.Call):
        func = node.func
        is_path_call = (
            isinstance(func, ast.Attribute)
            and func.attr == "Path"
            and isinstance(func.value, ast.Name)
            and func.value.id == "pathlib"
        )
        if is_path_call and len(node.args) == 1 and not node.keywords:
            return pathlib.Path(literal_value(node.args[0]))
    if isinstance(node, ast.List):
        return [literal_value(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(literal_value(item) for item in node.elts)
    if isinstance(node, ast.Set):
        return {literal_value(item) for item in node.elts}
    return ast.literal_eval(node)


def literal_assignment(module_text: str, name: str) -> Any:
    tree = ast.parse(module_text)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return literal_value(node.value)
    raise KeyError(name)


def checklist_config(module_path: pathlib.Path) -> dict[str, Any]:
    text = module_path.read_text(encoding="utf-8")
    outputs = literal_assignment(text, "VALIDATION_OUTPUTS")
    status_only = set(literal_assignment(text, "STATUS_ONLY_OUTPUTS"))
    records: list[dict[str, Any]] = []
    for name, rel in outputs:
        records.append({"name": str(name), "path": str(rel), "status_only": str(name) in status_only})
    return {
        "validator_count": len(records),
        "status_only_count": sum(1 for record in records if record["status_only"]),
        "records": records,
        "source_sha256": sha256_path(module_path),
    }


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    paper_path = workspace / PAPER
    validator_path = workspace / CHECKLIST_VALIDATOR
    output_path = workspace / CHECKLIST_OUTPUT
    policy_path = workspace / CONTEXT_POLICY_OUTPUT

    paper = paper_path.read_text(encoding="utf-8")
    checklist = section(paper, CHECKLIST_HEADING)
    if not checklist:
        errors.append("paper lacks release-readiness checklist section")
    checklist_lower = checklist.lower()

    config = checklist_config(validator_path)
    output = load_json(output_path) if output_path.exists() else {}
    if not output:
        errors.append(f"missing checklist output: {CHECKLIST_OUTPUT}")

    output_names = [str(record.get("name")) for record in output.get("validators", [])]
    config_names = [record["name"] for record in config["records"]]
    if output_names != config_names:
        errors.append("checklist output validator names do not match validator source order")
    if output.get("validator_count") != config["validator_count"]:
        errors.append(
            f"checklist output validator_count={output.get('validator_count')} does not match source count={config['validator_count']}"
        )
    if output.get("status") != "ok" or output.get("error_count") != 0:
        errors.append(f"checklist output is not clean ok: status={output.get('status')} error_count={output.get('error_count')}")

    missing_in_paper: list[str] = []
    for record in config["records"]:
        path = record["path"]
        prose_name = record["name"].replace("_", "-")
        prose_name_spaced = record["name"].replace("_", " ")
        prose_name_mixed = prose_name.replace("release-gate-summary-freshness", "release gate-summary freshness").replace("release-gate", "release gate")
        # Some gates are named in prose rather than by path; require either the
        # concrete path or an unambiguous gate name for status-only entries where
        # dependency-cycle ambiguity is most likely.
        name_present = any(variant in checklist_lower for variant in [prose_name, prose_name_spaced, prose_name_mixed])
        if record["status_only"] and path not in checklist and not name_present:
            missing_in_paper.append(path)
    if missing_in_paper:
        errors.append(f"paper checklist lacks status-only gate path/name references: {missing_in_paper}")

    if CONTEXT_CONSISTENCY_VALIDATOR in config_names:
        errors.append("context-consistency validator was promoted into release-readiness checklist dependencies")
    if str(CONTEXT_POLICY_OUTPUT) not in checklist:
        errors.append("paper checklist does not reference context-consistency policy output")
    if "rather than promoted into a new checklist dependency" not in checklist:
        errors.append("paper checklist lacks explicit out-of-band/not-new-dependency wording for context-consistency policy")

    missing_caveats = [fragment for fragment in REQUIRED_NON_CLEARANCE_FRAGMENTS if fragment not in checklist_lower]
    if missing_caveats:
        errors.append(f"paper checklist lacks non-clearance caveat fragments: {missing_caveats}")

    policy = load_json(policy_path) if policy_path.exists() else {}
    if not policy:
        errors.append(f"missing context-consistency policy validation output: {CONTEXT_POLICY_OUTPUT}")
    elif policy.get("status") != "ok" or policy.get("error_count") != 0:
        errors.append(
            f"context-consistency policy output is not clean ok: status={policy.get('status')} error_count={policy.get('error_count')}"
        )
    elif policy.get("warning_count", 0):
        warnings.append(
            f"{CONTEXT_POLICY_OUTPUT} has warning_count={policy.get('warning_count')}; preserve as manual-review context"
        )

    checklist_record = {
        "path": str(CHECKLIST_OUTPUT),
        "sha256": sha256_path(output_path) if output_path.exists() else None,
        "status": output.get("status"),
        "error_count": output.get("error_count"),
        "warning_count": output.get("warning_count"),
    }
    policy_record = {
        "path": str(CONTEXT_POLICY_OUTPUT),
        "sha256": sha256_path(policy_path) if policy_path.exists() else None,
        "status": policy.get("status"),
        "error_count": policy.get("error_count"),
        "warning_count": policy.get("warning_count"),
    }

    return {
        "schema": "urn:tyche:cassandra:paper-checklist-consistency-validation:0.1",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "paper": str(PAPER),
        "paper_sha256": sha256_path(paper_path),
        "checklist_validator": str(CHECKLIST_VALIDATOR),
        "checklist_validator_sha256": config["source_sha256"],
        "configured_validator_count": config["validator_count"],
        "configured_status_only_count": config["status_only_count"],
        "configured_validator_names": config_names,
        "checklist_output": checklist_record,
        "context_consistency_policy_output": policy_record,
        "context_consistency_validator_is_checklist_dependency": CONTEXT_CONSISTENCY_VALIDATOR in config_names,
        "research_caveat": "Local paper/checklist consistency validation only; verifies release-readiness wiring and out-of-band policy wording, not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, warning clearance, legal review, or publication approval.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/paper-checklist-consistency-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    out = workspace / args.output
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
