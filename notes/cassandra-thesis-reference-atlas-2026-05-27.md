# Cassandra thesis reference atlas

Date: 2026-05-27
Status: thesis and publication reference atlas for the Cassandra evidence-infrastructure case
Scope: Cassandra, EATF, MIRROR, Janus, Vesta, Icarus, MATx, h2oatlas, eaudit, Aletheia AI, PKI/eIDAS/ETSI/PKIC, and adjacent Tyche case material

## Core thesis sentence

Cassandra: from governance infrastructure to evidence infrastructure.

This case should sit vertically above and beside the submitted "PKI as governance infrastructure" paper. PKI is the governance substrate: certificates, trust lists, qualified trust services, supervisory lists, timestamping, certificates, policies, and validation conventions. Cassandra adds an evidence-infrastructure move: public governance artifacts can be observed over time, turned into bounded manifests, hashed, bundled, signed, displayed, and checked while preserving the distinction between evidence integrity and legal interpretation.

The phrase is not decorative. It is the chapter spine:

1. PKI as governance infrastructure: delegated trust, public authority, vendor/state coordination, legal effect, administrative capacity.
2. eIDAS and ETSI as the legal-technical grammar of that governance infrastructure.
3. Cassandra as a public observatory that turns the governance grammar into dated evidence objects.
4. EATF/AEP and MIRROR as the evidence packaging layer.
5. AI governance as the neighboring domain where the same evidence discipline becomes urgent.

## Citation status policy

Use each source according to its status. Do not make unpublished work look published.

| Status | How to cite | How not to cite |
|---|---|---|
| Peer-reviewed published article or official standard/regulation | normal formal citation | do not imply the standard endorses Cassandra |
| Zenodo or preprint deposit | cite as preprint, working paper, dataset, or software artifact with DOI | do not call it peer-reviewed |
| Submitted or under review manuscript | cite internally as "manuscript under review" or "submission packet"; disclose status when relevant | do not include in public bibliography as accepted/published |
| Internal project artifact | cite as "internal Tyche/Cassandra project artifact" with path/commit/date | do not cite as public evidence unless it is intentionally public |
| Prototype/demo/partner integration | cite as "prototype", "lab showcase", or "deployment attempt" only after checking public exposure and permission | do not use as proof of adoption |
| Synthetic case data | cite as synthetic fixture, test vector, or controlled demonstration | do not imply real user, student, patient, client, or regulator data |

## Submitted and Zenodo inventory from the vault

This inventory is intentionally conservative. Before any final public bibliography, re-check current status in the vault, journal portals, Zenodo, SSRN, IACR, and e-mail receipts.

