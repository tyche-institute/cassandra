# Hermes Full-Stack Publication Directive

Date: 2026-05-27
Project: Cassandra
Operator: Anton
Mode: autonomous Zeus/Hermes lane until operator intervention
Stop file: `STOP_CASSANDRA_HERMES`

## Core Sentence

Cassandra: from governance infrastructure to evidence infrastructure.

This is the spine. Do not dilute it. Cassandra is not "an XML parser paper". It is a case study in how public legal-technical governance state becomes observable, hashable, packageable, verifiable, and discussable without pretending to be legal supervision.

## Current Ground Truth

Repository:

- GitHub: `https://github.com/sapsan14/cassandra`
- Live dashboard: `https://cassandra-observatory.pages.dev/`
- Public data index: `https://cassandra-observatory.pages.dev/data/index.json`
- Current public index target: `latest_date=2026-05-27`, `run_count=4`, `eatf_verified_count=4`
- EATF signing profile: `github-secret:cassandra-eatf-key`
- Scheduled workflow: `.github/workflows/cassandra-observatory.yml`, cron `23 3 * * *`
- Full scheduled-compatible run with Cloudflare deploy: GitHub Actions run `26521328723`

Vault handoff:

- `/home/anton/projects/tyche-research-vault/papers/cassandra-trusted-list-observatory/observatory-deployment-handoff-2026-05-27.md`
- `/home/anton/projects/tyche-research-vault/papers/cassandra-trusted-list-observatory/publication-case-packet-2026-05-27.md`

## Immediate Mission

Build Cassandra into a clean publishable paper and case-study kit.

First create a full-stack usable transcript:

- output path: `notes/cassandra-full-stack-usable-transcript-YYYY-MM-DD.md`
- audience: Anton, thesis committee, reviewer, future Hermes/Codex agents
- purpose: a readable end-to-end transcript of what the system does, why the case matters, how the evidence loop works, and which artifacts support each claim
- include: architecture, data flow, EATF evidence boundary, dashboard boundary, paper argument, fixture expansion, risk register, cross-project map, and next experiments

Then improve the actual project and paper in small, commit-ready chunks.

## Why This Case Is Exciting

Cassandra touches a rare surface:

- public governance infrastructure that is machine-readable;
- legally meaningful trust state that can be observed without asserting legal effect;
- public administrative artifacts that can be turned into durable evidence packages;
- a bridge from eIDAS/PKI to AI Act evidence infrastructure;
- a live dashboard where the thesis argument is not just described but operated.

The strong claim is methodological:

> Public governance artifacts can be observed, hashed, bundled, signed, timestamped, displayed, and independently checked while preserving the distinction between evidence integrity and legal interpretation.

## Why So Few Fixtures

The current fixture base is too thin because the project began as an empirical lane, not a software library. The paper needs both real observations and controlled fixtures.

Add fixtures in priority order:

1. Stable no-change fixture: repeated manifests with zero structural diffs.
2. Normalized hash change fixture: same record count, changed canonical content hash.
3. Provider inventory fixture: provider added/removed under a hashed identifier.
4. Service inventory fixture: service key added/removed without naming the real entity.
5. Provider-service-detail fixture: details changed under aggregate-only output.
6. Fetch failure fixture: timeout, HTTP error, redirect, and unreachable pointer.
7. Non-XML fixture: PDF/HTML/non-parseable input handled as skip, not failure.
8. EATF success fixture: package verifies `ok`.
9. EATF tamper fixture: altered payload or AEP fails verification.
10. Missing-signing-input fixture: receipt is explicit `skipped_missing_signing_inputs`.
11. Dashboard fixture: small public index with multiple run states.
12. Claim-safety fixture: forbidden wording scanner catches overclaiming.

Prefer synthetic fixtures that preserve claim safety and do not expose names. Add tests and validation outputs for them.

## Formats And Cards To Produce

Create all useful formats, not noise. Use files that can be cited, reviewed, or reused.

Paper formats:

- `paper/draft.md` improved toward a clean 6k-8k word submission draft.
- `paper/abstract-card.md`
- `paper/venue-fit-card.md`
- `paper/reviewer-objection-card.md`
- `paper/claims-and-evidence-table.md`
- `paper/limitations-card.md`
- `paper/thesis-chapter-card.md`

