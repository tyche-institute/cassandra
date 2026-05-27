# Cassandra full-stack usable transcript — 2026-05-27

Audience: Anton, thesis committee, reviewers, and future Hermes/Codex agents.

Purpose: readable end-to-end transcript of what Cassandra does, why the case matters, how the evidence loop works, and which artifacts support each claim.

Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

Claim boundary: this transcript describes structural observation, evidence packaging, package-level verification, and dashboard publication of aggregate telemetry. It does not assert trusted-list legal validity, source signature validity, supervisory status, compliance, provider-specific status, public alerting, or absence of legally relevant change.

## 1. Executive transcript

Cassandra starts from a public governance surface: the European list-of-lists and the national trusted-list artifacts referenced from a saved LOTL snapshot. These artifacts are legally meaningful in their real institutional context, but Cassandra treats them as public machine-readable records for research observation only.

The workflow turns that governance surface into evidence infrastructure in a bounded sequence:

1. Fetch the public LOTL and LOTL-derived pointers.
2. Save dated raw snapshot manifests and per-endpoint metadata.
3. Normalize parseable XML for stable structural comparison.
4. Preserve non-XML, parser-error, timeout, redirect, and HTTP-error outcomes as corpus telemetry.
5. Compare normalized records against dated baselines and emit machine-readable structural diff classes.
6. Append cautious alert-roll-up telemetry for local research use.
7. Bundle dated run summaries with sources, hashes, claims, caveats, and local verification outputs.
8. Package selected evidence with EATF/AEP and verify package bytes and declared hashes.
9. Build a public dashboard data index with aggregate telemetry, hashes, receipt pointers, schema, cards, figures, and caveats.
10. Use the paper and cards to explain the method without crossing into legal interpretation.

The methodological claim is narrow and strong:

> Public governance artifacts can be observed, hashed, bundled, signed, timestamped, displayed, and independently checked while preserving the distinction between evidence integrity and legal interpretation.

## 2. Why the case matters

Cassandra is not mainly an XML-parser project. It is a case study in turning public legal-technical state into reviewable evidence artifacts. The rare surface is that trusted-list records are public, structured, periodically changing governance artifacts. They invite observation, but they also create overclaiming risk: a fetch result, parser result, diff, or receipt must not be mistaken for legal status, relying-party validation, or supervision.

The case is useful for a thesis committee or reviewer because it is concrete. The live dashboard and public data index show the argument in operation rather than only describing it. The project demonstrates how a governance record can acquire durable evidence handles: dates, manifests, hashes, packages, receipts, schemas, and dashboard cards.

The intellectual move is from governance infrastructure to evidence infrastructure:

- governance infrastructure: public artifacts that participate in an official legal-technical ecosystem;
- evidence infrastructure: reproducible records about what an observer collected, normalized, compared, packaged, and displayed;
- boundary: Cassandra makes the evidence process visible, not the legal meaning authoritative.

## 3. Current public state

Repository: `https://github.com/tyche-institute/cassandra`

Live dashboard: `https://cassandra-observatory.pages.dev/`

Public data index: `https://cassandra-observatory.pages.dev/data/index.json`

Local public index source: `observatory/public/data/index.json`

Current public index target recorded in the operator directive and local index:

- `latest_date`: `2026-05-27`
- `run_count`: `4`
- `eatf_verified_count`: `4`
- EATF signing profile label: `local-dev:eatf-dev-rsa4096` for the current local preprint package refresh; production GitHub Actions should use an organization secret before any public release note.
- Scheduled workflow: `.github/workflows/cassandra-observatory.yml`, cron `23 3 * * *`
- Full scheduled-compatible run with Cloudflare deploy: GitHub Actions run `26521328723`

These are dashboard/evidence-publication facts. They do not say the underlying trusted lists are valid, invalid, stable, unstable, supervised by Cassandra, or safe for relying-party use.

## 4. Architecture

Cassandra is a small full-stack observatory, not a single script. Its layers are:

