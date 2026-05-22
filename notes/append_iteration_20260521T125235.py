from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/home/anton/projects/cassandra')
START = '2026-05-21T12:52:35Z'
PRE_PROGRESS_SHA = '6ba391d8e7f9542846ec6088da17d56bbea5664fbe14e0f3850260c6f92b2145'
PRE_INDEX_SHA = '327fead1656bd3bc7ed14a1d10a9b22505876cc7d070959acdff038c012b1642'
PRE_PROGRESS_LINES = 5107
PRE_INDEX_LINES = 1876
DATE_OUTPUT = '2026-05-21T12:52:35.927144818Z'
CADENCE_PATH = ROOT / 'notes/daily-cadence-status-output.json'
PROGRESS_PATH = ROOT / 'HERMES_PROGRESS.md'
INDEX_PATH = ROOT / 'ARTIFACT_INDEX.md'


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int:
    with path.open('rb') as f:
        return sum(1 for _ in f)

cadence = json.loads(CADENCE_PATH.read_text(encoding='utf-8'))
entry = f"""

## 2026-05-21T12:52:35Z — same-date daily-fetch gate held; cadence status refreshed

Performed the required bounded iteration and held the daily-fetch gate because the current UTC date has not advanced beyond the latest completed local lineage:

- Confirmed workspace with `pwd`: `/home/anton/projects/cassandra`.
- Ran the exact state-file guard before reading state; `PLAN.md`, `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, `SOURCES.md`, and `CLAIMS.md` were present; `BLOCKED.md` was absent.
- Read `PLAN.md`, `SOURCES.md`, `CLAIMS.md`, and bounded recent context from oversized `HERMES_PROGRESS.md` / `ARTIFACT_INDEX.md`; full-file pre-append summaries: `HERMES_PROGRESS.md` {PRE_PROGRESS_LINES} lines / sha256 `{PRE_PROGRESS_SHA}`; `ARTIFACT_INDEX.md` {PRE_INDEX_LINES} lines / sha256 `{PRE_INDEX_SHA}`. No bootstrap registers were recreated or overwritten.
- Checked current UTC time with `date -u +%Y-%m-%dT%H:%M:%S.%NZ`; the shell reported `{DATE_OUTPUT}` during this workflow-boundary iteration.
- Ran `.venv/bin/python notes/report_daily_cadence_status.py --workspace . --output notes/daily-cadence-status-output.json`; it exited `0` with status `{cadence['status']}`, error_count `{cadence['error_count']}`, warning_count `{cadence['warning_count']}`, latest completed local lineage `{cadence['latest_completed_date']}`, today `{cadence['today_utc']}`, today guard status `{cadence['today_guard']['status']}`, next eligible date `{cadence['next_eligible_date']}`, and next eligible guard status `{cadence['next_eligible_guard']['status']}`.
- Did not run the real daily fetch/bundle/alert workflow because `snapshots/{cadence['latest_completed_date']}/` is already the latest completed dated lineage and the next planned daily date remains `{cadence['next_eligible_date']}`.
- Updated `ARTIFACT_INDEX.md` with refreshed hashes for `notes/daily-cadence-status-output.json` and this progress diary. Did not fetch external sources, overwrite dated snapshots, alter paper prose, or change `SOURCES.md` / `CLAIMS.md`; this entry records workflow-boundary telemetry only.

Next action: wait for UTC date `{cadence['next_eligible_date']}` or later before running the real daily fetch workflow; then refresh bundle, alert, aggregate, figure, paper, daily-cadence, and artifact-index validators with the same claim-safety caveats.
"""
with PROGRESS_PATH.open('a', encoding='utf-8') as f:
    f.write(entry)

progress_sha_after_entry = sha(PROGRESS_PATH)
cadence_sha = sha(CADENCE_PATH)
with INDEX_PATH.open('a', encoding='utf-8') as f:
    f.write(f"\n| `notes/daily-cadence-status-output.json` | Daily-cadence status report refreshed for same-date non-overwrite gate at `{START}`. | `sha256:{cadence_sha}` | yes: local cadence report status `ok` with same-date guard `refused_existing_outputs` and next eligible date `{cadence['next_eligible_date']}` / guard `dry_run_ok`; workflow telemetry only, not endpoint stability evidence, legal/status evidence, trusted-list validation, signature validation, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval. |\n")
    f.write(f"| `HERMES_PROGRESS.md` | Progress diary updated for same-date daily-fetch gate held bounded worker iteration at `{START}`. | `sha256:{progress_sha_after_entry}` | yes: non-mutating daily-cadence check completed under `.venv/bin/python`; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval. |\n")

validation_tmp = ROOT / 'notes' / 'artifact-index-current-hash-post-20260521T125235Z.json'
proc = subprocess.run([
    str(ROOT / '.venv/bin/python'),
    str(ROOT / 'notes/validate_artifact_index_current_hashes.py'),
    '--workspace', str(ROOT),
    '--output', str(validation_tmp),
], cwd=ROOT, text=True, capture_output=True)
validation = json.loads(validation_tmp.read_text(encoding='utf-8'))
verify_time = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
verification_note = f"""
Verification note ({verify_time}): ran artifact-index current-hash validation after appending cadence/progress rows via `.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output notes/artifact-index-current-hash-post-20260521T125235Z.json`; it exited `{proc.returncode}` with status `{validation.get('status')}`, missing paths `{validation.get('missing_paths')}`, stale paths `{validation.get('stale_paths')}`, duplicate path count `{len(validation.get('duplicate_paths', []))}`, and ignored self-output path count `{len(validation.get('ignored_self_output_paths', []))}`. This was local workflow-maintenance telemetry only; no external source was fetched, no dated snapshot was overwritten, and no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval was made.
"""
with PROGRESS_PATH.open('a', encoding='utf-8') as f:
    f.write(verification_note)
progress_sha_after_note = sha(PROGRESS_PATH)
validation_sha = sha(validation_tmp)
with INDEX_PATH.open('a', encoding='utf-8') as f:
    f.write(f"| `notes/artifact-index-current-hash-post-20260521T125235Z.json` | Artifact-index current-hash validation output for same-date daily-fetch gate held bounded worker iteration at `{START}`. | `sha256:{validation_sha}` | yes: validator exited `{proc.returncode}` with status `{validation.get('status')}`, missing paths `{validation.get('missing_paths')}`, stale paths `{validation.get('stale_paths')}`; duplicate rows preserved as workflow-maintenance context; no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval. |\n")
    f.write(f"| `HERMES_PROGRESS.md` | Progress diary appended post-entry artifact-index validation note for same-date daily-fetch gate held bounded worker iteration at `{verify_time}`. | `sha256:{progress_sha_after_note}` | yes: artifact-index current-hash validation exited `{proc.returncode}` with status `{validation.get('status')}`, missing paths `{validation.get('missing_paths')}`, stale paths `{validation.get('stale_paths')}`; duplicate rows preserved as workflow-maintenance context; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval. |\n")

summary = {
    'status': 'ok' if proc.returncode == 0 and validation.get('status') == 'ok' else 'check',
    'cadence_sha': cadence_sha,
    'progress_sha_after_note': progress_sha_after_note,
    'validation_sha': validation_sha,
    'validation_status': validation.get('status'),
    'validation_returncode': proc.returncode,
    'progress_lines': line_count(PROGRESS_PATH),
    'artifact_index_lines': line_count(INDEX_PATH),
}
print(json.dumps(summary, indent=2, sort_keys=True))
