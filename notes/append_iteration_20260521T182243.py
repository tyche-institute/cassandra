#!/usr/bin/env python3
"""Append bounded Cassandra worker iteration records for a same-date cadence gate."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "HERMES_PROGRESS.md"
INDEX = ROOT / "ARTIFACT_INDEX.md"
CADENCE = ROOT / "notes/daily-cadence-status-output.json"

ITER_TS = "2026-05-21T18:22:43.075785Z"
DATE_CMD_OUTPUT = "2026-05-21T18:22:43.075785887Z"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int:
    return path.read_text(encoding="utf-8").count("\n")


def append(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def artifact_row(path: str, purpose: str, digest: str, verified: str) -> str:
    return f"| `{path}` | {purpose} | `sha256:{digest}` | {verified} |\n"


def main() -> int:
    with CADENCE.open("r", encoding="utf-8") as f:
        cadence = json.load(f)

    pre_progress_lines = line_count(PROGRESS)
    pre_progress_hash = sha256(PROGRESS)
    pre_index_lines = line_count(INDEX)
    pre_index_hash = sha256(INDEX)
    cadence_hash = sha256(CADENCE)

    status = cadence.get("status")
    err = cadence.get("error_count")
    warn = cadence.get("warning_count")
    dates = ", ".join(cadence.get("completed_dates", []))
    latest = cadence.get("latest_completed_date")
    today = cadence.get("today_utc")
    today_guard = (cadence.get("today_guard") or {}).get("status")
    next_date = cadence.get("next_eligible_date")
    next_guard = (cadence.get("next_eligible_guard") or {}).get("status")
    completed_count = cadence.get("completed_date_count")

    helper_hash = sha256(Path(__file__).resolve())
    append(INDEX, "\n" + artifact_row(
        "notes/append_iteration_20260521T182243.py",
        f"Local bounded helper used to append the {ITER_TS} cadence/progress/artifact-index records.",
        helper_hash,
        "yes: helper performs only local cadence-refresh bookkeeping and state-register append operations; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval."
    ))
    append(INDEX, artifact_row(
        "notes/daily-cadence-status-output.json",
        f"Daily-cadence status report refreshed for same-date non-overwrite gate at `{ITER_TS}`.",
        cadence_hash,
        f"yes: local cadence report status `{status}` with same-date guard `{today_guard}` and next eligible date `{next_date}` / guard `{next_guard}`; workflow telemetry only, not endpoint stability evidence, legal/status evidence, trusted-list validation, signature validation, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval."
    ))

    progress_entry = f"""

## {ITER_TS} — same-date daily-fetch gate held; cadence status refreshed

Performed the required bounded iteration and held the daily-fetch gate because the current UTC date has not advanced beyond the latest completed local lineage:

- Confirmed workspace with `pwd`: `/home/anton/projects/cassandra`.
- Ran the exact state-file guard before reading state: `PLAN.md` present; `HERMES_PROGRESS.md` present; `ARTIFACT_INDEX.md` present; `SOURCES.md` present; `CLAIMS.md` present; `BLOCKED.md` absent. No bootstrap registers were recreated or overwritten.
- Read `PLAN.md`, `SOURCES.md`, `CLAIMS.md`, recent oversized-state context, and full oversized state-register content through bounded readers: pre-append `HERMES_PROGRESS.md` {pre_progress_lines} lines / sha256 `{pre_progress_hash}` and pre-append `ARTIFACT_INDEX.md` {pre_index_lines} lines / sha256 `{pre_index_hash}`.
- Checked current UTC time with `date -u +%Y-%m-%dT%H:%M:%S.%NZ` (`{DATE_CMD_OUTPUT}`) and refreshed cadence report via `.venv/bin/python notes/report_daily_cadence_status.py --workspace . --output notes/daily-cadence-status-output.json`; command exits were `0` and `0`. Cadence report status `{status}`, error_count `{err}`, warning_count `{warn}`, completed local lineage count `{completed_count}`, completed dates `{dates}`, latest completed local lineage `{latest}`, today `{today}`, today guard status `{today_guard}`, next eligible date `{next_date}`, and next eligible guard status `{next_guard}`.
- Did not run the real daily fetch/bundle/alert workflow because `snapshots/2026-05-21/` is already the latest completed dated lineage and the next planned daily date remains `2026-05-22`.
- Did not fetch external sources, overwrite dated snapshots, alter paper prose, or change `SOURCES.md` / `CLAIMS.md`; this entry records workflow-boundary telemetry only.

