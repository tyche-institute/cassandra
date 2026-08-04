---
title: "Cassandra: From Governance Infrastructure to Evidence Infrastructure"
author: "Anton Sokolov"
affiliation: "Tyche Institute, Tallinn, Estonia"
date: "2026-05-27"
version: "v0.1 preprint candidate"
status: "operator-review required before external submission"
---

# Cassandra: From Governance Infrastructure to Evidence Infrastructure

Anton Sokolov  
Tyche Institute, Tallinn, Estonia  
v0.1 preprint candidate, 2026-05-27

## Abstract

Public-key infrastructure is often described as a cryptographic
substrate, but in practice it is also governance infrastructure: a
system of certificates, policies, revocation channels, trusted lists,
audits, supervisory conventions, software distribution, and institutional
delegation. This paper presents Cassandra, a bounded research
observatory for European list-of-lists-derived trusted-list artifacts.
Cassandra records dated attempts to collect public trusted-list
documents, normalizes comparable XML artifacts, emits structural diff
classes, packages each substantive run into evidence bundles, exposes
aggregate public dashboard data, and attaches EATF/AEP receipt metadata
to the resulting evidence packages. The case demonstrates a shift from
governance infrastructure to evidence infrastructure: public
legal-technical artifacts can be observed, hashed, bundled, signed,
displayed, and independently checked while preserving the distinction
between evidence integrity and legal interpretation. Across four dated
local/public lineages, Cassandra records 43 pointer attempts per run,
31 comparable normalized XML artifacts per run, 66 aggregate structural
diff entries under the configured method, four EATF-verified package
receipts, and five public dashboard cards. Synthetic fixtures cover
stable/no-change behavior, normalized-hash changes, provider/service
inventory changes, fetch failures, non-XML handling, EATF success and
tamper cases, missing signing inputs, dashboard states, and claim-safety
wording. Cassandra is not a trusted-list validator, not a relying-party
signature validator, and not a public alerting system. Cassandra is not a
supervisory tool and not a legal status oracle. Its contribution is
methodological: it shows how a public
governance surface can become a reproducible evidence stream, and how
the same discipline can inform emerging AI governance records without
collapsing cryptographic evidence into legal truth.

Keywords: evidence infrastructure; public-key infrastructure; trusted
lists; eIDAS; EATF; digital government; computational public
administration; reproducibility; AI governance.

## Claim-Safety Note

All observations in this preprint are limited to locally recorded
workflow telemetry and saved public-source artifacts: fetch metadata,
parser outcomes, normalized XML hashes, structural diff classes,
aggregate tables, evidence-bundle manifests, EATF/AEP receipt metadata,
dashboard cards, and synthetic fixture validation outputs. A Cassandra
run does not assert legal effect, does not determine whether any listed
entity has gained or lost status, does not validate source signatures
for relying-party purposes, does not supervise trusted lists, does not
certify compliance, and does not provide public alerting. The project is
an evidence-infrastructure case study, not a regulated trust service.

## 1. Introduction

Digital public administration increasingly depends on artifacts that are
both technical and institutional. Certificates, trust lists, validation
policies, audit regimes, public registers, and machine-readable
administrative documents do not merely describe government infrastructure
from the outside. They are part of how digital trust is governed. Yet the
research record around such artifacts is often thin: a public register
exists, a standard describes it, software consumes it, but the changing
public state itself is not always preserved as an evidence stream that a
later researcher, reviewer, or institution can replay.

Cassandra addresses this gap through a deliberately small case. It
observes the European public list-of-lists and the national trusted-list
documents referenced from locally saved LOTL snapshots. It records dated
collection attempts, classifies endpoint and parser outcomes, normalizes
comparable XML artifacts, emits configured structural diff classes,
bundles each substantive run with manifests and claims, and exposes a
caveated public dashboard index. The case is intentionally narrow. It
does not decide legal status, validate trusted-list signatures for
reliance, supervise any actor, or publish warnings. Its object is the
research workflow and the saved public artifacts under that workflow.

