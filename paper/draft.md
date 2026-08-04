# Cassandra: From Governance Infrastructure to Evidence Infrastructure

Author: Anton Sokolov  
Affiliation: Tyche Institute, Tallinn, Estonia  
Status: working draft; not for publication without operator review  
Generated: 2026-05-27

## Abstract

Cassandra is a research-only observatory for Europe's public trusted-list infrastructure. It begins with a simple but methodologically important claim: public legal-technical governance artifacts can be observed, hashed, bundled, signed, displayed, and independently checked while preserving the distinction between evidence integrity and legal interpretation. The project is not a trusted-list validator, a supervisory tool, a compliance engine, or a public alerting service. It is a case study in how public governance state can become evidence infrastructure.

The implemented workflow starts from a locally saved European list-of-lists snapshot, extracts the national document pointers contained in that public artifact, fetches the referenced files into dated snapshot directories, preserves endpoint and parser telemetry, normalizes comparable XML, emits bounded structural diffs, builds MIRROR-style evidence bundles, records EATF/AEP package-integrity receipts where signing inputs exist, and publishes an aggregate dashboard index. Current public dashboard data records completed runs through `latest_date=2026-05-27`, `run_count=4`, and `eatf_verified_count=4`; those values are dashboard telemetry, not legal or supervisory conclusions.

The paper argues that Cassandra matters because trusted lists sit at the intersection of PKI, eIDAS, ETSI standardization, public administration, and software operations. The case shows how the older governance infrastructure of digital trust can be made observable as a newer evidence infrastructure: dated manifests, hashes, bundles, receipts, schemas, dashboard cards, fixtures, replay instructions, and claim-safety checks. Synthetic fixtures complement real observations by testing no-change behavior, normalized-hash churn, provider/service inventory movement, fetch failures, non-XML inputs, EATF success and tamper cases, missing signing inputs, dashboard multistate handling, and forbidden overclaiming language. The contribution is methodological and bounded: Cassandra supports reproducible structural observation of saved public artifacts; it does not assert legal effect, validate source signatures for relying-party purposes, determine provider or service status, supervise trusted lists, certify compliance, issue public alerts, or approve publication.

## Claim-safety note

All observations in this draft are limited to locally recorded structural artifacts: fetched files, endpoint metadata, parser telemetry, normalized XML hashes, machine-readable diff records, evidence bundles, package-integrity receipts, dashboard data, and synthetic fixture outputs. A structural diff observed by this project does not assert legal effect and should not be read as evidence that any provider, service, scheme, certificate, authority, or list has gained or lost legal status. Signature-related fields are treated as structural or package-integrity evidence only. Cassandra does not perform relying-party validation, does not describe relying-party validation, supervisory review, conformity assessment, public alerting, legal review, or publication approval.

## 1. Introduction: from governance infrastructure to evidence infrastructure

Public-key infrastructure is governance infrastructure. It coordinates cryptographic keys, certificate policies, audits, revocation mechanisms, timestamping, supervisory expectations, software behavior, and public/private institutional roles. In the European trust-service setting, this governance infrastructure becomes visible through eIDAS, ETSI standards, national supervisory publication practices, and the European list-of-lists mechanism. These artifacts are not merely technical files. They are public administrative surfaces through which legal-technical state is represented to software and institutions.

Cassandra asks what happens when such public governance artifacts are treated as evidence objects without pretending that observation is legal supervision. The core sentence is therefore: Cassandra: from governance infrastructure to evidence infrastructure. The move is not to reinterpret trusted lists as a new dataset detached from law. The move is to preserve the evidence boundary: observe public artifacts, record the method, hash the bytes, normalize cautiously, compare structure, bundle sources and claims, produce package receipts, display aggregate telemetry, and state explicitly what none of those steps can prove.

That boundary is the reason the case is stronger than an ordinary XML-monitoring exercise. Trusted-list documents are legally meaningful in their institutional setting, but Cassandra does not claim to determine their legal meaning. The workflow can say that a locally saved run attempted a given number of LOTL-derived pointers, fetched a given number of content files, recorded endpoint or parser outcomes, normalized a given number of XML artifacts, emitted configured structural diff classes, and packaged the resulting evidence. It cannot say that a trust service is valid, invalid, qualified, revoked, compliant, supervised, reliable, or risky.

The paper's research question is methodological: how can public legal-technical governance state be made observable, reproducible, and discussable while preserving the line between evidence integrity and legal interpretation? Cassandra answers with an operating case. It combines a scheduled GitHub Action, local evidence bundles, EATF/AEP receipts, a public Cloudflare dashboard, machine-readable schema and card files, paper-facing claims tables, and synthetic fixtures. The dashboard is not marketing. It is a public method surface that shows what the evidence stream contains and what it refuses to claim.

This case also provides a bridge to AI governance. The AI Act creates recordkeeping, logging, transparency, documentation, post-market, and conformity-assessment evidence problems. Cassandra is not an AI monitor and does not observe model behavior. Its relevance is analogical and infrastructural: the same evidence discipline needed for public trusted-list artifacts is needed for AI governance records. AI systems will require dated artifacts, source manifests, tamper-evident packages, replayable verification, clear claim boundaries, and public explanation of failure modes. Cassandra makes that abstract evidence-infrastructure argument concrete in a public, inspectable, lower-risk governance domain.

## 2. Background: PKI, eIDAS, and trusted lists as public administrative artifacts

