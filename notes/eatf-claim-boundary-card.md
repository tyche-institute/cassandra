# EATF claim-boundary card — Cassandra

Purpose: reusable paper, dashboard, and reviewer card explaining what Cassandra EATF/AEP receipts can and cannot prove.

Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

## Safe claim

For Cassandra, an EATF/AEP receipt is evidence that a declared Cassandra observation payload, package envelope, and recorded hashes verify according to the configured package verifier for that run.

This is an evidence-integrity claim about Cassandra's package bytes. It is not a legal or supervisory claim about the trusted-list source material.

## What the receipt covers

| Layer | Covered evidence | Safe interpretation |
|---|---|---|
| Payload | `evidence/YYYY-MM-DD/cassandra-observation.json` | Declared observation metadata, artifact paths, hashes, counts, and caveats. |
| Package | `evidence/YYYY-MM-DD/cassandra-observation.aep` | AEP envelope/package bytes for the Cassandra observation. |
| Receipt | `evidence/YYYY-MM-DD/eatf-verification.json` | Verifier result, status, timestamps or test-vector labels, and package/payload hash checks. |
| Public index | `observatory/public/data/index.json` `runs[].eatf` | Dashboard-consumable status and hash pointers, with caveats retained. |

## What the receipt does not cover

Cassandra EATF/AEP receipts do not assert any of the following:

- trusted-list legal validity;
- source trusted-list signature or certificate validity;
- any supervisory approval or disapproval;
- any compliance judgment;
- relying-party processing outcome;
- public alerting or warning clearance;
- absence of legally relevant change;
- provider-specific legal or operational status.

## Status vocabulary

| Status | Meaning for Cassandra | Required dashboard behavior |
|---|---|---|
| `ok` | Package/payload verification succeeded for the declared Cassandra observation artifacts. | Display as evidence-package verification, not source legal validation. |
| `skipped_missing_signing_inputs` | The packaging script could not sign because required signing material was absent. | Preserve as explicit skip telemetry; do not coerce to failure or success. |
| `verify_failed` | A synthetic or real verification check failed for the package/payload evidence. | Display as package-verification review telemetry, not trusted-list status. |

## Reviewer answer

If asked whether EATF makes Cassandra's observations legally authoritative, answer:

> No. EATF/AEP is used here to make Cassandra's evidence package independently checkable as bytes, hashes, and declared metadata. It strengthens reproducibility and tamper evidence for the observatory output, while preserving the boundary that Cassandra does not validate trusted-list legal status, source signatures, supervisory meaning, or compliance.

## Artifact anchors

- Packaging helper: `scripts/eatf_package_snapshot.py`
- Public index contract: `observatory/public/data/index.json`
- Schema/card companion: `notes/evidence-package-format.md`
- Missing-input fixture: `notes/test_eatf_missing_signing_fixture.py`
- Dashboard multi-state fixture: `notes/fixtures/dashboard-public-index-multistate.json`