Dataset/evidence formats:

- `notes/data-dictionary.md`
- `notes/fixture-matrix.md`
- `notes/evidence-package-format.md`
- `notes/replay-capsule.md`
- `notes/public-index-schema.md`
- `notes/eatf-claim-boundary-card.md`
- `notes/mirror-bundle-card.md`

Dashboard/product formats:

- `observatory/public/data/index.json` stays machine-readable.
- Add a public `observatory/public/data/schema.json` if useful.
- Add `observatory/public/data/cards/*.json` for dashboard cards if useful.
- Add a printable dashboard snapshot or card pack if the local toolchain supports it.

Thesis/case formats:

- `notes/thesis-integration-card.md`
- `notes/cassandra-vesta-icarus-xroad-map.md`
- `notes/eidas-to-ai-act-evidence-map.md`
- `notes/case-study-one-pager.md`
- `notes/press-safe-summary.md`

Do not create decorative fluff. Every card must support a paper, thesis chapter, dashboard, or reviewer answer.

## Cross-Project Connections

Connect Cassandra to:

- EATF: AEP packages and offline verification.
- MIRROR: evidence bundles, claims, source manifests.
- PKI Atlas: explanatory trusted-list/tutorial layer, not the empirical corpus.
- X-Road agent attestation: operational public-sector trust infrastructure case.
- Vesta: public web/citation drift as evidence infrastructure.
- Icarus: reproducibility audit as evidence infrastructure.
- Breakable receipts: verifier UX and failure-mode education.
- Tyche thesis hub: paper map and chapter placement.

Do not merge these projects. Build a careful map of distinct roles.

## Paper Shape

Working title:

> Cassandra: From Governance Infrastructure to Evidence Infrastructure

Alternative:

> Watching the Trust List: Longitudinal Structural Observation of Europe's Machine-Readable Trust Infrastructure

Target paper structure:

1. Introduction: the governance-to-evidence move.
2. Background: EU LOTL and trusted-list XML as public administrative artifacts.
3. Method: cautious structural observation, normalization, diffing, bundling, EATF/AEP receipts.
4. System: scheduled GitHub Action, dashboard, public index, evidence package loop.
5. Results: current first series plus fixture-backed behavior.
6. Case analysis: what becomes visible and what remains outside observation.
7. AI/EATF connection: evidence infrastructure for AI governance records, not AI model behavior.
8. Limitations: no legal-status determination, no relying-party validation, no supervision.
9. Conclusion: evidence infrastructure as a computational public-governance method.

## Claim Boundary

Allowed:

- structural observation;
- public-source longitudinal telemetry;
- hash/package verification;
- evidence integrity;
- method demonstration;
- reproducible public-data observatory.

Forbidden unless separately implemented and reviewed:

- trusted-list legal validity;
- signature validity;
- supervisory status;
- compliance judgment;
- public alerting;
- absence of legally relevant change;
- provider-specific claims in prose.

## Operating Loop

Repeat in bounded iterations until `STOP_CASSANDRA_HERMES` exists or Anton intervenes:

1. Pull latest `origin/main`.
2. Read this directive, `PLAN.md`, `CLAIMS.md`, `SOURCES.md`, `ARTIFACT_INDEX.md`, `BLOCKED.md`, `HERMES_PROGRESS.md`, `paper/draft.md`, `observatory/README.md`, and current public `data/index.json`.
3. Choose one coherent improvement unit.
4. Implement it directly.
5. Run relevant tests/validators.
6. Update `HERMES_PROGRESS.md` and, if needed, a concise run log.
7. Commit and push to `origin/main`.
8. Continue.

Preferred early units:

- Create full-stack usable transcript.
- Add fixture matrix and first synthetic fixtures/tests.
- Improve paper intro and system/method sections.
- Add data dictionary and evidence package schema.
- Add dashboard card JSON pack.
- Add cross-case map to thesis/vault if appropriate.

Never stage unrelated local files. Never force-push. Never leak secrets.