The central claim is captured in one sentence: Cassandra moves from
governance infrastructure to evidence infrastructure. PKI and eIDAS
trusted lists already provide governance infrastructure: certificates,
policies, supervisory lists, validation conventions, and trust-service
roles. Cassandra does not replace that infrastructure. It watches one
public surface of it and turns the observation process itself into
evidence infrastructure: dated manifests, hashes, diffs, receipts,
public cards, and explicit claim boundaries.

This matters beyond trusted lists. The EU AI Act creates adjacent
evidence problems around logging, transparency, technical documentation,
post-market monitoring, and lifecycle records. The AI governance problem
is not only whether an AI system is safe or lawful; it is also whether
claims about the system, the review, the data, the decision boundary, and
the monitoring process can be bound to reproducible records. Cassandra is
not an AI monitor. It is a public-governance-artifact case that makes the
evidence-infrastructure problem small enough to inspect.

The paper makes four contributions. First, it gives a cautious method
for longitudinal structural observation of public trusted-list artifacts.
Second, it reports a working full-stack observatory with scheduled
GitHub Actions, Cloudflare dashboard output, aggregate tables, figures,
dashboard cards, and EATF/AEP evidence receipts. Third, it maps synthetic
fixtures to reviewer-facing claims so that software behavior is tested
without exposing provider or service names. Fourth, it positions
Cassandra inside a thesis program in which PKI is governance
infrastructure and EATF/MIRROR-style packages provide an adjacent
evidence layer for AI and public-administration records.

## 2. Background: Trusted Lists as Governance Artifacts

The European trust-services framework is a legal-technical system, not
only a family of cryptographic formats. Regulation (EU) No 910/2014
(eIDAS) establishes the EU framework for electronic identification and
trust services. Regulation (EU) 2024/1183 amends eIDAS through the
European Digital Identity Framework. Commission Implementing Decision
(EU) 2015/1505 specifies trusted-list formats. ETSI TS 119 612 defines
the trusted-list grammar; ETSI EN 319 401 describes general policy
requirements for trust service providers; ETSI EN 319 411-1 and EN 319
422 connect the trusted-list layer to certificate-issuing and timestamp
service governance. These sources explain why the observed XML is not
arbitrary markup. It is a public administrative artifact embedded in a
larger trust-services regime.

At the protocol layer, RFC 5280 anchors X.509 certificate and CRL
profiles, RFC 3161 anchors timestamp protocol vocabulary, and RFC 8785
is useful for thinking about deterministic JSON evidence representations
adjacent to Cassandra's EATF/AEP package design. Outside the EU
trust-list context, CA/Browser Forum baseline requirements and the PKI
Consortium show that PKI governance also exists as an ecosystem of
multi-stakeholder rules, assurance expectations, and operational
transition problems. NIST FIPS 203, 204, and 205 further show that even
core cryptographic primitives are moving under post-quantum transition
pressure. The evidence layer must therefore be able to record not only
stable states but also migrations, caveats, and changing assumptions.

The public-administration and infrastructure-studies literature helps
name what is otherwise easy to miss. Infrastructure is relational,
learned in practice, and often visible through maintenance and failure.
Classifications and standards organize institutional reality; they do
not merely label it. Turning-point theory helps frame why technological
deployment phases demand institutional reshaping, not just invention.
The useful lesson for Cassandra is modest: if public digital trust is
governed through structured artifacts, then those artifacts and their
changes deserve reproducible evidence records.

This background also defines the boundary. Citing eIDAS, ETSI, RFCs,
NIST, CA/Browser Forum, or PKIC does not imply that Cassandra is
endorsed by those bodies, implements their standards as a relying-party
validator, or determines legal status. The sources establish the
environment and the vocabulary. Cassandra contributes a research method
for observing a public surface of that environment.

## 3. Related Work and Positioning

Cassandra intersects five fields.

