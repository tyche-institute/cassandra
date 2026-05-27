# Cassandra full-stack usable transcript — 2026-05-27

Audience: Anton, thesis committee, reviewer, and future Hermes/Codex agents.  
Purpose: readable end-to-end transcript of what Cassandra does, why the case matters, how the evidence loop works, and which artifacts support each claim.  
Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

## 0. Claim boundary before the transcript

Cassandra observes public, machine-readable governance artifacts as local research evidence. It does not perform relying-party trusted-list validation, does not determine legal status, does not supervise trusted-service providers, does not validate signatures for operational reliance, does not issue public alerts, and does not prove absence of legally relevant change.

Allowed phrasing: structural observation, public-source longitudinal telemetry, hash/package verification, evidence integrity, method demonstration, reproducible public-data observatory.

Forbidden phrasing unless separately implemented and reviewed: legal validity of a trusted list, signature validity, supervisory status, compliance judgment, public alerting, absence of legally relevant change, and provider-specific prose claims.

## 1. What the system is

Cassandra is a research-only observatory for the public European list-of-lists and the national trusted-list artifacts referenced from saved LOTL snapshots. Its method is to fetch public artifacts, record local provenance, normalize parseable XML for stable comparison, emit cautious structural diffs, bundle evidence, sign/package selected run evidence through EATF/AEP, and publish aggregate dashboard telemetry.

The case is not exciting because it parses XML. It is exciting because it turns a public legal-technical governance surface into evidence infrastructure: observable, hashable, packageable, verifiable, displayable, and discussable while preserving the boundary between evidence integrity and legal interpretation.

Current public endpoints and state:

- Repository: https://github.com/sapsan14/cassandra
- Live dashboard: https://cassandra-observatory.pages.dev/
- Public index: https://cassandra-observatory.pages.dev/data/index.json
- Local public index file: `observatory/public/data/index.json`
- Public index latest date: `2026-05-27`
- Public index run count: `4`
- EATF verified count: `4`
- Scheduled workflow: `.github/workflows/cassandra-observatory.yml`, cron `23 3 * * *`
- EATF signing profile label: `github-secret:cassandra-eatf-key`

## 2. Why this case matters

Cassandra sits on a rare research surface:

1. The inputs are public administrative/governance artifacts, not private logs.
2. The artifacts are legally meaningful in their native ecosystem, but Cassandra treats them only as observable documents.
3. The data can be collected repeatedly into a longitudinal corpus.
4. The evidence can be hashed, bundled, signed, timestamped, and checked offline.
5. The live dashboard can expose method telemetry without pretending to be a regulator, relying party, or compliance monitor.

The methodological claim is narrow but strong:

> Public governance artifacts can be observed, hashed, bundled, signed, timestamped, displayed, and independently checked while preserving the distinction between evidence integrity and legal interpretation.

This connects eIDAS/PKI research to AI Act evidence infrastructure because many AI-governance records will face the same problem: public or semi-public records must be made durable and checkable without turning evidence packaging into substantive legal approval.

## 3. Architecture transcript

Cassandra currently has five working layers.

### 3.1 Collection layer

Primary files:

- `fetch.py`
- `run_daily.py`
- `notes/pointers.json`
- `snapshots/YYYY-MM-DD/manifest.json`
- `snapshots/YYYY-MM-DD/*.xml|*.pdf|*.xtsl` plus adjacent metadata

Transcript:

1. Fetch the EU LOTL XML from the configured public endpoint.
2. Save the raw LOTL file and metadata under `sources/`.
3. Parse the saved LOTL to extract national pointer URLs into `notes/pointers.json`.
4. For a dated run, attempt each LOTL-derived pointer.
5. Save fetched content files and adjacent metadata.
6. Record endpoint failures as observations in the manifest instead of silently dropping them.

Boundary: a successful or failed fetch is an operational observation about this collection run. It is not evidence that a trusted list is valid, invalid, current, obsolete, legally effective, or legally irrelevant.

### 3.2 Normalization and structural parsing layer

Primary files:

- `parse.py`
- `normalized/YYYY-MM-DD/manifest.json`
- `normalized/YYYY-MM-DD/*.xml`

Transcript:

1. Read the dated snapshot manifest.
2. Attempt deterministic XML normalization for XML-like fetched artifacts.
3. Skip non-XML/PDF artifacts as collection telemetry, not as fatal errors.
4. Record parser errors as parser telemetry.
5. Extract coarse structural fields, normalized hashes, signature-shape observations, and hashed provider/service inventory keys.