The PKI literature and standards ecosystem show that digital trust is institutional before it is merely computational. Maurer's trust models, Ellison and Schneier's risk analysis, RFC 5280 certificate and CRL profiles, RFC 3161 timestamping, RFC 6960 OCSP, certificate-transparency work, CA/Browser Forum requirements, WebTrust and ETSI audit regimes, PKI Consortium resources, and NIST FIPS publications all point to a mature but contested governance substrate. Certificates, revocation, timestamps, and validation conventions require coordination among standards bodies, regulators, auditors, operators, software vendors, and relying parties.

eIDAS and ETSI give that substrate a European legal-technical grammar. Regulation (EU) No 910/2014, Regulation (EU) 2024/1183, Commission Implementing Decision (EU) 2015/1505, ETSI TS 119 612, ETSI EN 319 401, ETSI EN 319 411 and 319 412, ETSI EN 319 102, and ETSI EN 319 422 explain why trusted lists are more than arbitrary XML. They are public governance artifacts with formal roles in the trust-service ecosystem. Cassandra cites these sources to establish context and document semantics, not to claim that the project performs validation, conformity assessment, or supervision.

Cassandra sits at the intersection of five literature and standards clusters. First, PKI and cryptographic-governance work explains the older trust substrate: certificate policy, revocation, timestamping, validation, assurance regimes, and ecosystem coordination.[^pki-governance] Checked anchors include RFC 5280, RFC 3161, RFC 8785, CA/Browser Forum Baseline Requirements v2.2.7, PKIC ecosystem material, and NIST FIPS 203/204/205. These sources are relevant because they show that PKI is already a governance infrastructure, not merely a cryptographic primitive set. Cassandra does not replace that infrastructure and does not perform relying-party validation; it observes one public administrative surface of it.

Second, eIDAS and ETSI sources provide the legal-technical grammar of the observed artifacts.[^trusted-list-boundary] Regulation (EU) No 910/2014, Regulation (EU) 2024/1183, Commission Implementing Decision (EU) 2015/1505, the European Commission trusted-list page, ETSI TS 119 612 V2.4.1, ETSI EN 319 401 V3.1.1, ETSI EN 319 411-1 V1.5.1, and ETSI EN 319 422 V1.1.1 explain why trusted lists are public governance artifacts with formal roles. Cassandra cites them to establish context and source semantics, not to claim supervision, legal-status determination, signature validation, or conformity assessment.

Third, public-administration and digital-state scholarship explains why this matters. Work by Drechsler, Kattel, Lember, Tonurist, Mazzucato, Bannister and Connolly, Margetts and Dorobantu, OECD digital-government authors, and Estonian e-state/X-Road scholars frames digital state capacity as a matter of institutional records, public value, trust, administrative routines, and technical infrastructures. Trusted lists are a small but revealing surface of that capacity. They show how governance becomes machine-readable and how machine-readable artifacts become part of public administration.

Fourth, infrastructure studies and turning-point theory provide the evidence-infrastructure frame. Perez's turning-point logic emphasizes that technological regimes require institutional reshaping during deployment. Star and Ruhleder, Bowker and Star, Edwards, Plantin and coauthors, Larkin, and Jasanoff show that infrastructures become visible through maintenance, classification, breakdown, imagination, and public contestation. Cassandra operationalizes this insight modestly: it makes a specialized governance surface inspectable through manifests, hashes, diffs, bundles, receipts, schemas, cards, and dashboard views.

Computational social-science and evidence-method literature supplies the caution. Lazer, Salganik, Grimmer, Roberts, Stewart, Edelmann, Bail, and related authors show that repeated observation of public or digital traces can be valuable only when measurement validity, reproducibility, aggregation choices, and interpretation risks are explicit. Cassandra's synthetic fixtures, aggregate-only prose, forbidden-wording scanner, publication-status discipline, and EATF/MIRROR boundaries are therefore part of the method, not decorative compliance language.

Fifth, computational social-science and evidence-method literature, including Lazer, Salganik, Grimmer/Roberts/Stewart, Edelmann, and Bail, supplies the cautionary method frame.[^method-humility] Repeated observation of public artifacts can produce useful evidence, but measurement validity, reproducibility, aggregation choices, and public interpretation risks must be explicit. Cassandra's synthetic fixtures, aggregate-only prose, claim-safety scanning, and EATF/MIRROR boundaries are therefore not ancillary engineering details; they are part of the research method. The checked reference ledger is maintained in `notes/cassandra-checked-reference-ledger-2026-05-27.md`; the fuller reference scaffold is maintained in `paper/related-work-card.md`, a controlled seed bibliography is maintained in `paper/reference-seed-bibliography.md`, and the wider thesis case posture is mapped in `notes/case-study-maturity-matrix.md`.

[^pki-governance]: PKI is often introduced through algorithms, but it operates through certificates, policies, revocation, audits, root distribution, software defaults, and institutional delegation. That is governance work with cryptographic parts, not cryptography wearing a small administrative hat.

[^trusted-list-boundary]: eIDAS and ETSI explain why the XML matters. They do not turn Cassandra into a validator, supervisor, conformity assessor, or public-warning feed; the project is more modest, and therefore more publishable.

[^turning-point-infrastructure]: Perez supplies the large turning-point vocabulary; Star/Ruhleder and Bowker/Star keep it grounded where infrastructure actually lives: maintenance, categories, access, and failure modes. Grand theory earns its keep here only if it can survive the manifest.

[^method-humility]: The highest compliment for an evidence pipeline may be that it becomes boring in a reproducible way. Cassandra's method claim is not "trust us"; it is "re-run the trail and see exactly where the claim stops."

## 3. Dataset boundary and source handling

Cassandra's dataset boundary is intentionally narrow. A run starts from the public European list-of-lists endpoint and the document pointers extracted from the locally saved XML copy. The workflow does not add ad hoc targets, search for alternative endpoints, infer substitutions, or treat a failed request as evidence of any legal status. This keeps each run tied to a reproducible input: saved LOTL bytes, extracted pointer JSON, a dated snapshot manifest, adjacent fetch metadata, and local hashes.

