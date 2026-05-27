# Cassandra preprint operator-review packet

Date: 2026-05-27
Status: operator-review required before any external submission or deposit
Core sentence: Cassandra: from governance infrastructure to evidence infrastructure.

This packet turns the v0.1 preprint candidate into a reviewable object for Anton, a thesis committee, and future agents. It is not publication approval, not legal review, not trusted-list validation, not source-signature validation, not supervision, not public alerting, and not an endorsement claim. It is a bounded checklist for deciding what must be read, rechecked, narrowed, or expanded before any release-facing action.

## Review decision boundary

A positive review of this packet may mean only that the manuscript and supporting kit are coherent enough for the next editing step. It does not mean that any trusted list is valid, that any provider or service has a legal status, that any source XML signature has been validated for relying-party purposes, that a supervisory conclusion exists, that the dashboard should be treated as an alerting channel, or that an external deposit may proceed without operator approval.

The packet assumes the current v0.1 candidate remains a local/pre-publication artifact even though the repository and dashboard have public surfaces. External dissemination still requires a separate operator decision, boundary review, metadata review, and target-specific formatting pass.

## Reading order

1. `paper/preprint/cassandra-preprint-v0.1.md` — main human-readable preprint candidate.
2. `paper/preprint/cassandra-preprint-v0.1.pdf` — built PDF representation for layout review.
3. `paper/preprint/cassandra-preprint-v0.1.docx` — editable exchange copy for committee or collaborator comments.
4. `notes/preprint-candidate-validation-output.json` — mechanical preprint validation output produced by `notes/validate_preprint_candidate.py`.
5. `notes/cassandra-checked-reference-ledger-2026-05-27.md` — release-facing reference ledger; use before adding or defending references.
6. `notes/fixture-to-claim-map.md` — reviewer bridge from synthetic fixtures to bounded paper claims.
7. `notes/publication-status-discipline.md` — status vocabulary separating draft, public data, preprint, submission, and publication claims.
8. `notes/publication-case-kit-readiness-output.json` — inventory validation for the paper/case-study kit.
9. `notes/cassandra-full-stack-usable-transcript-2026-05-27.md` — end-to-end transcript for committee, reviewer, and future-agent context.

## Operator checklist

- [ ] Confirm that the title keeps the spine: Cassandra: from governance infrastructure to evidence infrastructure.
- [ ] Confirm that the abstract does not frame Cassandra as merely an XML parser or parser paper.
- [ ] Confirm that all claims about EATF/AEP receipts remain limited to package/payload/hash verification and do not imply trusted-list legal validity.
- [ ] Confirm that dashboard language presents a public method surface, not public alerting.
- [ ] Confirm that no provider-specific claim appears in release-facing prose unless separately approved.
- [ ] Confirm that employment/IP/confidentiality boundaries are acceptable for the final target venue.
- [ ] Confirm that Tyche affiliation and author metadata are acceptable for the intended target.
- [ ] Confirm that no current or prior employer, partner, or standards body is implied to endorse the project.
- [ ] Confirm that repository-public and dashboard-public facts are still current before citing them externally.
- [ ] Confirm whether Zenodo, OSF, SSRN, arXiv, journal, conference, or thesis-chapter routing is desired.

## Committee/reviewer checklist

- [ ] Can a reviewer explain the difference between governance infrastructure and evidence infrastructure after reading sections 1-3?
- [ ] Can a reviewer identify the observed object: LOTL-derived public trusted-list artifacts and local/public evidence outputs?
- [ ] Can a reviewer identify what Cassandra refuses to claim: legal effect, source-signature validity, supervisory status, compliance, public alerts, and absence of legally relevant change?
- [ ] Can a reviewer connect each empirical claim to a path, validation output, fixture, dashboard index, or EATF/MIRROR boundary card?
- [ ] Can a reviewer see why synthetic fixtures strengthen the case rather than replace real observations?
- [ ] Can a reviewer distinguish Cassandra from MIRROR, EATF, Janus, MATx, Vesta, Icarus, eaudit, h2oatlas, and Aletheia prototypes?
- [ ] Can a reviewer see the AI Act connection as an evidence-infrastructure analogy rather than a claim that Cassandra monitors AI systems?
- [ ] Can a reviewer see the publication-status labels for checked sources, Zenodo/preprints, submitted manuscripts, internal artifacts, and prototypes?

## Release blockers to resolve before any external deposit

- BLOCKER: Operator must choose target route and permitted publicness level before any Zenodo, OSF, SSRN, arXiv, journal, conference, or thesis-hub release.
- BLOCKER: Legal/IP/confidentiality boundary must be reviewed for overlap with employment, identity, eIDAS, public-sector trust-service, and partner-related constraints.
- BLOCKER: Live deployment claims must be rechecked immediately before external citation, including `https://cassandra-observatory.pages.dev/` and `https://cassandra-observatory.pages.dev/data/index.json`.
- BLOCKER: References beyond `notes/cassandra-checked-reference-ledger-2026-05-27.md` must not be added to release-facing prose until checked and claim-connected.
- BLOCKER: Any named-entity example from trusted lists requires a separate approval path; the default release posture remains aggregate-only.
- BLOCKER: Any claim about eaudit, h2oatlas, Aletheia, avatar.eatf.eu, Janus, MATx, Vesta, Icarus, X-Road, PKI Atlas, or Kolmogorov must be rechecked for current publicness, rights, and status.
- BLOCKER: Final PDF/DOCX output must be regenerated and revalidated after any manuscript edit.

## Safe next actions

- Expand the v0.1 candidate toward a longer venue-specific submission while preserving the same claim boundary.
- Prepare deposit metadata as a draft file only, with explicit `operator-review required` status and no upload action.
- Prepare a reviewer-response memo that maps common objections to `notes/fixture-to-claim-map.md`, `notes/case-study-maturity-matrix.md`, and `notes/cassandra-checked-reference-ledger-2026-05-27.md`.
- Prepare target-specific formatting notes for one venue without claiming submission approval.
- Rebuild `paper/preprint/cassandra-preprint-v0.1.pdf` and `paper/preprint/cassandra-preprint-v0.1.docx` only after text edits pass the existing validators.

## Packet validation

This review packet is validated mechanically by `notes/validate_preprint_review_packet.py`, which checks required sections, referenced artifacts, open review checkboxes, release blockers, and boundary vocabulary. The validator is intentionally narrow. It cannot perform legal review, scholarly review, reference interpretation, source-signature validation, trusted-list validation, supervisory review, or publication approval.
