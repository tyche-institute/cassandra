# Cassandra dashboard card pack

Generated: 2026-05-27T18:02:48.429971+00:00

Purpose: reviewer-readable rendering of the public dashboard card JSON pack.

Case sentence: Cassandra: from governance infrastructure to evidence infrastructure.

Public index: `observatory/public/data/index.json` (`sha256:8a9293cf6473194877a131dcaec9f22bab6b74c516910fb5432cd363f6e3df29`)
Card index: `observatory/public/data/cards/index.json` (`sha256:6c42788f9bf657ced513b13436c03cb8f5db3f25f854259c958b45d7ef7a1e50`)

Boundary: Reviewer dashboard-card rendering only; it summarizes public observatory JSON cards and hash checks. It is not trusted-list validation, source-signature validation, legal-status determination, supervision, compliance judgment, public alerting, endorsement, legal review, or publication approval.

## Dashboard telemetry snapshot

- latest_date: `2026-05-27`
- run_count: `4`
- packaged_evidence_count: `4`
- eatf_verified_count: `4`
- caveat: Public observatory data for Cassandra structural observation only; not trusted-list validation, legal-status determination, supervision, signature validation, relying-party processing, or public alerting.

## Card index hash checks

- `data/cards/aggregate-diffs.json`: exists=`True`, sha256=`508103a91b1b66adc7a8aebd1aa743d194114679e8537402808a75ce28174f4f`, index_sha256=`508103a91b1b66adc7a8aebd1aa743d194114679e8537402808a75ce28174f4f`
- `data/cards/caveat.json`: exists=`True`, sha256=`7a14950891211873dc2e3c98f6831d5b2836b2ed41824dea5f6b3d7453075a34`, index_sha256=`7a14950891211873dc2e3c98f6831d5b2836b2ed41824dea5f6b3d7453075a34`
- `data/cards/claim-boundary.json`: exists=`True`, sha256=`1a390ec7b2c27c402975d138910b243035d7085eb0a4e434d3452482e439114a`, index_sha256=`1a390ec7b2c27c402975d138910b243035d7085eb0a4e434d3452482e439114a`
- `data/cards/eatf-receipt.json`: exists=`True`, sha256=`90ca7805c8aecd5fa60567d82431f7e98dbe8c8ba2062411698fee05a2a458b8`, index_sha256=`90ca7805c8aecd5fa60567d82431f7e98dbe8c8ba2062411698fee05a2a458b8`
- `data/cards/latest-run.json`: exists=`True`, sha256=`8f92a91648cf249fb894f4a0e8c27eca708aed71da4a8dc7ed0ee62103aa7990`, index_sha256=`8f92a91648cf249fb894f4a0e8c27eca708aed71da4a8dc7ed0ee62103aa7990`

## Claim boundary

- id: claim-boundary
- summary: Cassandra observes and packages structural telemetry over saved LOTL-derived public artifacts.
- interpretation: Evidence integrity and aggregate method telemetry are in scope; legal interpretation is out of scope.
- caveat: Public observatory data for Cassandra structural observation only; not trusted-list validation, legal-status determination, supervision, signature validation, relying-party processing, or public alerting.
- not_a: trusted-list validation; legal-status determination; signature validation; supervision; compliance judgment; relying-party processing; public alerting; publication approval

Data:
- asserts:
  - Cassandra records dated structural observation telemetry over local LOTL-derived artifacts.
  - EATF receipts, when status is ok, verify the corresponding package envelope and payload bytes.
- does_not_assert:
  - legal effect of any trusted list
  - signature or certificate validity
  - supervisory approval
  - absence of legally relevant change

## Latest Cassandra run

- id: latest-run
- summary: Latest dated structural-observation run exposed through the public index.
- interpretation: Run counts describe Cassandra's saved workflow telemetry for the date, not external legal state.
- caveat: Public observatory data for Cassandra structural observation only; not trusted-list validation, legal-status determination, supervision, signature validation, relying-party processing, or public alerting.
- not_a: trusted-list validation; legal-status determination; signature validation; supervision; compliance judgment; relying-party processing; public alerting; publication approval

Data:
- date: `2026-05-27`
- diff_change_count: `40`
- eatf_status: `ok`
- fetch_errors: `1`
- fetched_content_files: `42`
- normalized_xml_artifacts: `31`
- pointer_attempts: `43`

## EATF receipt boundary

- id: eatf-receipt
- summary: Latest EATF/AEP receipt status for the Cassandra evidence package.
- interpretation: A status of ok verifies package bytes, envelope structure, and declared hashes only.
- caveat: Public observatory data for Cassandra structural observation only; not trusted-list validation, legal-status determination, supervision, signature validation, relying-party processing, or public alerting.
- not_a: trusted-list validation; legal-status determination; signature validation; supervision; compliance judgment; relying-party processing; public alerting; publication approval

Data:
- date: `2026-05-27`
- package_path: `evidence/2026-05-27/cassandra-observation.aep`
- package_sha256: `3ef7f33b391afac388ce4bcf9716ac7018508ed613933f4ee86a3008d42023f6`
- receipt_path: `evidence/2026-05-27/eatf-verification.json`
- receipt_sha256: `1e971e12a46b0d8be72635671b45be0b2dc21a283c5f29f1257d3dde4d6407d0`
- signing_profile: `github-secret:cassandra-eatf-key`
- status: `ok`
- valid: `True`

## Aggregate structural diffs

- id: aggregate-diffs
- summary: Diff-class totals across public Cassandra runs.
- interpretation: Diff classes are local structural-observation buckets against Cassandra baselines, not compliance or legal-effect classes.
- caveat: Public observatory data for Cassandra structural observation only; not trusted-list validation, legal-status determination, supervision, signature validation, relying-party processing, or public alerting.
- not_a: trusted-list validation; legal-status determination; signature validation; supervision; compliance judgment; relying-party processing; public alerting; publication approval

Data:
- diff_change_count: `66`
- diff_class_totals:
  - listed_document_added: `0`
  - listed_document_removed: `0`
  - normalized_hash_changed: `7`
  - provider_inventory_changed: `0`
  - provider_service_detail_changed: `26`
  - service_inventory_changed: `5`
  - summary_field_changed: `28`
- latest_date: `2026-05-27`
- run_count: `4`

## Dashboard caveat

- id: caveat
- summary: Reusable public caveat for dashboard panels and downstream cards.
- interpretation: Keep this caveat attached to dashboard cards, figures, and public-index excerpts.
- caveat: Public observatory data for Cassandra structural observation only; not trusted-list validation, legal-status determination, supervision, signature validation, relying-party processing, or public alerting.
- not_a: trusted-list validation; legal-status determination; signature validation; supervision; compliance judgment; relying-party processing; public alerting; publication approval

Data:
- caveat: `Public observatory data for Cassandra structural observation only; not trusted-list validation, legal-status determination, supervision, signature validation, relying-party processing, or public alerting.`
- source: `observatory public index`

## Reviewer use

Use this pack to check whether dashboard prose keeps the Cassandra boundary visible: structural observation, local hashes, bundles, receipts, schemas, and caveats are in scope; legal interpretation, provider/service status, source-signature validation, supervision, compliance judgment, public alerting, endorsement, legal review, and publication approval are out of scope.