The first collection layer preserves operational facts. For each pointer, Cassandra records the attempted URL, local path, access timestamp, HTTP status or exception, response hash when applicable, redirect information where available, and content type or filename context. Endpoint failures, redirects, PDF references, HTML/TXT responses, and unreachable pointers are not hidden. They are collection telemetry. They may matter for reproducibility, but they are not public warnings, endpoint certification, status judgments, or supervision.

The parsing layer narrows the corpus again. XML-like artifacts are parsed and normalized using deterministic serialization so that comparable records can be diffed. PDF and other non-XML artifacts are skipped as non-comparable input; malformed XML becomes parser telemetry. Signature-shaped XML structures may be counted or recorded as structural fields, but the parser does not validate signatures. The distinction is crucial: a signature-shaped element in saved XML is not the same thing as a relying-party verification result.

The source-handling rule for the paper follows from this boundary. Run-specific counts cite local artifacts such as `snapshots/<date>/manifest.json`, `normalized/<date>/manifest.json`, `diffs/<date>.json`, `bundles/<date>/snapshot-summary.json.bundle/manifest.json`, `alerts.jsonl`, and `observatory/public/data/index.json`. Live URLs remain source provenance for collected files, but historical claims are about what the saved run recorded at its access time. The draft should not re-query current endpoints while writing a sentence about a past observation.

This boundary also protects the public dashboard. The dashboard index and cards are presentation artifacts derived from the local evidence loop. They can report `latest_date`, run counts, aggregate diff classes, receipt statuses, caveats, and artifact paths. They cannot claim that an endpoint is valid, a signature is valid, a provider is qualified, a service changed legal status, or a public alert has been issued. The public dashboard is an evidence-interface, not a trust service, not a relying-party process, not as a complete or authoritative registry, and its local JSONL/event rows are not public alerts.

## 4. Method: collection, normalization, diffing, bundling, and receipts

The method separates collection, normalization, comparison, packaging, and presentation. This separation is the evidence-engineering contribution. Each step has its own artifacts, validators, and claim boundary, so a later reviewer can inspect where a statement came from and what it does not imply.

Collection uses the LOTL-derived pointer list to create dated snapshot directories. The fetcher preserves both successful files and failure metadata. It treats timeouts, HTTP errors, redirects, and unreachable pointers as explicit workflow states. This design avoids a common evidence failure: silently dropping failed collection attempts and later presenting only the clean subset as if it were the whole corpus.

Normalization is deliberately less ambitious than a trusted-list processor. It canonicalizes XML-like artifacts for comparison, records coarse scheme metadata, and extracts structural fields such as provider/service inventory counts and signature-shape observations. Provider and service comparison handles are stable local hashes, not narrative identifiers. Raw listed names remain inside local machine-readable evidence unless the operator later approves a named example and its wording.

Diffing compares normalized records against a configured baseline. The implemented classes include listed-document addition or removal, normalized-hash change, summary-field change, provider-inventory change, service-inventory change, and provider-service-detail change. A zero-change result means only that this parser, normalizer, and baseline did not emit configured structural changes for the saved inputs. A nonzero result means only that a configured structural difference was observed in local artifacts. Neither result determines legal effect.

Bundling wraps substantive run summaries in MIRROR-style evidence packages. A bundle contains a manifest, claims file, notes, source copies or source references, and verification output. Its purpose is human-reviewable provenance: what artifact is being claimed, which sources support it, what caveats apply, and which hashes can be checked offline. MIRROR-style bundling organizes evidence; it does not certify the legal meaning of the source documents.

EATF/AEP receipt handling adds package-integrity evidence. When signing inputs are present, Cassandra can create an AEP package and verification receipt for a bounded observation payload. The receipt can support statements about package bytes, declared hashes, signer profile metadata, and verifier outcome. It does not validate source XML signatures, determine trusted-list legal status, supervise trust services, or approve publication. When signing inputs are absent, the workflow records `skipped_missing_signing_inputs` rather than pretending a receipt exists.

The public observatory index is the final presentation layer. `observatory/public/data/index.json` remains machine-readable and is accompanied by a schema and dashboard card JSON files. The cards expose claim boundary, latest-run summary, EATF receipt summary, aggregate diff classes, and caveats. They are designed for dashboard consumers and reviewers who need a compact public method surface without losing the non-claim boundary.

## 5. Results: current observations and fixture-backed behavior

The current public index target records `latest_date=2026-05-27`, `run_count=4`, and `eatf_verified_count=4`. The corresponding dashboard is live at `https://cassandra-observatory.pages.dev/`, and the public data index is available at `https://cassandra-observatory.pages.dev/data/index.json`. These facts demonstrate that the evidence loop is not only described in prose: it operates through scheduled workflow artifacts, Cloudflare deployment, public JSON, figure files, and dashboard cards. They do not demonstrate legal validity, supervisory status, endpoint reliability, or compliance.

The earliest baseline run remains useful because it explains the semantics of a row. It attempted 43 LOTL-derived pointers, recorded successful content files and endpoint failures, normalized a subset of comparable XML artifacts, skipped non-XML/PDF artifacts, recorded parser outcomes, and initialized a zero-change baseline because no prior baseline existed. Later runs extend that lineage into a small longitudinal sequence and add aggregate dashboard state. The appropriate interpretation is local workflow telemetry: dates, counts, paths, hashes, and configured diff classes.