First, PKI and cryptographic governance explain the substrate. PKI is
often introduced through keys and algorithms, but it operates through
certificate policies, revocation mechanisms, audits, root distribution,
software defaults, identity-proofing conventions, and institutional
delegation. That is governance work with cryptographic parts.[^pki]
Cassandra uses this point to avoid treating trusted lists as mere input
files. They are public records of a governance system.

Second, eIDAS and ETSI trust-service sources explain the legal-technical
grammar. Trusted lists have prescribed roles and formats. This makes
them attractive for structural observation, but it also makes careless
claims dangerous. A structural diff is not a legal event; an endpoint
failure is not a supervisory conclusion; an XML signature-shaped element
is not a signature-validation result. Cassandra's claim boundary is
therefore part of the method, not a disclaimer pasted on at the end.

Third, digital-government and public-administration scholarship explain
why public machine-readable artifacts matter institutionally. Work on
e-Estonia, public-sector innovation, public value, trust in digital
government, and AI in government all points toward the same practical
problem: administrative capacity is increasingly expressed through
digital artifacts that need to be maintained, interpreted, audited, and
remembered.

Fourth, infrastructure studies and classification studies provide the
conceptual bridge. Star and Ruhleder's infrastructure lens, Bowker and
Star's work on classification, and related knowledge-infrastructure
work all resist the fantasy that technical records are neutral pipes.
They are maintained systems with categories, access conditions, and
failure modes. Cassandra's contribution is intentionally operational:
it makes a specialized governance surface inspectable through manifests,
hashes, diffs, dashboard cards, and receipts.[^manifest]

Fifth, computational social science and digital research methods supply
the cautionary frame. Repeated observation of public artifacts can
produce useful evidence, but measurement validity, corpus boundaries,
reproducibility, aggregation choices, and public interpretation risks
must be explicit. Cassandra's synthetic fixtures, aggregate-only prose,
claim-safety checks, and abstention rules are therefore methodological
features. The highest compliment for an evidence pipeline may be that it
becomes boring in a reproducible way.[^boring]

## 4. System Overview

Cassandra is implemented as a research-only workflow around dated runs.
Each run begins from a saved copy of the public European list-of-lists.
The workflow extracts trusted-list pointer URLs from that saved LOTL
copy, fetches the referenced public artifacts, records per-endpoint
metadata, normalizes XML-like inputs where possible, records non-XML and
parser outcomes, compares normalized records against a configured
baseline, emits structural diff classes, builds aggregate result tables
and figures, creates evidence bundles, signs or packages the run through
the EATF/AEP lane when signing inputs are available, and exposes a
public dashboard index.

The core files and steps are:

- `fetch.py`: collection and LOTL pointer extraction with endpoint error
  metadata.
- `parse.py`: deterministic XML normalization and structural extraction.
- `diff.py`: configured structural diff classes over normalized records.
- `run_daily.py`: dated orchestration with overwrite guards.
- `create_bundle.py`: MIRROR-style evidence-bundle creation.
- `scripts/eatf_package_snapshot.py`: EATF/AEP packaging integration.
- `scripts/build_observatory_index.py`: public index and dashboard-card
  generation.

The public observatory is deployed at
`https://cassandra-observatory.pages.dev/`. Its machine-readable index is
available at `https://cassandra-observatory.pages.dev/data/index.json`.
As of the 2026-05-27 build, the public index reports four runs, latest
date `2026-05-27`, four EATF-verified receipts, and five dashboard cards.
The cards cover the latest run, EATF receipt boundary, aggregate diff
classes, claim boundary, and dashboard caveat. Each card repeats that
the data is structural-observation telemetry only, not trusted-list
validation, signature validation, legal-status determination,
supervision, compliance judgment, relying-party processing, public
alerting, or publication approval.

The workflow's most important design decision is abstention. Cassandra
keeps endpoint failures, non-XML artifacts, parser errors, and zero-diff
days inside the record. It does not clean them away to tell a simpler
story. A failed fetch is collection telemetry. A non-XML pointer is
corpus-shape telemetry. A parser error is a local parser event. A zero
diff means no configured structural diff was emitted by this
parser/baseline pair. None of these observations determines legal status.