| Layer | Main artifacts | Role | Boundary |
|---|---|---|---|
| Source capture | `fetch.py`, `sources/eu-lotl.xml`, `notes/pointers.json`, `snapshots/YYYY-MM-DD/manifest.json` | Fetch LOTL and LOTL-derived artifacts; record endpoint metadata. | Collection telemetry only. |
| Parsing and normalization | `parse.py`, `normalized/YYYY-MM-DD/manifest.json` | Normalize XML-like files; record skips and parse errors. | Parser telemetry, not source validation. |
| Structural comparison | `diff.py`, `baselines/YYYY-MM-DD.json`, `diffs/YYYY-MM-DD.json` | Compare comparable normalized records and emit diff classes. | Structural diffs, not legal changes. |
| Roll-up and aggregation | `alert_rollup.py`, `alerts.jsonl`, `notes/aggregate_results.py`, `notes/aggregate-results-*.json`, `notes/aggregate-results-table.csv` | Build dated and cross-date telemetry. | Internal research telemetry, not public alerts. |
| Evidence bundles | `create_bundle.py`, `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/` | Bind claims, sources, hashes, notes, and local verification. | Provenance package, not legal truth. |
| EATF/AEP package | `scripts/eatf_package_snapshot.py`, `evidence/YYYY-MM-DD/*` | Package evidence and verify payload/envelope bytes. | Package integrity, not trusted-list legal or signature status. |
| Public dashboard data | `scripts/build_observatory_index.py`, `observatory/public/data/index.json`, `schema.json`, `cards/*.json`, SVG figures | Publish aggregate, schema-backed observatory data. | Display layer with caveats, not supervision. |
| Paper and cards | `paper/draft.md`, `paper/*-card.md`, `notes/*-card.md` | Explain the method, claim boundary, evidence map, and reviewer answers. | Working research artifacts pending operator review. |
| Validators and fixtures | `notes/test_*.py`, `notes/fixtures/*.json`, validation outputs | Check schema, fixtures, wording, links, hashes, and release gates. | Mechanical quality gates, not legal review or publication approval. |

## 5. Data flow transcript

A future agent should read the system as a flow of evidence handles.

### 5.1 LOTL and pointer extraction

Input: public EU LOTL endpoint and the saved local copy.

Artifacts:

- `sources/eu-lotl.xml`
- `sources/eu-lotl.xml.meta.json`
- `notes/pointers.json`
- `notes/lotl-fetch-output.json`
- `notes/pointers-output.json`

Meaning: the local saved LOTL snapshot yielded a pointer set for Cassandra's structural-observation run. Pointer count claims are about that saved snapshot and extractor behavior.

Non-meaning: pointer extraction does not certify completeness, legal effect, or endpoint currentness.

### 5.2 Dated snapshots

Input: LOTL-derived pointer list.

Artifacts:

- `snapshots/YYYY-MM-DD/manifest.json`
- raw saved files such as `snapshots/YYYY-MM-DD/<ordinal>-<territory>.<ext>`
- adjacent `.meta.json` files
- `notes/daily-run-YYYY-MM-DD-output.json`

Meaning: a dated run attempted LOTL-derived pointers, saved successful content, and recorded failures or redirects as operational telemetry.

Non-meaning: fetch success or failure is not a legal-status judgment, endpoint certification, supervision, or public alert.

### 5.3 Normalization

Input: saved snapshot files.

Artifacts:

- `normalized/YYYY-MM-DD/manifest.json`
- normalized XML artifacts
- `notes/normalize-output.json` and dated validation outputs

Meaning: parseable XML-like files are converted to deterministic canonical structural artifacts; PDFs, HTML, text, malformed XML, and parser errors are recorded rather than hidden.

Non-meaning: normalization does not validate source signatures, certificates, legal status, or relying-party semantics.

### 5.4 Diffing

Input: normalized manifest and configured local baseline.

Artifacts:

- `baselines/YYYY-MM-DD.json`
- `diffs/YYYY-MM-DD.json`
- `notes/diff-output.json` and related validators

Diff classes currently include:

- `listed_document_added`
- `listed_document_removed`
- `normalized_hash_changed`
- `summary_field_changed`
- `provider_inventory_changed`
- `service_inventory_changed`
- `provider_service_detail_changed`

Meaning: a configured local comparison emitted structural telemetry.

Non-meaning: zero diffs do not prove absence of legally relevant change; nonzero diffs do not prove legal effect or provider/service status.

### 5.5 Alert roll-up and aggregation

Input: dated manifests, diffs, bundles, and alert entries.

Artifacts:

- `alerts.jsonl`
- `notes/aggregate-results-YYYY-MM-DD-output.json`
- `notes/aggregate-results-table.csv`
- `observatory/public/data/aggregate-results.json`
- `observatory/public/data/aggregate-results-table.csv`

Meaning: machine-readable local telemetry and aggregate public dashboard data.