The fixture suite is now central to the paper. Real observations show that the workflow can operate on public LOTL-derived artifacts. Synthetic fixtures show that the software behaves safely in controlled edge cases without exposing real provider or service names. The stable no-change fixture checks that identical comparable records do not emit structural diffs. The normalized-hash fixture checks that canonical-content churn is observable even when record counts remain stable. Provider-inventory, service-inventory, and provider-service-detail fixtures check that hashed handles can express structural movement without provider-specific prose.

Fetch and non-XML fixtures show failure-mode discipline. They cover timeout, HTTP error, redirect, unreachable pointer, PDF/HTML/TXT skips, valid XML, and malformed XML. The result is not that any real endpoint is good or bad. The result is that the workflow makes operational conditions explicit and does not confuse absence of comparable XML with legal or supervisory meaning.

EATF fixtures test package-integrity boundaries. The success fixture uses non-secret synthetic material and a fake local EATF CLI to show an `ok` package receipt in a controlled environment. The tamper fixture alters synthetic package bytes and expects verifier failure. The missing-input fixture records `skipped_missing_signing_inputs`. Together they answer a reviewer question that the live receipts alone cannot answer safely: an EATF result is about package evidence and verifier behavior, not the legal or cryptographic validity of the underlying trusted-list source.

Dashboard and claim-safety fixtures test public interpretation. A dashboard multistate fixture checks that `ok`, `verify_failed`, and `skipped_missing_signing_inputs` receipt states remain caveated data states rather than public alerts. The claim-safety fixture scans controlled wording samples for forbidden overclaims about legal validity, source-signature validity, supervisory approval, compliance, public alerting, and absence of legally relevant change. The scanner is heuristic and does not replace operator review, but it makes the abstention boundary executable.

The combined result is a mature case-study kit rather than a thin parser demo. Cassandra has real observations, controlled fixtures, schema, dashboard cards, evidence packages, EATF boundary cards, MIRROR bundle documentation, a replay capsule, publication-status discipline, a reference atlas, a related-work card, a case-study maturity matrix, and a fixture-to-claim reviewer map. The paper can therefore argue about evidence infrastructure with both an operating public system and controlled software-behavior evidence.

## 6. Case analysis: what becomes visible and what remains outside observation

Cassandra makes several things visible. It makes collection conditions visible: which pointer attempts produced content, redirects, HTTP errors, timeout-like failures, non-XML artifacts, or parser exceptions. It makes normalization scope visible: which saved files entered the comparable XML subset and which did not. It makes structural change classes visible: document-level, normalized-hash, summary-field, provider-inventory, service-inventory, provider-service-detail, and signature-shape movement under the configured parser. It makes evidence lineage visible: which local paths, hashes, bundles, receipts, and dashboard rows support a statement.

It also makes abstention visible. The public dashboard and paper cards state that Cassandra is not legal supervision, not relying-party validation, not compliance assessment, not a trust service, not public alerting, and not publication approval. This refusal is not a weakness. It is part of the contribution. Evidence infrastructure is useful only when its users can see where evidence stops.

Several questions remain outside observation. Cassandra does not determine whether a source trusted list is legally valid, whether a signature verifies under relying-party rules, whether a provider or service has a particular status, whether a supervisory body has taken or should take action, whether an endpoint is fulfilling a duty, or whether no legally relevant change occurred. It also does not rank countries, authorities, schemes, providers, or services. Counts can guide research triage, but they cannot become risk rankings without a new method and review boundary.

The case-study maturity matrix clarifies adjacent roles. Cassandra is the public-governance-artifact case. MIRROR is the human-reviewable bundle pattern. EATF/AEP is the package-level attestation and verifier layer. PKI Atlas is explanatory, not the empirical corpus. X-Road attestation is an adjacent public-sector trust-infrastructure case requiring status checks. Vesta and Icarus are evidence-infrastructure cases for web/citation drift and reproducibility. Janus addresses multilingual AI-assisted review drift. MATx addresses AI decision-level replay and tamper evidence under synthetic/no-real-learner-data boundaries unless public deployment facts are rechecked. h2oatlas, eaudit, Aletheia, and avatar.eatf.eu require publicness, permission, and wording verification before public claims. Kolmogorov remains inventory-first.

This map prevents case sprawl. The point is not to merge all projects into Cassandra. The point is to show that evidence infrastructure has distinct roles: public artifact observation, source/claim bundling, package attestation, dashboard explanation, verifier UX, AI decision replay, multilingual drift review, public web preservation, reproducibility audit, and professional disclosure. Cassandra is strongest when it remains the trusted-list observatory case and uses the other projects only as carefully labelled comparators.

## 7. AI governance connection: evidence records rather than model behavior

The AI Act connection should be framed with care. Cassandra does not monitor AI models, high-risk systems, training data, learner data, decisions, or post-market incidents. It should not be cited as proof that an AI system is compliant. Its relevance is that AI governance will require evidence infrastructure with many of the same properties demonstrated here: dated records, source manifests, cryptographic hashes, package receipts, replayable verification, dashboard summaries, failure-mode education, and explicit claim boundaries.

eIDAS and PKI show that older digital trust infrastructures already solved parts of the evidence problem: identity, delegation, certificates, timestamps, revocation, validation conventions, policy documents, audit regimes, and public lists. AI governance needs a sibling layer for models, datasets, outputs, human review, deployment changes, translations, evaluations, and incidents. Cassandra shows how one public governance surface can be converted into evidence objects without collapsing evidence integrity into legal interpretation.

This distinction matters for EATF/AEP. An AEP package can help verify bytes, hashes, metadata, signer profiles, and tamper evidence. It does not by itself certify that an AI decision was lawful, fair, accurate, or compliant. The same is true in Cassandra: an EATF receipt can verify a Cassandra observation package; it does not validate the trusted-list source as a relying party. The paper should use this symmetry as a teaching point. Evidence infrastructure can strengthen governance only when verifier UX tells users what is verified, what is not verified, and which interpretation steps require humans or institutions.

