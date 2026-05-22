# Diff review — 2026-05-22

Aggregate structural-observation review only; not trusted-list validation, not signature validation, not supervision, not legal-status determination, not listed-entity status evidence, not public alerting, and not publication approval.

Reviewed diff: `diffs/2026-05-22.json`
Change entries: 26 (reported: 26)

## Aggregate class counts

- `normalized_hash_changed`: 3
- `provider_service_detail_changed`: 6
- `service_inventory_changed`: 3
- `summary_field_changed`: 14

## Aggregate key coverage

- Country-code keys with observed structural entries: SE, SI, SK
- Raw listed names were not dereferenced or reproduced in this review.

## Summary-field counts

- `issue_date_time`: 3
- `next_update`: 3
- `sequence_number`: 3
- `signature_shape`: 2
- `tsp_service_count`: 3

## Service-inventory movements

- `SE`: service count 12 -> 14 (delta +2); added hashed service keys 2; removed hashed service keys 0.
- `SI`: service count 100 -> 105 (delta +5); added hashed service keys 5; removed hashed service keys 0.
- `SK`: service count 183 -> 186 (delta +3); added hashed service keys 3; removed hashed service keys 0.

## Signature-shape movements

- `SI`: signature method shape ['http://www.w3.org/2001/04/xmldsig-more#rsa-sha512'] -> ['http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha512']; no cryptographic verification performed.
- `SK`: signature method shape ['http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'] -> ['http://www.w3.org/2001/04/xmldsig-more#rsa-sha512']; no cryptographic verification performed.

## Decision

Add or refine a semantic diff roll-up focused on signature-shape and service-inventory aggregate classes before adding named examples or public prose.

The first non-empty run is concentrated in three country-code keys with metadata/date fields, service-count additions, and two signature-method shape changes; aggregate roll-up will reduce overinterpretation risk.