Non-meaning: the alert roll-up is not public alerting, regulatory notification, risk scoring, or legal interpretation.

### 5.6 Bundles and EATF receipts

Input: dated run summary, sources, claims, hashes, and selected public evidence artifacts.

Artifacts:

- `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/manifest.json`
- `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/claims.json`
- `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/notes.md`
- `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/verification.json`
- `evidence/YYYY-MM-DD/cassandra-observation.json`
- `evidence/YYYY-MM-DD/cassandra-observation.aep`
- `evidence/YYYY-MM-DD/eatf-verification.json`

Meaning: the MIRROR-style bundle makes the dated run reviewable as an evidence object; EATF/AEP verification checks package/payload bytes and declared hashes.

Non-meaning: neither MIRROR nor EATF makes the source trusted lists legally authoritative, validates their signatures for relying-party use, supervises providers, or approves publication.

### 5.7 Dashboard publication

Input: aggregate outputs, figures, cards, schemas, run metadata, and EATF receipt pointers.

Artifacts:

- `observatory/public/data/index.json`
- `observatory/public/data/schema.json`
- `observatory/public/data/latest.json`
- `observatory/public/data/cards/*.json`
- `observatory/public/data/figures/*.svg`
- `observatory/README.md`

Meaning: public dashboard consumers can inspect current aggregate telemetry, run rows, artifact hashes, EATF status fields, and claim boundaries.

Non-meaning: the dashboard is not a trusted-list validator, public warning service, supervisory console, compliance register, or legal-status endpoint.

## 6. Evidence boundary: EATF, MIRROR, and dashboard

Cassandra has three related evidence surfaces.

### MIRROR-style bundle boundary

MIRROR-style bundles organize evidence for human review: source references, claims, caveats, artifact hashes, and local verification outputs. They answer: what did this dated run say, what local files support it, and are the bundle references internally checkable?

Primary explanatory artifact: `notes/mirror-bundle-card.md`.

### EATF/AEP boundary

EATF/AEP receipts verify the Cassandra evidence package as bytes and declared hashes. They answer: does this package envelope and payload verify according to the configured verifier for the run?

Primary explanatory artifact: `notes/eatf-claim-boundary-card.md`.

Safe EATF claim: an `ok` receipt supports package/payload integrity for the Cassandra observation evidence package.

Unsafe EATF claim: an `ok` receipt proves trusted-list legal validity, source signature validity, provider status, supervisory approval, compliance, or absence of legally relevant change.

### Dashboard boundary

The dashboard makes the method legible and navigable. It exposes current aggregate telemetry, run counts, hashes, cards, figures, and caveats.

Primary explanatory artifacts:

- `observatory/README.md`
- `notes/public-index-schema.md`
- `notes/data-dictionary.md`
- `observatory/public/data/schema.json`
- `observatory/public/data/index.json`

Safe dashboard claim: the public index is a schema-backed aggregate view of Cassandra structural-observation evidence.

Unsafe dashboard claim: the dashboard is a public alerting service, trusted-list legal monitor, relying-party validator, or regulatory tool.

## 7. Paper argument

Working title:

> Cassandra: From Governance Infrastructure to Evidence Infrastructure

Alternative title:

> Watching the Trust List: Longitudinal Structural Observation of Europe's Machine-Readable Trust Infrastructure

The paper should make Cassandra legible as a method demonstration and case study. Its strongest shape is:

1. Introduction: the governance-to-evidence move.
2. Background: EU LOTL and trusted-list XML as public administrative artifacts.
3. Method: cautious structural observation, normalization, diffing, bundling, EATF/AEP receipts.
4. System: scheduled GitHub Action, dashboard, public index, evidence package loop.
5. Results: current first series plus fixture-backed behavior.
6. Case analysis: what becomes visible and what remains outside observation.
7. AI/EATF connection: evidence infrastructure for AI governance records, not AI model behavior.
8. Limitations: no legal-status determination, no relying-party validation, no supervision.
9. Conclusion: evidence infrastructure as a computational public-governance method.

Current paper artifacts:

- `paper/draft.md`
- `paper/abstract-card.md`
- `paper/venue-fit-card.md`
- `paper/reviewer-objection-card.md`
- `paper/claims-and-evidence-table.md`
- `paper/limitations-card.md`
- `paper/thesis-chapter-card.md`

