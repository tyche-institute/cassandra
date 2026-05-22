#!/usr/bin/env python3
"""Validate Cassandra bundle files and alert templates for claim-safe wording.

Local research-only check. It scans public-adjacent machine-readable and bundle
artifacts for hard compliance rails and required caveats. It does not provide
legal analysis, publication approval, trusted-list validation, supervision, or
signature verification.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
OUTPUT_PATH = WORKSPACE / "notes" / "public-artifact-safety-validation-output.json"

BUNDLE_DIR = WORKSPACE / "bundles" / "2026-05-20" / "snapshot-summary.json.bundle"

TEXT_PATHS = [
    BUNDLE_DIR / "notes.md",
    WORKSPACE / "figures" / "aggregate-run-telemetry.svg",
    WORKSPACE / "figures" / "aggregate-diff-classes.svg",
]
JSON_PATHS = [
    BUNDLE_DIR / "manifest.json",
    BUNDLE_DIR / "claims.json",
    WORKSPACE / "notes" / "bundle-generic-existing-guard-output.json",
    WORKSPACE / "notes" / "bundle-generic-missing-inputs-output.json",
    WORKSPACE / "notes" / "bundle-generic-helper-check-output.json",
]
JSONL_PATHS = [
    WORKSPACE / "alerts.jsonl",
]

FORBIDDEN_PATTERNS = [
    ("zetes_mention", re.compile(r"\bZetes\b", re.IGNORECASE)),
    ("zetes_estonia_mention", re.compile(r"\bZetes\s+Estonia\b", re.IGNORECASE)),
    ("employee_identification", re.compile(r"\b(employee|employed)\b.{0,80}\bZetes\b", re.IGNORECASE | re.DOTALL)),
    ("service_provision_claim", re.compile(r"\b(Tyche Institute|Anton Sokolov|Cassandra)\b.{0,120}\b(provides?|offers?|sells?|operates?)\b.{0,80}\b(trust services?|qualified certificates?|timestamps?|identity solutions?|border-control solutions?)\b", re.IGNORECASE | re.DOTALL)),
    ("qtsp_claim", re.compile(r"\b(Tyche Institute|Anton Sokolov|Cassandra)\b.{0,120}\b(QTSP|qualified trust service provider)\b", re.IGNORECASE | re.DOTALL)),
]

RISKY_PHRASES = [
    "certifies compliance",
    "proves legal compliance",
    "official audit",
    "guarantees",
    "qualifies as a QTSP",
    "legal-status determination",
    "public alerting",
    "relying-party validation",
    "signature verification",
]

REQUIRED_PHRASES_BY_PATH = {
    "bundles/2026-05-20/snapshot-summary.json.bundle/notes.md": [
        "research-only evidence bundle",
        "does not perform cryptographic signature verification",
        "does not determine or assert legal status",
        "aggregate-only",
    ],
    "alerts.jsonl": [
        "Machine-readable research telemetry",
        "legal_effect",
        "not asserted",
        "signature_validation",
        "not performed",
    ],
    "bundles/2026-05-20/snapshot-summary.json.bundle/manifest.json": [
        "research-only structural observation",
        "No regulated trust-service output is created by this bundle.",
        "Tyche Institute, Tallinn, Estonia",
    ],
    "bundles/2026-05-20/snapshot-summary.json.bundle/claims.json": [
        "safe_wording",
        "No trusted-list legal status is inferred.",
        "No signature validity or legal effect is asserted.",
    ],
    "notes/bundle-generic-existing-guard-output.json": [
        "urn:tyche:cassandra:bundle-run:0.2",
        "research-only structural observation",
        "not legal-status determination",
        "not legal-status determination, supervision, signature validation, relying-party processing, public alerting, regulated trust-service output, or publication readiness",
    ],
    "notes/bundle-generic-missing-inputs-output.json": [
        "urn:tyche:cassandra:bundle-run:0.2",
        "research-only structural observation",
        "not legal-status determination",
        "not legal-status determination, supervision, signature validation, relying-party processing, public alerting, regulated trust-service output, or publication readiness",
    ],
    "notes/bundle-generic-helper-check-output.json": [
        "refused_existing_outputs",
        "missing_inputs",
        "research-only structural observation",
    ],
    "figures/aggregate-run-telemetry.svg": [
        "Local structural-observation telemetry only",
        "not trusted-list validation",
        "not legal-status determination",
        "not supervision",
        "not signature validation",
        "not public alerting",
        "not publication approval",
        "Listed names are intentionally absent from this figure.",
    ],
    "figures/aggregate-diff-classes.svg": [
        "Local structural-observation telemetry only",
        "not trusted-list validation",
        "not legal-status determination",
        "not supervision",
        "not signature validation",
        "not public alerting",
        "not publication approval",
        "Listed names are intentionally absent from this figure.",
    ],
}

ALLOWED_ALERT_EVENT_TYPES = {
    "baseline_initialized",
    "no_structural_diff_observed",
    "structural_diff_observed",
}


@dataclass
class Finding:
    path: str
    category: str
    pattern: str
    line: int
    snippet: str
    severity: str


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(WORKSPACE.resolve()))


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def make_snippet(text: str, start: int, end: int, width: int = 100) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return " ".join(text[left:right].split())


def scan_text(path: Path, text: str) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    relative = rel(path)
    for name, pattern in FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(Finding(relative, "forbidden_pattern", name, line_number(text, match.start()), make_snippet(text, match.start(), match.end()), "error"))

    lowered = text.lower()
    for phrase in RISKY_PHRASES:
        start = 0
        phrase_lower = phrase.lower()
        while True:
            index = lowered.find(phrase_lower, start)
            if index < 0:
                break
            findings.append(Finding(relative, "risky_phrase_review", phrase, line_number(text, index), make_snippet(text, index, index + len(phrase)), "warning"))
            start = index + len(phrase_lower)

    required_presence = {
        phrase: phrase in text
        for phrase in REQUIRED_PHRASES_BY_PATH.get(relative, [])
    }
    stats = {
        "path": relative,
        "sha256": file_sha256(path),
        "bytes": path.stat().st_size,
        "line_count": text.count("\n") + (1 if text else 0),
        "word_count": len(re.findall(r"\b\w+\b", text)),
    }
    return findings, stats | {"required_presence": required_presence}


def parse_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    entries: list[dict[str, Any]] = []
    errors: list[str] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {lineno}: JSON parse error: {exc}")
            continue
        entries.append(item)
    return entries, errors


def validate_bundle_json(path: Path, doc: dict[str, Any]) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    relative = rel(path)
    stats: dict[str, Any] = {"kind": "bundle_json"}

    if path.name == "manifest.json":
        stats["schema"] = doc.get("schema")
        stats["source_count"] = len(doc.get("sources") or [])
        stats["assumption_count"] = len(doc.get("assumptions") or [])
        if doc.get("schema") != "urn:tyche:mirror:bundle:0.1":
            findings.append(Finding(relative, "bundle_manifest", "unexpected_schema", 1, str(doc.get("schema")), "error"))
        if doc.get("created_by", {}).get("affiliation") != "Tyche Institute, Tallinn, Estonia":
            findings.append(Finding(relative, "bundle_manifest", "unexpected_affiliation", 1, str(doc.get("created_by")), "error"))
        producer_mode = str(doc.get("producer", {}).get("mode", ""))
        if "research-only structural observation" not in producer_mode:
            findings.append(Finding(relative, "bundle_manifest", "missing_research_only_mode", 1, producer_mode, "error"))
        caveat = str(doc.get("attestation", {}).get("caveat", ""))
        if "No regulated trust-service output" not in caveat:
            findings.append(Finding(relative, "bundle_manifest", "missing_attestation_caveat", 1, caveat, "error"))
        artifact_sha = ((doc.get("artifact") or {}).get("sha256") or {}).get("value")
        if not artifact_sha:
            findings.append(Finding(relative, "bundle_manifest", "missing_artifact_sha256", 1, str(doc.get("artifact")), "error"))
        for idx, source in enumerate(doc.get("sources") or [], start=1):
            value = ((source.get("sha256") or {}).get("value"))
            if not value:
                findings.append(Finding(relative, "bundle_manifest_source", "missing_source_sha256", idx, str(source), "error"))

    elif path.name == "claims.json":
        claims = doc.get("claims") or []
        stats["schema"] = doc.get("schema")
        stats["claim_count"] = len(claims)
        if doc.get("schema") != "urn:tyche:mirror:claims:0.1":
            findings.append(Finding(relative, "bundle_claims", "unexpected_schema", 1, str(doc.get("schema")), "error"))
        if not claims:
            findings.append(Finding(relative, "bundle_claims", "empty_claims", 1, "claims array is empty", "error"))
        for idx, claim in enumerate(claims, start=1):
            safe = str(claim.get("safe_wording", ""))
            evidence = claim.get("evidence") or []
            notes = str(claim.get("notes", ""))
            if not safe:
                findings.append(Finding(relative, "bundle_claims", "missing_safe_wording", idx, str(claim), "error"))
            if not evidence:
                findings.append(Finding(relative, "bundle_claims", "missing_evidence", idx, str(claim), "error"))
            caveated_text = (safe + " " + notes).lower()
            if not any(token in caveated_text for token in ["legal", "signature", "operational observations only", "parser telemetry"]):
                findings.append(Finding(relative, "bundle_claims", "missing_claim_safety_caveat", idx, safe[:160], "error"))

    elif relative.startswith("notes/bundle-generic-"):
        stats["kind"] = "bundle_helper_output"
        stats["schema"] = doc.get("schema")
        stats["status"] = doc.get("status")
        stats["missing_input_count"] = len(doc.get("missing_inputs") or [])
        stats["existing_output_count"] = len(doc.get("existing_outputs") or [])
        if path.name != "bundle-generic-helper-check-output.json" and doc.get("schema") != "urn:tyche:cassandra:bundle-run:0.2":
            findings.append(Finding(relative, "bundle_helper_output", "unexpected_schema", 1, str(doc.get("schema")), "error"))
        if doc.get("status") not in {"refused_existing_outputs", "missing_inputs", "ok"}:
            findings.append(Finding(relative, "bundle_helper_output", "unexpected_status", 1, str(doc.get("status")), "error"))
        caveat = str(doc.get("research_caveat", ""))
        required_caveat_tokens = [
            "research-only structural observation",
            "not legal-status determination",
            "supervision",
            "signature validation",
            "regulated trust-service output",
            "publication readiness",
        ]
        if path.name != "bundle-generic-helper-check-output.json":
            missing = [token for token in required_caveat_tokens if token not in caveat]
            if missing:
                findings.append(Finding(relative, "bundle_helper_output", "missing_research_caveat_tokens", 1, str(missing), "error"))
        else:
            checks = doc.get("checks") or {}
            for key in ["existing", "missing"]:
                nested = checks.get(key) or {}
                nested_caveat = str(nested.get("research_caveat", ""))
                missing = [token for token in required_caveat_tokens if token not in nested_caveat]
                if missing:
                    findings.append(Finding(relative, "bundle_helper_output", f"missing_{key}_research_caveat_tokens", 1, str(missing), "error"))
                if nested.get("schema") != "urn:tyche:cassandra:bundle-run:0.2":
                    findings.append(Finding(relative, "bundle_helper_output", f"unexpected_{key}_schema", 1, str(nested.get("schema")), "error"))
            if doc.get("status") != "ok":
                findings.append(Finding(relative, "bundle_helper_output", "helper_check_not_ok", 1, str(doc.get("status")), "error"))

    return findings, stats


def validate_alert_entries(path: Path, entries: list[dict[str, Any]]) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    relative = rel(path)
    seen_dedupe = set()
    missing_dedupe = 0
    for index, item in enumerate(entries, start=1):
        event_type = item.get("event_type")
        if event_type not in ALLOWED_ALERT_EVENT_TYPES:
            findings.append(Finding(relative, "alert_schema", "unexpected_event_type", index, str(event_type), "error"))
        caveat = str(item.get("caveat", ""))
        if "research telemetry" not in caveat:
            findings.append(Finding(relative, "alert_caveat", "missing_research_telemetry_caveat", index, caveat[:160], "error"))
        claim_safety = item.get("claim_safety") or {}
        if claim_safety.get("legal_effect") != "not asserted":
            findings.append(Finding(relative, "alert_claim_safety", "legal_effect_not_asserted", index, str(claim_safety), "error"))
        if claim_safety.get("signature_validation") != "not performed":
            findings.append(Finding(relative, "alert_claim_safety", "signature_validation_not_performed", index, str(claim_safety), "error"))
        counts = item.get("counts") or {}
        if counts.get("diff_change_count") is None:
            findings.append(Finding(relative, "alert_counts", "missing_diff_change_count", index, str(counts), "error"))
        dedupe_key = item.get("dedupe_key")
        if dedupe_key:
            if dedupe_key in seen_dedupe:
                findings.append(Finding(relative, "alert_schema", "duplicate_dedupe_key", index, str(dedupe_key), "error"))
            seen_dedupe.add(dedupe_key)
        else:
            # v0.1 bootstrap entries predate dedupe keys; record for visibility only.
            missing_dedupe += 1
            findings.append(Finding(relative, "alert_schema", "legacy_entry_without_dedupe_key", index, event_type or "", "warning"))
    stats = {
        "entry_count": len(entries),
        "legacy_entries_without_dedupe_key": missing_dedupe,
        "event_types": sorted({str(item.get("event_type")) for item in entries}),
    }
    return findings, stats


def main() -> int:
    findings: list[Finding] = []
    file_stats: list[dict[str, Any]] = []
    jsonl_stats: dict[str, Any] = {}
    missing_files: list[str] = []

    for path in TEXT_PATHS:
        if not path.exists():
            missing_files.append(rel(path))
            continue
        text = path.read_text(encoding="utf-8")
        found, stats = scan_text(path, text)
        findings.extend(found)
        file_stats.append(stats)

    for path in JSON_PATHS:
        if not path.exists():
            missing_files.append(rel(path))
            continue
        text = path.read_text(encoding="utf-8")
        found, stats = scan_text(path, text)
        findings.extend(found)
        try:
            doc = json.loads(text)
        except json.JSONDecodeError as exc:
            findings.append(Finding(rel(path), "json_parse", "parse_error", 0, str(exc), "error"))
            file_stats.append(stats)
            continue
        json_findings, json_stats = validate_bundle_json(path, doc)
        findings.extend(json_findings)
        file_stats.append(stats | json_stats)

    for path in JSONL_PATHS:
        if not path.exists():
            missing_files.append(rel(path))
            continue
        text = path.read_text(encoding="utf-8")
        found, stats = scan_text(path, text)
        findings.extend(found)
        file_stats.append(stats)
        entries, parse_errors = parse_jsonl(path)
        for err in parse_errors:
            findings.append(Finding(rel(path), "jsonl_parse", "parse_error", 0, err, "error"))
        alert_findings, alert_stats = validate_alert_entries(path, entries)
        findings.extend(alert_findings)
        jsonl_stats[rel(path)] = alert_stats

    required_presence_by_path = {
        stats["path"]: stats.get("required_presence", {})
        for stats in file_stats
    }
    missing_required = []
    for path, phrases in required_presence_by_path.items():
        for phrase, present in phrases.items():
            if not present:
                missing_required.append({"path": path, "phrase": phrase})

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    status = "ok" if not missing_files and not missing_required and not errors else "needs_review"

    result = {
        "schema_version": "cassandra-public-artifact-safety-validator-v0.2",
        "created": datetime.now(timezone.utc).isoformat(),
        "workspace": str(WORKSPACE),
        "status": status,
        "scope": "bundle notes, bundle manifest/claims JSON, and alert JSONL; local wording/schema check, not legal analysis or publication approval",
        "missing_files": missing_files,
        "file_stats": file_stats,
        "jsonl_stats": jsonl_stats,
        "required_presence_by_path": required_presence_by_path,
        "missing_required": missing_required,
        "findings": [asdict(f) for f in findings],
        "error_count": len(errors),
        "warning_count": len(warnings),
        "caveat": "Passing this check does not assert legal compliance, trusted-list legal effect, signature validity, supervision, public alerting, or publication readiness.",
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
