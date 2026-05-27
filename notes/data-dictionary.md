# Cassandra data dictionary

Purpose: reviewer-facing dictionary for the public Cassandra observatory data and local evidence artifacts. This document explains field meaning for structural-observation research only. It does not define a trusted-list validator, legal-status register, signature-validation result, supervisory process, public alerting service, or publication clearance.

Current public index source: `observatory/public/data/index.json`  
Current latest date: `2026-05-27`  
Current run count: `4`

## Top-level public index fields

| Field | Type | Meaning | Claim boundary |
|---|---|---|---|
| `project` | string | Project identifier, currently `cassandra`. | Naming only. |
| `repo` | string | Public repository URL. | Source location, not endorsement or legal status. |
| `case_study_sentence` | string | Narrative spine for the case study. | Method framing only. |
| `caveat` | string | Public boundary statement for the index. | Must remain visible in dashboard consumers. |
| `created_at` | ISO timestamp | Time the public index was built. | Build time, not endpoint-currentness guarantee. |
| `latest_date` | date string | Latest dated local lineage included in the public index. | Local lineage date, not legal/current status date. |
| `run_count` | integer | Count of dated run rows included. | Dataset size telemetry only. |
| `packaged_evidence_count` | integer | Count of runs with package metadata. | Packaging availability only. |
| `eatf_verified_count` | integer | Count of runs whose EATF receipt status is `ok`. | Package/receipt verification count, not trusted-list validation. |
| `claim_boundary` | object | Explicit allowed/denied public claims. | Consumers should display or preserve this boundary. |
| `aggregate` | object | Cross-run aggregate telemetry and artifact hashes. | Aggregate structural-observation data only. |
| `runs` | array | Per-date run summaries. | Dated local telemetry only. |
| `figures` | array | Public SVG figure metadata. | Visual summaries must keep caveats. |

## `aggregate.totals`

| Field | Meaning | Safe use |
|---|---|---|
| `pointer_attempts` | Total LOTL-derived pointer attempts across included runs. | Describe collection workload. |
| `fetched_content_files` | Total successfully saved content files. | Describe saved corpus size. |
| `fetch_errors` | Total endpoint fetch errors recorded by the lane. | Describe operational collection telemetry only. |
| `normalized_xml_artifacts` | Total XML artifacts normalized for comparison. | Describe comparable XML set size. |
| `normalization_skips` | Total non-XML/PDF/skip outcomes. | Describe corpus shape. |
| `normalization_errors` | Total parser/normalization error outcomes. | Describe parser telemetry. |
| `diff_change_count` | Total machine-readable structural diff entries. | Structural churn count only. |
| `alert_entry_count` | Total append-only alert-roll-up telemetry entries. | Internal roll-up count, not public alerting. |
| `provider_count_total` | Sum of observed provider-count fields across runs. | Aggregate parser telemetry, not provider status. |
| `service_count_total` | Sum of observed service-count fields across runs. | Aggregate parser telemetry, not service status. |

## Diff classes

| Class | Meaning | Non-claim |
|---|---|---|
| `listed_document_added` | Comparable document key appears in current normalized set but not baseline. | Does not mean a legal list/entity was added. |
| `listed_document_removed` | Comparable document key appears in baseline but not current normalized set. | Does not mean legal status was removed. |
| `normalized_hash_changed` | Canonical normalized XML bytes differ for the comparable key. | Does not explain legal significance. |
| `summary_field_changed` | One coarse parsed summary field changed. | Does not validate semantic/legal effect. |
| `provider_inventory_changed` | Hashed provider-key set changed. | Hash keys are local handles, not prose identifiers. |
| `service_inventory_changed` | Hashed service-key set changed. | Hash keys are local handles, not legal-status claims. |
| `provider_service_detail_changed` | Aggregate details under a provider hash changed. | Requires cautious review; not provider-specific prose. |

## Per-run fields

| Field path | Meaning | Claim boundary |
|---|---|---|
| `runs[].date` | Dated local lineage. | Run date only. |
| `runs[].counts.*` | Count telemetry from snapshot, normalization, diff, and alert artifacts. | Workflow evidence only. |
| `runs[].diff_classes.*` | Per-run counts by structural diff class. | Structural observations only. |
| `runs[].artifacts.*` | Local artifact paths and hashes. | Evidence linkage, not claim truth. |
| `runs[].eatf.status` | EATF verification status string. | Package verification status only. |
| `runs[].eatf.valid` | Boolean receipt validity as reported by verifier. | Does not validate trusted-list content or signatures. |
| `runs[].eatf.package_sha256` | Hash of AEP package bytes. | Byte integrity handle. |
| `runs[].eatf.payload_sha256` | Hash of package payload bytes. | Byte integrity handle. |
| `runs[].eatf.receipt_sha256` | Hash of verification receipt JSON. | Receipt provenance handle. |
| `runs[].caveat` | Per-run boundary statement. | Must not be stripped in public reuse. |

## Local artifact families

| Family | Example | Role |
|---|---|---|
| Sources | `sources/eu-lotl.xml`, `notes/pointers.json` | Saved public input and extracted pointer set. |
| Snapshots | `snapshots/YYYY-MM-DD/manifest.json` | Dated collection telemetry and file metadata. |
| Normalized | `normalized/YYYY-MM-DD/manifest.json` | Comparable XML summary and normalization telemetry. |
| Diffs | `diffs/YYYY-MM-DD.json` | Machine-readable structural comparisons. |
| Bundles | `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/` | MIRROR-style local evidence package. |
| EATF | `evidence/YYYY-MM-DD/*.aep`, `eatf-verification.json` | Offline package/receipt verification. |
| Observatory | `observatory/public/data/*.json`, `*.csv`, figures | Public aggregate dashboard data. |
| Paper/cards | `paper/draft.md`, `notes/*.md` | Human-readable argument and review aids. |
