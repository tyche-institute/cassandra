#!/usr/bin/env python3
"""Refresh index rows for bounded cadence-maintenance outputs.

Local workflow helper only; does not fetch endpoints, validate trusted lists,
clear warnings, or approve publication.
"""
from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "ARTIFACT_INDEX.md"
PROGRESS = ROOT / "HERMES_PROGRESS.md"

CAVEAT = (
    "workflow telemetry only, not endpoint/status evidence, legal effect, "
    "signature validation, supervision, public alerting, regulated trust-service "
    "output, legal review, warning clearance, or publication approval"
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def append_index(rel: str, purpose: str) -> None:
    digest = sha(ROOT / rel)
    with INDEX.open("a", encoding="utf-8") as f:
        f.write(
            f"| `{rel}` | {purpose} | `sha256:{digest}` | "
            f"yes: sha256 computed locally; {CAVEAT}. |\n"
        )


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def main() -> int:
    # Make the newly refreshed cadence output current in the append-only index,
    # then rerun the reference validator that depends on that current row.
    append_index(
        "notes/daily-cadence-status-output.json",
        "Daily-cadence status refreshed during bounded maintenance while next eligible fetch date remains gated.",
    )
    code, out = run([
        ".venv/bin/python",
        "notes/validate_daily_cadence_reference_freshness.py",
        "--workspace",
        ".",
        "--output",
        "notes/daily-cadence-reference-freshness-validation-output.json",
    ])
    if code != 0:
        print(out)
        return code

    refreshed = [
        ("notes/daily-cadence-reference-freshness-validation-output.json", "Daily-cadence reference freshness validation rerun after indexing refreshed cadence output."),
        ("notes/paper-checklist-consistency-validation-output.json", "Paper/checklist consistency validation refreshed during bounded cadence maintenance."),
        ("notes/paper-claim-safety-validation-output.json", "Paper claim-safety validation refreshed during bounded cadence maintenance."),
    ]
    for rel, purpose in refreshed:
        append_index(rel, purpose)

    code, out = run([
        ".venv/bin/python",
        "notes/validate_artifact_index_current_hashes.py",
        "--workspace",
        ".",
        "--output",
        "notes/artifact-index-current-hash-validation-output.json",
    ])
    if code != 0:
        print(out)
        return code
    append_index(
        "notes/artifact-index-current-hash-validation-output.json",
        "Artifact-index current-hash validation output after bounded cadence maintenance indexing.",
    )

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    progress_entry = f"""
## {now} — bounded cadence-maintenance refresh

Performed one bounded maintenance iteration while the live UTC date remains before the next eligible real daily fetch date:

- Confirmed workspace and exact state-file guard at start; `PLAN.md`, `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, `SOURCES.md`, and `CLAIMS.md` were present, and `BLOCKED.md` was absent. No bootstrap registers were recreated or overwritten.
- Read `PLAN.md`, `SOURCES.md`, `CLAIMS.md`, and recent bounded tails of oversized `HERMES_PROGRESS.md` / `ARTIFACT_INDEX.md` for resumption context.
- Checked live UTC time with `date -u +%Y-%m-%dT%H:%M:%S.%NZ`; the date remained `2026-05-21`, so no real fetch/normalize/diff/bundle/alert workflow was run and no dated snapshot outputs were overwritten.
- Refreshed `notes/daily-cadence-status-output.json`; it reported status `ok`, latest completed local lineage `2026-05-22`, today_utc `2026-05-21`, future_completed_dates_relative_to_today `["2026-05-22"]`, and next_eligible_date `2026-05-23`.
- Refreshed bounded local validators: `notes/daily-cadence-reference-freshness-validation-output.json` status `ok` after indexing the refreshed cadence hash, `notes/paper-checklist-consistency-validation-output.json` status `ok`, and `notes/paper-claim-safety-validation-output.json` status `ok` with preserved caveated warnings.
- Ran `.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output notes/artifact-index-current-hash-validation-output.json`; exit `0`, status `ok`, with duplicate rows preserved as append-only maintenance context and current matching hashes present.
- Updated `ARTIFACT_INDEX.md` with current hashes for the refreshed cadence/validator outputs and this validation output.
- Did not fetch external sources, overwrite dated snapshots, dereference raw listed names, publish, push, upload, or modify sibling workspaces. All outputs remain local workflow/release-readiness telemetry only; they do not assert endpoint stability, legal effect, absence or presence of legally relevant change, signature validity, supervision, public alerting, listed-entity status, regulated trust-service output, legal review, warning clearance, or publication approval.

Next action: when UTC date reaches 2026-05-23 or later, run the guarded real daily fetch/normalize/diff/bundle/alert workflow; before that, perform only bounded aggregate-only validator or paper maintenance.
"""
    with PROGRESS.open("a", encoding="utf-8") as f:
        f.write(progress_entry)
    append_index(
        "HERMES_PROGRESS.md",
        "Append-only progress diary updated with bounded cadence-maintenance refresh and next action.",
    )
    append_index(
        "ARTIFACT_INDEX.md",
        "Artifact index updated with bounded cadence-maintenance output hashes and progress diary row.",
    )
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
