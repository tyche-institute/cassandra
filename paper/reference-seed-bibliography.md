# Cassandra reference seed bibliography

Date: 2026-05-27
Status: curated seed bibliography for reviewer-facing drafting; not final Bluebook/APA/CSL output
Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

## Purpose and use

This file turns the broad related-work clusters into a citable seed list that can be promoted into `paper/draft.md` after bibliographic verification. It separates primary legal/standards sources from scholarly framing and Tyche/internal works. The entries are deliberately claim-bounded: citing a regulation, standard, RFC, report, or scholar does not make Cassandra a trusted-list validator, a conformity assessor, a supervisory body, a public alerting system, a legal opinion, or publication approval.

## Citation-status rules

- Official law, standards, RFC, NIST, OECD, and public documentation entries may be used as context after checking the exact version and access date.
- Scholarly entries below are anchors for the argument; verify exact title, edition, venue, year, DOI/URL, and page range before final submission.
- Tyche/EATF/MIRROR/adjacent-project entries must follow `notes/publication-status-discipline.md` and the thesis atlas: public, submitted, internal, prototype, and synthetic statuses must not be collapsed.
- Synthetic fixture artifacts may support software-behavior claims only. They must not be cited as empirical evidence about real trusted-list content, legal status, source-signature validity, supervisory action, provider/service status, or compliance.

## A. Primary legal and standards sources

