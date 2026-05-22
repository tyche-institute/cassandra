#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "HERMES_PROGRESS.md"
text = path.read_text(encoding="utf-8")
marker = "\n### 2026-05-20T23:22:54Z\n"
idx = text.rfind(marker)
if idx == -1:
    raise SystemExit("marker not found")
entry = """
### 2026-05-20T23:22:54Z

Added failure-mode and recovery discipline paper prose with bounded verification:
- Confirmed workspace with `pwd`: `/home/anton/projects/cassandra`.
- Ran the exact state-file guard; `PLAN.md`, `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, `SOURCES.md`, and `CLAIMS.md` were present; `BLOCKED.md` was absent.
- Read `PLAN.md`, bounded state-register ranges, `SOURCES.md`, `CLAIMS.md`, and `/home/anton/projects/tyche-research-vault/AGENT.md` before touching public-facing paper prose. `HERMES_PROGRESS.md` and `ARTIFACT_INDEX.md` exceed single-read safety limits, so they were read by bounded ranges/tail rather than overwritten.
- Checked current UTC date with `date -u +%F` and `date -u +%FT%TZ`; UTC date is still 2026-05-20, so no same-date daily fetch was run and no mature snapshot, normalization, diff, baseline, or bundle outputs were overwritten.
- Refreshed the same-date daily-run preflight guard outputs in `notes/daily-run-2026-05-20-preflight-output.json` and `notes/daily-run-2026-05-20-preflight-run.json`; status remained `refused_existing_outputs`.
- Added `notes/append_failure_modes_section.py` and inserted `## Failure-mode and recovery discipline` into `paper/draft.md`. The 292-word section frames endpoint failures, parser exceptions, and overwrite guards as workflow telemetry before research interpretation, with caveats against legal-effect, signature-validation, supervision, public-alerting, and publication-approval readings.
- Verification commands: `.venv/bin/python -m py_compile notes/append_failure_modes_section.py`; `.venv/bin/python notes/append_failure_modes_section.py > notes/paper-failure-modes-section-run.json`; `.venv/bin/python notes/validate_paper_claim_safety.py > notes/paper-claim-safety-validation-run.json`; `.venv/bin/python notes/validate_paper_section_order.py --workspace . --output notes/paper-section-order-validation-output.json > notes/paper-section-order-validation-run.json`; `.venv/bin/python notes/validate_paper_evidence_refs.py --workspace . --output notes/paper-evidence-reference-validation-output.json > notes/paper-evidence-reference-validation-run.json`; `.venv/bin/python notes/validate_paper_subsection_risk_coverage.py --workspace . --output notes/paper-subsection-risk-coverage-validation-output.json > notes/paper-subsection-risk-coverage-validation-run.json`; `.venv/bin/python notes/validate_artifact_index_current_hashes.py --workspace . --output notes/artifact-index-current-hash-validation-output.json > notes/artifact-index-current-hash-validation-run.json`. Final commands exited 0.
- Final validation statuses: failure-mode helper `ok` with zero errors and 292 words; paper claim-safety validator `ok` with zero hard errors and two caveated warnings; paper section-order validator `ok`; paper evidence-reference validator `ok` with duplicate-row maintenance warning only; paper subsection-risk validator `ok`; final ARTIFACT_INDEX current-hash validator `ok` with zero missing paths, zero stale paths, and duplicate-row maintenance warnings only.
- Updated `ARTIFACT_INDEX.md` and `CLAIMS.md` with hashes and cautious wording for the new section, helper, same-date preflight refresh, refreshed paper validators, state-update helper, and final artifact-index validation outputs.

Next action: if UTC date has advanced, run `.venv/bin/python run_daily.py --workspace . --date <YYYY-MM-DD> --output notes/daily-run-<YYYY-MM-DD>-output.json > notes/daily-run-<YYYY-MM-DD>-run.json`, then run `create_bundle.py` and `alert_rollup.py`; otherwise continue aggregate-only paper work or extend multi-day readiness validation after a second completed dated snapshot exists.
"""
path.write_text(text[:idx] + "\n" + entry.lstrip(), encoding="utf-8")
print("fixed progress entry")
