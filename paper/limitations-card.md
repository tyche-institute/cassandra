# Cassandra limitations card

Purpose: keep the paper's negative space explicit and reusable in reviewer responses about structural observation.

## Hard limitations

1. Cassandra does not determine the legal effect of any trusted list or listed entity.
2. Cassandra does not validate trusted-list signatures for relying-party purposes.
3. Cassandra does not supervise trusted lists, providers, services, or public authorities.
4. Cassandra does not issue public alerts or compliance judgments.
5. Cassandra does not prove absence of legally relevant change.
6. Cassandra does not make provider-specific prose claims in the paper/dashboard.
7. Cassandra does not approve publication or replace legal/operator review.

## Method limitations

| Limitation | Why it matters | Mitigation |
|---|---|---|
| Dated local lineage | Public endpoints may change after a run. | Use saved manifests, hashes, and source metadata for dated claims. |
| Fetch failures and skips | Collection is imperfect and documents may be non-XML or unavailable. | Record fetch errors, redirects, skips, and parser telemetry explicitly. |
| Structural diff scope | Diff classes are configured observations, not complete semantic interpretation. | Use cautious wording and fixture-backed expected behavior. |
| Aggregate hashing | Provider/service handles are local structural keys. | Avoid named-provider prose and keep aggregate-only outputs. |
| EATF receipt scope | Receipts verify package bytes and declared hashes only. | Preserve EATF caveats in index, paper, and dashboard. |
| Early corpus length | Current public series is short. | Present live observations as first series and use fixtures for controlled behavior. |

## Suggested paper wording

"Cassandra demonstrates a reproducible evidence loop for public governance artifacts. Its outputs support structural-observation and package-integrity claims only; they do not establish legal status, relying-party validity, supervisory approval, compliance, public alerting, or absence of legally relevant change."
