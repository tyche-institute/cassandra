# MIRROR bundle card — Cassandra

Purpose: explain how Cassandra's MIRROR-style bundles preserve local provenance for dated structural-observation runs.

Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

## Safe claim

A Cassandra MIRROR-style bundle packages a dated run summary with local source references, hashes, cautious claims, notes, and verification metadata. It supports reproducible review of what Cassandra observed and how the observation artifacts are connected.

The bundle does not assert legal effect, trusted-list validity, signature validity, supervisory status, compliance, public warning status, or provider-specific status.

## Bundle shape

Typical path: `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/`

| File | Role | Reviewer use |
|---|---|---|
| `manifest.json` | Bundle manifest with artifact hash, source records, claim links, caveats, and verification pointers. | Check package structure and provenance anchors. |
| `claims.json` | Cautious structural claims tied to local evidence artifacts. | Trace paper/dashboard statements to bounded evidence. |
| `notes.md` | Human-readable method notes and non-claim boundaries. | Verify that interpretation limits travel with the bundle. |
| `sources/` | Copied local manifests or source-reference records. | Reproduce counts and artifact lineage without refetching public endpoints. |
| `verification.json` | Local hash/presence verification output. | Check internal package consistency, not legal truth. |

## Evidence boundary

MIRROR bundles are useful because they bind together:

1. collection telemetry from `snapshots/YYYY-MM-DD/manifest.json`;
2. normalization telemetry from `normalized/YYYY-MM-DD/manifest.json`;
3. structural diff telemetry from `diffs/YYYY-MM-DD.json`;
4. alert roll-up and aggregate summaries;
5. caveats that forbid legal/status overclaiming;
6. hashes that make later replay and citation safer.

The bundle is therefore a provenance object for Cassandra's research workflow. It is not a substitute for an official source, a trusted-list processor, a relying-party validator, a regulator, or legal review.

## Relationship to EATF

MIRROR-style bundles and EATF/AEP receipts play distinct roles:

| Layer | MIRROR-style bundle | EATF/AEP receipt |
|---|---|---|
| Main function | Organize evidence, sources, claims, and caveats. | Verify a package/payload envelope and hashes. |
| Human value | Makes the case reviewable and citable. | Makes package integrity independently checkable. |
| Non-claim | Does not legalize or supervise observations. | Does not validate trusted-list legal or signature status. |

Together, they demonstrate evidence infrastructure: the observation can be packaged for human review and checked for package integrity without crossing into legal interpretation.

## Reviewer answer

If asked why Cassandra needs MIRROR-style bundles when it already has a public dashboard, answer:

> The dashboard is a presentation and navigation layer. The MIRROR-style bundle is the reviewable evidence object behind a dated run: it carries the manifest, source references, bounded claims, notes, hashes, and verification metadata needed to audit the observatory's own workflow without refetching or trusting the UI.

## Artifact anchors

- Generic bundle helper: `create_bundle.py`
- Evidence package card: `notes/evidence-package-format.md`
- Public index schema card: `notes/public-index-schema.md`
- Date-specific bundle manifests: `bundles/YYYY-MM-DD/snapshot-summary.json.bundle/manifest.json`
- Paper evidence bundle: `paper/draft.md.bundle/manifest.json`