| Item | Current local status | Stable reference anchor | Use in Cassandra/thesis |
|---|---|---|---|
| Cryptographic Attestation for AI Agent Governance under the EU AI Act: A Survey of Approaches and Standards | Zenodo concept DOI; v2.5 paper packet present; CSUR-related packet appears in vault | concept DOI `10.5281/zenodo.20185410`; v2.5 DOI `10.5281/zenodo.20357731`; older v2.3 DOI `10.5281/zenodo.20255280` | Literature base for AI attestation, EATF/AEP, standards mapping, and case taxonomy. |
| Operationalizing the EU AI Act through eIDAS Trust Services Primitives | Zenodo concept DOI; v1.1-preprint referenced; JIPITEC/CSI-style packets referenced in vault | concept DOI `10.5281/zenodo.20257971`; v1.1-preprint DOI `10.5281/zenodo.20357732`; earlier v1.0.1 DOI `10.5281/zenodo.20265919` | Direct bridge from eIDAS/ETSI primitives to AI Act evidence duties; cite as mapping preprint unless accepted. |
| On the Crossroads: Marketplace versus Distributed Trust in Agent Attestation Frameworks | Zenodo concept DOI; publication manuscript in vault | concept DOI `10.5281/zenodo.20257933`; v0.4.1 DOI `10.5281/zenodo.20265925`; later manuscript DOI `10.5281/zenodo.20357727` appears in vault | The distributed-trust argument that helps explain why Cassandra uses public evidence objects instead of a single marketplace or registry. |
| From Bayesian Knowledge Tracing to Verifiable Educational AI | Zenodo concept DOI; MATx/BKT case material; JLA and IEEE S&P Magazine packets appear in vault | concept DOI `10.5281/zenodo.20257996`; v0.3.1 DOI `10.5281/zenodo.20265926`; educational-AI artifacts DOI `10.5281/zenodo.20273730` | Use as AI decision-level contrast: MATx logs model events; Cassandra logs governance artifacts. |
| EATF / Agent Evidence Package artifacts | EATF Zenodo concept and artifact references appear in vault | EATF concept DOI `10.5281/zenodo.20273729`; educational artifact DOI `10.5281/zenodo.20273730` | Cite as technical evidence framework and test-vector source, not as regulated trust service. |
| BSEADE Paper A / public-documentation analysis | Zenodo working paper and SSRN abstract submitted 2026-05-21 | concept DOI `10.5281/zenodo.20329188`; version DOI `10.5281/zenodo.20329189`; SSRN abstract ID `6809759` | Use as public-documentation/compliance-adjacent case only if thematically needed. |
| PKI as Governance Infrastructure: Five Dimensions of Delegated Trust in the Estonian e-State | Halduskultuur submission #419 under review per vault notes | cite as "Sokolov, manuscript under review, Halduskultuur submission #419" unless accepted | This is the vertical paper above Cassandra. Cassandra should cite it as submitted/internal if final thesis allows, not as published. |
| Trust-fields / second Halduskultuur submission | Vault notes mention Halduskultuur #421 submitted 2026-05-25 | cite as "manuscript under review" only after portal check | Potential conceptual extension; avoid overloading Cassandra with it unless needed. |
| JeDEM Paper D / e-government evidence material | Vault notes mention submission 2026-05-25 | cite as submitted only after portal check | Possible bridge to e-government and computational methods. |
| Nekropolis negative-results / AI content regime | Zenodo supplementary and companion paper references; companion submitted to Accountability in Research | corpus concept DOI `10.5281/zenodo.20405511`; v0.3 DOI `10.5281/zenodo.20405512`; companion concept DOI `10.5281/zenodo.20409915`; companion v0.2 DOI `10.5281/zenodo.20409916`; Taylor & Francis manuscript `265159523` | Useful for evidence infrastructure in scholarly integrity, but only adjacent to Cassandra. |
| Janus multilingual claim drift | Separate repo has DMLR/TMLR/OpenReview preparation and MIRROR-style bundles | local repo `/home/anton/projects/janus`; submission artifacts under `submission/dmlr/` | Use as case of evidence infrastructure for machine-generated multilingual research claims. |
| Cassandra trusted-list observatory | Live Cloudflare deployment and scheduled GitHub Action; not yet peer-reviewed | dashboard `https://cassandra-observatory.pages.dev/`; public index `https://cassandra-observatory.pages.dev/data/index.json`; repo `https://github.com/tyche-institute/cassandra` | Primary case study for thesis article/chapter on governance-to-evidence infrastructure. |

## Case constellation

Only use applicable cases. The value of the thesis is not a pile of demos; it is a mapped ecology of evidence problems.