Boundary: normalization produces comparable local research records. Signature-shape metadata is not relying-party signature validation. Hashed provider/service keys are local comparison handles, not public status identifiers.

### 3.3 Diff layer

Primary files:

- `diff.py`
- `diffs/YYYY-MM-DD.json`
- `baselines/YYYY-MM-DD.json`
- `baselines/current.json`

Transcript:

1. Load the current normalized manifest.
2. Load the configured baseline.
3. Compare comparable records by structural keys.
4. Emit machine-readable diff classes.
5. Preserve aggregate-only and hash-keyed output for provider/service movements.

Observed public-index diff class totals:

| Diff class | Count |
|---|---:|
| listed_document_added | 0 |
| listed_document_removed | 0 |
| normalized_hash_changed | 7 |
| provider_inventory_changed | 0 |
| provider_service_detail_changed | 26 |
| service_inventory_changed | 5 |
| summary_field_changed | 28 |

Boundary: a diff is a structural observation against a configured local baseline. It does not assert legal effect, provider status, signature validity, supervision, or absence of legally relevant change.

### 3.4 Evidence bundle and EATF/AEP layer

Primary files:

- `create_bundle.py`
- `scripts/eatf_package_snapshot.py`
- `bundles/YYYY-MM-DD/snapshot-summary.json`
- `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/manifest.json`
- `evidence/YYYY-MM-DD/cassandra-observation.json`
- `evidence/YYYY-MM-DD/cassandra-observation.aep`
- `evidence/YYYY-MM-DD/eatf-verification.json`

Transcript:

1. Summarize the dated observation run into a snapshot summary.
2. Create a MIRROR-style bundle with manifest, claims, source copies/references, notes, and verification output.
3. Create an EATF/AEP package for selected public evidence material.
4. Verify the EATF/AEP receipt offline and expose the receipt status in the public index.

Boundary: EATF/AEP verification says the package envelope, payload bytes, and declared hashes verify according to the package verifier. It does not say the underlying trusted-list content has legal status, that signatures are operationally valid, or that a supervisor approved anything.

### 3.5 Observatory/dashboard layer

Primary files:

- `notes/aggregate_results.py`
- `notes/render_aggregate_figures.py`
- `scripts/build_observatory_index.py`
- `observatory/public/index.html`
- `observatory/public/data/index.json`
- `observatory/public/data/aggregate-results.json`
- `observatory/public/data/aggregate-results-table.csv`
- `observatory/public/figures/*.svg`

Transcript:

1. Aggregate dated run manifests, diffs, alerts, bundle summaries, and EATF receipts.
2. Emit public JSON/CSV with caveats and hashes.
3. Render aggregate figures.
4. Build the static dashboard data index.
5. Deploy `observatory/public` through GitHub Actions and Cloudflare Pages when secrets are available.

Boundary: the dashboard is a public method demonstration and aggregate evidence index, not an alerting service or legal-status monitor.

## 4. Current data-flow facts from the public index

Current public-index totals:

| Metric | Value |
|---|---:|
| alert_entry_count | 5 |
| diff_change_count | 66 |
| fetch_errors | 5 |
| fetched_content_files | 167 |
| normalization_errors | 4 |
| normalization_skips | 39 |
| normalized_xml_artifacts | 124 |
| pointer_attempts | 172 |
| provider_count_total | 1572 |
| service_count_total | 19086 |

Run table:

| Date | Pointer attempts | Fetched content | Fetch errors | Normalized XML | Normalization errors | Diff changes | EATF status |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-05-20 | 43 | 41 | 2 | 31 | 1 | 0 | ok |
| 2026-05-21 | 43 | 42 | 1 | 31 | 1 | 0 | ok |
| 2026-05-22 | 43 | 42 | 1 | 31 | 1 | 26 | ok |
| 2026-05-27 | 43 | 42 | 1 | 31 | 1 | 40 | ok |

These rows support aggregate method claims only. They are local/public-index telemetry about what Cassandra recorded and packaged.

## 5. Artifact-to-claim map

