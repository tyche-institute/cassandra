# Status-only report reference-checker policy

Date: 2026-05-21

## Scope

`notes/validate_status_only_release_gates_report_references.py` remains an out-of-band operator-review check rather than a release-readiness checklist dependency. The checker reads the release-readiness checklist output and the status-only release gate report, then verifies that the report embeds the current checklist hash and remains referenced by both the paper checklist and the checklist validator source.

## Cycle-avoidance decision

The checker is intentionally not added to `notes/validate_release_readiness_checklist.py` as another status-only gate. Adding it would create a checklist/report/checker freshness loop:

1. The checklist would read the checker output for status and warning counts.
2. The status-only report would summarize the checklist and embed the checklist hash.
3. The checker would validate that embedded checklist hash.
4. Regenerating any one of the three files could force another refresh without changing substantive provenance.

Keeping the checker out-of-band preserves a simple operator-review sequence: refresh the checklist, refresh the status-only report, then run the reference/freshness checker as an independent guard. This is not missing provenance; it is deliberate cycle avoidance for local workflow telemetry.

## Claim-safety boundary

This policy note and its validator do not clear warnings and do not approve publication, perform legal review, validate signatures for relying-party purposes, supervise trusted lists, determine listed-entity status, provide public alerting, assert trusted-list legal effect, or create regulated trust-service output. In short, the policy does not clear warnings; it only records the workflow-boundary decision. They only document why one workflow-maintenance checker remains out-of-band until an operator chooses a different gate topology.