## 5. Evidence Package Design

Each substantive run can be wrapped as an evidence package. The package
contains a summary artifact, manifest, claims file, notes, source copies
or source references, hashes, and verification output. This is a
MIRROR-style pattern: claims are made explicit, source links are
recorded, and local verification is possible without asking the reader
to trust a prose paragraph.

EATF/AEP adds package-level attestation semantics. For indexed `ok`
runs, the EATF receipt verifies the corresponding package envelope,
payload bytes, and declared hashes. It does not validate the underlying
trusted-list source signatures, does not determine legal effect, and
does not confer supervisory meaning. The distinction is crucial:
evidence integrity is not legal truth. A package receipt can say that
the evidence package is internally consistent under the declared
verification process. It cannot say that a trust service is lawful, that
a provider's status changed, or that a public authority has taken a
legally significant act.

The 2026-05-27 public card records an EATF package path
`evidence/2026-05-27/cassandra-observation.aep`, package hash
`3ef7f33b391afac388ce4bcf9716ac7018508ed613933f4ee86a3008d42023f6`,
receipt path `evidence/2026-05-27/eatf-verification.json`, receipt hash
`1e971e12a46b0d8be72635671b45be0b2dc21a283c5f29f1257d3dde4d6407d0`,
and status `ok`. The interpretation attached to that card is deliberately
narrow: `ok` verifies package bytes, envelope structure, and declared
hashes only.

This boundary is especially important for AI governance. If evidence
packages are to support AI lifecycle records, they must avoid the same
overreach. A signed package can preserve what was reviewed, logged, or
claimed. It does not prove that a model is safe, fair, lawful, or
accurate. Cassandra provides a concrete public-artifact case for this
discipline before the argument is transferred to more sensitive AI
contexts.

## 6. Dataset and Current Results

The current Cassandra evidence base contains four dated runs:
2026-05-20, 2026-05-21, 2026-05-22, and 2026-05-27. Each run starts from
43 LOTL-derived pointer attempts. The aggregate-results table records:

| Date | Pointer attempts | Fetched content files | Fetch errors | Normalized XML artifacts | Parser errors | Diff count | Provider count total | Service count total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-05-20 | 43 | 41 | 2 | 31 | 1 | 0 | 393 | 4743 |
| 2026-05-21 | 43 | 42 | 1 | 31 | 1 | 0 | 393 | 4743 |
| 2026-05-22 | 43 | 42 | 1 | 31 | 1 | 26 | 393 | 4753 |
| 2026-05-27 | 43 | 42 | 1 | 31 | 1 | 40 | 393 | 4847 |

Across the four runs, Cassandra records 66 aggregate structural diff
entries under the configured method. The dashboard card reports the
class totals:

- `normalized_hash_changed`: 7.
- `summary_field_changed`: 28.
- `service_inventory_changed`: 5.
- `provider_service_detail_changed`: 26.
- `listed_document_added`, `listed_document_removed`, and
  `provider_inventory_changed`: 0.

These are structural-observation classes, not legal-effect classes.
Provider and service totals are aggregate parser outputs over the saved
local corpus. The paper intentionally does not name providers, services,
schemes, or authorities in narrative prose. Hashed provider/service
handles support local comparison while reducing the temptation to turn a
research draft into a provider-specific status feed.

The results show that the workflow can preserve multiple kinds of
evidence at once: collection conditions, parser boundaries, comparable
records, structural changes, package hashes, EATF receipt status, public
dashboard summaries, and caveats. The result is not a claim that the
trusted-list ecosystem was stable or unstable. It is a claim that
Cassandra can produce reproducible structural-observation telemetry over
saved public artifacts and preserve enough context for later review.

## 7. Fixture-Backed Behavior

Real public observations are not enough to make the case publishable.
The paper also needs controlled behavior tests. Cassandra therefore
maintains a fixture-to-claim map that links synthetic test classes to
paper claims, reviewer questions, evidence artifacts, and explicit
non-claims.

