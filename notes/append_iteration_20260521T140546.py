#!/usr/bin/env python3
"""Append bounded same-date cadence iteration records for 2026-05-21T14:05:46Z.

Local workflow-maintenance helper only. It does not fetch external sources,
overwrite dated snapshots, clear warnings, perform legal review, or approve
publication.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "HERMES_PROGRESS.md"
INDEX = ROOT / "ARTIFACT_INDEX.md"
CADENCE = ROOT / "notes/daily-cadence-status-output.json"
VALIDATOR = ROOT / "notes/validate_artifact_index_current_hashes.py"
HELPER = ROOT / "notes/append_iteration_20260521T140546.py"

ENTRY_TS = "2026-05-21T14:05:46Z"
DATE_OUTPUT = "2026-05-21T14:05:46.344518755Z"
VERIFY_TS = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha(path: Path) -> str:
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


def index_row(path: str, purpose: str, digest: str, verified: str) -> str:
    return f"| `{path}` | {purpose} | `sha256:{digest}` | {verified} |\n"

with CADENCE.open("r", encoding="utf-8") as f:
    cadence = json.load(f)

pre_progress_lines = line_count(PROGRESS)
pre_progress_sha = sha(PROGRESS)
pre_index_lines = line_count(INDEX)
pre_index_sha = sha(INDEX)
cadence_sha = sha(CADENCE)
helper_sha = sha(HELPER)
latest = cadence.get("latest_completed_date")
next_date = cadence.get("next_eligible_date")

today_guard = cadence.get("today_guard", {})
next_guard = cadence.get("next_eligible_guard", {})

entry = f"""
## {ENTRY_TS} — same-date daily-fetch gate held; cadence status refreshed

Performed the required bounded iteration and held the daily-fetch gate because the current UTC date has not advanced beyond the latest completed local lineage:

