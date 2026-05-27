# Cassandra public index schema

Purpose: reviewer-facing and dashboard-consumer description of `observatory/public/data/schema.json`, the machine-readable contract for `observatory/public/data/index.json`.

Claim boundary: the schema describes Cassandra structural-observation telemetry only. It does not define a trusted-list validator, legal-status register, signature-validation result, supervisory workflow, public alert feed, or publication approval mechanism.

## Schema identity

- Schema file: `observatory/public/data/schema.json`
- Public index file: `observatory/public/data/index.json`
- Schema id: `urn:tyche:cassandra:observatory-public-index:0.1`
- JSON Schema dialect: `https://json-schema.org/draft/2020-12/schema`

The public index also carries a top-level `schema` field with the same identifier. Consumers should treat that field as a compatibility handle, not as proof that the data has legal or supervisory meaning.

## Required public-index sections

| Section | Role | Safe interpretation |
|---|---|---|
| `schema` | Compatibility identifier. | Describes the data contract only. |
| `created_at` | Public index build timestamp. | Build time, not endpoint-currentness or legal-status time. |
| `project`, `repo`, `case_study_sentence` | Project metadata and narrative spine. | Method framing and source location only. |
| `latest_date`, `run_count` | Included dated lineage summary. | Local evidence-row count only. |
| `packaged_evidence_count`, `eatf_verified_count` | Packaging and receipt-status counts. | Package-byte and declared-hash verification only. |
| `aggregate` | Cross-run totals, diff-class totals, public JSON/CSV hashes. | Aggregate structural-observation telemetry. |
| `figures` | Public SVG figure metadata and hashes. | Visual summaries of local counts. |
| `runs` | Per-date counts, diff classes, artifacts, EATF receipt metadata, caveats. | Dated local run evidence. |
| `claim_boundary`, `caveat` | Consumer-visible non-claim rails. | Must remain visible in reuse. |

## Consumer rules

1. Preserve `claim_boundary` and `caveat` when reusing the public index.
2. Treat `eatf.status == "ok"` as evidence-package verification only.
3. Treat `diff_classes` as structural-observation buckets, not legal conclusions.
4. Treat zero diff counts as "no configured structural diff emitted" only, not absence of legally relevant change.
5. Do not convert provider/service aggregate counts into named provider or service claims.
6. Prefer local artifact paths and hashes over live endpoint reinterpretation for dated run claims.

## Validation artifact

`notes/test_public_index_schema.py` checks that the schema file exists, that the current public index declares the schema id, that required sections are present, and that every current run preserves counts, diff classes, artifacts, EATF status, and caveat text.

Verification command:

```bash
.venv/bin/python notes/test_public_index_schema.py
```

A passing test means the current public index matches the local schema contract checked by this repository. It does not approve publication, perform legal review, validate signatures for relying-party purposes, supervise trusted lists, determine listed-entity status, provide public alerting, or create regulated trust-service output.
