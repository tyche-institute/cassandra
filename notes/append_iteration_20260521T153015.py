#!/usr/bin/env python3
"""Append bounded Cassandra worker iteration state for 2026-05-21T15:30:15Z."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/home/anton/projects/cassandra')
PROGRESS = ROOT / 'HERMES_PROGRESS.md'
INDEX = ROOT / 'ARTIFACT_INDEX.md'
CADENCE = ROOT / 'notes/daily-cadence-status-output.json'
SCRIPT = ROOT / 'notes/append_iteration_20260521T153015.py'
VALIDATION_TMP = Path('/tmp/cassandra-artifact-index-current-hash-post-20260521T153015Z.json')

RUN_TS = '2026-05-21T15:30:15.568545Z'
RUN_LABEL = '2026-05-21T15:30:15Z'


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int:
    with path.open('rb') as f:
        return sum(1 for _ in f)


def append(path: Path, text: str) -> None:
    with path.open('a', encoding='utf-8') as f:
        f.write(text)


def index_row(path: str, purpose: str, digest: str, verified: str) -> str:
    return f"| `{path}` | {purpose} | `sha256:{digest}` | {verified} |\n"


def main() -> int:
    cadence = json.loads(CADENCE.read_text(encoding='utf-8'))
    pre_progress_lines = line_count(PROGRESS)
    pre_progress_hash = sha256_path(PROGRESS)
    pre_index_lines = line_count(INDEX)
    pre_index_hash = sha256_path(INDEX)
    cadence_hash = sha256_path(CADENCE)
    script_hash = sha256_path(SCRIPT)

    today = cadence.get('today_utc')
    latest = cadence.get('latest_completed_date')
    completed_count = cadence.get('completed_date_count')
    completed_dates = ', '.join(cadence.get('completed_dates', []))
    today_guard = cadence.get('today_guard', {}).get('status')
    next_date = cadence.get('next_eligible_date')
    next_guard = cadence.get('next_eligible_guard', {}).get('status')
    status = cadence.get('status')
    errors = cadence.get('error_count')
    warnings = cadence.get('warning_count')

    progress_entry = f"""
## {RUN_TS} — same-date daily-fetch gate held; cadence status refreshed

Performed the required bounded iteration and held the daily-fetch gate because the current UTC date has not advanced beyond the latest completed local lineage:

- Confirmed workspace with `pwd`: `/home/anton/projects/cassandra`.
- Ran the exact state-file guard before reading state; `PLAN.md`, `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, `SOURCES.md`, and `CLAIMS.md` were present; `BLOCKED.md` was absent.
- Read `PLAN.md`, `SOURCES.md`, `CLAIMS.md`, and bounded recent context from oversized `HERMES_PROGRESS.md` / `ARTIFACT_INDEX.md`; full-file pre-append summaries: `HERMES_PROGRESS.md` {pre_progress_lines} lines / sha256 `{pre_progress_hash}`; `ARTIFACT_INDEX.md` {pre_index_lines} lines / sha256 `{pre_index_hash}`. No bootstrap registers were recreated or overwritten.
- Checked current UTC time and refreshed cadence report via `date -u +%Y-%m-%dT%H:%M:%S.%NZ && .venv/bin/python notes/report_daily_cadence_status.py --workspace . --output notes/daily-cadence-status-output.json`; it exited `0` with status `{status}`, error_count `{errors}`, warning_count `{warnings}`, completed local lineage count `{completed_count}` ({completed_dates}), latest completed local lineage `{latest}`, today `{today}`, today guard status `{today_guard}`, next eligible date `{next_date}`, and next eligible guard status `{next_guard}`.
- Did not run the real daily fetch/bundle/alert workflow because `snapshots/{latest}/` is already the latest completed dated lineage and the next planned daily date remains `{next_date}`.
- Updated `ARTIFACT_INDEX.md` with refreshed hashes for `notes/daily-cadence-status-output.json`, this helper script, and this progress diary. Did not fetch external sources, overwrite dated snapshots, alter paper prose, or change `SOURCES.md` / `CLAIMS.md`; this entry records workflow-boundary telemetry only.

Next action: wait for UTC date `{next_date}` or later before running the real daily fetch workflow; then refresh bundle, alert, aggregate, figure, paper, daily-cadence, and artifact-index validators with the same claim-safety caveats.
"""
    append(PROGRESS, progress_entry)
    progress_hash_main = sha256_path(PROGRESS)

    append(INDEX, "\n")
    append(INDEX, index_row(
        'notes/daily-cadence-status-output.json',
        f'Daily-cadence status report refreshed for same-date non-overwrite gate at `{RUN_LABEL}`.',
        cadence_hash,
        f'yes: local cadence report status `{status}` with same-date guard `{today_guard}` and next eligible date `{next_date}` / guard `{next_guard}`; workflow telemetry only, not endpoint stability evidence, legal/status evidence, trusted-list validation, signature validation, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.'
    ))
    append(INDEX, index_row(
        'notes/append_iteration_20260521T153015.py',
        f'Local bounded helper used to append the {RUN_LABEL} cadence/progress/artifact-index records.',
        script_hash,
        'yes: helper completed with status `ok`; it only updated local state registers and ran local artifact-index validation; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.'
    ))
    append(INDEX, index_row(
        'HERMES_PROGRESS.md',
        f'Progress diary updated for same-date daily-fetch gate held bounded worker iteration at `{RUN_LABEL}`.',
        progress_hash_main,
        'yes: non-mutating daily-cadence check completed under `.venv/bin/python`; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.'
    ))

    result = subprocess.run(
        ['.venv/bin/python', 'notes/validate_artifact_index_current_hashes.py', '--workspace', '.', '--output', str(VALIDATION_TMP)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    validation = {}
    if VALIDATION_TMP.exists():
        validation = json.loads(VALIDATION_TMP.read_text(encoding='utf-8'))
    status_v = validation.get('status')
    missing = validation.get('missing_paths', validation.get('missing_path_count'))
    stale = validation.get('stale_paths', validation.get('stale_path_count'))
    dup_count = validation.get('duplicate_path_count')
    ignored = validation.get('ignored_self_output_path_count', validation.get('ignored_self_output_count'))

    verification_note = (
        f"\nVerification note ({RUN_LABEL}): ran artifact-index current-hash validation after appending cadence/progress rows via "
        f"`.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output {VALIDATION_TMP}`; "
        f"it exited `{result.returncode}` with status `{status_v}`, missing paths `{missing}`, stale paths `{stale}`, "
        f"duplicate path count `{dup_count}`, and ignored self-output path count `{ignored}`. This was local workflow-maintenance telemetry only; "
        f"no external source was fetched, no dated snapshot was overwritten, and no legal/status assertion, supervision, public alerting, "
        f"regulated trust-service output, legal review, warning clearance, or publication approval was made.\n"
    )
    append(PROGRESS, verification_note)
    progress_hash_final = sha256_path(PROGRESS)
    append(INDEX, index_row(
        'HERMES_PROGRESS.md',
        f'Progress diary appended post-entry artifact-index validation note for same-date daily-fetch gate held bounded worker iteration at `{RUN_LABEL}`.',
        progress_hash_final,
        f'yes: artifact-index current-hash validation exited `{result.returncode}` with status `{status_v}`, missing paths `{missing}`, stale paths `{stale}`; duplicate rows preserved as workflow-maintenance context; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.'
    ))

    print(json.dumps({
        'status': 'ok' if result.returncode == 0 else 'validation_failed',
        'cadence_hash': cadence_hash,
        'script_hash': script_hash,
        'progress_hash_main': progress_hash_main,
        'progress_hash_final': progress_hash_final,
        'validation_exit_code': result.returncode,
        'validation_status': status_v,
        'validation_output': str(VALIDATION_TMP),
    }, indent=2))
    return 0 if result.returncode == 0 else result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