The draft already contains many local safety gates and reproducibility sections. The next paper improvement should be editorial consolidation: turn the accumulated append-only sections into a clean 6k–8k submission draft with a direct narrative arc, while preserving the caveats and evidence references.

## 8. Fixture expansion transcript

The fixture program exists because the real observation lane began empirically. The paper needs controlled cases showing that the software behaves safely under known conditions without exposing real provider/service names.

Primary artifact: `notes/fixture-matrix.md`.

Reviewer bridge: `notes/fixture-to-claim-map.md` maps each fixture class to the specific paper claim, reviewer question, evidence path, and non-claim it supports. Use it when moving fixture results into the Methods, Results, or reviewer-response sections.

Current implemented fixture classes include:

| Fixture class | Purpose | Main artifacts |
|---|---|---|
| Stable no-change | Repeated comparable records emit no structural diff. | `notes/fixtures/synthetic-diff-fixtures.json`, `notes/test_synthetic_diff_fixtures.py` |
| Normalized hash change | Same record count but changed canonical content hash. | `notes/fixtures/synthetic-diff-fixtures.json`, `notes/test_synthetic_diff_fixtures.py` |
| Provider inventory | Hashed provider key added/removed. | `notes/fixtures/synthetic-diff-fixtures.json`, `notes/test_synthetic_diff_fixtures.py` |
| Service inventory | Hashed service key added/removed. | `notes/fixtures/synthetic-diff-fixtures.json`, `notes/test_synthetic_diff_fixtures.py` |
| Provider-service detail | Aggregate/hash-key detail changes without real names. | `notes/fixtures/synthetic-diff-fixtures.json`, `notes/test_synthetic_diff_fixtures.py` |
| Fetch failure | Timeout, HTTP error, redirect, unreachable pointer. | `notes/test_fetch_and_non_xml_fixtures.py`, `notes/fetch-non-xml-fixture-validation-output.json` |
| Non-XML | PDF/HTML/TXT skip and malformed XML parse error. | `notes/test_fetch_and_non_xml_fixtures.py`, `notes/fetch-non-xml-fixture-validation-output.json` |
| Missing signing input | Explicit `skipped_missing_signing_inputs`. | `notes/test_eatf_missing_signing_fixture.py`, `notes/eatf-missing-signing-fixture-validation-output.json` |
| Dashboard multistate | Small public index with multiple run states. | `notes/test_dashboard_public_index_fixture.py`, `notes/fixtures/dashboard-public-index-multistate.json` |
| Claim safety | Forbidden wording scanner catches overclaiming. | `notes/test_claim_safety_fixture.py`, `notes/fixtures/claim-safety-wording-fixtures.json` |

Recent fixture expansion note:

- EATF success and tamper fixtures are now covered by `notes/test_eatf_success_tamper_fixture.py` and `notes/eatf-success-tamper-fixture-validation-output.json` using synthetic non-secret inputs and a fake local EATF CLI.
- The success fixture checks package-wrapper handling of an `ok` receipt; the tamper fixture alters the synthetic AEP and expects `verify_failed`.

Remaining high-value fixture gaps:

- Broader dashboard card pack fixture if dashboard cards become a cited reviewer surface.
- Optional fixture documentation that maps each fixture directly to a paper claim row.

Fixture claim boundary: fixtures prove expected software behavior on synthetic inputs. They do not validate any real trusted list, provider, service, legal status, source signature, or compliance claim.

## 9. Risk register

| Risk | Why it matters | Mitigation artifacts / discipline |
|---|---|---|
| Legal overclaiming | Readers may confuse structural observation with legal status or supervision. | `CLAIMS.md`, `paper/claims-and-evidence-table.md`, `notes/eatf-claim-boundary-card.md`, claim-safety tests. |
| Signature overclaiming | EATF or XML signature-shape fields may be mistaken for source signature validation. | EATF boundary card, paper claim-safety note, parser-scope sections. |
| Zero-diff overclaiming | No emitted structural diff may be read as no legally relevant change. | Paper limitations, fixture matrix notes, public index caveat. |
| Provider-specific exposure | Raw names could turn aggregate research into entity-specific claims. | Hashed inventory keys, aggregate-only prose, claim-safety fixture. |
| Dashboard misinterpretation | Public UI can look like a monitoring or alerting service. | `observatory/README.md`, public index caveat, schema consumer rules, dashboard cards. |
| Bundle/receipt overinterpretation | Hash verification can be mistaken for claim truth. | `notes/mirror-bundle-card.md`, `notes/evidence-package-format.md`, EATF card. |
| Endpoint volatility | Live sources change after a dated run. | Local saved artifacts, dated manifests, replay capsule, source-handling section. |
| Validator fetishism | Clean validators may be mistaken for publication or legal approval. | Release-readiness checklist, persistent-warning policy, operator-review gates. |
| Employment/IP boundary | Tyche strategy must avoid overlap with restricted Zetes identity/eIDAS/public-sector trust-service work unless cleared. | Keep Cassandra as public research artifact; avoid commercial/legal-service claims and confidential sources. |

