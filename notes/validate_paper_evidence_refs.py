#!/usr/bin/env python3
"""Validate paper reference/evidence checklist coverage for Cassandra.

Local research-safety and reproducibility helper only. It checks that the
paper's local evidence references resolve to workspace artifacts, are represented
in the artifact index where appropriate, and keep claim wording bounded. It does
not assert legal compliance, trusted-list legal effect, supervision, signature
validation, public alerting, regulated trust-service output, or publication
readiness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
from typing import Any

REQUIRED_REFERENCE_PATHS = [
    "sources/eu-lotl.xml",
    "sources/eu-lotl.xml.meta.json",
    "notes/pointers.json",
    "snapshots/2026-05-20/manifest.json",
    "normalized/2026-05-20/manifest.json",
    "diffs/2026-05-20.json",
    "alerts.jsonl",
    "bundles/2026-05-20/snapshot-summary.json.bundle/",
]

BUNDLE_REQUIRED_FILES = [
    "manifest.json",
    "claims.json",
    "notes.md",
    "verification.json",
]

REQUIRED_CLAIM_CAVEATS = [
    "does not assert legal effect",
    "does not determine",
    "does not describe relying-party validation",
]

FORBIDDEN_TOKENS = [
    "Zetes",
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "we offer",
]

ARTIFACT_INDEX_EXEMPT_DIRS = {
    "bundles/2026-05-20/snapshot-summary.json.bundle/",
}


def sha256_path(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact_index_hashes(index_text: str, rel_path: str) -> list[str]:
    pattern = rf"`{re.escape(rel_path)}`[^\n]*`sha256:([0-9a-f]{{64}})`"
    return re.findall(pattern, index_text)


def line_for(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    if idx < 0:
        return None
    return text.count("\n", 0, idx) + 1


def validate(workspace: pathlib.Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked_refs: list[dict[str, Any]] = []

    paper_path = workspace / "paper" / "draft.md"
    artifact_index_path = workspace / "ARTIFACT_INDEX.md"
    claims_path = workspace / "CLAIMS.md"
    sources_path = workspace / "SOURCES.md"

    paper = paper_path.read_text(encoding="utf-8")
    artifact_index = artifact_index_path.read_text(encoding="utf-8")
    claims = claims_path.read_text(encoding="utf-8")
    sources = sources_path.read_text(encoding="utf-8")

    for token in FORBIDDEN_TOKENS:
        if token in paper:
            errors.append(f"paper contains forbidden token: {token}")

    missing_caveats = [fragment for fragment in REQUIRED_CLAIM_CAVEATS if fragment not in paper]
    if missing_caveats:
        errors.append(f"paper missing required claim-safety caveats: {missing_caveats}")

    if "## References and local evidence" not in paper:
        errors.append("paper lacks References and local evidence section")

    for rel in REQUIRED_REFERENCE_PATHS:
        if rel not in paper:
            errors.append(f"paper does not reference required local evidence path: {rel}")
        path = workspace / rel
        exists = path.exists()
        entry: dict[str, Any] = {
            "path": rel,
            "exists": exists,
            "paper_line": line_for(paper, rel),
        }
        if not exists:
            errors.append(f"referenced local evidence path is missing: {rel}")
            checked_refs.append(entry)
            continue
        if path.is_dir():
            entry["type"] = "directory"
            missing_bundle = [name for name in BUNDLE_REQUIRED_FILES if not (path / name).exists()]
            entry["required_bundle_files_present"] = not missing_bundle
            entry["missing_bundle_files"] = missing_bundle
            if missing_bundle:
                errors.append(f"bundle directory {rel} missing required files: {missing_bundle}")
        else:
            digest = sha256_path(path)
            index_digests = artifact_index_hashes(artifact_index, rel)
            entry.update({"type": "file", "sha256": digest, "artifact_index_sha256_candidates": index_digests})
            if not index_digests:
                errors.append(f"artifact index lacks hash row for referenced file: {rel}")
            elif digest not in index_digests:
                errors.append(f"artifact index hash mismatch for {rel}: candidates {index_digests}, actual {digest}")
            elif len(index_digests) > 1:
                warnings.append(f"artifact index has multiple rows for {rel}; one row matches the current file hash")
        checked_refs.append(entry)

    claims_refs = [
        "paper/draft.md",
        "notes/validate_paper_claim_safety.py",
        "notes/validate_paper_figure_refs.py",
        "bundles/2026-05-20/snapshot-summary.json.bundle/",
        "alerts.jsonl",
    ]
    missing_claim_links = [rel for rel in claims_refs if rel not in claims]
    if missing_claim_links:
        warnings.append(f"CLAIMS.md does not mention expected evidence-related paths: {missing_claim_links}")

    source_refs = ["EU list of trusted lists XML", "MIRROR evidence bundle schema", "Operator compliance profile"]
    missing_source_refs = [token for token in source_refs if token not in sources]
    if missing_source_refs:
        errors.append(f"SOURCES.md missing expected source context rows: {missing_source_refs}")

    return {
        "schema": "urn:tyche:cassandra:paper-evidence-reference-validation:0.1",
        "status": "ok" if not errors else "needs_review",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "paper": str(paper_path.relative_to(workspace)),
        "checked_reference_count": len(checked_refs),
        "checked_references": checked_refs,
        "research_caveat": "Local paper evidence-reference validation only; not legal compliance, trusted-list legal effect, supervision, signature validation, public alerting, regulated trust-service output, or publication readiness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--output", default="notes/paper-evidence-reference-validation-output.json")
    args = parser.parse_args()
    workspace = pathlib.Path(args.workspace).resolve()
    result = validate(workspace)
    output_path = workspace / args.output
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