| Claim family | Supporting artifacts | Safe interpretation |
|---|---|---|
| LOTL-derived input boundary | `sources/eu-lotl.xml`, `sources/eu-lotl.xml.meta.json`, `notes/pointers.json`, `SOURCES.md` | The run starts from a saved public LOTL snapshot and extracted pointers. |
| Dated collection | `snapshots/YYYY-MM-DD/manifest.json`, adjacent snapshot metadata | Cassandra attempted configured pointers and recorded successes/errors. |
| XML comparability | `normalized/YYYY-MM-DD/manifest.json` | Parseable XML-like artifacts were normalized and summarized for local comparison. |
| Structural changes | `diffs/YYYY-MM-DD.json`, `baselines/current.json` | Machine-readable structural diffs exist against a local baseline. |
| Evidence integrity | `bundles/.../manifest.json`, `bundles/.../verification.json`, `evidence/.../eatf-verification.json` | Local bundle/AEP bytes and declared hashes can be checked. |
| Public dashboard state | `observatory/public/data/index.json`, aggregate JSON/CSV, SVG figures | A public aggregate index exposes method telemetry with caveats. |
| Paper argument | `paper/draft.md`, `CLAIMS.md`, `ARTIFACT_INDEX.md` | The prose is evidence-linked and constrained by claim-safety rules. |

## 6. Paper argument transcript

Working title:

Cassandra: From Governance Infrastructure to Evidence Infrastructure

Paper shape:

1. Introduction: the governance-to-evidence move.
2. Background: EU LOTL and trusted-list XML as public administrative artifacts.
3. Method: cautious structural observation, normalization, diffing, bundling, EATF/AEP receipts.
4. System: scheduled GitHub Action, dashboard, public index, evidence package loop.
5. Results: current first series plus fixture-backed behavior.
6. Case analysis: what becomes visible and what remains outside observation.
7. AI/EATF connection: evidence infrastructure for AI governance records, not AI model behavior.
8. Limitations: no legal-status determination, no relying-party validation, no supervision.
9. Conclusion: evidence infrastructure as a computational public-governance method.

The existing `paper/draft.md` already contains many cautious sections and validator-linked references. The next paper work should consolidate rather than keep appending indefinitely: convert the current rich working draft into a clean 6k-8k word submission draft with fewer maintenance-process subsections and stronger narrative flow around the core sentence.

## 7. Fixture expansion transcript

Why fixtures are needed: the live corpus demonstrates empirical operation, but reviewers need controlled behavior to see that the method handles normal and adverse cases intentionally. Synthetic fixtures should preserve claim safety and avoid raw named-provider prose.

Priority fixture matrix:

| Priority | Fixture | Purpose | Expected safe behavior |
|---:|---|---|---|
| 1 | Stable no-change fixture | Repeated manifests with zero structural diffs | Diff emits zero changes without claiming real-world absence. |
| 2 | Normalized hash change fixture | Same record count, changed canonical content hash | Diff emits `normalized_hash_changed`. |
| 3 | Provider inventory fixture | Provider key added/removed under a hashed identifier | Aggregate/hash-keyed provider inventory change. |
| 4 | Service inventory fixture | Service key added/removed without naming entity | Aggregate/hash-keyed service inventory change. |
| 5 | Provider-service-detail fixture | Details changed under aggregate-only output | Provider/service detail class without raw names in prose. |
| 6 | Fetch failure fixture | Timeout, HTTP error, redirect, unreachable pointer | Manifest records collection telemetry, not legal/status meaning. |
| 7 | Non-XML fixture | PDF/HTML/non-parseable input | Skip or parser telemetry, not fatal lane failure. |
| 8 | EATF success fixture | Package verifies `ok` | Receipt says bytes/hash verification only. |
| 9 | EATF tamper fixture | Altered payload or AEP | Verification fails explicitly. |
| 10 | Missing-signing-input fixture | Missing EATF signing inputs | Receipt/status is `skipped_missing_signing_inputs`. |
| 11 | Dashboard fixture | Small public index with multiple run states | Dashboard parser renders multiple statuses safely. |
| 12 | Claim-safety fixture | Forbidden wording scanner | Unsafe wording fails validation. |

Recommended next implementation unit: create `notes/fixture-matrix.md` and the first stable/no-change synthetic fixture tests, then expand toward tamper and dashboard fixtures.

## 8. Risk register