| Short key | Draft citation seed | Status | Use in Cassandra | URL or lookup handle |
|---|---|---|---|---|
| eIDAS-2014 | Regulation (EU) No 910/2014 of the European Parliament and of the Council of 23 July 2014 on electronic identification and trust services for electronic transactions in the internal market. | Official EU law; verify consolidated/current text before final submission. | Legal-technical context for trust services and trusted-list ecosystem; not a claim that Cassandra determines legal effect. | https://eur-lex.europa.eu/eli/reg/2014/910/oj |
| eIDAS2-2024 | Regulation (EU) 2024/1183 amending Regulation (EU) No 910/2014 as regards establishing the European Digital Identity Framework. | Official EU law; verify final/current text. | Context for evolving European digital-identity and trust-service governance. | https://eur-lex.europa.eu/eli/reg/2024/1183/oj |
| EU-AI-Act-2024 | Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence. | Official EU law; verify final/current text. | Analogical evidence-infrastructure context for logging, documentation, transparency, post-market, and lifecycle records. | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| Trusted-list-format-2015 | Commission Implementing Decision (EU) 2015/1505 laying down technical specifications and formats relating to trusted lists. | Official EU implementing decision. | Direct trusted-list format context; not proof that Cassandra validates list semantics. | https://eur-lex.europa.eu/eli/dec_impl/2015/1505/oj |
| ETSI-TS-119-612 | ETSI TS 119 612, Electronic Signatures and Infrastructures (ESI); Trusted Lists. | Standards context; exact version to verify. | Explains trusted-list grammar and fields used by the public artifacts. | ETSI standards portal lookup: TS 119 612 |
| ETSI-EN-319-401 | ETSI EN 319 401, General Policy Requirements for Trust Service Providers. | Standards context; exact version to verify. | Trust-service governance and assurance context. | ETSI standards portal lookup: EN 319 401 |
| ETSI-EN-319-411-412 | ETSI EN 319 411 and EN 319 412 series on certificate policy and certificate profiles. | Standards context; exact parts/versions to verify. | PKI/trust-service assurance context; not relying-party validation. | ETSI standards portal lookup: EN 319 411; EN 319 412 |
| ETSI-EN-319-102 | ETSI EN 319 102 series, Procedures for Creation and Validation of AdES Digital Signatures. | Standards context; exact part/version to verify. | Boundary contrast: Cassandra records signature shape but does not perform relying-party validation. | ETSI standards portal lookup: EN 319 102 |
| ETSI-EN-319-422 | ETSI EN 319 422, Time-stamping protocol and timestamping authority policy context. | Standards context; exact version to verify. | Timestamping/evidence context alongside RFC 3161. | ETSI standards portal lookup: EN 319 422 |
| RFC-5280 | Cooper et al., RFC 5280: Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List Profile. | IETF RFC. | PKI substrate context; Cassandra does not build certificate paths. | https://www.rfc-editor.org/rfc/rfc5280 |
| RFC-3161 | Adams et al., RFC 3161: Internet X.509 Public Key Infrastructure Time-Stamp Protocol. | IETF RFC. | Timestamping/evidence context. | https://www.rfc-editor.org/rfc/rfc3161 |
| RFC-6960 | Santesson et al., RFC 6960: X.509 Internet Public Key Infrastructure Online Certificate Status Protocol - OCSP. | IETF RFC. | Revocation/status-protocol context; not used by Cassandra as a validator. | https://www.rfc-editor.org/rfc/rfc6960 |
| RFC-6962 | Laurie, Langley, and Kasper, RFC 6962: Certificate Transparency. | IETF experimental RFC. | Public-log and transparency context; distinguish from Cassandra's saved-artifact observatory. | https://www.rfc-editor.org/rfc/rfc6962 |
| NIST-FIPS-140-3 | NIST FIPS 140-3, Security Requirements for Cryptographic Modules. | NIST FIPS; verify current publication page. | Cryptographic assurance ecosystem context. | https://csrc.nist.gov/pubs/fips/140-3/final |
| NIST-FIPS-186-5 | NIST FIPS 186-5, Digital Signature Standard. | NIST FIPS; verify current publication page. | Signature-standard context; Cassandra does not validate signatures for reliance. | https://csrc.nist.gov/pubs/fips/186-5/final |
| NIST-FIPS-203 | NIST FIPS 203, Module-Lattice-Based Key-Encapsulation Mechanism Standard. | NIST FIPS; verify current publication page. | PQC governance-transition context. | https://csrc.nist.gov/pubs/fips/203/final |
| NIST-FIPS-204 | NIST FIPS 204, Module-Lattice-Based Digital Signature Standard. | NIST FIPS; verify current publication page. | PQC signature-transition context. | https://csrc.nist.gov/pubs/fips/204/final |
| NIST-FIPS-205 | NIST FIPS 205, Stateless Hash-Based Digital Signature Standard. | NIST FIPS; verify current publication page. | PQC signature-transition context. | https://csrc.nist.gov/pubs/fips/205/final |
| CABF-BRs | CA/Browser Forum Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates. | Ecosystem governance document; version to verify. | PKI governance and assurance coordination context; no endorsement claim. | https://cabforum.org/working-groups/server/baseline-requirements/ |
| PKIC | PKI Consortium publications and ecosystem resources. | Ecosystem context; use as contemporary context, not endorsement. | PKI governance and PQC ecosystem context. | https://pkic.org/ |

## B. Scholarly and public-administration anchors to verify