MIRROR reinforces the same lesson. A source manifest, claims file, notes file, and local verification output make a bundle reviewable. They do not make every claim true. They make the claim's evidence boundary inspectable. AI governance records will need similar bundles for model cards, evaluation reports, incident logs, translated materials, human review queues, and post-market observations. Cassandra is a public, low-conflict case for developing that discipline.

## 8. Limitations and threats to validity

The main limitation is legal non-interpretation. Cassandra observes public artifacts but does not interpret legal status. This means the method cannot answer many questions that readers may care about: whether a trusted list is authoritative, whether a specific service is qualified, whether a signature is valid, whether a supervisory duty has been met, or whether a change has legal effect. The paper should state this limitation plainly rather than treating it as a footnote.

A second limitation is parser perspective. The normalizer and structural parser see selected XML structure under current implementation choices. Namespace edge cases, parser failures, non-XML pointers, schema variations, and implementation bugs can affect counts. Synthetic fixtures reduce some risk by testing expected behavior, but they do not prove semantic completeness. Results should keep parser-success counts next to diff counts and avoid treating the comparable subset as the whole public ecosystem.

A third limitation is temporal shallowness. Four public-index runs and early dated lineages are enough to demonstrate the evidence loop and public dashboard, but they are not enough for broad trend claims. The paper should avoid words such as stability, volatility, typical, recurring, or national pattern unless they are scoped to configured local observations over a clearly stated period and backed by longer series evidence.

A fourth limitation is presentation pressure. Charts, dashboard cards, and receipt states can invite readers to infer legal importance from visual prominence. Cassandra mitigates this with caveats, schema fields, card text, fixture tests, and claim-safety scanning, but final publication still requires operator review. Clean validators do not approve publication.

A fifth limitation is publication and status discipline. Reference cards include official sources, standards, scholarly anchors, Zenodo/preprint items, submitted manuscripts, internal artifacts, prototypes, and synthetic fixtures. These statuses must remain separated. Submitted Tyche work must not be presented as accepted or peer-reviewed. Prototype or hidden-showcase projects must not be presented as public adoption. Synthetic fixtures must not be presented as empirical evidence about real trusted-list actors.

## 9. Reproducibility, dashboard, and release gates

A reviewer should be able to replay Cassandra at several levels. The no-fetch replay path reads existing local artifacts, validates schemas, runs fixture tests, checks aggregate-only naming, verifies paper evidence references, and inspects public dashboard data without contacting trusted-list endpoints. The guarded new-run path waits for a new eligible date, creates a new snapshot lineage, normalizes comparable XML, computes diffs, builds bundles, creates or records EATF receipts, updates alerts, regenerates aggregate results, renders figures, and rebuilds the public index. Both paths preserve the same claim boundary.

The public index schema and dashboard cards make the presentation layer machine-readable. Consumers can distinguish project metadata, latest date, run count, aggregate totals, figures, per-run artifacts, EATF status, claim-boundary caveats, and dashboard-card references. The schema does not turn the dashboard into a validator. It gives consumers predictable fields and caveats so they do not have to infer semantics from layout.

Release gates remain manual. Before external circulation, the operator should review named-entity use, source boundaries, affiliation, employment/IP constraints, legal wording, reference status, figure captions, dashboard wording, and whether any artifact could be mistaken for regulated trust-service output or public alerting. Validators support that review by checking paths, hashes, schema conformance, fixture behavior, aggregate-only naming, and forbidden wording. They do not replace review.

The artifact index is append-only. Duplicate rows and stale historical hashes can occur because repeated maintenance changes files and records current hashes later. The current-hash validator distinguishes maintenance warnings from missing or stale current artifacts. This policy protects provenance from destructive cleanup. A reviewer should read duplicate rows as local evidence-ledger mechanics, not as public endpoint behavior.

## 10. Conclusion

Cassandra demonstrates a bounded governance-to-evidence move. It takes public trusted-list artifacts, records dated observations, preserves collection and parser telemetry, normalizes comparable XML, emits structural diffs, builds evidence bundles, attaches package-integrity receipts, publishes a caveated dashboard index, and tests edge cases with synthetic fixtures. The result is not a status monitor. It is an evidence-infrastructure case study.

The contribution is strongest when stated narrowly. Public governance artifacts can be observed, hashed, bundled, signed, displayed, and independently checked while preserving the distinction between evidence integrity and legal interpretation. This method can support research, reviewer discussion, thesis integration, and AI-governance analogy. It cannot determine legal effect, validate source signatures for relying-party purposes, supervise trusted lists, certify compliance, issue public alerts, or approve publication.

Future work should extend the dated series, refine aggregate figures, verify bibliographic metadata, and, only after operator review, consider carefully worded named examples if they materially improve the paper. The longer-term thesis contribution is that PKI and eIDAS are not obsolete background for AI governance. They are the older governance infrastructure from which a new evidence infrastructure can learn: identity, delegation, timestamps, lists, audits, verification, failure modes, and institutional boundaries. Cassandra makes that lesson concrete.


## 11. Paper structure and reviewer-facing argument

The submission should not be organized as a tool inventory. A useful paper structure begins with the governance-to-evidence claim, then explains why trusted lists are a rare public surface where the claim can be tested. The introduction should make three moves. First, it should say that PKI is governance infrastructure: a coordination system involving law, standards, audits, public lists, software, and institutions. Second, it should say that Cassandra watches one public administrative surface of that infrastructure. Third, it should say that the contribution is an evidence method, not a legal conclusion.