| Case | Primary evidence object | Why it matters | Citation posture |
|---|---|---|---|
| Cassandra | public trusted-list snapshots, diffs, dashboard index, EATF/AEP receipts | Public governance artifacts become longitudinal evidence streams. | Primary case; live system and synthetic fixtures. |
| MIRROR | source manifests, claims, notes, hashes, local verifier output | Human-reviewable provenance bundle pattern; separates evidence organization from legal effect. | Cite local repo and bundle schema unless public paper exists. |
| EATF / eatf.eu | AEP packages, verifiers, timestamp/signature profile, agent card metadata | Attestation framework for package-level integrity and offline verification. | Cite as research framework, not trust service provider. |
| Janus | multilingual round-trip claim drift cells, redacted samples, MIRROR bundles | Evidence infrastructure for AI-assisted multilingual review queues; avoids claiming translation truth. | Strong adjacent case; inspect latest submission status before public claim. |
| Vesta | public web/citation drift and preservation evidence | Shows evidence infrastructure for citation decay, page drift, and public web memory. | Use as adjacent if latest artifacts are present; avoid claiming deployment until checked. |
| Icarus | reproducibility audits, artifact badges, paper evidence checks | Evidence infrastructure for scientific reproducibility and artifact claims. | Use as adjacent scholarly-integrity case if current repo/vault artifacts are present. |
| MATx | BKT event payloads, AEP examples, tamper/replay demo | AI decision-level evidence package: each model action can become replayable and tamper-evident. | Use as synthetic/deployed vertical only with exact conflict disclosure and no real learner-data implication. |
| h2oatlas.ee / water-quality-ee | public environmental map/data pipeline evidence | Evidence infrastructure for public environmental information; governance-adjacent but not PKI core. | Use only if current public deployment and data rights are checked. |
| eaudit.ee | AI-assisted construction-audit workstation, public agent disclosure, human final-decision boundary | Evidence/disclosure pattern for professional high-stakes assistance with human decision boundaries. | Use as product/prototype case only if public wording and permission are clear. |
| Aletheia AI | GRC connector kit, partner integrations, hidden showcases, `avatar.eatf.eu` attempts | Evidence infrastructure for enterprise compliance connectors and agent disclosure surfaces. | Treat as hidden/prototype unless public exposure and permission are verified. |
| PKI Atlas | explanatory trusted-list/tutorial/atlas layer | Makes PKI governance infrastructure intelligible; not necessarily empirical corpus. | Use as explanatory public-scholarship layer. |
| X-Road agent attestation | X-Road / public-sector carrier layer with agent evidence framing | Operational public-sector trust infrastructure case adjacent to Estonian e-state. | Use as Article 2/3 candidate after status check. |
| Breakable receipts | verifier UX, tamper demos, failure-mode education | Shows why evidence packages need public failure modes, not only success receipts. | Use as pedagogical/UX companion. |
| Kolmogorov | not located in current local scan | Potential hidden showcase or conceptual case; do not claim. | Inventory required before citation. |

## Thesis structure proposal

Working thesis title:

Evidence Infrastructure at the Turning Point: PKI, eIDAS, and Attestable AI Governance

Alternative:

From PKI as Governance Infrastructure to Evidence Infrastructure: Trust Services, Public Administration, and Verifiable AI Records

Proposed article-based thesis:

1. Article 1: PKI as Governance Infrastructure. Conceptual framework, Estonian e-state, delegated trust, public administration, state capacity, eIDAS. Current anchor: Halduskultuur #419 if verified.
2. Article 2: eIDAS primitives as AI evidence infrastructure. Mapping of eIDAS/ETSI/RFC/NIST trust-service primitives to AI Act logging, transparency, post-market, and conformity-assessment evidence duties. Current anchor: mapping paper Zenodo and submission packet.
3. Article 3: Cassandra as governance-to-evidence case. Longitudinal public trusted-list observatory, EATF/MIRROR evidence packages, live Cloudflare dashboard, synthetic fixtures, replay capsule, public claim boundary.
4. Article 4 or thesis chapter: comparative evidence-infrastructure cases. Janus, MATx, MIRROR, Vesta, Icarus, eaudit, h2oatlas, Aletheia prototypes, and breakable receipts as scoped vignettes.
5. Synthesis chapter: from Carlota Perez's turning-point logic to institutional evidence infrastructure. The question is not only which technology exists, but which evidence institutions make the next regime governable.

The strongest dissertation move is to state that PKI is not obsolete in AI governance. PKI is the older governance infrastructure that already solved pieces of identity, delegation, timestamping, certification, revocation, list publication, and validation. AI governance needs a sibling layer: evidence infrastructure for model behavior, public artifacts, and institutional accountability.

## Governance and public-administration literature

Primary clusters to use from the thesis reading list:

- Drechsler, W. (2018). "Pathfinder: e-Estonia as the beta-version." JeDEM.
- Kattel, R.; Lember, V.; Tonurist, P. on public-sector innovation and digital governance.
- Mazzucato, M.; Kattel, R.; Drechsler, W. on public value, capacity, and mission-oriented governance.
- Bannister, F.; Connolly, R. on trust and transformational government.
- Margetts, H.; Dorobantu, C. on rethinking government with AI.
- Bouckaert, G. on trust and public administration.
- OECD digital government and data governance reports, especially the Digital Government Index.
- Vassil, Solvak, and Estonian e-government/e-voting literature.
- Kerikmae and Rull on Estonian digital society and legal digitalization.
- Kotka, Vargas, and Korjus on e-residency and digital state capacity.

