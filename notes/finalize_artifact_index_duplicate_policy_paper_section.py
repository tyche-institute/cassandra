#!/usr/bin/env python3
"""Finalize artifact-index duplicate-policy paper-section iteration."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
CLAIMS = WORKSPACE / "CLAIMS.md"
INDEX = WORKSPACE / "ARTIFACT_INDEX.md"
PROGRESS = WORKSPACE / "HERMES_PROGRESS.md"

CAVEAT = "workflow ledger/paper telemetry only; not endpoint/status evidence, legal effect, signature validation, supervision, listed-entity status evidence, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval"

ARTIFACTS = [
    ("notes/append_artifact_index_duplicate_policy_section.py", "Helper that appends and validates the cautious artifact-index append-only duplicate-row paper subsection."),
    ("paper/draft.md", "Paper draft updated with artifact-index append-only duplicate-row policy subsection and local evidence references."),
    ("notes/paper-artifact-index-duplicate-policy-section-check-output.json", "Local check output for artifact-index duplicate-row policy paper subsection."),
    ("notes/paper-claim-safety-validation-output.json", "Paper claim-safety validation refreshed after artifact-index duplicate-row policy subsection."),
    ("notes/paper-section-order-validation-output.json", "Paper section-order validation refreshed after artifact-index duplicate-row policy subsection."),
    ("notes/paper-evidence-reference-validation-output.json", "Paper evidence-reference validation refreshed after artifact-index duplicate-row policy subsection."),
    ("notes/paper-subsection-risk-coverage-validation-output.json", "Paper subsection risk-coverage validation refreshed after artifact-index duplicate-row policy subsection."),
    ("notes/paper-checklist-consistency-validation-output.json", "Paper/checklist consistency validation refreshed after artifact-index duplicate-row policy subsection."),
    ("notes/paper-aggregate-only-naming-validation-output.json", "Aggregate-only paper naming validation refreshed after artifact-index duplicate-row policy subsection."),
    ("notes/artifact-index-append-only-duplicates-policy-validation-output.json", "Append-only duplicate-row policy validation refreshed after paper subsection linkage."),
    ("notes/finalize_artifact_index_duplicate_policy_paper_section.py", "Finalizer for artifact-index duplicate-row policy paper-section iteration."),
]


def sha256(rel: str) -> str:
    return hashlib.sha256((WORKSPACE / rel).read_bytes()).hexdigest()


def append_index(rel: str, purpose: str, digest: str | None = None) -> None:
    digest = digest or sha256(rel)
    with INDEX.open("a", encoding="utf-8") as fh:
        fh.write(f"| `{rel}` | {purpose} | `sha256:{digest}` | yes: sha256 computed locally; {CAVEAT}. |\n")


def main() -> int:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    claim = (
        "| The paper draft now includes a cautious artifact-index append-only duplicate-row policy subsection that frames duplicate rows as local ledger provenance when current-hash validation remains clean, not as warning clearance or evidence about external trusted-list status. "
        "| `paper/draft.md`; `notes/append_artifact_index_duplicate_policy_section.py`; `notes/paper-artifact-index-duplicate-policy-section-check-output.json`; `notes/artifact-index-append-only-duplicates-policy.md`; `notes/artifact-index-append-only-duplicates-policy-validation-output.json`; refreshed paper validators. "
        "| Low for local ledger-maintenance semantics; medium if duplicate-row warnings are mistaken for endpoint/status evidence, legal effect, signature validation, supervision, public alerting, regulated trust-service output, warning clearance, legal review, or publication approval. "
        "| The added subsection treats duplicate ARTIFACT_INDEX rows as append-only local provenance only; it does not assert endpoint stability, structural trusted-list change, legal effect, signature validity, supervision, listed-entity status, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval. |\n"
    )
    if claim not in CLAIMS.read_text(encoding="utf-8"):
        CLAIMS.open("a", encoding="utf-8").write(claim)

    for rel, purpose in ARTIFACTS:
        append_index(rel, purpose)
    append_index("CLAIMS.md", "Claims register updated with cautious artifact-index duplicate-row policy paper-section claim.")

    print(f"finalizer indexed {len(ARTIFACTS) + 1} artifacts at {now}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
