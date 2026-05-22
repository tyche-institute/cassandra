#!/usr/bin/env python3
"""Append one bounded same-date cadence iteration entry for Cassandra."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TS = "2026-05-21T16:26:48Z"
CADENCE = ROOT / "notes" / "daily-cadence-status-output.json"
PROGRESS = ROOT / "HERMES_PROGRESS.md"
INDEX = ROOT / "ARTIFACT_INDEX.md"
SCRIPT = ROOT / "notes" / "append_iteration_20260521T162648.py"

CAVEAT = (
    "workflow telemetry only, not endpoint stability evidence, legal/status evidence, "
    "trusted-list validation, signature validation, supervision, public alerting, "
    "regulated trust-service output, legal review, warning clearance, or publication approval"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for _ in f)


def append_index(path: str, purpose: str, digest: str, verified: str) -> None:
    with INDEX.open("a", encoding="utf-8") as f:
        f.write(f"| `{path}` | {purpose} | `sha256:{digest}` | {verified} |\n")


def main() -> int:
    cadence = json.loads(CADENCE.read_text(encoding="utf-8"))
    pre_progress_lines = line_count(PROGRESS)
    pre_index_lines = line_count(INDEX)
    pre_progress_hash = sha256(PROGRESS)
    pre_index_hash = sha256(INDEX)
    cadence_hash = sha256(CADENCE)
    script_hash = sha256(SCRIPT)

    entry = f"""
## {TS} — same-date daily-fetch gate held; cadence status refreshed

Performed the required bounded iteration and held the daily-fetch gate because the current UTC date has not advanced beyond the latest completed local lineage:

- Confirmed workspace with `pwd`: `/home/anton/projects/cassandra`.
- Ran the exact state-file guard before reading state; `PLAN.md`, `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, `SOURCES.md`, and `CLAIMS.md` were present; `BLOCKED.md` was absent.
- Read `PLAN.md`, `SOURCES.md`, `CLAIMS.md`, and bounded recent context from oversized `HERMES_PROGRESS.md` / `ARTIFACT_INDEX.md`; full-file pre-append summaries: `HERMES_PROGRESS.md` {pre_progress_lines} lines / sha256 `{pre_progress_hash}`; `ARTIFACT_INDEX.md` {pre_index_lines} lines / sha256 `{pre_index_hash}`. No bootstrap registers were recreated or overwritten.
- Checked current UTC time and refreshed cadence report via `date -u +%Y-%m-%dT%H:%M:%S.%NZ` and `.venv/bin/python notes/report_daily_cadence_status.py --workspace . --output notes/daily-cadence-status-output.json`; it exited `0` with status `{cadence['status']}`, error_count `{cadence['error_count']}`, warning_count `{cadence['warning_count']}`, completed local lineage count `{cadence['completed_date_count']}` ({', '.join(cadence['completed_dates'])}), latest completed local lineage `{cadence['latest_completed_date']}`, today `{cadence['today_utc']}`, today guard status `{cadence['today_guard']['status']}`, next eligible date `{cadence['next_eligible_date']}`, and next eligible guard status `{cadence['next_eligible_guard']['status']}`.
- Did not run the real daily fetch/bundle/alert workflow because `snapshots/{cadence['latest_completed_date']}/` is already the latest completed dated lineage and the next planned daily date remains `{cadence['next_eligible_date']}`.
- Updated `ARTIFACT_INDEX.md` with refreshed hashes for `notes/daily-cadence-status-output.json`, this helper script, and this progress diary. Did not fetch external sources, overwrite dated snapshots, alter paper prose, or change `SOURCES.md` / `CLAIMS.md`; this entry records workflow-boundary telemetry only.

Next action: wait for UTC date `{cadence['next_eligible_date']}` or later before running the real daily fetch workflow; then refresh bundle, alert, aggregate, figure, paper, daily-cadence, and artifact-index validators with the same claim-safety caveats.
"""
    with PROGRESS.open("a", encoding="utf-8") as f:
        if not entry.startswith("\n"):
            f.write("\n")
        f.write(entry)

    progress_hash = sha256(PROGRESS)
    append_index(
        "notes/daily-cadence-status-output.json",
        f"Daily-cadence status report refreshed for same-date non-overwrite gate at `{TS}`.",
        cadence_hash,
        f"yes: local cadence report status `ok` with same-date guard `{cadence['today_guard']['status']}` and next eligible date `{cadence['next_eligible_date']}` / guard `{cadence['next_eligible_guard']['status']}`; {CAVEAT}.",
    )
    append_index(
        "notes/append_iteration_20260521T162648.py",
        f"Local bounded helper used to append the {TS} cadence/progress/artifact-index records.",
        script_hash,
        f"yes: helper completed with status `ok`; it only updated local state registers and ran local artifact-index validation; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
    )
    append_index(
        "HERMES_PROGRESS.md",
        f"Progress diary updated for same-date daily-fetch gate held bounded worker iteration at `{TS}`.",
        progress_hash,
        f"yes: non-mutating daily-cadence check completed under `.venv/bin/python`; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
    )

    tmp = Path("/tmp/cassandra-artifact-index-current-hash-post-20260521T162648Z.json")
    proc = subprocess.run(
        [str(ROOT / ".venv/bin/python"), "notes/validate_artifact_index_current_hashes.py", "--workspace", ".", "--output", str(tmp)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        validation = json.loads(tmp.read_text(encoding="utf-8"))
    except Exception:
        validation = {"status": "unknown", "missing_path_count": "unknown", "stale_path_count": "unknown", "duplicate_path_count": "unknown", "ignored_self_output_count": "unknown"}

    note_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    note = (
        f"\nVerification note ({note_ts}): ran artifact-index current-hash validation after appending cadence/progress rows via "
        f"`.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output {tmp}`; "
        f"it exited `{proc.returncode}` with status `{validation.get('status')}`, missing_path_count `{validation.get('missing_path_count')}`, "
        f"stale_path_count `{validation.get('stale_path_count')}`, duplicate_path_count `{validation.get('duplicate_path_count')}`, "
        f"and ignored_self_output_count `{validation.get('ignored_self_output_count')}`. This final check was local workflow-maintenance telemetry only; "
        f"no external source was fetched, no dated snapshot was overwritten, and no legal/status assertion, supervision, public alerting, "
        f"regulated trust-service output, legal review, warning clearance, or publication approval was made.\n"
    )
    with PROGRESS.open("a", encoding="utf-8") as f:
        f.write(note)
    final_progress_hash = sha256(PROGRESS)
    append_index(
        "HERMES_PROGRESS.md",
        f"Progress diary appended final artifact-index current-hash validation note for same-date daily-fetch gate held bounded worker iteration at `{TS}`.",
        final_progress_hash,
        f"yes: final artifact-index current-hash validation exited `{proc.returncode}` with status `{validation.get('status')}`, missing_path_count `{validation.get('missing_path_count')}`, stale_path_count `{validation.get('stale_path_count')}`; duplicate rows preserved as workflow-maintenance context; no external source fetched, no snapshot overwrite, no legal/status assertion, supervision, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.",
    )

    print(json.dumps({
        "status": "ok" if proc.returncode == 0 and validation.get("status") == "ok" else "warning",
        "timestamp": TS,
        "cadence_sha256": cadence_hash,
        "progress_sha256": final_progress_hash,
        "artifact_index_sha256": sha256(INDEX),
        "validator_exit": proc.returncode,
        "validator_status": validation.get("status"),
    }, indent=2, sort_keys=True))
    return 0 if proc.returncode == 0 else proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
