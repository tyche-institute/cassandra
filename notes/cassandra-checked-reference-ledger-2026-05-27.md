# Cassandra checked reference ledger

Date checked: 2026-05-27
Status: release-facing reference-control ledger for Cassandra paper/thesis prose
Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

## Reading rule

This ledger is not a bibliography dump. Each row records a real source,
how it was checked, what claim role it can carry, and how it connects
the Cassandra case horizontally across neighboring fields and vertically
down to legal, standards, protocol, implementation, artifact, and
limitation layers.

Do not cite a source from this ledger as an endorsement of Cassandra.
Primary legal and standards sources explain the environment Cassandra
observes. Scholarly sources provide concepts and methodological caution.
Local artifacts prove only the local evidence workflow.

## Verification notes

- EUR-Lex, European Commission, RFC Editor, CA/Browser Forum, PKIC,
  NIST CSRC, W3C, ETSI delivery URLs, DOI/publisher pages, PubMed, and
  Google Books or publisher records were checked on 2026-05-27.
- Shell reachability was tested for the main official URLs. ETSI PDFs
  returned HTTP 200 when requested with a browser user agent.
- Some publisher pages, including MIT Press and INFORMS, may return HTTP
  403 to shell requests while remaining identifiable through publisher
  pages, DOI metadata, and web search. Treat those as checked publisher
  anchors, not machine-fetched local evidence.
- Anything not in this ledger remains a planning reference until
  Mnemosyne records title, authority, URL/DOI/identifier, date checked,
  source status, and claim role.

## Vertical reference stack

| Layer | Checked source | Real anchor | Claim role in Cassandra | Context connection |
|---|---|---|---|---|
| Legal base | Regulation (EU) No 910/2014, eIDAS | EUR-Lex `https://eur-lex.europa.eu/eli/reg/2014/910/oj` | Establishes the EU electronic identification and trust-services regime that makes trusted lists legally meaningful public artifacts. | Use for the governance-infrastructure layer; never as proof Cassandra determines legal status. |
| Legal update | Regulation (EU) 2024/1183, European Digital Identity Framework / eIDAS amendment | EUR-Lex `https://eur-lex.europa.eu/eli/reg/2024/1183/oj` | Shows that the trust-services and identity framework is still evolving, so longitudinal evidence practices are not archival nostalgia. | Connects Cassandra to EUDI Wallet and renewed digital identity governance. |
| AI governance neighbor | Regulation (EU) 2024/1689, AI Act | EUR-Lex `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689` | Provides the adjacent evidence problem: AI systems need documentation, logging, monitoring, and auditable records. | Use analogically; Cassandra observes public governance artifacts, not AI model behavior. |
| Trusted-list format law | Commission Implementing Decision (EU) 2015/1505 | EUR-Lex `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32015D1505` | Anchors trusted-list technical specifications and formats as official public-administration outputs. | Use to explain why the observed files have institutional form, not just XML shape. |
| Operational public source | European Commission, list of qualified trust service providers in the EU | EC Digital Strategy `https://digital-strategy.ec.europa.eu/en/policies/eu-trusted-lists` | Documents the public obligation and access point for trusted lists. | Connects source collection to official public infrastructure, not search-engine discovery. |
| Trusted-list standard | ETSI TS 119 612 V2.4.1 (2025-08), Electronic Signatures and Trust Infrastructures; Trusted Lists | ETSI deliver `https://www.etsi.org/deliver/etsi_ts/119600_119699/119612/02.04.01_60/ts_119612v020401p.pdf` | Defines the trusted-list standard context that Cassandra treats as source grammar. | Use for artifact semantics; do not claim Cassandra implements the standard as a validator. |
| Trust-service policy | ETSI EN 319 401 V3.1.1 (2024-06), General Policy Requirements for Trust Service Providers | ETSI deliver `https://www.etsi.org/deliver/etsi_en/319400_319499/319401/03.01.01_60/en_319401v030101p.pdf` | Shows the policy layer around qualified/non-qualified trust services. | Connects governance to institutional duties and audits. |
| CA policy/security | ETSI EN 319 411-1 V1.5.1 (2025-04), certificate-issuing TSP requirements | ETSI deliver `https://www.etsi.org/deliver/etsi_en/319400_319499/31941101/01.05.01_60/en_31941101v010501p.pdf` | Provides the CA/certificate-policy layer below trusted-list publication. | Use to show vertical depth from list publication to certificate-lifecycle governance. |
| Timestamp profile | ETSI EN 319 422 V1.1.1 (2016-03), time-stamping protocol and time-stamp token profiles | ETSI deliver `https://www.etsi.org/deliver/etsi_en/319400_319499/319422/01.01.01_60/en_319422v010101p.pdf` | Connects evidence-time claims to RFC 3161-style timestamping. | Useful for EATF/AEP receipt discussion; no claim of qualified timestamp service. |
| PKI protocol | RFC 5280, Internet X.509 PKI Certificate and CRL Profile | RFC Editor `https://www.rfc-editor.org/rfc/rfc5280` | Anchors certificate and CRL profile language. | Shows Cassandra is near PKI infrastructure but does not do path validation. |
| Timestamp protocol | RFC 3161, Time-Stamp Protocol | RFC Editor `https://www.rfc-editor.org/rfc/rfc3161` | Anchors timestamp-token vocabulary. | Use as protocol comparator for evidence packages and receipt time semantics. |
| Canonical JSON | RFC 8785, JSON Canonicalization Scheme | RFC Editor `https://www.rfc-editor.org/rfc/rfc8785` | Explains why deterministic representation matters for hashing/signing JSON evidence. | Relevant to AEP/MIRROR package design, not to Cassandra XML normalization directly. |
| Browser-trusted PKI governance | CA/Browser Forum Baseline Requirements for TLS Server Certificates, v2.2.7, 19-May-2026 | CA/B Forum `https://cabforum.org/working-groups/server/baseline-requirements/requirements/` | Shows non-state multi-stakeholder PKI rule-making and audit-like governance. | Horizontal comparison: PKI governance exists outside eIDAS as well. |
| PKI ecosystem body | PKI Consortium / PKIC | PKIC `https://pkic.org/` | Contemporary PKI community, including maturity and post-quantum transition discussions. | Use as ecosystem context only; no endorsement or standards authority claim. |
| Post-quantum transition | NIST FIPS 203, ML-KEM; FIPS 204, ML-DSA; FIPS 205, SLH-DSA | NIST CSRC `https://csrc.nist.gov/pubs/fips/203/final`, `https://csrc.nist.gov/pubs/fips/204/final`, `https://csrc.nist.gov/pubs/fips/205/final` | Shows that cryptographic governance is not static; the evidence layer must survive algorithm transitions. | Vertical depth: governance infrastructure must track protocols, algorithms, and migration evidence. |
| Credential evidence comparator | W3C Verifiable Credentials Data Model v2.0 | W3C `https://www.w3.org/TR/vc-data-model-2.0/` | Comparator for claims, issuers, holders, and verification models. | Useful for AI/evidence infrastructure comparison; do not collapse VC, eIDAS, and EATF into one regime. |
| Infrastructure studies | Star and Ruhleder, "Steps Toward an Ecology of Infrastructure" (1996) | DOI `10.1287/isre.7.1.111` | Gives the "infrastructure in practice" lens. | Explains why maintenance, access, and use conditions matter as much as technical form. |
| Classification studies | Bowker and Star, Sorting Things Out (1999) | MIT Press DOI `10.7551/mitpress/6352.001.0001` | Explains how classifications and standards become social infrastructure. | Use for trusted-list categories, provider/service classes, and the politics of labels. |
| Turning-point theory | Carlota Perez, Technological Revolutions and Financial Capital (Edward Elgar, 2002) | Google Books `https://books.google.com/books/about/Technological_Revolutions_and_Financial.html?id=FW-aAAAAIAAJ` | Provides the macro frame: deployment periods need institutional reshaping. | Use cautiously; Cassandra is a small case, not evidence for the whole Perez model. |
| Digital-state case | Wolfgang Drechsler, "Pathfinder: e-Estonia as the beta-version" (JeDEM, 2018) | DOI `10.29379/jedem.v10i2.513` | Supports the public-administration/digital-state context. | Relevant to Estonian e-state and PKI-governance thesis spine. |
| Trust in e-government | Bannister and Connolly, "Trust and transformational government" (Government Information Quarterly, 2011) | DOI `10.1016/j.giq.2010.06.010` | Supplies a trust/public-government frame that is not reducible to cryptography. | Use to bridge public trust and technical trust without claiming they are the same. |
| Computational method | Lazer et al., "Computational Social Science" (Science, 2009) | DOI `10.1126/science.1167742` | Supports computational observation as a research mode with scale and interpretation risks. | Use for method humility: public-document telemetry still needs validity discipline. |
| Digital social research | Salganik, Bit by Bit: Social Research in the Digital Age (Princeton University Press, 2017) | Princeton/Oxford review anchor `https://academic.oup.com/jrsssa/article/181/3/917/7072048` | Supports observation, ethics, and research design in digital environments. | Helps justify why Cassandra keeps source boundaries and abstention rules explicit. |

