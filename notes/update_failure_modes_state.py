#!/usr/bin/env python3
"""Append state-register rows for failure-mode paper section iteration."""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"
CLAIMS = ROOT / "CLAIMS.md"


def sha256(rel: str) -> str:
    h = hashlib.sha256()
    with (ROOT / rel).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

rows = [
    ("paper/draft.md", "Working paper draft extended with a failure-mode and recovery discipline section.", "yes: failure-mode helper and paper claim/section/evidence/risk validators exited 0; research-only recovery caveats retained."),
    ("notes/append_failure_modes_section.py", "Idempotent helper that inserts and checks the paper failure-mode and recovery discipline section.", "yes: py_compile ok; helper run status ok with section word count in range."),
    ("notes/paper-failure-modes-section-check-output.json", "Machine-readable check output for the failure-mode and recovery discipline paper section.", "yes: helper status ok; required cautious fragments present; forbidden hits empty."),
    ("notes/paper-failure-modes-section-run.json", "Captured helper stdout for the failure-mode and recovery discipline section run.", "yes: helper exited 0."),
    ("notes/daily-run-2026-05-20-preflight-output.json", "Refreshed same-date daily-run preflight output confirming non-overwrite guard still refuses existing 2026-05-20 outputs.", "yes: dry-run command exit code 0; status refused_existing_outputs; no dated snapshot/diff overwrite."),
    ("notes/daily-run-2026-05-20-preflight-run.json", "Captured stdout from refreshed same-date daily-run preflight guard.", "yes: dry-run command exit code 0; status refused_existing_outputs."),
    ("notes/paper-claim-safety-validation-output.json", "Refreshed paper claim-safety validation after adding failure-mode section.", "yes: validator exited 0 with status ok and zero hard errors."),
    ("notes/paper-claim-safety-validation-run.json", "Captured stdout from refreshed paper claim-safety validation after failure-mode section.", "yes: validator exited 0."),
    ("notes/paper-section-order-validation-output.json", "Refreshed paper section-order validation after adding failure-mode section.", "yes: validator exited 0 with status ok and expected headings retained."),
    ("notes/paper-section-order-validation-run.json", "Captured stdout from refreshed paper section-order validation after failure-mode section.", "yes: validator exited 0."),
    ("notes/paper-evidence-reference-validation-output.json", "Refreshed paper evidence-reference validation after adding failure-mode section.", "yes: validator exited 0 with status ok; duplicate-row warning is workflow-maintenance only."),
    ("notes/paper-evidence-reference-validation-run.json", "Captured stdout from refreshed paper evidence-reference validation after failure-mode section.", "yes: validator exited 0."),
    ("notes/paper-subsection-risk-coverage-validation-output.json", "Refreshed paper subsection risk-coverage validation after adding failure-mode section.", "yes: validator exited 0 with status ok; configured sections retained required caveats."),
    ("notes/paper-subsection-risk-coverage-validation-run.json", "Captured stdout from refreshed paper subsection risk-coverage validation after failure-mode section.", "yes: validator exited 0."),
    ("notes/failure-modes-section-hashes.txt", "sha256 command output for failure-mode section artifacts and refreshed validation outputs.", "yes: generated locally after verification commands exited 0."),
]

with ARTIFACT_INDEX.open("a", encoding="utf-8") as fh:
    for rel, purpose, verified in rows:
        fh.write(f"| `{rel}` | {purpose} | `sha256:{sha256(rel)}` | {verified} |\n")

claim = "| The paper draft now includes a 292-word failure-mode and recovery discipline section that treats endpoint failures, parser exceptions, and overwrite guards as workflow telemetry before research interpretation. | `paper/draft.md`; `notes/append_failure_modes_section.py`; `notes/paper-failure-modes-section-check-output.json`; refreshed paper claim-safety, section-order, evidence-reference, and subsection-risk validation outputs. | Medium: failure/recovery prose could be overread as operational monitoring or status assessment if caveats are removed; low for current local draft after validators reported zero hard errors. | The added failure-mode section frames recovery as local reproducibility discipline and states that collection failures, parser outcomes, guard refusals, and clean validation output do not assert legal effect, validate signatures, supervise trusted lists, provide public alerting, or imply publication approval. |\n"
with CLAIMS.open("a", encoding="utf-8") as fh:
    fh.write(claim)

print("appended", len(rows), "artifact rows and 1 claim row")
