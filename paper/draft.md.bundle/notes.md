# Cassandra paper draft evidence bundle

Created: 2026-05-22T17:16:10Z

## Purpose

This MIRROR-style bundle records reproducible local provenance for `paper/draft.md`, the Cassandra lane's research-only companion paper draft. The bundle is adjacent to the draft and supports offline hash and source-reference replay. It does not publish the paper, approve publication, provide legal review, validate trusted-list signatures, supervise trusted lists, determine listed-entity status, provide public alerting, or create regulated trust-service output.

## Methodology

The bundle records the current draft hash, copies local state registers, paper validator outputs, aggregate result artifacts, figure artifacts, and dated snapshot-bundle manifests into `sources/`, and lists cautious claims in `claims.json`. The evidence is local workspace evidence only. No network calls were made to create this paper bundle, and no live endpoint was reinterpreted for paper claims.

## Known gaps

- Validator outputs are heuristic and do not replace operator or legal review.
- The bundle does not sign or timestamp the paper.
- The draft remains a local research artifact and is not approved for external circulation.
- Aggregate structural observations must not be read as legal effect, supervision, relying-party validation, or listed-entity status determination.

## Assumptions

- Local source files copied into this bundle reflect the workspace state at creation time.
- Historical dated snapshot bundles remain available under `bundles/YYYY-MM-DD/`.
- The paper should continue to avoid raw listed-entity prose unless the operator explicitly approves a named example.
