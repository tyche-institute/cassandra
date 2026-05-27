# Cassandra related-work card

Date: 2026-05-27
Status: merge-ready literature scaffold for `paper/draft.md`; not a final bibliography
Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

## Purpose

This card gives the Cassandra paper a real related-work spine without turning it into a general PKI survey. It should be used to merge a compact section into the draft and to guide later formal citations. It separates official primary sources, peer-reviewed or scholarly literature, standards ecosystems, and Tyche internal/prototype work by publication status.

## Citation-status discipline

- Use `notes/cassandra-checked-reference-ledger-2026-05-27.md` as the
  current release-facing source ledger. A source is not paper-ready until
  it has a real anchor, a date checked, a source-status label, and a
  claim role.
- Regulations, ETSI documents, RFCs, NIST FIPS publications, CA/Browser Forum material, OECD reports, and official list-of-lists documentation may be cited as primary source or standards context. They do not endorse Cassandra.
- Peer-reviewed or published scholarly works may be cited normally after bibliographic verification.
- Zenodo deposits and preprints must be labelled as preprints, working papers, datasets, or software artifacts.
- Submitted Tyche manuscripts must be labelled as submitted or under review, not as accepted.
- Internal/prototype cases such as Aletheia, avatar.eatf.eu, eaudit, h2oatlas, MATx, Janus, Vesta, and Icarus require status checks before public claims.
- Synthetic fixtures may support behavior claims about the software method; they must not be described as real governance, learner, client, regulator, environmental, or supervisory evidence.

## Reference shape

The literature review should show horizontal range and vertical depth.
Horizontal range means Cassandra has looked sideways: EU law, ETSI,
IETF/RFC, CA/B Forum, PKIC, NIST, W3C, public administration,
infrastructure studies, and computational social science. Vertical depth
means each large claim can be followed down: concept, legal instrument,
standard, protocol, implementation choice, local artifact, validator,
and limitation.

Footnotes are allowed, but only when they work. A good Cassandra
footnote should clarify a boundary, connect two literatures, or name a
skeptical caveat. A footnote that exists only to wink at the reader is
still an unsupported claim in smaller type.

## Cluster 1 — PKI and cryptographic governance

Cassandra should be positioned above an old but still active governance substrate: public-key infrastructure, certificate policy, revocation, timestamping, validation, assurance audits, and ecosystem coordination. Checked anchors include RFC 5280 for X.509 certificate/CRL profiles, RFC 3161 for timestamping, RFC 8785 for deterministic JSON evidence comparators, CA/Browser Forum Baseline Requirements v2.2.7 (19-May-2026), PKI Consortium work, ETSI audit/policy regimes, and NIST FIPS 203/204/205 for the post-quantum transition. Maurer on PKI trust models and Ellison/Schneier on PKI risks remain useful secondary anchors, but must be added to the checked ledger before final bibliography.

Use this cluster to argue that Cassandra does not invent trust infrastructure. It watches one public administrative surface of that infrastructure and turns observations into bounded evidence packages. Do not imply that PKI sources validate the Cassandra method or that Cassandra performs certificate-path or signature validation.

## Cluster 2 — eIDAS, ETSI, and trusted lists

The checked legal-technical substrate is eIDAS Regulation 910/2014, the eIDAS amendment Regulation 2024/1183, Commission Implementing Decision 2015/1505 on trusted-list technical specifications and formats, the European Commission trusted-list page, ETSI TS 119 612 V2.4.1 on trusted lists, ETSI EN 319 401 V3.1.1 on policy requirements for trust service providers, ETSI EN 319 411-1 V1.5.1 on certificate-issuing TSP requirements, and ETSI EN 319 422 V1.1.1 on timestamping. Cassandra should cite these as the grammar of the public artifacts it observes. Additional ETSI EN 319 412, EN 319 102, and AdES profile references are plausible, but should stay in planning notes until exact versions and claim roles are checked.

The paper should be explicit that reference to eIDAS or ETSI does not make the project a relying-party validator, conformity assessor, trust service, supervisory body, or legal-status oracle. Cassandra's empirical object is the saved public artifact and its local structural telemetry.

## Cluster 3 — AI governance and evidence duties

The AI Act, Regulation 2024/1689, creates a neighboring evidence problem: logging, transparency, documentation, post-market monitoring, and conformity-assessment records need credible lifecycle evidence. Cassandra is not an AI model-behavior monitor; it is a public-governance-artifact case that demonstrates methods likely to matter for AI governance records: dated observations, hashes, manifests, package-level receipts, replayable verification, and explicit claim boundaries.

