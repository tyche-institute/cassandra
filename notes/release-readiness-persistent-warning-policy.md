# Release-readiness persistent-warning policy note

Created: 2026-05-21T00:42:30.126871+00:00
Source report: `notes/release-readiness-warning-report-output.json`
Source report status: `ok`
Release-readiness warning sources: `4`

## Purpose

This local note records which release-readiness warning classes are expected to persist across append-only Cassandra history. It exists to prevent future workers from treating stable, caveated warnings as either hard failures or as safe-to-clear items. It is not a publication gate and is not a legal review.

## Current persistent warning classes

- `artifact_index_duplicate_row_current_hash_present`: 1 observed in the current warning report.
- `caveated_alert_risky_phrase`: 7 observed in the current warning report.
- `caveated_bundle_helper_risky_phrase`: 8 observed in the current warning report.
- `caveated_bundle_risky_phrase`: 1 observed in the current warning report.
- `caveated_public_alerting_phrase`: 1 observed in the current warning report.
- `caveated_relying_party_validation_phrase`: 1 observed in the current warning report.
- `caveated_svg_risky_phrase`: 12 observed in the current warning report.
- `legacy_append_only_alert_context`: 1 observed in the current warning report.
- `manual_review_warning`: 1 observed in the current warning report; this covers the hash-cycle policy reference validator preserving checklist warning context rather than clearing it.

## Interpretation policy

Persistent warnings remain visible because Cassandra keeps append-only alert rows, historical bundle notes, generated SVG caveats, and repeated artifact-index rows as reproducibility evidence. The current warning-report output classifies these items as manual-review context only. A future worker may refresh validators and reports, but should not automatically delete historical rows, rewrite frozen bundles, or remove caveated words merely to obtain a zero-warning release-readiness checklist.

The expected maintenance posture is:

1. Keep hard errors at zero before any operator review.
2. Preserve warning classes that document legacy append-only context, caveated risky-phrase detections, or duplicate rows with at least one current matching hash.
3. Escalate to `BLOCKED.md` if a warning becomes an uncaveated claim of legal effect, supervision, relying-party signature validation, public alerting, regulated trust-service output, listed-entity status, or publication approval.
4. Treat any proposal to rewrite historical bundles, remove append-only alert entries, or publish externally as operator-review work, not autonomous worker cleanup.

## Non-clearance caveat

This note is local workflow-maintenance context only. It does not clear warnings, rewrite historical artifacts, approve publication, perform legal review, validate signatures, supervise trusted lists, determine listed-entity status, provide public alerting, or create regulated trust-service output.
