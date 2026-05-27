# Cassandra publication-status discipline

Date: 2026-05-27
Status: operator-review scaffold; not publication approval
Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

## Purpose

This card prevents Cassandra's evidence quality from being confused with publication readiness, legal review, endpoint certification, or public alerting. Cassandra can build strong local evidence objects while still remaining a working draft and research-only observatory until Anton explicitly approves external circulation.

## Status labels

| Label | Meaning | Allowed public-facing use | Forbidden inference |
|---|---|---|---|
| Working draft | Local paper prose under active revision | Internal review, thesis planning, reviewer-prep notes | Not publication-ready, accepted, peer reviewed, legally reviewed, or externally cleared |
| Local evidence artifact | Snapshot, normalized manifest, diff, bundle, validator output, dashboard card, or fixture stored in repo | Cite by path/hash inside draft or thesis packet | Not legal-status determination, supervision, compliance evidence, public alerting, or reliance guidance |
| Public dashboard data | Machine-readable index and cards deployed to Cassandra observatory | Demonstrates bounded observatory method and public-data schema | Not a public warning feed, official list, trusted-list validator, or supervisory source |
| Synthetic fixture | Controlled test data or tamper/failure case | Software behavior demonstration and claim-safety evidence | Not real provider/service/governance/learner/client/regulator evidence |
| Preprint / Zenodo artifact | Public research artifact with DOI or stable page | Cite with exact version/status once verified | Not peer reviewed unless independently accepted |
| Submitted / under-review manuscript | Manuscript in review workflow | Internal thesis context or disclosed status reference | Not accepted, forthcoming, or published |
| Internal/prototype case | Local, hidden, partner, or product-prototype material | Use only in private matrix until publicness and permission are checked | Not deployment, adoption, endorsement, or public case evidence |
| Operator-approved release | Explicit Anton-approved external circulation package | External sharing according to approved scope | Still not legal/supervisory/compliance claim unless separately reviewed |

## External-circulation gate

Before any paper, figure, bundle, dataset slice, dashboard claim, or case-study packet is circulated outside the repo/vault context, check:

1. The item has a declared status label from this card.
2. Any public URL or DOI has been rechecked for current availability and exact version.
3. Any submitted manuscript is labelled as submitted/under review, not as accepted.
4. Any internal/prototype case has publicness, permission, and data-sensitivity status checked.
5. No prose says or implies legal validity, signature validity, supervisory status, compliance judgment, public alerting, provider-specific status, or absence of legally relevant change.
6. Named examples, if any, have operator approval and path/hash/source context.
7. EATF/AEP wording says package/integrity verification only, not trust-service or legal validation.
8. Dashboard wording says research observatory/public data surface only, not official monitoring or warning service.

## How to cite Cassandra itself

Safe internal citation style:

> Cassandra trusted-list observatory, working research artifact, local repository and public dashboard data index, 2026-05-27, structural observation only; not trusted-list validation, legal-status determination, supervision, signature validation, relying-party processing, or public alerting.

Short paper wording:

> The current Cassandra system is an operated research observatory with a public dashboard and machine-readable index, but the paper remains a working draft pending operator review.

## How to cite Tyche adjacent works

- Published or official sources: cite normally after bibliographic verification.
- Zenodo/preprints: cite as preprint, working paper, dataset, or software artifact with DOI/version.
- Submitted manuscripts: cite internally as submitted/under review, with status visible.
- Internal cases: cite only in private thesis maps unless public release and permissions are explicit.
- Prototypes: mark as prototype or deployment attempt, not adoption.
- Synthetic examples: mark as synthetic fixture/test vector.

## Reviewer-answer value

If a reviewer sees hashes, receipts, and a dashboard and asks whether Cassandra is claiming legal authority, the answer is no. These are evidence-integrity and reproducibility controls: not trusted-list validation, not legal-status determination, not signature validation, not supervision, and not a public warning feed. Publication status, legal interpretation, trust-service status, and public alerting all remain outside the autonomous lane unless separately reviewed and approved.