## Horizontal field coverage

The ledger deliberately crosses:

- EU law and official administrative sources: eIDAS, eIDAS2, AI Act,
  Implementing Decision 2015/1505, EC trusted-list page.
- Trust-service standards: ETSI trusted lists, TSP policy, CA policy,
  timestamping, RFC PKIX and timestamping.
- PKI ecosystem governance: CA/B Forum, PKIC, NIST post-quantum
  standards.
- Evidence-format comparators: RFC 8785 and W3C VC Data Model.
- Institutional literature: public administration, digital state, trust,
  infrastructure studies, classification, and turning-point theory.
- Method discipline: computational social science and digital social
  research.

This breadth is useful only if each citation remains attached to its
job. A wide bibliography without claim roles is just fog with page
numbers.

## Footnote palette for the draft

Use footnotes sparingly. Each one should either clarify a boundary,
connect literatures, or make a skeptical distinction more readable.

- PKI governance footnote: PKI is often introduced through algorithms,
  but it operates through policies, lists, audits, software distribution,
  revocation, and institutional delegation. That is governance work.
- Trusted-list boundary footnote: eIDAS and ETSI explain why the XML
  matters; they do not turn Cassandra into a legal-status oracle.
- Infrastructure footnote: Perez supplies the large turning-point
  vocabulary; Star/Ruhleder and Bowker/Star keep it grounded where
  infrastructure actually lives: maintenance, categories, access, and
  failures.
- Method footnote: the highest compliment for an evidence pipeline may
  be that it becomes boring in a reproducible way.

## Release checklist

Before the Cassandra paper or thesis chapter leaves the workspace:

1. Convert this ledger into formal bibliography entries in the venue
   style.
2. Replace planning references in `paper/related-work-card.md` with
   checked rows or remove them.
3. Label Tyche works as published, Zenodo/preprint, submitted,
   internal, prototype, or synthetic.
4. Keep prototype cases in the maturity matrix unless publicness,
   permission, and artifact status are verified.
5. Run paper claim-safety and aggregate-only validators after any
   related-work edit.