| Risk | Why it matters | Mitigation artifact/process |
|---|---|---|
| Legal-status overclaiming | Trusted-list artifacts are legally meaningful outside Cassandra. | `CLAIMS.md`, claim-safety validators, paper caveats. |
| Signature-validation confusion | Signature-shape observation can be misread as cryptographic validation. | Explicit EATF and parser boundaries in paper/dashboard. |
| Provider-specific prose leakage | Named entities invite unintended status claims. | Aggregate-only prose, hashed keys, naming validators. |
| Endpoint/current-state confusion | Live endpoint behavior can differ from saved run evidence. | Dated manifests and source metadata. |
| Dashboard misconstrued as public alerting | Public UI may look operational. | Dashboard caveat and no-alerting wording. |
| EATF receipt overread as truth | Package verification can be mistaken for claim/legal validation. | EATF claim-boundary card and receipt caveats. |
| Append-only state bloat | Huge state files obscure current argument. | Full-stack transcript, resumption summaries, clean cards. |
| Fixture thinness | Reviewers need controlled behavior, not only live observations. | Synthetic fixture matrix and tests. |
| Employment/IP boundary | Tyche/Zetes boundary requires caution around eIDAS/public-sector trust services. | Keep Cassandra as public-source research; seek legal/operator review before commercial overlap. |

## 9. Cross-project map

| Project | Cassandra connection | Distinct role |
|---|---|---|
| EATF | Packages and verifies AEP evidence receipts for Cassandra runs. | Evidence-envelope integrity, not trusted-list interpretation. |
| MIRROR | Bundle manifest/claims/source pattern for dated observation evidence. | General evidence bundle format. |
| PKI Atlas | Can explain trusted-list concepts and tutorials. | Explanatory layer, not Cassandra empirical corpus. |
| X-Road agent attestation | Another public-sector trust-infrastructure case. | Operational attestation comparison case, not merged dataset. |
| Vesta | Public web/citation drift evidence infrastructure. | Drift/citation evidence parallel. |
| Icarus | Reproducibility audit as evidence infrastructure. | Reproducibility-audit parallel. |
| Breakable receipts | Verifier UX and failure-mode education. | Human-facing receipt failure pedagogy. |
| Tyche thesis hub | Places Cassandra as one case in an evidence-infrastructure thesis. | Case-study/chapter integration map. |

Do not merge these projects. Use the map to explain roles, analogies, and thesis placement.

## 10. Next experiments

1. Fixture-backed behavior suite: implement stable no-change, normalized-hash-change, provider/service inventory, fetch failure, non-XML, EATF success/tamper, missing signing input, dashboard, and claim-safety fixtures.
2. Evidence package format card: document payload, AEP, receipt, manifest, hash, and caveat fields.
3. Public index schema: add or document `observatory/public/data/schema.json` for dashboard consumers.
4. Dashboard cards: generate small `observatory/public/data/cards/*.json` summaries for claim boundary, latest run, EATF receipt, aggregate diffs, and caveats.
5. Paper consolidation: refactor `paper/draft.md` toward a clean 6k-8k word submission narrative using this transcript as an outline.
6. Reviewer objection card: pre-answer likely objections about legal claims, signature validation, selection bias, fixture realism, dashboard overinterpretation, and reproducibility.
7. Thesis integration card: position Cassandra as the governance-artifact case in the Tyche evidence-infrastructure thesis.

## 11. Operator/future-agent quick start

Before changing code or prose:

1. Check `STOP_CASSANDRA_HERMES`.
2. Pull `origin/main`.
3. Read `PLAN.md`, `CLAIMS.md`, `SOURCES.md`, `ARTIFACT_INDEX.md`, `BLOCKED.md`, `HERMES_PROGRESS.md`, `paper/draft.md`, `observatory/README.md`, and `observatory/public/data/index.json`.
4. Pick one coherent improvement unit.
5. Run the smallest relevant tests/validators.
6. Update `HERMES_PROGRESS.md` and state registers when new artifacts are created.
7. Commit and push to `origin/main`.

Current best next unit after this transcript: add fixture matrix and first synthetic no-change/hash-change fixture tests.

## 12. Transcript closing

Cassandra demonstrates a governance-to-evidence move: public administrative artifacts can be collected into a reproducible evidence loop and made publicly inspectable without crossing into legal supervision, relying-party validation, compliance judgment, or provider-specific claims. The live dashboard makes the method operational; the paper should make the boundary intelligible; the fixtures should make the behavior reviewable.