The current fixture set covers:

- Stable no-change behavior: identical comparable records emit no
  structural diff.
- Normalized hash changes: stable record counts with changed canonical
  bytes are surfaced.
- Provider inventory and service inventory movements: synthetic
  hashed handles support aggregate comparison without real names.
- Provider-service detail changes: detail movement can be separated from
  whole-provider or whole-service movements.
- Fetch failures: timeout, HTTP-error, redirect, and unreachable-pointer
  telemetry are preserved.
- Non-XML handling: PDF, HTML, TXT, and non-parseable inputs become skips
  or parser events rather than fatal workflow failures.
- EATF success: a synthetic package can produce an `ok` receipt.
- EATF tamper: altered synthetic package bytes fail verification.
- Missing signing input: absent signing material is recorded explicitly
  as `skipped_missing_signing_inputs`.
- Dashboard multistate: public-index consumers can represent `ok`,
  `verify_failed`, and skipped states without turning them into alerts.
- Claim safety: configured overclaiming phrases are detected in
  controlled wording samples.

The fixture boundary is explicit: fixtures prove expected software
behavior on synthetic inputs. They are not empirical evidence about real
trusted-list content, source signatures, legal status, supervision,
compliance, public alerts, or publication approval. Their role is to
answer reviewer questions about the method: does the system fail closed
under tampering? Does it preserve failure states? Does it avoid silent
success when signing inputs are missing? Does it catch common wording
overclaims? These are software and method claims, not legal claims.

## 8. Discussion: From PKI Governance to AI Evidence

Cassandra's strongest thesis value is not that trusted lists are an
especially fashionable dataset. It is that trusted lists sit at a rare
intersection: public authority, structured technical artifacts,
cryptographic governance, institutional trust, and machine-readable
state. This makes them a useful case for observing how governance
infrastructure can be transformed into evidence infrastructure.

The phrase "PKI as governance infrastructure" matters because it stops
the analysis from shrinking PKI into algorithms. PKI includes keys and
signatures, but it also includes policies, identity checks, root stores,
certificate profiles, revocation conventions, timestamps, audit
frameworks, trust lists, and relying-party software. Cassandra watches a
public administrative surface of that infrastructure. The watched surface
is not the whole governance system, but it is enough to demonstrate the
evidence move.

The AI governance connection is vertical and adjacent. The AI Act does
not ask Cassandra to monitor AI systems. Instead, it makes visible a
similar institutional problem: records about systems, reviews, logs,
risks, datasets, human oversight, transparency, and post-market
monitoring need to be reproducible enough to support accountability.
EATF/AEP and MIRROR-style packages offer one grammar for such records:
claims, manifests, hashes, receipts, caveats, source references, and
local verification. Cassandra supplies a public, non-sensitive case where
that grammar can be tested against real public artifacts and synthetic
failure modes.

This is also why the dashboard matters. The dashboard is not a marketing
surface. It is a method surface. It exposes what the evidence stream
contains and repeats what it refuses to claim. The public cards make the
claim boundary visible at the point of consumption: run counts, receipt
status, aggregate diff classes, and caveats travel together. That design
choice is small, but it is a discipline AI governance systems will need:
evidence must be packaged with its limits, not separated from them.

## 9. Limitations

The limitations are not incidental. They define the research object.

First, Cassandra observes saved public artifacts under one workflow. It
does not establish endpoint completeness, current public availability,
or authoritative state beyond the local evidence collected at a given
time.

Second, the parser is not a trusted-list relying-party implementation.
It records structural fields, signature-shaped elements, hashes, and
parser outcomes. It does not perform source-signature validation,
certificate-path validation, OCSP/CRL checks, or legal interpretation.

Third, the diff classes are descriptive buckets. A normalized-hash
change, summary-field change, service-inventory movement, or
provider-service-detail movement is a local structural observation. It
is not a status change, compliance finding, risk score, or supervisory
signal.

