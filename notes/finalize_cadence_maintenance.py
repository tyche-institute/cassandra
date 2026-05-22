#!/usr/bin/env python3
"""Finalize bounded cadence-maintenance iteration state.

Local workflow helper only; no network fetch, publication, or trusted-list validation.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "ARTIFACT_INDEX.md"
PROGRESS = ROOT / "HERMES_PROGRESS.md"
CLAIMS = ROOT / "CLAIMS.md"
CAVEAT = (
    "workflow telemetry only, not endpoint/status evidence, legal effect, signature validation, "
    "supervision, public alerting, regulated trust-service output, legal review, warning clearance, "
    "or publication approval"
)


def sha(rel: str) -> str:
    h = hashlib.sha256()
    with (ROOT / rel).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def append_index(rel: str, purpose: str) -> None:
    INDEX.open("a", encoding="utf-8").write(
        f"| `{rel}` | {purpose} | `sha256:{sha(rel)}` | yes: sha256 computed locally; {CAVEAT}. |\n"
    )


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return p.returncode, p.stdout + p.stderr


def append_claim_once() -> None:
    marker = "The artifact-index current-hash validator treats ARTIFACT_INDEX.md as self-referential"
    text = CLAIMS.read_text(encoding="utf-8")
    if marker in text:
        return
    CLAIMS.open("a", encoding="utf-8").write(
        "| The artifact-index current-hash validator treats ARTIFACT_INDEX.md as self-referential append-only state while still checking ordinary indexed artifacts for at least one current matching hash row. | "
        "`notes/validate_artifact_index_current_hashes.py`; `notes/artifact-index-current-hash-validation-output.json`; `ARTIFACT_INDEX.md`. | "
        "Low for workflow-maintenance semantics; medium if self-reference handling is mistaken for warning clearance, external timestamping, legal/status evidence, or publication approval. | "
        "The local artifact-index freshness validator ignores only self-referential index/output artifacts for current-row matching and continues to report ordinary stale or missing paths; this is reproducibility telemetry only, not legal compliance, trusted-list legal effect, signature validation, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval. |\n"
    )


def main() -> int:
    code, out = run([".venv/bin/python", "-m", "py_compile", "notes/validate_artifact_index_current_hashes.py", "notes/refresh_cadence_maintenance_index.py"])
    if code:
        print(out)
        return code
    code, out = run([".venv/bin/python", "notes/validate_artifact_index_current_hashes.py", "--workspace", ".", "--output", "notes/artifact-index-current-hash-validation-output.json"])
    print(out)
    if code:
        return code
    result = json.loads((ROOT / "notes/artifact-index-current-hash-validation-output.json").read_text(encoding="utf-8"))
    if result.get("status") != "ok":
        print("artifact index validation did not report ok")
        return 1

    append_claim_once()
    for rel, purpose in [
        ("notes/validate_artifact_index_current_hashes.py", "Artifact-index validator patched to treat append-only ARTIFACT_INDEX.md as self-referential while preserving ordinary current-hash checks."),
        ("notes/refresh_cadence_maintenance_index.py", "One-off bounded cadence-maintenance indexing helper."),
        ("notes/finalize_cadence_maintenance.py", "One-off finalizer for bounded cadence-maintenance state, validation, and progress entry."),
        ("notes/artifact-index-current-hash-validation-output.json", "Artifact-index current-hash validation output after self-reference handling patch and cadence-maintenance indexing."),
        ("CLAIMS.md", "Claims register updated with cautious artifact-index self-reference handling claim."),
    ]:
        append_index(rel, purpose)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    cadence = json.loads((ROOT / "notes/daily-cadence-status-output.json").read_text(encoding="utf-8"))
    freshness = json.loads((ROOT / "notes/daily-cadence-reference-freshness-validation-output.json").read_text(encoding="utf-8"))
    entry = f"""

## {now} — bounded cadence-maintenance refresh finalized

Performed a bounded maintenance follow-up after the cadence status refresh:

- Confirmed the real daily collection gate remained closed: `notes/daily-cadence-status-output.json` reports today_utc `{cadence.get('today_utc')}`, latest completed local lineage `{cadence.get('latest_completed_date')}`, future_completed_dates_relative_to_today `{cadence.get('future_completed_dates_relative_to_today')}`, and next_eligible_date `{cadence.get('next_eligible_date')}`. No real fetch/normalize/diff/bundle/alert workflow was run.
- Indexed the refreshed cadence output and reran `notes/validate_daily_cadence_reference_freshness.py`; status `{freshness.get('status')}`, error_count `{freshness.get('error_count')}`, warning_count `{freshness.get('warning_count')}`.
- Patched `notes/validate_artifact_index_current_hashes.py` so `ARTIFACT_INDEX.md` is treated like validator output as a self-referential append-only artifact: ordinary indexed files still require at least one current matching hash row, while the index file itself is reported under ignored self-output paths with an explicit reason.
- Verification: `.venv/bin/python -m py_compile notes/validate_artifact_index_current_hashes.py notes/refresh_cadence_maintenance_index.py` exited `0`; `.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output notes/artifact-index-current-hash-validation-output.json` exited `0` with status `{result.get('status')}`, missing_path_count `{result.get('missing_path_count')}`, stale_path_count `{result.get('stale_path_count')}`, duplicate_path_count `{result.get('duplicate_path_count')}`, ignored_self_output_count `{result.get('ignored_self_output_count')}`.
- Updated `CLAIMS.md` and `ARTIFACT_INDEX.md` with current hashes for the modified validator, bounded helper scripts, refreshed validator output, claims register, and this diary entry.
- Did not fetch external sources, overwrite dated snapshots, dereference raw listed names, publish, push, upload, or modify sibling workspaces. All outputs remain local workflow/release-readiness telemetry only; they do not assert endpoint stability, legal effect, absence or presence of legally relevant change, signature validity, supervision, public alerting, listed-entity status, regulated trust-service output, legal review, warning clearance, or publication approval.

Next action: when UTC date reaches 2026-05-23 or later, run the guarded real daily fetch/normalize/diff/bundle/alert workflow; before that, perform only bounded aggregate-only validator or paper maintenance.
"""
    PROGRESS.open("a", encoding="utf-8").write(entry)
    append_index("HERMES_PROGRESS.md", "Append-only progress diary updated with finalized bounded cadence-maintenance refresh.")
    append_index("ARTIFACT_INDEX.md", "Artifact index updated with finalized bounded cadence-maintenance hashes and progress diary row.")
    print("finalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