The background section should be selective. It should not become a general history of PKI or a full eIDAS treatise. Its job is to show why a machine-readable trusted-list artifact is institutionally meaningful. The legal and standards references establish that the observed files are part of a formal trust-service grammar. Public-administration and infrastructure studies establish that such artifacts are governance infrastructure. Computational-method references establish why repeated observation, aggregation, fixtures, and claim boundaries are necessary for responsible publication.

The method section should be written as a chain of abstentions as much as a chain of operations. Collection abstains from substituting sources. Normalization abstains from relying-party validation. Diffing abstains from legal interpretation. Bundling abstains from claiming truth beyond source, hash, and caveat linkage. EATF/AEP receipts abstain from validating source legal meaning. Dashboard cards abstain from public alerting. This structure is reviewer-friendly because it turns likely objections into design choices rather than after-the-fact disclaimers.

The results section should pair real observations with synthetic fixture evidence. Real dated runs show that the pipeline operates on public LOTL-derived artifacts and produces dashboard-visible evidence. Fixtures show that controlled edge cases behave as intended. This pairing answers the likely objection that four early runs are too small for empirical trend claims: Cassandra is not yet claiming trends. It is claiming a full-stack evidence loop and a test-backed method for future longitudinal observation.

The case-analysis section should explicitly state what becomes visible: collection conditions, parser scope, comparable XML subsets, structural diff classes, evidence lineage, package-integrity status, and dashboard-state semantics. It should also state what remains outside observation: legal effect, source-signature validity, provider/service status, supervisory conclusions, compliance, public warnings, and absence of legally relevant change. Keeping both lists side by side prevents the paper from sounding timid. The method is ambitious about evidence integrity precisely because it is disciplined about interpretation.

The AI-governance section should remain analogical. The best sentence is not that Cassandra solves AI Act compliance. It is that Cassandra demonstrates the kind of evidence discipline that AI governance records will need: dated observations, source manifests, hashes, bundles, receipts, replay capsules, dashboards, and failure-mode education. The paper should connect to EATF/AEP and MIRROR as evidence infrastructure patterns, while refusing any claim that those tools by themselves determine legality, fairness, safety, or compliance.

The conclusion should return to the core sentence. Cassandra moves from governance infrastructure to evidence infrastructure by making a public governance artifact observable, packageable, and discussable. It does not transform observation into supervision. It gives researchers, reviewers, and future thesis chapters a bounded method for studying public legal-technical artifacts over time.

## 12. Reviewer objections and planned answers

A first reviewer may say that Cassandra is only an XML parser. The answer is that XML parsing is one component inside a larger evidence loop. The project includes source-boundary discipline, dated snapshots, endpoint telemetry, deterministic normalization, structural diffs, hashed provider/service comparison handles, MIRROR-style bundles, EATF/AEP package receipts, public dashboard schema, dashboard card JSON, replay instructions, fixture tests, claim-safety scanning, publication-status discipline, and thesis/cross-case mapping. The parser is necessary, but the case contribution is the packaging of public governance state into bounded evidence objects.

A second reviewer may say that early run counts are too small. The answer is that the paper should not claim mature longitudinal trends from early rows. The early results establish operational feasibility, public dashboard continuity, evidence-package integrity, schema stability, and fixture-backed behavior. A longer series will be needed for empirical claims about document-structure churn. The current submission can still be valuable as a case-study method paper if it is honest about temporal shallowness and does not use words such as stability, volatility, or national pattern beyond method-scoped context.

A third reviewer may ask whether Cassandra validates trusted lists. The answer must be unambiguous: no. Cassandra is not trusted-list validation, not source-signature validation, not legal-status determination, not supervision, not compliance review, not public alerting, and not publication approval. It observes saved public artifacts and verifies its own evidence packages. This distinction should appear in the abstract, method, results, limitation, dashboard cards, and figure captions.

A fourth reviewer may question whether synthetic fixtures are artificial. The answer is that they are intentionally artificial because the paper needs controlled behavior evidence without exposing provider/service names or implying real legal status changes. Synthetic no-change, hash-change, provider/service inventory, fetch failure, non-XML, EATF success, EATF tamper, missing-input, dashboard, and claim-safety fixtures demonstrate software and wording behavior. They do not replace real observations; they complement them by proving that edge cases are represented safely.

A fifth reviewer may worry that public dashboard publication turns the system into an alerting service. The answer is that the dashboard is deliberately limited to aggregate telemetry, caveats, schemas, cards, and artifact pointers. It does not rank actors, issue severity warnings, name providers in prose, instruct relying parties, or state legal conclusions. Dashboard visibility is a method-surface choice: it lets reviewers and future agents inspect what the evidence loop contains. It is not a public warning feed.

A sixth reviewer may ask how Cassandra relates to AI governance. The answer is that the relationship is infrastructural, not empirical. Cassandra does not evaluate AI systems. It demonstrates how public governance records can be turned into reproducible evidence packages. AI governance records will face analogous problems: how to preserve logs, claims, source manifests, model or data changes, human review decisions, translations, evaluations, and incident evidence without making automated evidence integrity sound like legal compliance. Cassandra is a safe case for developing that vocabulary.

A seventh reviewer may ask whether the project risks overclaiming because trusted-list artifacts are legally meaningful. The answer is that the legal meaningfulness is exactly why the abstention boundary is central. Cassandra's contribution is not to make legally meaningful artifacts legally interpretable by an autonomous agent. It is to make public artifacts observable and verifiable as evidence while keeping legal interpretation outside the automated lane. That separation is the paper's methodological novelty.

## 13. Publication-status and citation discipline

