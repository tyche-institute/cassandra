# Cassandra reviewer-objection card

Purpose: pre-answer likely reviewer concerns with artifact-backed, claim-safe responses.

| Objection | Safe answer | Supporting artifacts |
|---|---|---|
| "Is this just an XML parser?" | No. XML parsing is one layer in a larger evidence loop: dated collection, normalization, structural diffing, packaging, EATF/AEP receipt verification, public dashboard indexing, schema documentation, and fixtures. | `notes/cassandra-full-stack-usable-transcript-2026-05-27.md`; `observatory/README.md`; `paper/draft.md` |
| "Are you claiming legal validity or provider status?" | No. Cassandra records structural observations over public artifacts and explicitly excludes legal-status, supervisory, compliance, and provider-specific claims. | `CLAIMS.md`; `notes/data-dictionary.md`; `notes/public-index-schema.md` |
| "Do EATF receipts prove the source trusted lists are valid?" | No. In Cassandra, EATF/AEP receipts verify package envelope/payload bytes and declared hashes. They do not validate trusted-list signatures or legal effect. | `notes/evidence-package-format.md`; `evidence/YYYY-MM-DD/eatf-verification.json` |
| "Can zero diffs mean no legally relevant change?" | No. Zero diffs mean only that the configured local structural comparison emitted no changes for comparable records. | `notes/fixture-matrix.md`; `notes/test_synthetic_diff_fixtures.py` |
| "Why use synthetic fixtures?" | The live corpus shows empirical operation; fixtures show intended behavior for reviewable edge cases without leaking names or implying real-world status. | `notes/fixture-matrix.md`; `notes/fixtures/*.json`; `notes/test_*fixture*.py` |
| "Is the dashboard an alerting service?" | No. The dashboard is a public method demonstration and aggregate evidence index with caveats. It should not be used as public alerting or relying-party processing. | `observatory/public/data/index.json`; `observatory/README.md`; `notes/test_dashboard_public_index_fixture.py` |
| "Is the corpus complete?" | The paper should claim only the dated local lineage derived from saved LOTL pointers and recorded fetch outcomes, including errors and skips. | `SOURCES.md`; `snapshots/YYYY-MM-DD/manifest.json`; `notes/data-dictionary.md` |
| "What is the AI Act connection?" | Cassandra is not about AI model behavior. It is a governance-record case showing how public/semi-public governance evidence could be packaged and checked while separating evidence integrity from legal interpretation. | `notes/cassandra-full-stack-usable-transcript-2026-05-27.md`; `paper/draft.md` |

## Mandatory response pattern

When answering reviewers, cite artifacts first, then state the boundary. Do not upgrade package verification into legal-status interpretation, legal status interpretation, or dashboard telemetry into public alerting.
