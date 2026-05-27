# Cassandra claims and evidence table

Purpose: compact paper-facing map from claim families to evidence artifacts and safe wording for structural observation.

| Claim family | Safe claim | Evidence artifacts | Boundary |
|---|---|---|---|
| Public-source collection | Cassandra records dated attempts to collect public LOTL-derived artifacts and preserves success/error telemetry. | `fetch.py`; `run_daily.py`; `sources/`; `snapshots/YYYY-MM-DD/manifest.json`; `SOURCES.md` | Collection telemetry is not endpoint-currentness, legal status, or completeness proof. |
| Deterministic normalization | Parseable XML-like artifacts are normalized and summarized for local structural comparison; non-XML and parse errors are recorded. | `parse.py`; `normalized/YYYY-MM-DD/manifest.json`; `notes/test_fetch_and_non_xml_fixtures.py` | Normalization is not relying-party validation or signature validation. |
| Structural diffing | Cassandra emits configured structural diff classes over comparable normalized records. | `diff.py`; `diffs/YYYY-MM-DD.json`; `notes/test_synthetic_diff_fixtures.py` | Diffs do not determine legal effect or provider/service status. |
| Aggregate public telemetry | The public index exposes run counts, aggregate totals, diff-class totals, figures, hashes, and caveats. | `observatory/public/data/index.json`; `observatory/public/data/schema.json`; `notes/public-index-schema.md`; `notes/data-dictionary.md` | Dashboard data is method telemetry, not public alerting or legal advice. |
| Evidence packaging | Dated run artifacts are bundled with manifests, claims, hashes, source references, and verification output. | `create_bundle.py`; `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/`; `notes/evidence-package-format.md` | Bundle verification checks local evidence package integrity, not truth of legal claims. |
| EATF/AEP receipts | For indexed `ok` runs, the EATF receipt verifies package envelope/payload bytes and declared hashes. | `scripts/eatf_package_snapshot.py`; `evidence/YYYY-MM-DD/`; `notes/evidence-package-format.md` | EATF does not validate source trusted-list signatures or confer supervisory meaning. |
| Fixture-backed behavior | Synthetic fixtures cover stable/no-change, hash change, provider/service inventory, fetch failure, non-XML, missing signing input, dashboard state, and claim-safety wording. | `notes/fixture-matrix.md`; `notes/fixtures/*.json`; `notes/test_*fixture*.py` | Fixtures are synthetic workflow evidence only. |
| Thesis contribution | Cassandra is a governance-artifact case for evidence infrastructure: observable, hashable, packageable, verifiable, displayable, and discussable. | `notes/cassandra-full-stack-usable-transcript-2026-05-27.md`; `paper/draft.md` | The thesis claim is methodological, not regulatory or legal. |