Infrastructure studies and turning-point theory:

- Perez, C. Technological Revolutions and Financial Capital. Use for the "turning point" frame: deployment periods need institutional reshaping, not only invention.
- Star, S. L.; Ruhleder, K. on infrastructure as relational and learned in practice.
- Bowker, G. C.; Star, S. L. Sorting Things Out. Use for classification infrastructure.
- Edwards, P. N. on knowledge infrastructures.
- Plantin et al. on infrastructure/platform tensions.
- Larkin, B. on the politics and poetics of infrastructure.
- Jasanoff on sociotechnical imaginaries and public reason if the thesis needs science-and-technology-studies support.

Trust, institutions, and cryptographic governance:

- Luhmann on trust and complexity.
- Hardin on trust and trustworthiness.
- Maurer (1996) on models of trust and public-key infrastructure.
- Ellison and Schneier (2000) on ten risks of PKI.
- Recordon and Reed on OpenID/social identity if tracing decentralized identity lineage.
- Clark, Wilson, Lampson, Saltzer/Schroeder as classic security architecture anchors where relevant.
- Lessig, Reidenberg, and "code as law"/Lex Informatica literature for legal-technical governance.

Computational social science and method:

- Lazer et al. (2009) on computational social science.
- Salganik, Bit by Bit, for computational social research design.
- Grimmer, Roberts, and Stewart on text as data and social science method.
- Edelmann et al. on computational social science.
- Bail on computational social science and public-facing interpretation risks.

## Official legal, standards, and standards-body references

These should be cited as primary sources where possible. The URLs are deliberately included so Hermes and future agents can re-check them.

EU and eIDAS:

- Regulation (EU) No 910/2014, eIDAS: `https://eur-lex.europa.eu/eli/reg/2014/910/oj`
- Regulation (EU) 2024/1183, European Digital Identity Framework / eIDAS amendment: `https://eur-lex.europa.eu/eli/reg/2024/1183/oj`
- Regulation (EU) 2024/1689, AI Act: `https://eur-lex.europa.eu/eli/reg/2024/1689/oj`
- Commission Implementing Decision (EU) 2015/1505 on technical specifications and formats for trusted lists: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32015D1505`
- Commission Recommendation (EU) 2024/1101 on a coordinated implementation roadmap for the transition to post-quantum cryptography: verify exact title and citation before final use.
- EU Trusted List / List of the Lists official endpoints and documentation: cite the exact endpoint used by Cassandra and the saved local metadata.

ETSI trust services:

- ETSI TS 119 612, Trusted Lists: `https://www.etsi.org/deliver/etsi_ts/119600_119699/119612/`
- ETSI EN 319 401, General Policy Requirements for Trust Service Providers: `https://www.etsi.org/deliver/etsi_en/319400_319499/319401/`
- ETSI EN 319 411-1 and EN 319 411-2, policy and security requirements for certification authorities.
- ETSI EN 319 412 series, certificate profiles.
- ETSI EN 319 102-1, procedures for creation and validation of AdES digital signatures.
- ETSI EN 319 122 / 132 / 142, CAdES / XAdES / PAdES profiles as needed.
- ETSI EN 319 422, time-stamping protocol and time-stamp token profiles.

IETF/RFC:

- RFC 5280, Internet X.509 Public Key Infrastructure Certificate and CRL Profile: `https://www.rfc-editor.org/rfc/rfc5280`
- RFC 3161, Time-Stamp Protocol: `https://www.rfc-editor.org/rfc/rfc3161`
- RFC 6960, OCSP.
- RFC 6962, Certificate Transparency.
- RFC 8446, TLS 1.3.
- RFC 8785, JSON Canonicalization Scheme, relevant to AEP canonical payloads.
- RFC 7515/7517/7519, JWS/JWK/JWT, if using JOSE comparisons.
- SD-JWT VC IETF OAuth draft: `https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-10.html` or latest successor; verify current draft number before final citation.

PKI ecosystem:

- CA/Browser Forum Baseline Requirements: `https://cabforum.org/working-groups/server/baseline-requirements/`
- CA/Browser Forum S/MIME and Code Signing Baseline Requirements where appropriate.
- PKI Consortium / PKIC: `https://pkic.org/`
- PKIC working groups to mention when relevant: PQC, PKI Maturity Model, Cryptographic Module, CA, Training and Certification.
- WebTrust for Certification Authorities and ETSI audits as assurance-comparison material.

NIST and cryptography:

- FIPS 140-3, Security Requirements for Cryptographic Modules.
- FIPS 186-5, Digital Signature Standard.
- FIPS 203, ML-KEM, published 2024-08-13: `https://csrc.nist.gov/pubs/fips/203/final`
- FIPS 204, ML-DSA, published 2024-08-13: `https://csrc.nist.gov/pubs/fips/204/final`
- FIPS 205, SLH-DSA, published 2024-08-13: `https://csrc.nist.gov/pubs/fips/205/final`
- NIST SP 800-57 key management, SP 800-63 digital identity, SP 800-208 stateful hash-based signatures, and SP 800-227 KEM recommendations if needed.

ISO, W3C, OpenID, supply-chain evidence:

- ISO/IEC 27001:2022: `https://www.iso.org/standard/27001`
- ISO/IEC 27002, 27005, 27036, 15408 Common Criteria, 18045, 19790; use official ISO/IEC entries or library copies.
- W3C Verifiable Credentials Data Model v2.0: `https://www.w3.org/TR/vc-data-model-2.0/`
- W3C Decentralized Identifiers, WebAuthn, and related credential work.
- OpenID Connect, OpenID for Verifiable Credential Issuance, OpenID for Verifiable Presentations, SIOPv2, FAPI.
- Sigstore, Rekor, in-toto, SLSA, SPDX, CycloneDX, OpenTelemetry as software/supply-chain evidence comparators.

## Cassandra paper argument

Working title:

Cassandra: From Governance Infrastructure to Evidence Infrastructure

Contribution:

1. A method for cautious longitudinal observation of public trusted-list governance artifacts.
2. A live full-stack observatory with scheduled refresh, public dashboard, public index schema, EATF receipt fields, and dashboard cards.
3. A fixture-backed evidence package showing expected behavior under no-change, hash-change, provider/service inventory change, fetch failures, non-XML inputs, missing signing inputs, dashboard state variation, and claim-safety boundaries.
4. A thesis bridge from eIDAS/PKI governance infrastructure to AI evidence infrastructure.

Do not frame Cassandra as:

- a trusted-list validator;
- a legal-status checker;
- a supervisory authority;
- a compliance tool;
- a public-alerting system;
- proof that no legally relevant change occurred.

Frame Cassandra as:

- a structural observer;
- a public evidence stream;
- a reproducible evidence-package case;
- a method paper and thesis case;
- a bridge between public administration, PKI governance, and AI accountability.

## What to add next

Highest-value additions:

1. EATF success/tamper fixtures with non-secret synthetic keys and intentionally broken payload/AEP cases.
2. One month of scheduled observations, summarized as a longitudinal run table.
3. A paper section that explicitly ties Cassandra to PKI as governance infrastructure and to Perez-style "turning point" institutional restructuring.
4. A formal related-work section using the clusters above.
5. A "case-study maturity matrix" comparing Cassandra, Janus, MATx, Vesta, Icarus, MIRROR, eaudit, h2oatlas, and Aletheia prototypes across evidence object, publicness, data sensitivity, verification method, and publication risk.
6. Dashboard UI wiring for the generated card JSON, if not already visible.
7. Vault sync note that distinguishes public/Zenodo references from submissions and internal prototypes.
8. A final thesis chapter packet: abstract, research question, method, evidence table, case map, standards table, limitations, and references.

## Reference statement for the thesis

The dissertation should make one clean statement:

PKI did not merely secure transactions; it institutionalized a way of governing digital trust through certificates, lists, policies, audits, timestamps, revocation, and validation. AI governance now needs the adjacent layer: evidence infrastructure that can bind claims about systems, data, decisions, public artifacts, and reviews to reproducible records. Cassandra is the public-governance-artifact case. MATx is the AI-decision case. Janus is the AI-assisted knowledge-translation case. MIRROR and EATF provide the evidence-package grammar. The thesis contribution is to show how these layers connect without collapsing evidence integrity into legal truth.
