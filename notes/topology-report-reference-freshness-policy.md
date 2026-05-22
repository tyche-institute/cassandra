# Topology-report reference freshness policy

Date: 2026-05-21

## Scope

`notes/validate_topology_report_reference_freshness.py` remains an out-of-band operator-review check rather than a release-readiness checklist dependency. The checker reads the paper checklist, `notes/release-readiness-topology-report-output.json`, and `ARTIFACT_INDEX.md`, then verifies that the paper still references the topology report and that at least one artifact-index row matches the current topology-report hash.

## Cycle-avoidance decision

The checker is intentionally not added to `notes/validate_release_readiness_checklist.py` as another status-only gate. Adding it would create a checklist/topology/freshness loop:

1. The checklist would read the topology-reference freshness output for status and warning counts.
2. The paper checklist references the topology report as operator-review context.
3. The topology-reference freshness checker validates the paper reference and the topology report's current artifact-index hash.
4. Regenerating the checklist, topology report, or freshness checker output could force another refresh without changing substantive provenance.

Keeping the checker out-of-band preserves a simple operator-review sequence: refresh the checklist and topology report, then run the topology-reference freshness checker as an independent evidence-reference guard. This is not missing provenance; it is deliberate cycle avoidance for local workflow telemetry.

## Claim-safety boundary

This policy note and its validator do not clear warnings and do not approve publication, perform legal review, validate signatures for relying-party purposes, supervise trusted lists, determine listed-entity status, provide public alerting, assert trusted-list legal effect, or create regulated trust-service output. In short, the policy does not clear warnings; it only records why one paper/topology evidence-reference checker remains out-of-band until an operator chooses a different gate topology.
