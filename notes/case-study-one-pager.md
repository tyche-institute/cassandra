# Cassandra case-study one-pager

## Spine

Cassandra: from governance infrastructure to evidence infrastructure.

## What it is

Cassandra is a research-only observatory over public European list-of-lists and national trusted-list artifacts. It records dated collection telemetry, normalizes parseable XML, emits cautious structural diffs, packages evidence, verifies EATF/AEP receipts for package integrity, and publishes aggregate dashboard data with caveats.

## Why it matters

The case shows that public legal-technical governance artifacts can become observable, hashable, packageable, verifiable, displayable, and discussable without pretending that the observer is a regulator, relying party, or legal authority.

## Current public state

- Dashboard: `https://cassandra-observatory.pages.dev/`
- Public data index: `https://cassandra-observatory.pages.dev/data/index.json`
- Latest local/public index date: `2026-05-27`
- Run count: `4`
- EATF verified count: `4`
- Local schema: `observatory/public/data/schema.json`

## Evidence loop

1. Fetch public LOTL-derived artifacts.
2. Save dated manifests and metadata.
3. Normalize parseable XML and record skips/errors.
4. Compare structural summaries against local baselines.
5. Bundle claims, sources, hashes, and verification outputs.
6. Package selected evidence with EATF/AEP and verify receipts.
7. Publish aggregate dashboard telemetry and caveats.

## What it does not do

Cassandra does not determine legal status, validate trusted-list signatures for relying-party use, supervise providers, issue public alerts, make compliance judgments, or prove absence of legally relevant change.
