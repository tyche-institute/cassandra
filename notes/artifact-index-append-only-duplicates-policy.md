# ARTIFACT_INDEX append-only duplicate rows policy

Date: 2026-05-21
Scope: Cassandra local workflow-maintenance state registers.

## Decision

`ARTIFACT_INDEX.md` is an append-only research ledger. Duplicate rows for the same artifact path are expected when an artifact is refreshed across iterations. A duplicate path is not, by itself, a cleanup requirement or a validation failure when at least one row for that path matches the artifact's current sha256 and ordinary current-hash validation reports `ok`.

## Rationale

The Cassandra lane records each bounded iteration as local provenance. Rewriting
historical index rows to remove stale hashes would make the ledger less useful
for reconstructing what a worker saw and verified at a previous point in time.
The safer default is to preserve history and add a current matching row after a
refresh. Destructive cleanup, if ever needed for readability, must be a separate
operator-reviewed edit rather than an automatic maintenance step.

## Operational rule

- Preserve historical duplicate rows.
- Add a new row with the current sha256 when an artifact changes.
- Treat duplicate-row counts as warning-context telemetry, not a hard failure,
  when `notes/validate_artifact_index_current_hashes.py` reports zero stale or
  missing ordinary artifacts.
- Use `notes/report_artifact_index_duplicates.py` for diagnostics and
  `notes/propose_artifact_index_duplicate_cleanup.py` only as proposal-only operator-review material; neither helper should rewrite `ARTIFACT_INDEX.md`.
- Do not wire duplicate-row cleanup into release-readiness gates without
  explicit operator review.

## Caveat

This policy is local reproducibility telemetry only. It does not assert endpoint stability, legal effect, signature validity, supervision, listed-entity status, public alerting, regulated trust-service output, legal review, warning clearance, or publication approval.
