# Cassandra 2026-05-20 snapshot summary bundle

## Purpose

This MIRROR-style bundle records reproducible local provenance for the Cassandra lane's 2026-05-20 snapshot, normalization, baseline, and diff summary. It is a research-only evidence bundle for structural observation.

## Methodology

The lane used the locally pinned Python environment to fetch the public EU LOTL XML, extract national-list pointers, fetch the listed public endpoints, normalize XML-like artifacts, and initialize a day-one diff baseline. This bundle summarizes local manifests rather than reproducing every large raw XML/PDF file.

## Known gaps

- The bundle does not perform cryptographic signature verification.
- The bundle does not determine or assert legal status for any listed entity or service.
- Two endpoint fetches produced operational errors during the recorded run.
- One fetched content file produced an XML parse error in the normalizer.
- The day-one diff is empty because the baseline was initialized on this date.

## Assumptions

- Local workspace files referenced by hashes remain available for deeper replay.
- Counts are tool telemetry and should be reviewed before public use.
- Prose should remain aggregate-only unless Anton explicitly approves named-entity discussion.
