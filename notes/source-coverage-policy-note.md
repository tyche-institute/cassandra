# Source coverage policy note

Date: 2026-05-21
Lane: cassandra
safe_to_rewrite_historical_bundles: false

This note records the local provenance policy behind the current SOURCES.md coverage checks. SOURCES.md is a provenance register for external inputs and local reference context: it records the public URL or read-only local path, access date, reliability note, and local snapshot or metadata path that made the source observable in this workspace. It does not duplicate every bundle-source hash for every frozen MIRROR-style bundle, because those hashes already live in the bundle manifests that were created at the time of each dated run.

For Cassandra, the validator therefore checks two layers separately. First, snapshot manifest entries must have URL and destination-path coverage in SOURCES.md, so a reader can trace which LOTL-derived public endpoint produced which local snapshot path. Second, bundle source-file hashes are checked from frozen bundle manifests, because the manifest is the evidence bundle's own integrity boundary. Repeating every bundle-source hash in SOURCES.md would create a second mutable ledger and invite accidental drift after later validators refresh derived files.

This policy explains the current source-coverage warning report without rewriting historical bundles. Older bundle rows may have documentation-style warnings when they do not have date-specific SOURCES.md rows, but those warnings are not hard provenance failures when the bundle manifest lists its sources and local hash checks pass. The default response is to preserve historical bytes, record the warning context, and require operator review before any external circulation or named listed entities are used in prose.

The policy is research-only. It does not assert legal effect, does not perform trusted-list validation, does not validate signatures for relying-party purposes, does not supervise trusted lists, does not provide public alerting, does not create regulated trust-service output, and does not imply publication approval.
