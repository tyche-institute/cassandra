#!/usr/bin/env python3
"""Append a cautious paper section about ARTIFACT_INDEX duplicate-row policy."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
PAPER = WORKSPACE / "paper" / "draft.md"
OUTPUT = WORKSPACE / "notes" / "paper-artifact-index-duplicate-policy-section-check-output.json"
HEADING = "## Artifact-index append-only duplicate-row policy"
REFERENCES_HEADING = "## References and local evidence"

SECTION = """## Artifact-index append-only duplicate-row policy

Cassandra's `ARTIFACT_INDEX.md` is an append-only ledger rather than a deduplicated catalog. During repeated maintenance iterations, the same path can receive multiple rows because the file's hash changes after a validator refresh, paper edit, or diary append. Those duplicate rows are preserved as provenance when the current-hash validator can still find at least one row whose hash matches the present file bytes. The resulting duplicate count is therefore a maintenance warning and review cue, not an instruction to rewrite historical index rows.

The local policy note, `notes/artifact-index-append-only-duplicates-policy.md`, documents this boundary so that later workers do not "clean" the ledger destructively. Its validator checks the policy against the duplicate report and the current-hash validation output. A clean policy validation means that the no-rewrite/no-auto-cleanup rule is documented and that ordinary indexed artifacts still have current matching hashes. It does not clear warnings, provide external timestamping, perform legal review, validate trusted-list signatures, supervise any trusted list, determine listed-entity status, provide public alerting, or approve publication.

For paper interpretation, duplicate index rows should be described only as local evidence-ledger mechanics. They help explain why repeated validator outputs can produce warning counts even when current-hash validation is otherwise clean. They should not be used as evidence about endpoint stability, structural change in a trusted-list document, public risk, or legal effect. If duplicate-row volume later becomes operationally confusing, the safe response is an operator-reviewed migration or archival policy, not autonomous deletion of ledger history.
"""

REFERENCE_LINES = [
    "- `notes/artifact-index-append-only-duplicates-policy.md`.",
    "- `notes/artifact-index-append-only-duplicates-policy-validation-output.json`.",
    "- `notes/artifact-index-duplicate-report-output.json`.",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    inserted_section = False
    inserted_refs: list[str] = []

    if HEADING not in text:
        if REFERENCES_HEADING not in text:
            raise SystemExit(f"missing anchor: {REFERENCES_HEADING}")
        text = text.replace(REFERENCES_HEADING, SECTION + "\n" + REFERENCES_HEADING, 1)
        inserted_section = True

    lines = text.splitlines()
    ref_idx = None
    for i, line in enumerate(lines):
        if line.strip() == REFERENCES_HEADING:
            ref_idx = i
            break
    if ref_idx is None:
        raise SystemExit(f"missing references heading after section insertion: {REFERENCES_HEADING}")

    existing = set(lines)
    insert_at = len(lines)
    for line in REFERENCE_LINES:
        if line not in existing:
            lines.insert(insert_at, line)
            insert_at += 1
            inserted_refs.append(line)
            existing.add(line)

    new_text = "\n".join(lines) + "\n"
    if new_text != text:
        PAPER.write_text(new_text, encoding="utf-8")

    word_count = len(SECTION.split())
    result = {
        "status": "ok",
        "created": datetime.now(timezone.utc).isoformat(),
        "paper": str(PAPER.relative_to(WORKSPACE)),
        "paper_sha256": sha256(PAPER),
        "section_heading": HEADING,
        "section_inserted": inserted_section,
        "section_word_count": word_count,
        "references_inserted": inserted_refs,
        "caveat": "Local evidence-ledger mechanics only; not warning clearance, legal review, signature validation, trusted-list supervision, listed-entity status evidence, public alerting, regulated trust-service output, endpoint-status evidence, or publication approval.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