Fourth, the empirical series is still short. Four dated runs are enough
to demonstrate a full evidence loop, public dashboard, EATF receipts,
and fixture-backed behavior. They are not enough to estimate long-term
churn, seasonal patterns, national differences, authority behavior, or
trust-service ecosystem stability.

Fifth, the public prose is aggregate-only by design. Named examples may
be useful in a later paper version, but only after operator review,
source-path checks, bundle context, exact wording review, and a decision
that the example improves explanation without turning the paper into a
status feed.

Sixth, EATF/AEP receipts verify package integrity under the declared
process. They do not validate underlying legal truth. This limitation is
also the point. Evidence infrastructure becomes credible when it knows
where evidence stops.

## 10. Conclusion

Cassandra shows that a public governance artifact can be turned into a
bounded evidence stream without pretending to become a regulator,
validator, or oracle. The system collects public LOTL-derived artifacts,
preserves endpoint and parser telemetry, normalizes comparable XML,
emits structural diff classes, packages run evidence, attaches EATF/AEP
receipts, exposes public dashboard cards, and validates its own claim
boundaries through synthetic fixtures.

The case supports a broader thesis: PKI did not merely secure digital
transactions; it institutionalized a way of governing digital trust
through certificates, lists, policies, audits, revocation, timestamps,
and validation conventions. AI governance now needs an adjacent evidence
infrastructure for systems, decisions, reviews, logs, public artifacts,
and lifecycle records. Cassandra is the public-governance-artifact case.
Its lesson is deliberately restrained: evidence integrity can be made
visible and reproducible, but it must not be confused with legal truth.

## Artifact Availability

Repository: `https://github.com/tyche-institute/cassandra`
Dashboard: `https://cassandra-observatory.pages.dev/`  
Public index: `https://cassandra-observatory.pages.dev/data/index.json`

Key local artifacts for this preprint:

- `paper/preprint/cassandra-preprint-v0.1.md`
- `paper/reference-seed-bibliography.md`
- `paper/claims-and-evidence-table.md`
- `notes/cassandra-checked-reference-ledger-2026-05-27.md`
- `notes/cassandra-checked-reference-url-validation-output.json`
- `notes/fixture-to-claim-map.md`
- `notes/fixture-matrix.md`
- `notes/case-study-maturity-matrix.md`
- `notes/publication-status-discipline.md`
- `observatory/public/data/index.json`
- `observatory/public/data/cards/index.json`
- `evidence/2026-05-27/eatf-verification.json`

## References

Bannister, F., and Connolly, R. (2011). Trust and transformational
government: A proposed framework for research. Government Information
Quarterly. DOI: `10.1016/j.giq.2010.06.010`.

Bowker, G. C., and Star, S. L. (1999). Sorting Things Out:
Classification and Its Consequences. MIT Press. DOI:
`10.7551/mitpress/6352.001.0001`.

CA/Browser Forum. Baseline Requirements for the Issuance and Management
of Publicly-Trusted TLS Server Certificates, version 2.2.7, 19 May 2026.
`https://cabforum.org/working-groups/server/baseline-requirements/requirements/`.

Commission Implementing Decision (EU) 2015/1505 laying down technical
specifications and formats relating to trusted lists.
`https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32015D1505`.

Cooper, D., Santesson, S., Farrell, S., Boeyen, S., Housley, R., and
Polk, W. (2008). RFC 5280: Internet X.509 Public Key Infrastructure
Certificate and Certificate Revocation List (CRL) Profile.
`https://www.rfc-editor.org/rfc/rfc5280`.

Drechsler, W. (2018). Pathfinder: e-Estonia as the beta-version. JeDEM.
DOI: `10.29379/jedem.v10i2.513`.

ETSI EN 319 401 V3.1.1 (2024-06). Electronic Signatures and
Infrastructures (ESI); General Policy Requirements for Trust Service
Providers.
`https://www.etsi.org/deliver/etsi_en/319400_319499/319401/03.01.01_60/en_319401v030101p.pdf`.