The draft must keep source statuses visible. Official legal materials, standards, RFCs, NIST publications, CA/Browser Forum documents, PKI Consortium resources, and OECD-style public reports can be cited as primary context after version and access-date verification. Scholarly works can be cited normally only after bibliographic details are checked. Zenodo and preprint items should be labelled as preprints, software artifacts, datasets, or working papers. Submitted Tyche manuscripts should be labelled as submitted or under review. Internal artifacts should remain internal unless intentionally released. Prototype or permission-sensitive cases should be called prototypes or omitted.

This discipline matters because Cassandra's thesis value depends on credibility. If unpublished work is made to look peer-reviewed, or prototype work is made to look adopted, the evidence-infrastructure argument weakens. The paper should be conservative even when that makes the bibliography less impressive. The reference seed bibliography is a drafting-control artifact, not a final authority. Its job is to keep clusters visible while preventing premature citation upgrades.

The case-study maturity matrix serves the same function for adjacent projects. Cassandra can be public and live as the main case. MIRROR and EATF/AEP can be used as evidence-framework patterns with exact status labels. Janus, MATx, Vesta, Icarus, h2oatlas, eaudit, Aletheia, avatar.eatf.eu, X-Road attestation, PKI Atlas, breakable receipts, and Kolmogorov should not be collapsed into a single proof of adoption. Each has a different evidence object, publicness level, permission status, and relevance to the thesis. The paper should use them as carefully labelled comparators or future work, not as inflated evidence.

The final submission should therefore include a compact formal bibliography, but keep the extended reference atlas and seed bibliography as reviewer-support artifacts. The main paper should cite enough literature to make the governance-to-evidence move intelligible: PKI governance, eIDAS/ETSI trusted-list grammar, AI Act evidence duties, public administration, infrastructure studies, and computational method. It should not overload the reader with every adjacent Tyche project unless a specific comparison advances the argument.

## 14. Next experiments

The next empirical experiment is simple: keep the scheduled run alive and accumulate a longer dated series. After each new eligible date, the workflow should fetch, normalize, diff, bundle, receipt, roll up, rebuild the public index, and rerun validators. The results should first be checked for lineage parity and schema stability. Only after that should figures or prose be updated.

The next fixture experiment is to expand from unit-like synthetic cases to small replay capsules that combine multiple states: a fetch anomaly followed by a parser skip, a normalized-hash change with unchanged provider/service inventory, a provider/service-detail movement with unchanged aggregate counts, and an EATF receipt state transition. These capsules would help reviewers see how Cassandra handles mixed evidence conditions without relying on named real examples.

The next dashboard experiment is a printable card pack. If the local toolchain supports it, the JSON cards can be rendered into a static PDF or HTML page showing the claim boundary, latest run, EATF receipt interpretation, aggregate diff classes, replay path, and non-claims. The output should remain a reviewer aid, not a public alert sheet.

The next paper experiment is bibliography verification. The reference seed should be converted into formal citations with exact versions, URLs, DOIs, and access dates. Tyche internal works should be rechecked against Zenodo, submission portals, public repositories, and operator notes before any public bibliography uses them. This is not busywork; it is part of the same evidence-infrastructure discipline the paper advocates.

The next thesis experiment is comparative maturity scoring. Cassandra, MIRROR, EATF/AEP, Janus, MATx, Vesta, Icarus, eaudit, h2oatlas, Aletheia, PKI Atlas, X-Road attestation, breakable receipts, and Kolmogorov can be compared by evidence object, publicness, verifier maturity, dashboard maturity, fixture coverage, legal boundary, and publication status. Unknown cases should remain unknown. A matrix that marks gaps honestly is more useful than a map that pretends every prototype is a deployed system.

Finally, the next governance experiment is to test whether the Cassandra vocabulary helps explain AI governance records to non-PKI audiences. The phrase "evidence integrity is not legal interpretation" should become portable. If reviewers understand that sentence in the trusted-list case, it can later support EATF/AEP, MIRROR, MATx, Janus, Vesta, Icarus, and professional disclosure cases without overclaiming what any individual artifact proves.

## References and local evidence

### Primary legal, standards, and ecosystem context to verify before final submission

- Regulation (EU) No 910/2014 (eIDAS).
- Regulation (EU) 2024/1183 (European Digital Identity Framework / eIDAS amendment).
- Regulation (EU) 2024/1689 (AI Act).
- Commission Implementing Decision (EU) 2015/1505 on trusted-list technical specifications and formats.
- ETSI TS 119 612; ETSI EN 319 401; ETSI EN 319 411/412; ETSI EN 319 102; ETSI EN 319 422.
- RFC 5280; RFC 3161; RFC 6960; RFC 6962.
- NIST FIPS 140-3, 186-5, 203, 204, and 205.
- CA/Browser Forum Baseline Requirements and PKI Consortium resources.

### Scholarly anchors to complete bibliographically

- Maurer on PKI trust models; Ellison and Schneier on PKI risks.
- Drechsler; Kattel; Lember; Tonurist; Mazzucato; Bannister and Connolly; Margetts and Dorobantu; OECD digital-government literature; Estonian e-state and X-Road literature.
- Perez; Star and Ruhleder; Bowker and Star; Edwards; Plantin and coauthors; Larkin; Jasanoff.
- Lazer; Salganik; Grimmer, Roberts, and Stewart; Edelmann and coauthors; Bail.

### Cassandra evidence artifacts

