# Cassandra replay capsule

Purpose: compact reviewer/operator/future-agent guide for replaying Cassandra's evidence loop from local artifacts without refetching public endpoints unless an explicit new dated run is intended.

Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

## Replay boundary

This replay capsule is about reproducibility of Cassandra's local research workflow. It does not assert legal effect, trusted-list legal validity, source signature validity, supervisory status, compliance, public alerting, absence of legally relevant change, provider-specific status, or publication approval.

## Inputs to inspect first

| Input | Why it matters |
|---|---|
| `observatory/public/data/index.json` | Public dashboard contract, latest dated runs, aggregate counts, EATF receipt pointers, and caveats. |
| `observatory/public/data/schema.json` | Machine-readable public-index schema. |
| `notes/cassandra-full-stack-usable-transcript-2026-05-27.md` | End-to-end system transcript and artifact map. |
| `notes/fixture-matrix.md` | Synthetic behavior coverage and remaining fixture gaps. |
| `notes/evidence-package-format.md` | MIRROR/EATF package field semantics. |
| `notes/eatf-claim-boundary-card.md` | EATF receipt claim boundary. |
| `notes/mirror-bundle-card.md` | MIRROR-style provenance bundle boundary. |
| `paper/claims-and-evidence-table.md` | Paper-facing claim-to-evidence map. |

## No-fetch replay path

Use this path when the goal is to check the existing evidence series rather than create a new dated observation.

1. Confirm `STOP_CASSANDRA_HERMES` is absent only if operating as an autonomous lane.
2. Inspect `observatory/public/data/index.json` and keep its top-level `caveat` with any copied output.
3. Validate JSON syntax for public data and local validation outputs.
4. Re-run local validators that do not fetch public endpoints.
5. Check current hashes against `ARTIFACT_INDEX.md` rows where validators require freshness.
6. Read date-specific bundle manifests under `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/manifest.json`.
7. Read EATF receipts under `evidence/YYYY-MM-DD/eatf-verification.json` only as package/payload verification evidence.
8. Compare paper/card claims against `paper/claims-and-evidence-table.md` and `CLAIMS.md`.

Suggested local commands:

```bash
.venv/bin/python -m json.tool observatory/public/data/index.json >/tmp/cassandra-index.pretty.json
.venv/bin/python -m json.tool observatory/public/data/schema.json >/tmp/cassandra-schema.pretty.json
.venv/bin/python notes/test_public_index_schema.py
.venv/bin/python notes/test_dashboard_public_index_fixture.py
.venv/bin/python notes/test_claim_safety_fixture.py
.venv/bin/python notes/test_eatf_missing_signing_fixture.py
```

## New dated run path

Use this only when the operator intends to create a new dated observation lineage.

1. Pull `origin/main` with `--ff-only`.
2. Confirm that the target date is not already present, or that overwriting is explicitly intended and safe.
3. Run `run_daily.py` for the target date.
4. Run `create_bundle.py` for the same date.
5. Run `scripts/eatf_package_snapshot.py` only with the configured non-leaking signing profile or explicit missing-input behavior.
6. Run `alert_rollup.py`.
7. Rebuild aggregate public data and dashboard artifacts using the existing project helpers.
8. Validate schema, claim-safety, public-artifact, aggregate, figure, and paper references.
9. Update `ARTIFACT_INDEX.md`, `CLAIMS.md`, `SOURCES.md` if new source/bundle rows were created, and `HERMES_PROGRESS.md`.
10. Commit only related files; leave unrelated local logs unstaged.

## Artifact interpretation rules

- Snapshot manifests record collection attempts, successes, and failures; they are operational telemetry.
- Normalized manifests record local parser/normalizer outputs; they are not trusted-list processors.
- Diff files record structural differences against configured baselines; they are not legal-change determinations.
- MIRROR-style bundles organize local evidence for review; they do not legalize observations.
- EATF/AEP receipts verify Cassandra package/payload bytes and declared hashes; they do not validate source trusted-list legal or signature status.
- Dashboard cards and public JSON display observatory telemetry; they are not public alerts.

## Reviewer replay answer

If a reviewer asks how to reproduce the case without trusting the dashboard, answer:

> Start from the public index and schema, then follow the artifact paths into local manifests, bundle manifests, validation outputs, and EATF receipts. The replay checks whether Cassandra's own evidence package is internally consistent and hash-addressed. It does not transform the observed public governance artifacts into legal conclusions.

## Future-agent stop rule

If a replay step would require legal interpretation, source trusted-list signature validation, supervisory assessment, public warning language, or provider-specific prose, stop and write the issue into `BLOCKED.md` or a review note instead of silently expanding Cassandra's claims.
