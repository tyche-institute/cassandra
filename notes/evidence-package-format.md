# Cassandra evidence package format

Purpose: concise card for the evidence package loop used by Cassandra. The package format supports reproducible structural-observation research. It does not convert observations into legal-status determinations, signature-validation results, supervisory actions, public alerts, compliance judgments, or publication approval.

## Package loop

1. Dated run creates snapshot, normalization, diff, alert, and aggregate artifacts.
2. `create_bundle.py` creates a MIRROR-style bundle for the dated snapshot summary.
3. `scripts/eatf_package_snapshot.py` creates an EATF/AEP payload and package for public evidence material.
4. The verifier writes `evidence/YYYY-MM-DD/eatf-verification.json`.
5. `scripts/build_observatory_index.py` exposes package paths, hashes, status, and caveats in `observatory/public/data/index.json`.

## MIRROR-style bundle directory

Typical path: `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/`

| File | Role | Required meaning |
|---|---|---|
| `manifest.json` | Bundle manifest: artifact path/hash, sources, claims, caveats, verification links. | Hash/presence and provenance index only. |
| `claims.json` | Cautious claims tied to local evidence. | Claims must stay structural and aggregate. |
| `notes.md` | Human-readable caveats and method notes. | Boundary explanation for reviewers. |
| `sources/` | Copied source manifests or source references. | Reproducibility support, not full legal source authority. |
| `verification.json` | Local bundle verification output. | Checks local hashes/presence, not legal truth. |

## EATF/AEP evidence files

Typical path: `evidence/YYYY-MM-DD/`

| File | Role | Safe interpretation |
|---|---|---|
| `cassandra-observation.json` | EATF payload describing the observation evidence package. | Structured evidence payload. |
| `cassandra-observation.aep` | AEP envelope/package. | Package bytes to verify. |
| `eatf-verification.json` | Verification receipt. | Verifier result for package/payload bytes and declared hashes. |

## Public index EATF fields

| Field | Meaning | Non-claim |
|---|---|---|
| `eatf.status` | Verifier status such as `ok` or explicit skip/failure. | Not trusted-list status. |
| `eatf.valid` | Boolean verifier result when applicable. | Not signature validity of source trusted lists. |
| `eatf.package_path` | Public/local package path. | Location only. |
| `eatf.package_sha256` | SHA-256 of AEP package. | Byte-integrity handle. |
| `eatf.payload_path` | Payload path. | Location only. |
| `eatf.payload_sha256` | SHA-256 of payload. | Byte-integrity handle. |
| `eatf.receipt_path` | Verification receipt path. | Location only. |
| `eatf.receipt_sha256` | SHA-256 of receipt. | Receipt-integrity handle. |
| `eatf.signing_profile` | Label for signing key source, e.g. GitHub secret profile. | Does not reveal secret material and does not imply legal authority. |
| `eatf.timestamp` | Timestamp source label or fixture marker. | Timestamp evidence only as declared by package process. |
| `eatf.caveat` | Boundary statement. | Must be retained by downstream readers. |

## Verification checklist for future agents

- Confirm package, payload, and receipt files exist for every indexed `ok` run.
- Confirm public-index hashes match local file hashes before claiming integrity.
- Preserve explicit skip/failure statuses; never coerce missing signing inputs into `ok`.
- Keep EATF wording to package/envelope/payload verification.
- Do not use EATF receipts to claim source trusted-list legal validity, signature validity, supervisory approval, provider status, public alerting, compliance, or publication readiness.

## Reviewer answer

If a reviewer asks what EATF proves here, the safe answer is:

> In Cassandra, EATF/AEP proves that a declared evidence package and payload verify according to the package verifier and recorded hashes. It does not prove the legal validity of any trusted list, the validity of any trusted-list signature for relying-party purposes, or the compliance/status of any provider or service.