- `sources/eu-lotl.xml` and `sources/eu-lotl.xml.meta.json`.
- `notes/pointers.json`.
- `snapshots/2026-05-20/manifest.json`.
- `normalized/2026-05-20/manifest.json`.
- `diffs/2026-05-20.json`.
- `alerts.jsonl`.
- `bundles/2026-05-20/snapshot-summary.json.bundle/`.
- `snapshots/2026-05-21/manifest.json`.
- `normalized/2026-05-21/manifest.json`.
- `diffs/2026-05-21.json`.
- `bundles/2026-05-21/snapshot-summary.json.bundle/`.
- `notes/aggregate-results-2026-05-21-output.json`.
- `notes/multiday-readiness-validation-output.json`.
- `notes/daily-cadence-status-output.json`.
- `notes/no-fetch-before-gate-validation-output.json`.
- `notes/paper-no-fetch-gate-section-check-output.json`.
- `notes/paper-future-dated-lineage-section-check-output.json`.
- `snapshots/2026-05-22/manifest.json`.
- `normalized/2026-05-22/manifest.json`.
- `diffs/2026-05-22.json`.
- `bundles/2026-05-22/snapshot-summary.json.bundle/`.
- `notes/semantic-diff-rollup-2026-05-22-output.json`.
- `notes/alert-rollup-2026-05-22-output.json`.
- `notes/artifact-index-append-only-duplicates-policy.md`.
- `notes/artifact-index-append-only-duplicates-policy-validation-output.json`.
- `notes/artifact-index-duplicate-report-output.json`.
- `notes/paper-aggregate-only-naming-validation-output.json`.
- `notes/paper-aggregate-only-naming-section-check-output.json`.
- `notes/resumption-state-summary-output.json`.
- `notes/resumption-state-summary.md`.
- `notes/append_bounded_state_register_reading_section.py`.
- `notes/paper-bounded-state-register-reading-section-check-output.json`.
- `notes/sources-bundle-row-coverage-output.json`.
- `notes/aggregate-results-table.csv`.
- `notes/aggregate-results-2026-05-20-output.json`.
- `figures/aggregate-run-telemetry.svg`.
- `figures/aggregate-diff-classes.svg`.
- `notes/cassandra-full-stack-usable-transcript-2026-05-27.md`.
- `paper/related-work-card.md` and `paper/reference-seed-bibliography.md`.
- `notes/cassandra-checked-reference-ledger-2026-05-27.md`.
- `notes/case-study-maturity-matrix.md` and `notes/publication-status-discipline.md`.
- `notes/fixture-matrix.md` and `notes/fixture-to-claim-map.md`.
- `notes/data-dictionary.md`, `notes/evidence-package-format.md`, `notes/public-index-schema.md`, `notes/replay-capsule.md`.
- `notes/eatf-claim-boundary-card.md` and `notes/mirror-bundle-card.md`.
- `observatory/public/data/index.json`, `observatory/public/data/schema.json`, and `observatory/public/data/cards/index.json`.
- `alerts.jsonl`, `bundles/<date>/snapshot-summary.json.bundle/`, `diffs/<date>.json`, `normalized/<date>/manifest.json`, and `snapshots/<date>/manifest.json` for completed dated runs.

Checked external anchors for the related-work section:

- Regulation (EU) No 910/2014, eIDAS: `https://eur-lex.europa.eu/eli/reg/2014/910/oj`.
- Regulation (EU) 2024/1183, European Digital Identity Framework: `https://eur-lex.europa.eu/eli/reg/2024/1183/oj`.
- Regulation (EU) 2024/1689, AI Act: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689`.
- Commission Implementing Decision (EU) 2015/1505: `https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32015D1505`.
- European Commission trusted lists page: `https://digital-strategy.ec.europa.eu/en/policies/eu-trusted-lists`.
- ETSI TS 119 612 V2.4.1: `https://www.etsi.org/deliver/etsi_ts/119600_119699/119612/02.04.01_60/ts_119612v020401p.pdf`.
- ETSI EN 319 401 V3.1.1: `https://www.etsi.org/deliver/etsi_en/319400_319499/319401/03.01.01_60/en_319401v030101p.pdf`.
- ETSI EN 319 411-1 V1.5.1: `https://www.etsi.org/deliver/etsi_en/319400_319499/31941101/01.05.01_60/en_31941101v010501p.pdf`.
- ETSI EN 319 422 V1.1.1: `https://www.etsi.org/deliver/etsi_en/319400_319499/319422/01.01.01_60/en_319422v010101p.pdf`.
- RFC 5280: `https://www.rfc-editor.org/rfc/rfc5280`; RFC 3161: `https://www.rfc-editor.org/rfc/rfc3161`; RFC 8785: `https://www.rfc-editor.org/rfc/rfc8785`.
- CA/Browser Forum Baseline Requirements: `https://cabforum.org/working-groups/server/baseline-requirements/requirements/`.
- PKI Consortium: `https://pkic.org/`.
- NIST FIPS 203/204/205: `https://csrc.nist.gov/pubs/fips/203/final`, `https://csrc.nist.gov/pubs/fips/204/final`, `https://csrc.nist.gov/pubs/fips/205/final`.
- W3C Verifiable Credentials Data Model v2.0: `https://www.w3.org/TR/vc-data-model-2.0/`.
- Star and Ruhleder (1996): DOI `10.1287/isre.7.1.111`; Bowker and Star (1999): DOI `10.7551/mitpress/6352.001.0001`.
- Perez (2002), Technological Revolutions and Financial Capital: `https://books.google.com/books/about/Technological_Revolutions_and_Financial.html?id=FW-aAAAAIAAJ`.
- Drechsler (2018): DOI `10.29379/jedem.v10i2.513`; Bannister and Connolly (2011): DOI `10.1016/j.giq.2010.06.010`; Lazer et al. (2009): DOI `10.1126/science.1167742`.