ETSI EN 319 411-1 V1.5.1 (2025-04). Electronic Signatures and
Infrastructures (ESI); Policy and security requirements for Trust
Service Providers issuing certificates; Part 1: General requirements.
`https://www.etsi.org/deliver/etsi_en/319400_319499/31941101/01.05.01_60/en_31941101v010501p.pdf`.

ETSI EN 319 422 V1.1.1 (2016-03). Electronic Signatures and
Infrastructures (ESI); Time-stamping protocol and time-stamp token
profiles.
`https://www.etsi.org/deliver/etsi_en/319400_319499/319422/01.01.01_60/en_319422v010101p.pdf`.

ETSI TS 119 612 V2.4.1 (2025-08). Electronic Signatures and
Infrastructures (ESI); Trusted Lists.
`https://www.etsi.org/deliver/etsi_ts/119600_119699/119612/02.04.01_60/ts_119612v020401p.pdf`.

European Commission. EU Trusted Lists / List of the Lists documentation.
`https://digital-strategy.ec.europa.eu/en/policies/eu-trusted-lists`.

European Parliament and Council. Regulation (EU) No 910/2014 on
electronic identification and trust services for electronic transactions
in the internal market. `https://eur-lex.europa.eu/eli/reg/2014/910/oj`.

European Parliament and Council. Regulation (EU) 2024/1183 establishing
the European Digital Identity Framework.
`https://eur-lex.europa.eu/eli/reg/2024/1183/oj`.

European Parliament and Council. Regulation (EU) 2024/1689 laying down
harmonised rules on artificial intelligence.
`https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689`.

Lazer, D., Pentland, A., Adamic, L., Aral, S., Barabasi, A.-L.,
Brewer, D., Christakis, N., Contractor, N., Fowler, J., Gutmann, M.,
Jebara, T., King, G., Macy, M., Roy, D., and Van Alstyne, M. (2009).
Computational Social Science. Science. DOI: `10.1126/science.1167742`.

NIST. FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism
Standard. `https://csrc.nist.gov/pubs/fips/203/final`.

NIST. FIPS 204: Module-Lattice-Based Digital Signature Standard.
`https://csrc.nist.gov/pubs/fips/204/final`.

NIST. FIPS 205: Stateless Hash-Based Digital Signature Standard.
`https://csrc.nist.gov/pubs/fips/205/final`.

Perez, C. (2002). Technological Revolutions and Financial Capital:
The Dynamics of Bubbles and Golden Ages. Edward Elgar.
`https://books.google.com/books/about/Technological_Revolutions_and_Financial.html?id=FW-aAAAAIAAJ`.

PKI Consortium. `https://pkic.org/`.

Salganik, M. J. (2017). Bit by Bit: Social Research in the Digital Age.
Princeton University Press.

Star, S. L., and Ruhleder, K. (1996). Steps Toward an Ecology of
Infrastructure: Design and Access for Large Information Spaces.
Information Systems Research. DOI: `10.1287/isre.7.1.111`.

Troncoso, C., and others. RFC 8785: JSON Canonicalization Scheme.
`https://www.rfc-editor.org/rfc/rfc8785`.

W3C. Verifiable Credentials Data Model v2.0.
`https://www.w3.org/TR/vc-data-model-2.0/`.

Adams, C., Cain, P., Pinkas, D., and Zuccherato, R. (2001). RFC 3161:
Internet X.509 Public Key Infrastructure Time-Stamp Protocol.
`https://www.rfc-editor.org/rfc/rfc3161`.

[^pki]: The common shorthand "PKI equals cryptography" is useful in a
    classroom and dangerous in governance. The keys do not audit
    themselves, revoke themselves, or explain themselves to a relying
    party at 03:00.

[^manifest]: Grand theory earns its keep here only if it can survive the
    manifest. Cassandra's theory chapter and its hash table should be on
    speaking terms.

[^boring]: "Boring" is not a complaint in evidence infrastructure. A
    reproducible system should be allowed at least one unglamorous virtue.