| Cluster | Author/anchor | Draft use | Verification needed |
|---|---|---|---|
| PKI governance | Ueli Maurer on PKI/trust models. | Shows PKI as institutional trust architecture, not only cryptography. | Exact paper/title/year/venue. |
| PKI risks | Carl Ellison and Bruce Schneier, "Ten Risks of PKI". | Explains why PKI governance and reliance semantics are fragile. | Exact proceedings/date/URL. |
| Digital state | Wolfgang Drechsler on e-Estonia and public administration. | Places machine-readable state artifacts in digital-state capacity. | Exact work(s), year, publisher. |
| Public-sector innovation | Rainer Kattel, Veiko Lember, Piret Tonurist. | Public-sector innovation and administrative capacity frame. | Exact work(s), coauthors, venue. |
| Public value/state capacity | Mariana Mazzucato, Kattel, Drechsler. | Public value and mission/state-capacity framing. | Exact work(s), edition. |
| Digital government trust | Frank Bannister and Regina Connolly. | Trust and transformational government framing. | Exact article(s), DOI. |
| AI and government | Helen Margetts and Cosmina Dorobantu. | Government/AI governance context. | Exact publication details. |
| Infrastructure studies | Susan Leigh Star and Karen Ruhleder. | Infrastructure becomes visible through use and breakdown. | Exact citation, DOI if available. |
| Classification/infrastructure | Geoffrey Bowker and Susan Leigh Star. | Classification and infrastructure as institutional evidence. | Book edition, publisher. |
| Knowledge infrastructures | Paul N. Edwards. | Data/infrastructure and reproducible knowledge frame. | Exact work(s). |
| Platform/infrastructure | Jean-Christophe Plantin and coauthors. | Platformization/infrastructuralization distinction. | Exact article details. |
| Infrastructure politics | Brian Larkin. | Infrastructure as political/aesthetic/technical object. | Exact article/book details. |
| Sociotechnical imaginaries | Sheila Jasanoff. | Governance imaginaries and sociotechnical order. | Exact edited volume/chapter. |
| Turning points | Carlota Perez. | Deployment turning points and institutional infrastructure. | Exact book/article edition. |
| Computational social science | David Lazer and coauthors. | Measurement validity and public-data caution. | Exact Science/Annual Review references. |
| Computational methods | Matthew Salganik. | Bit by Bit / reproducible social-data method. | Edition/URL. |
| Text as data | Grimmer, Roberts, and Stewart. | Measurement and interpretation discipline for computational evidence. | Exact book citation. |
| Digital trace data | Edelmann and coauthors; Bail. | Risks and validity of large-scale digital observation. | Exact publications. |

## C. Tyche and adjacent-project citation posture

| Work/case | Citation posture | Cassandra use |
|---|---|---|
| Cassandra | Public dashboard plus local repository artifacts; paper remains working draft until operator release. | Main empirical case. |
| EATF/AEP | Cite only public Zenodo/software/preprint artifacts with exact status; otherwise internal/prototype. | Package/receipt boundary and analogy for evidence infrastructure. |
| MIRROR | Cite as bundle/source-manifest pattern if public; otherwise internal method dependency. | Evidence-bundle discipline. |
| PKI Atlas | Explanatory/tutorial layer, not Cassandra empirical corpus. | Governance-infrastructure teaching context. |
| X-Road attestation | Use only with verified public facts. | Public-sector trust-infrastructure comparison. |
| Vesta and Icarus | Evidence-infrastructure cases; cite only if public/status verified. | Cross-case maturity matrix. |
| Janus, MATx, h2oatlas, eaudit, Aletheia/avatar.eatf.eu | Prototype/internal/permission-sensitive unless public facts are rechecked. | Maturity matrix only; avoid public claims until verified. |
| Breakable receipts | Verifier UX and failure-mode education. | Explain why tamper/failure fixtures matter. |
| Kolmogorov | Inventory unresolved. | Do not cite as established case. |

## D. Merge guidance for `paper/draft.md`

A final bibliography should not simply append every row. The paper needs a compact, verified reference list. Recommended merge order:

1. Cite eIDAS 910/2014, eIDAS2 2024/1183, Implementing Decision 2015/1505, ETSI TS 119 612, and RFC 5280/3161 in Background.
2. Cite Ellison/Schneier, Maurer, CA/B Forum, PKIC, and NIST FIPS sources in the PKI-as-governance paragraph.
3. Cite the AI Act only in the analogical AI-governance evidence-infrastructure section, not as proof that Cassandra monitors AI systems.
4. Use Star/Ruhleder, Bowker/Star, Edwards, Plantin, Larkin, Jasanoff, and Perez sparingly to support the governance-to-evidence framing.
5. Use Lazer/Salganik/Grimmer-Roberts-Stewart/Edelmann/Bail to justify measurement humility, reproducibility, aggregate-only prose, and fixture-backed method claims.
6. Keep Tyche project references status-labelled and separate from public official/scholarly references.

## Non-claims

This reference seed does not validate trusted lists, does not verify source signatures, does not determine provider or service status, does not perform legal review, does not supervise any actor, does not assert compliance, does not issue public alerts, does not imply endorsement by cited organizations, and does not approve publication. It is a drafting-control artifact.
