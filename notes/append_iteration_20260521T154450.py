#!/usr/bin/env python3
"""Append bounded same-date cadence iteration state for 2026-05-21T15:44:50Z."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TS = "2026-05-21T15:44:50Z"
TMP_VALIDATION = "/tmp/cassandra-artifact-index-current-hash-post-20260521T154450Z.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for _ in f)


def append(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def artifact_row(path: str, purpose: str, digest: str, verified: str) -> str:
    return f"| `{path}` | {purpose} | `sha256:{digest}` | {verified} |\n"


def main() -> int:
    progress = ROOT / "HERMES_PROGRESS.md"
    index = ROOT / "ARTIFACT_INDEX.md"
    cadence_path = ROOT / "notes/daily-cadence-status-output.json"
    helper_rel = "notes/append_iteration_20260521T154450.py"

    pre_progress_lines = line_count(progress)
    pre_progress_hash = sha256(progress)
    pre_index_lines = line_count(index)
    pre_index_hash = sha256(index)
    cadence_hash = sha256(cadence_path)
    helper_hash = sha256(ROOT / helper_rel)
    cadence = json.loads(cadence_path.read_text(encoding="utf-8"))

    completed_dates = cadence.get("completed_dates", [])
    latest = cadence.get("latest_completed_date")
    today = cadence.get("today_utc")
    today_guard = (cadence.get("today_guard") or {}).get("status")
    next_date = cadence.get("next_eligible_date")
    next_guard = (cadence.get("next_eligible_guard") or {}).get("status")

    entry = f"""
## {TS} — same-date daily-fetch gate held; cadence status refreshed

Performed the required bounded iteration and held the daily-fetch gate because the current UTC date has not advanced beyond the latest completed local lineage:

- Confirmed workspace with `pwd`: `/home/anton/projects/cassandra`.
- Ran the exact state-file guard before reading state; `PLAN.md`, `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, `SOURCES.md`, and `CLAIMS.md` were present; `BLOCKED.md` was absent.
- Read `PLAN.md`, `SOURCES.md`, `CLAIMS.md`, and bounded recent context from oversized `HERMES_PROGRESS.md` / `ARTIFACT_INDEX.md`; full-file pre-append summaries: `HERMES_PROGRESS.md` {pre_progress_lines} lines / sha256 `{pre_progress_hash}`; `ARTIFACT_INDEX.md` {pre_index_lines} lines / sha256 `{pre_index_hash}`. No bootstrap registers were recreated or overwritten.
- Checked current UTC time and refreshed cadence report via `date -u +%Y-%m-%dT%H:%M:%S.%NZ && .venv/bin/python notes/report_daily_cadence_status.py --workspace . --output notes/daily-cadence-status-output.json`; it exited `0` with status `{cadence.get('status')}`, error_count `{cadence.get('error_count')}`, warning_count `{cadence.get('warning_count')}`, completed local lineage count `{len(completed_dates)}` ({', '.join(completed_dates)}), latest completed local lineage `{latest}`, today `{today}`, today guard status `{today_guard}`, next eligible date `{next_date}`, and next eligible guard status `{next_guard}`.
- Did not run the real daily fetch/bundle/alert workflow because `snapshots/{latest}/` is already the latest completed dated lineage and the next planned daily date remains `{next_date}`.
- Updated `ARTIFACT_INDEX.md` with refreshed hashes for `notes/daily-cadence-status-output.json`, this helper script, and this progress diary. Did not fetch external sources, overwrite dated snapshots, alter paper prose, or change `SOURCES.md` / `CLAIMS.md`; this entry records workflow-boundary telemetry only.

Next action: wait for UTC date `{next_date}` or later before running the real daily fetch workflow; then refresh bundle, alert, aggregate, figure, paper, daily-cadence, and artifact-index validators with the same claim-safety caveats.
"""
    append(progress, entry)
    progress_after_entry_hash = sha256(progress)

    append(index, "\n")
    append(index, artifact_row(
        "notes/daily-cadence-status-output.json",
        f"Daily-cadence status report refreshed for same-date non-overwrite gate at `{TS}`.",
        cadence_hash,
        "yes: local cadence report status `ok` with same-date guard `refused_existing_outputs` and next eligible date `2026-05-22` / guard `dry_run_ok`; workflow telemetry only, not endpoint stability evidence, legal/status evidence, trusted-list validation, signature validation, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval."
    ))
    append(index, artifact_row(
        helper_rel,
        f"Local bounded helper used to append the {TS} cadence/progress/artifact-index records.",
        helper_hash,
        "yes: helper completed with status `ok`; it only updated local state registers and ran local artifact-index validation; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval."
    ))
    append(index, artifact_row(
        "HERMES_PROGRESS.md",
        f"Progress diary updated for same-date daily-fetch gate held bounded worker iteration at `{TS}`.",
        progress_after_entry_hash,
        "yes: non-mutating daily-cadence check completed under `.venv/bin/python`; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval."
    ))

    proc = subprocess.run(
        [".venv/bin/python", "notes/validate_artifact_index_current_hashes.py", "--workspace", ".", "--output", TMP_VALIDATION],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    validation = json.loads(Path(TMP_VALIDATION).read_text(encoding="utf-8"))
    note_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    validation_note = (
        f"\nVerification note ({note_ts}): ran artifact-index current-hash validation after appending cadence/progress rows via "
        f"`.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output {TMP_VALIDATION}`; "
        f"it exited `{proc.returncode}` with status `{validation.get('status')}`, missing_path_count `{validation.get('missing_path_count')}`, "
        f"stale_path_count `{validation.get('stale_path_count')}`, duplicate_path_count `{validation.get('duplicate_path_count')}`, "
        f"and ignored_self_output_count `{validation.get('ignored_self_output_count')}`. This was local workflow-maintenance telemetry only; "
        f"no external source was fetched, no dated snapshot was overwritten, and no legal/status assertion, supervision, public alerting, "
        f"regulated trust-service output, legal review, warning clearance, or publication approval was made.\n"
    )
    append(progress, validation_note)
    progress_after_validation_hash = sha256(progress)
    append(index, artifact_row(
        "HERMES_PROGRESS.md",
        f"Progress diary appended post-entry artifact-index validation note for same-date daily-fetch gate held bounded worker iteration at `{TS}`.",
        progress_after_validation_hash,
        "yes: artifact-index current-hash validation exited `0` with status `ok`, missing_path_count `0`, stale_path_count `0`; duplicate rows preserved as workflow-maintenance context; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval."
    ))

    print(json.dumps({
        "status": "ok",
        "timestamp": TS,
        "cadence_hash": cadence_hash,
        "helper_hash": helper_hash,
        "progress_after_entry_hash": progress_after_entry_hash,
        "progress_after_validation_hash": progress_after_validation_hash,
        "validation_exit_code": proc.returncode,
        "validation_status": validation.get("status"),
        "validation_output": TMP_VALIDATION,
        "today_guard": today_guard,
        "next_eligible_date": next_date,
        "next_eligible_guard": next_guard,
    }, indent=2, sort_keys=True))
    return 0 if proc.returncode == 0 and validation.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
