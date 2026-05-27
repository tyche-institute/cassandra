# Cassandra Full-Stack Usable Transcript Seed

Date: 2026-05-27
Status: seed transcript for the autonomous Zeus/Hermes publication lane

## One-Sentence Case

Cassandra turns public eIDAS trusted-list governance infrastructure into evidence infrastructure: dated observations, structural diffs, MIRROR-style bundles, EATF/AEP receipts, and a live public dashboard.

## What Exists Now

- Public dashboard: `https://cassandra-observatory.pages.dev/`
- Public index: `https://cassandra-observatory.pages.dev/data/index.json`
- Scheduled workflow: `.github/workflows/cassandra-observatory.yml`
- Dated observations: `2026-05-20`, `2026-05-21`, `2026-05-22`, `2026-05-27`
- Evidence status: all four observations have EATF `ok`
- Signing profile: `github-secret:cassandra-eatf-key`
- Full GitHub Action deploy run: `26521328723`

## Full-Stack Flow

```text
EU LOTL / national trusted-list sources
  -> pointer extraction and fetch manifests
  -> normalization manifests
  -> structural diff JSON
  -> aggregate tables and SVG figures
  -> MIRROR-style snapshot bundle
  -> EATF/AEP evidence package and verification receipt
  -> public dashboard index
  -> Cloudflare Pages deployment
  -> thesis/paper evidence case
```

## Why This Is More Than XML

Trusted lists are public legal-technical state. Cassandra does not interpret that state as a supervisor or relying party. Instead, it demonstrates how state can be observed, hashed, packaged, and verified while keeping legal interpretation outside the machine pipeline.

The exciting thesis move is that evidence infrastructure is not limited to AI model logs. Public governance artifacts can also be treated as evidence streams. That creates a bridge between eIDAS primitives and AI Act evidence duties.

## What Needs More Work

The empirical lane is real, but the fixture layer is thin. The paper should not rely only on four dated observations. It needs controlled fixtures that prove the software and claim boundary behave correctly.

Priority fixture additions:

- no-change run;
- normalized-hash change;
- provider inventory change;
- service inventory change;
- provider-service-detail change;
- fetch failure and redirect;
- non-XML skip;
- EATF ok package;
- EATF tampered package failure;
- missing signing inputs;
- dashboard multi-status index;
- claim-safety scanner fixture.

## Paper Contribution

The paper contribution should be framed as:

1. a method for longitudinal structural observation of public trust infrastructure;
2. a case study in separating evidence integrity from legal interpretation;
3. a working observatory that packages each snapshot as independently verifiable evidence;
4. a bridge from eIDAS/PKI trust primitives to AI governance evidence infrastructure.

## Cards To Build

The publication kit should include:

- abstract card;
- venue-fit card;
- reviewer-objection card;
- limitations card;
- claims-and-evidence table;
- data dictionary;
- fixture matrix;
- evidence package format card;
- EATF claim-boundary card;
- thesis integration card;
- cross-case map with EATF, MIRROR, PKI Atlas, X-Road, Vesta, Icarus, and Breakable Receipts.

## Reviewer-Safe Language

Use:

- structural observation;
- evidence package;
- public artifact;
- hash-verifiable snapshot;
- longitudinal telemetry;
- claim boundary;
- replay capsule.

Avoid:

- legal validity;
- compliance proof;
- official audit;
- provider-specific verdict;
- signature validation unless actually implemented and reviewed;
- public alerting;
- supervisory finding.

## First Hermes Deliverable

Create `notes/cassandra-full-stack-usable-transcript-2026-05-27.md` as a polished transcript that expands this seed into a paper-ready, reviewer-readable account. Then move into fixtures, schemas, cards, and paper edits.