Tyche/EATF/AEP manuscripts and Zenodo artifacts may be used here only with status labels. The strongest wording is analogical: eIDAS/PKI show mature trust primitives; Cassandra shows how public governance state can become evidence infrastructure; EATF/AEP and MIRROR show package and bundle patterns that could support AI governance evidence.

## Cluster 4 — public administration and digital-state literature

Cassandra should connect to digital government and public-administration scholarship because trusted lists are public administrative artifacts, not merely XML files. Useful anchors include Drechsler on e-Estonia, Kattel/Lember/Tonurist on public-sector innovation, Mazzucato/Kattel/Drechsler on public value and state capacity, Bannister and Connolly on trust and transformational government, Margetts and Dorobantu on AI and government, OECD digital government/data governance reports, and Estonian e-state/X-Road literature.

This cluster supports the phrase "governance infrastructure". It should not be used to claim that Cassandra evaluates government performance or supervises authorities.

## Cluster 5 — infrastructure studies and turning-point theory

Perez's turning-point theory helps frame why evidence institutions matter during deployment of new technological regimes. Star and Ruhleder, Bowker and Star, Edwards, Plantin, Larkin, and Jasanoff help explain infrastructure as relational, classificatory, institutional, political, and often visible only when maintained or broken. Cassandra fits this literature as a small operational case: the dashboard and evidence packages make an otherwise specialized governance surface discussable.

Use this cluster to lift the paper above tooling. Avoid turning it into grand theory unsupported by the current evidence base.

## Cluster 6 — computational social science and evidence method

Lazer, Salganik, Grimmer/Roberts/Stewart, Edelmann, and Bail are useful for method discipline: computational observation can scale public-document analysis, but public-facing claims require design validity, measurement humility, reproducible data handling, and careful interpretation. Cassandra's synthetic fixtures, aggregate-only prose, and claim-safety scanner should be presented as methodological safeguards.

## Tyche internal/public works

- PKI as Governance Infrastructure: use as submitted/under-review manuscript until status changes.
- EATF/AEP: cite Zenodo/software/preprint artifacts according to exact status; frame as package-level evidence framework, not regulated trust service.
- MIRROR: cite as bundle pattern and source/claim manifest discipline unless public paper exists.
- Janus, MATx, Vesta, Icarus, eaudit, h2oatlas, Aletheia: use only as maturity-matrix cases with honest publicness and permission labels.

## Mergeable paragraph for `paper/draft.md`

Cassandra sits at the intersection of PKI governance, eIDAS trusted-list publication, digital-state administration, infrastructure studies, and computational evidence methods. The relevant PKI and standards literature explains the older governance substrate: certificates, certificate policies, timestamping, revocation, audit regimes, and validation conventions. The eIDAS and ETSI sources explain why trusted lists are not arbitrary XML but public legal-technical artifacts. Public-administration and infrastructure studies explain why such artifacts matter institutionally, while computational social-science method explains why repeated observation requires measurement humility. Cassandra's contribution is therefore not a new validator or status oracle. It is a bounded method for turning a public governance surface into dated, hash-linked, packageable evidence while preserving the line between evidence integrity and legal interpretation.

## Reference seed artifact

The concrete seed bibliography lives in `paper/reference-seed-bibliography.md`. Use that file as the controlled bridge from clusters to draft citations; do not promote unverified scholarly entries, internal/prototype cases, or synthetic fixtures into final references without status checks.

## Footnote candidates

- PKI governance: PKI is introduced as cryptography, but it lives as
  certificates, policies, revocation, audits, root distribution, and
  institutional delegation. Cassandra watches one public record of that
  governance work.
- Trusted-list boundary: trusted-list standards make the observed XML
  meaningful. They do not promote the observer into a supervisor.
- Turning point: Perez helps name the institutional moment; infrastructure
  studies explain why the moment shows up in maintenance routines, lists,
  schemas, and failure modes.
- Method humility: repeated observation is powerful because it is dull
  enough to re-check. That dullness is a feature, not a defect.

## Next bibliography tasks

1. Convert this card into formal references with complete author/title/year/URL/DOI metadata.
2. Promote additional secondary sources only after they appear in the checked-reference ledger with claim roles.
3. Re-check Tyche internal/public status before any public bibliography.
4. Keep the main draft's related-work section compact; use this card as the extended reviewer-answer artifact.