## 10. Cross-project map

Cassandra should connect to other Tyche work as a distinct role, not be merged into it.

| Project | Distinct role | Cassandra connection | Separation rule |
|---|---|---|---|
| EATF | Evidence package and receipt verification. | Cassandra uses AEP packages and offline verification for dated observatory evidence. | EATF verifies package bytes/hashes, not trusted-list legal meaning. |
| MIRROR | Evidence bundle structure. | Cassandra uses MIRROR-style bundles for claims, sources, hashes, and caveats. | Bundle organization is not legal interpretation. |
| PKI Atlas | Explanatory/tutorial layer for trust infrastructure. | Can explain trusted-list concepts around Cassandra. | Not the empirical corpus and not a legal authority. |
| X-Road agent attestation | Operational public-sector trust infrastructure case. | Comparative case for public-sector trust and evidence boundaries. | Do not transfer Cassandra claims into X-Road operational/legal context. |
| Vesta | Public web/citation drift. | Parallel evidence-infrastructure case for public record drift. | Separate corpus and method claims. |
| Icarus | Reproducibility audit. | Parallel case for audit traces and reproducibility evidence. | Do not convert Cassandra dashboard counts into reproducibility scores. |
| Breakable receipts | Verifier UX and failure-mode education. | Useful for explaining EATF tamper/missing-input fixtures. | Educational verifier UX, not legal status proof. |
| Tyche thesis hub | Thesis map and chapter placement. | Cassandra is the governance-artifact observatory case. | Thesis integration must preserve claim boundary. |

Supporting notes:

- `notes/thesis-integration-card.md`
- `notes/cassandra-vesta-icarus-xroad-map.md`
- `notes/eidas-to-ai-act-evidence-map.md`
- `notes/case-study-one-pager.md`
- `notes/press-safe-summary.md`

## 11. Reviewer objection transcript

Likely objection: "Isn't this just scraping XML?"

Answer: no. The interesting contribution is the evidence loop: public governance artifacts become dated, hashed, normalized, diffed, bundled, verified at package level, displayed, and cited with explicit non-claim rails. XML parsing is one component.

Likely objection: "Does this validate trusted lists?"

Answer: no. Cassandra does not perform relying-party validation, source signature validation, legal-status determination, supervision, public alerting, or compliance review.

Likely objection: "Why use EATF if it does not prove legal validity?"

Answer: because the project is about evidence integrity. EATF/AEP makes the Cassandra package and declared hashes independently checkable while preserving the boundary that legal interpretation is outside scope.

Likely objection: "Why fixtures if there are real observations?"

Answer: real observations show the system operating on public artifacts; synthetic fixtures show expected behavior under controlled cases without exposing names or making provider-specific claims.

Likely objection: "Is the dashboard a public alerting system?"

Answer: no. It is a public presentation and data-contract layer for aggregate structural-observation telemetry. Its caveats and schema rules explicitly forbid alerting, supervision, legal-status, and relying-party interpretations.

## 12. Next experiments

Recommended next bounded units, in priority order:

1. Editorially consolidate `paper/draft.md` into a clean 6k–8k submission draft around the governance-to-evidence argument.
2. Add EATF success and tamper fixtures with synthetic minimal packages and explicit verifier failure/success semantics.
3. Add or strengthen dashboard card fixture coverage if dashboard cards become cited in the paper.
4. Create a printable dashboard snapshot/card pack only if the local toolchain can do it without decorative fluff.
5. Expand `paper/claims-and-evidence-table.md` into the canonical reviewer map for every central paper claim.
6. Add a short "method vs legal interpretation" figure or table to the paper, reusing the claim-boundary vocabulary.
7. Re-run public index schema, dashboard fixture, claim-safety, and artifact hash validators after every dashboard or paper-facing change.
8. Keep cross-project cards aligned with Tyche thesis hub without merging corpora.

## 13. Future-agent operating checklist