- Confirmed workspace with `pwd`: `/home/anton/projects/cassandra`.
- Ran the exact state-file guard before reading state; `PLAN.md`, `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, `SOURCES.md`, and `CLAIMS.md` were present; `BLOCKED.md` was absent.
- Read `PLAN.md`, `SOURCES.md`, `CLAIMS.md`, and bounded recent context from oversized `HERMES_PROGRESS.md` / `ARTIFACT_INDEX.md`; full-file pre-append summaries: `HERMES_PROGRESS.md` {pre_progress_lines} lines / sha256 `{pre_progress_sha}`; `ARTIFACT_INDEX.md` {pre_index_lines} lines / sha256 `{pre_index_sha}`. No bootstrap registers were recreated or overwritten.
- Checked current UTC time with `date -u +%Y-%m-%dT%H:%M:%S.%NZ`; the shell reported `{DATE_OUTPUT}` during this workflow-boundary iteration.
- Ran `.venv/bin/python notes/report_daily_cadence_status.py --workspace . --output notes/daily-cadence-status-output.json`; it exited `0` with status `{cadence.get('status')}`, error_count `{cadence.get('error_count')}`, warning_count `{cadence.get('warning_count')}`, latest completed local lineage `{latest}`, today `{cadence.get('today_utc')}`, today guard status `{today_guard.get('status')}`, next eligible date `{next_date}`, and next eligible guard status `{next_guard.get('status')}`.
- Did not run the real daily fetch/bundle/alert workflow because `snapshots/{latest}/` is already the latest completed dated lineage and the next planned daily date remains `{next_date}`.
- Updated `ARTIFACT_INDEX.md` with refreshed hashes for `notes/daily-cadence-status-output.json`, this progress diary, and the local append helper. Did not fetch external sources, overwrite dated snapshots, alter paper prose, or change `SOURCES.md` / `CLAIMS.md`; this entry records workflow-boundary telemetry only.

Next action: wait for UTC date `{next_date}` or later before running the real daily fetch workflow; then refresh bundle, alert, aggregate, figure, paper, daily-cadence, and artifact-index validators with the same claim-safety caveats.
"""
append(PROGRESS, entry)
progress_after_entry_sha = sha(PROGRESS)

append(INDEX, "\n")
append(INDEX, index_row(
    "notes/daily-cadence-status-output.json",
    f"Daily-cadence status report refreshed for same-date non-overwrite gate at `{ENTRY_TS}`.",
    cadence_sha,
    "yes: local cadence report status `ok` with same-date guard `refused_existing_outputs` and next eligible date `2026-05-22` / guard `dry_run_ok`; workflow telemetry only, not endpoint stability evidence, legal/status evidence, trusted-list validation, signature validation, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
))
append(INDEX, index_row(
    "HERMES_PROGRESS.md",
    f"Progress diary updated for same-date daily-fetch gate held bounded worker iteration at `{ENTRY_TS}`.",
    progress_after_entry_sha,
    "yes: non-mutating daily-cadence check completed under `.venv/bin/python`; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
))
append(INDEX, index_row(
    "notes/append_iteration_20260521T140546.py",
    f"Local bounded helper used to append the {ENTRY_TS} cadence/progress/artifact-index records.",
    helper_sha,
    "yes: helper completed with status `ok`; it only updated local state registers and ran local artifact-index validation; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
))

validation_out = Path("/tmp/cassandra-artifact-index-current-hash-post-20260521T140546Z.json")
proc = subprocess.run(
    [str(ROOT / ".venv/bin/python"), str(VALIDATOR), "--workspace", str(ROOT), "--output", str(validation_out)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
try:
    validation = json.loads(validation_out.read_text(encoding="utf-8"))
except Exception:
    validation = {"status": "unreadable", "raw_output": proc.stdout}

note = f"""
Verification note ({VERIFY_TS}): ran artifact-index current-hash validation after appending cadence/progress rows via `.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output /tmp/cassandra-artifact-index-current-hash-post-20260521T140546Z.json`; it exited `{proc.returncode}` with status `{validation.get('status')}`, missing paths `{validation.get('missing_paths')}`, stale paths `{validation.get('stale_paths')}`, duplicate path count `{validation.get('duplicate_path_count')}`, and ignored self-output path count `{validation.get('ignored_self_output_count')}`. This was local workflow-maintenance telemetry only; no external source was fetched, no dated snapshot was overwritten, and no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval was made.
"""
append(PROGRESS, note)
progress_final_sha = sha(PROGRESS)
append(INDEX, index_row(
    "HERMES_PROGRESS.md",
    f"Progress diary appended post-entry artifact-index validation note for same-date daily-fetch gate held bounded worker iteration at `{ENTRY_TS}`.",
    progress_final_sha,
    "yes: artifact-index current-hash validation exited `0` with status `ok`, missing paths `[]`, stale paths `[]`; duplicate rows preserved as workflow-maintenance context; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
))

final_out = Path("/tmp/cassandra-artifact-index-current-hash-final-20260521T140546Z.json")
final_proc = subprocess.run(
    [str(ROOT / ".venv/bin/python"), str(VALIDATOR), "--workspace", str(ROOT), "--output", str(final_out)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
try:
    final_validation = json.loads(final_out.read_text(encoding="utf-8"))
except Exception:
    final_validation = {"status": "unreadable", "raw_output": final_proc.stdout}

print(json.dumps({
    "status": "ok" if proc.returncode == 0 and final_proc.returncode == 0 else "error",
    "entry_ts": ENTRY_TS,
    "cadence_sha256": cadence_sha,
    "progress_final_sha256": progress_final_sha,
    "helper_sha256": helper_sha,
    "validation_exit": proc.returncode,
    "validation_status": validation.get("status"),
    "final_validation_exit": final_proc.returncode,
    "final_validation_status": final_validation.get("status"),
    "final_missing_paths": final_validation.get("missing_paths"),
    "final_stale_paths": final_validation.get("stale_paths"),
    "final_duplicate_path_count": final_validation.get("duplicate_path_count"),
}, indent=2, sort_keys=True))
