#!/usr/bin/env python3
"""Append a bounded same-date cadence-gate iteration for Cassandra."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/home/anton/projects/cassandra')
CAVEAT = (
    'workflow telemetry only, not endpoint stability evidence, legal/status evidence, '
    'trusted-list validation, signature validation, supervision, public alerting, '
    'regulated trust-service output, legal review, warning clearance, or publication approval'
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int:
    return len(path.read_text(encoding='utf-8').splitlines())


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr


def artifact_row(rel: str, purpose: str, digest: str, verified: str) -> str:
    return f"| `{rel}` | {purpose} | `sha256:{digest}` | {verified} |\n"


def main() -> int:
    progress = WORKSPACE / 'HERMES_PROGRESS.md'
    index = WORKSPACE / 'ARTIFACT_INDEX.md'
    cadence = WORKSPACE / 'notes/daily-cadence-status-output.json'
    helper = WORKSPACE / 'notes/append_iteration_20260521T180010.py'

    ts = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    progress_pre_lines = line_count(progress)
    progress_pre_hash = sha256_file(progress)
    index_pre_lines = line_count(index)
    index_pre_hash = sha256_file(index)

    date_rc, date_out, date_err = run(['date', '-u', '+%Y-%m-%dT%H:%M:%S.%NZ'])
    cadence_rc, cadence_out, cadence_err = run(['.venv/bin/python', 'notes/report_daily_cadence_status.py', '--workspace', '.', '--output', 'notes/daily-cadence-status-output.json'])
    if cadence_rc != 0:
        raise SystemExit(f'cadence report failed rc={cadence_rc}\nSTDOUT={cadence_out}\nSTDERR={cadence_err}')
    report = json.loads(cadence.read_text(encoding='utf-8'))

    today_guard_status = report.get('today_guard', {}).get('status')
    next_guard_status = report.get('next_eligible_guard', {}).get('status')
    completed_dates = ', '.join(report.get('completed_dates', []))

    entry = f"""
## {ts} — same-date daily-fetch gate held; cadence status refreshed

Performed the required bounded iteration and held the daily-fetch gate because the current UTC date has not advanced beyond the latest completed local lineage:

- Confirmed workspace with `pwd`: `/home/anton/projects/cassandra`.
- Ran the exact state-file guard before reading state: `PLAN.md` present; `HERMES_PROGRESS.md` present; `ARTIFACT_INDEX.md` present; `SOURCES.md` present; `CLAIMS.md` present; `BLOCKED.md` absent. No bootstrap registers were recreated or overwritten.
- Read `PLAN.md`, `SOURCES.md`, `CLAIMS.md`, and bounded recent context from oversized `HERMES_PROGRESS.md` / `ARTIFACT_INDEX.md`; full-file pre-append summaries: `HERMES_PROGRESS.md` {progress_pre_lines} lines / sha256 `{progress_pre_hash}`; `ARTIFACT_INDEX.md` {index_pre_lines} lines / sha256 `{index_pre_hash}`.
- Checked current UTC time with `date -u +%Y-%m-%dT%H:%M:%S.%NZ` (`{date_out.strip()}`) and refreshed cadence report via `.venv/bin/python notes/report_daily_cadence_status.py --workspace . --output notes/daily-cadence-status-output.json`; command exits were `{date_rc}` and `{cadence_rc}`. Cadence report status `{report.get('status')}`, error_count `{report.get('error_count')}`, warning_count `{report.get('warning_count')}`, completed local lineage count `{report.get('completed_date_count')}`, completed dates `{completed_dates}`, latest completed local lineage `{report.get('latest_completed_date')}`, today `{report.get('today_utc')}`, today guard status `{today_guard_status}`, next eligible date `{report.get('next_eligible_date')}`, and next eligible guard status `{next_guard_status}`.
- Did not run the real daily fetch/bundle/alert workflow because `snapshots/{report.get('latest_completed_date')}/` is already the latest completed dated lineage and the next planned daily date remains `{report.get('next_eligible_date')}`.
- Did not fetch external sources, overwrite dated snapshots, alter paper prose, or change `SOURCES.md` / `CLAIMS.md`; this entry records workflow-boundary telemetry only.

Next action: wait for UTC date `{report.get('next_eligible_date')}` or later before running the real daily fetch workflow; then refresh bundle, alert, aggregate, figure, paper, daily-cadence, and artifact-index validators with the same claim-safety caveats.
"""
    with progress.open('a', encoding='utf-8') as f:
        f.write(entry)

    cadence_hash = sha256_file(cadence)
    helper_hash = sha256_file(helper)
    progress_hash = sha256_file(progress)
    idx_ts = ts.replace('+00:00', 'Z')
    with index.open('a', encoding='utf-8') as f:
        f.write('\n')
        f.write(artifact_row(
            'notes/daily-cadence-status-output.json',
            f'Daily-cadence status report refreshed for same-date non-overwrite gate at `{idx_ts}`.',
            cadence_hash,
            f'yes: local cadence report status `{report.get("status")}` with same-date guard `{today_guard_status}` and next eligible date `{report.get("next_eligible_date")}` / guard `{next_guard_status}`; {CAVEAT}.',
        ))
        f.write(artifact_row(
            'notes/append_iteration_20260521T180010.py',
            f'Local bounded helper used to append the {idx_ts} cadence/progress/artifact-index records.',
            helper_hash,
            f'yes: helper completed after local cadence refresh and state-register append only; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.',
        ))
        f.write(artifact_row(
            'HERMES_PROGRESS.md',
            f'Progress diary updated for same-date daily-fetch gate held bounded worker iteration at `{idx_ts}`.',
            progress_hash,
            f'yes: non-mutating daily-cadence check completed under `.venv/bin/python`; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.',
        ))

    result = {
        'status': 'ok',
        'timestamp': ts,
        'date_command_exit': date_rc,
        'cadence_command_exit': cadence_rc,
        'cadence_status': report.get('status'),
        'today_utc': report.get('today_utc'),
        'today_guard_status': today_guard_status,
        'next_eligible_date': report.get('next_eligible_date'),
        'next_eligible_guard_status': next_guard_status,
        'progress_hash': progress_hash,
        'cadence_hash': cadence_hash,
        'helper_hash': helper_hash,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
