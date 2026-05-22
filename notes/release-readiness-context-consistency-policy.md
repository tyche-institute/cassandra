# Release-readiness context-consistency policy

Date: 2026-05-21

`notes/validate_release_readiness_context_consistency.py` remains an out-of-band operator-review check. It is intentionally not added to `notes/report_release_readiness_topology.py` as a topology source and is intentionally not added to `notes/validate_release_readiness_checklist.py` as a release-readiness checklist dependency.

The reason is deliberate cycle avoidance, not missing provenance. The context-consistency validator reads the current topology report, warning report, gate summary, and status-only release gate report to check that their names and counts remain mutually aligned. If the topology report depended on the context-consistency output, the workflow would form a topology/context-consistency loop in which refreshing either artifact would stale the other. If the release-readiness checklist depended on this checker, it would extend the existing checklist/report/freshness churn that the status-only and out-of-band policies already avoid.

The policy is therefore:

- keep `notes/release-readiness-context-consistency-validation-output.json` as local operator-review workflow telemetry;
- keep it outside the release-readiness checklist unless Anton explicitly requests a topology change;
- keep it outside the topology report source list unless a future non-cyclic design is added;
- record its hash in `ARTIFACT_INDEX.md` and its cautious claim in `CLAIMS.md`;
- treat warnings as manual-review context only.

This policy does not clear warnings, approve publication, perform legal review, validate signatures, supervise trusted lists, determine listed-entity status, provide public alerting, assert trusted-list legal effect, or create regulated trust-service output.