Next action: wait for UTC date `2026-05-22` or later before running the real daily fetch workflow; then refresh bundle, alert, aggregate, figure, paper, daily-cadence, and artifact-index validators with the same claim-safety caveats.
"""
    append(PROGRESS, progress_entry)
    progress_hash_after_entry = sha256(PROGRESS)
    append(INDEX, artifact_row(
        "HERMES_PROGRESS.md",
        f"Progress diary updated for same-date daily-fetch gate held bounded worker iteration at `{ITER_TS}`.",
        progress_hash_after_entry,
        "yes: non-mutating daily-cadence check completed under `.venv/bin/python`; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval."
    ))

    mid_output = f"/tmp/cassandra-artifact-index-current-hash-mid-{ITER_TS.replace(':','').replace('-','').replace('.','_')}.json"
    mid = subprocess.run([
        str(ROOT / ".venv/bin/python"),
        "notes/validate_artifact_index_current_hashes.py",
        "--workspace", ".",
        "--output", mid_output,
    ], cwd=ROOT, text=True, capture_output=True)
    mid_data = {}
    try:
        mid_data = json.loads(Path(mid_output).read_text(encoding="utf-8"))
    except Exception:
        pass

    ver_ts = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    verification_note = (
        f"Verification note ({ver_ts}): ran artifact-index current-hash validation after appending cadence/progress rows via "
        f"`.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output {mid_output}`; "
        f"it exited `{mid.returncode}` with status `{mid_data.get('status')}`, missing_path_count `{mid_data.get('missing_path_count')}`, "
        f"stale_path_count `{mid_data.get('stale_path_count')}`, duplicate_path_count `{mid_data.get('duplicate_path_count')}`, "
        f"and ignored_self_output_count `{mid_data.get('ignored_self_output_count')}`. This final check was local workflow-maintenance telemetry only; "
        f"no external source was fetched, no dated snapshot was overwritten, and no legal/status assertion, supervision, public alerting, "
        f"regulated trust-service output, legal review, warning clearance, or publication approval was made.\n"
    )
    append(PROGRESS, verification_note)
    progress_hash_final_note = sha256(PROGRESS)
    append(INDEX, artifact_row(
        "HERMES_PROGRESS.md",
        f"Progress diary appended artifact-index current-hash validation note for same-date daily-fetch gate held bounded worker iteration at `{ITER_TS}`.",
        progress_hash_final_note,
        f"yes: artifact-index current-hash validation exited `{mid.returncode}` with status `{mid_data.get('status')}`, missing_path_count `{mid_data.get('missing_path_count')}`, stale_path_count `{mid_data.get('stale_path_count')}`; duplicate rows preserved as workflow-maintenance context; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval."
    ))

    final_output = f"/tmp/cassandra-artifact-index-current-hash-final-{ITER_TS.replace(':','').replace('-','').replace('.','_')}.json"
    final = subprocess.run([
        str(ROOT / ".venv/bin/python"),
        "notes/validate_artifact_index_current_hashes.py",
        "--workspace", ".",
        "--output", final_output,
    ], cwd=ROOT, text=True, capture_output=True)
    final_data = {}
    try:
        final_data = json.loads(Path(final_output).read_text(encoding="utf-8"))
    except Exception:
        pass

    print(json.dumps({
        "iteration": ITER_TS,
        "cadence_hash": cadence_hash,
        "progress_hash_after_entry": progress_hash_after_entry,
        "progress_hash_after_verification_note": progress_hash_final_note,
        "mid_validator_exit": mid.returncode,
        "mid_validator": mid_data,
        "final_validator_exit": final.returncode,
        "final_validator": final_data,
        "final_output": final_output,
    }, indent=2, sort_keys=True))
    return final.returncode


if __name__ == "__main__":
    raise SystemExit(main())
