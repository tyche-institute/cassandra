# Cassandra venue-fit card

Purpose: help choose venues and position the submission without overstating what Cassandra implements.

## Best-fit venue families

| Venue family | Why Cassandra fits | Framing to emphasize | Framing to avoid |
|---|---|---|---|
| Digital government / public administration technology | The case studies public machine-readable governance artifacts and administrative evidence flows. | Governance artifacts as reproducible public evidence infrastructure. | Operational regulator, compliance monitor, or public alerting service. |
| Trust, identity, PKI, and security engineering workshops | The empirical surface is eIDAS/PKI-adjacent and involves hashable artifacts, evidence packages, and verifier UX. | Structural observation, package integrity, reproducible telemetry. | Relying-party trusted-list validation or source signature validation. |
| FAccT / AI governance infrastructure workshops | The methodological bridge to AI Act evidence records is strong. | How governance records can become durable, checkable evidence without becoming legal approval. | Claims about AI model behavior, AI risk scoring, or compliance judgment. |
| Reproducibility / research software tracks | The project is an operated pipeline with public index, schema, fixtures, and evidence packages. | Reusable evidence loop and fixture-backed behavior. | Dataset completeness or legal authority. |

## Primary submission pitch

Cassandra is a case-study system paper: it turns a public governance surface into an end-to-end evidence loop and uses eIDAS trusted-list artifacts as the empirical case. The novelty is not an XML parser; it is the disciplined boundary between observation, packaging, verification, dashboard display, and non-interpretation.

## Reviewer-facing angle

The paper should foreground three deliverables:

1. A live but claim-limited observatory over public governance artifacts.
2. A reproducible evidence package loop using hashes, manifests, and EATF/AEP receipts.
3. Synthetic fixtures that make edge behavior reviewable without exposing provider-specific claims.

## Submission caution

Any venue pitch must keep the case within structural observation and evidence integrity. Cassandra does not determine trusted-list legal status or legal effect, validate trusted-list signatures for relying-party use, supervise providers, issue public alerts, or approve publication.