Before modifying Cassandra in autonomous mode:

1. Stop if `STOP_CASSANDRA_HERMES` exists.
2. Pull `origin/main` with `--ff-only`.
3. Read `PLAN.md`, `CLAIMS.md`, `SOURCES.md`, `ARTIFACT_INDEX.md`, `BLOCKED.md`, `HERMES_PROGRESS.md`, `paper/draft.md`, `observatory/README.md`, and `observatory/public/data/index.json`.
4. Choose one coherent improvement unit.
5. Implement only related files; never stage unrelated local files such as session logs.
6. Run the smallest relevant validators/tests.
7. Update `HERMES_PROGRESS.md` and state registers when needed.
8. Commit and push to `origin/main`.
9. Preserve the core sentence and the claim boundary.

## 14. Artifact map for claims

| Claim type | Cite these artifacts first |
|---|---|
| Public dashboard state | `observatory/public/data/index.json`, `observatory/public/data/schema.json`, `observatory/README.md` |
| Data dictionary / schema semantics | `notes/data-dictionary.md`, `notes/public-index-schema.md` |
| Evidence package semantics | `notes/evidence-package-format.md`, `notes/eatf-claim-boundary-card.md`, `notes/mirror-bundle-card.md` |
| Fixture coverage | `notes/fixture-matrix.md`, `notes/fixtures/*.json`, `notes/test_*.py` fixture tests |
| Paper argument | `paper/draft.md`, `paper/abstract-card.md`, `paper/claims-and-evidence-table.md`, `paper/reviewer-objection-card.md` |
| Thesis integration | `notes/thesis-integration-card.md`, `notes/cassandra-vesta-icarus-xroad-map.md`, `notes/eidas-to-ai-act-evidence-map.md` |
| Public safe summary | `notes/case-study-one-pager.md`, `notes/press-safe-summary.md` |
| Replay / future operation | `notes/replay-capsule.md`, `HERMES_PROGRESS.md`, `PLAN.md` |

## 15. One-paragraph version

Cassandra is a research-only observatory that turns public trusted-list governance artifacts into evidence infrastructure: it captures dated LOTL-derived artifacts, records provenance and hashes, normalizes parseable XML, emits structural diffs, packages claims and sources into reviewable bundles, verifies EATF/AEP evidence packages at the byte/hash level, and publishes aggregate dashboard telemetry with explicit caveats. Its contribution is not legal supervision, signature validation, provider-status determination, public alerting, or compliance judgment; its contribution is a reproducible method for making public governance records observable, packageable, verifiable, and discussable without collapsing evidence integrity into legal interpretation.

## 16. v0.2 preprint polish transcript

The v0.2 preprint pass turns the Cassandra packet from a usable candidate into a cleaner thesis-ready case study. The important editorial change is not ornament. It is evidence discipline made visible: no local absolute paths in the manuscript body, no full SHA strings in prose, no raw URL code spans, no long markdown bullet lists that split across pages, and no table or figure caption left hanging without nearby content.

The manuscript now includes three small working lemmas. They are deliberately modest. An EATF/AEP package can show that a declared byte sequence, hash, receipt, and verifier outcome travel together; it cannot by itself prove legal truth. A structural diff can show that two normalized observations differ; it cannot by itself decide whether a legally relevant event occurred. A claim plus source, hash, receipt, and caveat is not the same claim after the caveat is removed.

The failed case is now explicit enough for reviewers. The positive fixture represents a package accepted under the local profile. The tamper fixture alters the package after the receipt path is known, and the verifier must report `verify_failed`. The missing-input fixture is separate: it records `skipped_missing_signing_inputs`, preserving the payload and metadata for review without pretending that package signing happened.

The case-study bridge has also been made more honest. Cassandra is the PKI/eIDAS public-governance observatory. MIRROR/EATF supplies the evidence-envelope method. Janus/MATx, Vesta/Icarus, eaudit/h2oatlas, and Aletheia/Kolmogorov remain adjacent thesis cases only where their own artifacts can carry the citation burden. That posture keeps the final thesis ambitious without turning every promising prototype into an overclaimed precedent.

Current v0.2 status: markdown, PDF, DOCX, LaTeX header, review packet, deposit-metadata draft, and publication-kit readiness outputs validate with zero errors and zero warnings. This is still operator-review material, not external submission, legal review, DOI reservation, trusted-list validation, source-signature validation, supervision, public alerting, or publication approval.
