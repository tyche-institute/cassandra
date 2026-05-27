# Cassandra fixture-to-claim reviewer map

Purpose: map each controlled Cassandra fixture to the paper claim it supports, the reviewer question it answers, and the boundary it does not cross.

Scope: this is a reviewer-facing bridge between `notes/fixture-matrix.md`, `paper/claims-and-evidence-table.md`, and the full-stack transcript. It should be read together with the fixture tests and validation outputs, not as a substitute for them.

Boundary sentence: fixtures prove expected software behavior on synthetic inputs. They are not trusted-list validation, not source-signature validation, not legal-status determination, not supervision, not public alerting, not compliance review, and not publication approval.

## Summary table

| Fixture class | Paper claim supported | Reviewer question answered | Primary evidence artifacts | Boundary / non-claim |
|---|---|---|---|---|
| Stable no-change | Cassandra can distinguish an unchanged comparable structural record from a changed one under a configured baseline. | If nothing changes in controlled inputs, does the diff engine stay quiet? | `notes/fixture-matrix.md`; `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py`; `notes/synthetic-diff-fixture-validation-output.json` | A zero-change fixture only proves expected synthetic diff behavior; it does not prove absence of legally relevant change in real trusted-list artifacts. |
| Normalized hash change | Cassandra can surface canonical-content churn without requiring provider-specific prose. | If record counts are stable but canonical bytes differ, is the difference observable? | `notes/fixture-matrix.md`; `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py`; `notes/synthetic-diff-fixture-validation-output.json` | A normalized-hash change is a structural prompt for review, not legal effect, source signature validity, or status evidence. |
| Provider inventory | Cassandra can compare provider-level inventory through synthetic hashed handles. | Can the method show provider-like additions/removals without exposing real names? | `notes/fixture-matrix.md`; `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py`; `notes/synthetic-diff-fixture-validation-output.json` | Hash handles are local comparison keys, not identifiers for public legal or provider-specific claims. |
| Service inventory | Cassandra can compare service-level inventory through synthetic hashed handles. | Can service-like additions/removals be detected while preserving aggregate-only prose? | `notes/fixture-matrix.md`; `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py`; `notes/synthetic-diff-fixture-validation-output.json` | Service keys remain synthetic/hash-only and do not support real service-status conclusions. |
| Provider-service detail | Cassandra can notice detail movement under aggregate/hash-keyed provider-service structures. | Can the system distinguish aggregate detail changes from whole-provider or whole-service additions? | `notes/fixture-matrix.md`; `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py`; `notes/synthetic-diff-fixture-validation-output.json` | Detail movement is parser-level structure, not evidence about service quality, compliance, or legal status. |
| Fetch failure | Cassandra preserves timeout, HTTP-error, redirect, and unreachable-pointer telemetry instead of hiding failed endpoints. | Does collection failure become explicit evidence rather than silent absence? | `notes/fixture-matrix.md`; `fetch.py`; `notes/test_fetch_and_non_xml_fixtures.py`; `notes/fetch-non-xml-fixture-validation-output.json` | Fetch telemetry is not endpoint certification, public warning, or legal-status interpretation. |
| Non-XML | Cassandra treats PDF/HTML/TXT/non-parseable inputs as skips or parser events rather than fatal workflow failures. | Can the corpus include non-XML public artifacts without breaking the evidence loop? | `notes/fixture-matrix.md`; `parse.py`; `notes/test_fetch_and_non_xml_fixtures.py`; `notes/fetch-non-xml-fixture-validation-output.json` | Non-XML and parser outcomes are corpus-shape telemetry, not claims about trusted-list legal effect or source validity. |
| EATF success | Cassandra can produce and read a successful package-integrity receipt for synthetic non-secret material. | What exactly does an `ok` EATF receipt prove in this case? | `notes/fixture-matrix.md`; `scripts/eatf_package_snapshot.py`; `notes/test_eatf_success_tamper_fixture.py`; `notes/eatf-success-tamper-fixture-validation-output.json` | An `ok` fixture receipt supports package bytes and declared hashes only; it does not validate the underlying trusted-list source. |
| EATF tamper | Cassandra can make tampering visible as verifier failure in a controlled synthetic package. | Does the evidence-package loop fail closed when bytes are altered? | `notes/fixture-matrix.md`; `notes/test_eatf_success_tamper_fixture.py`; `notes/eatf-success-tamper-fixture-validation-output.json` | Tamper failure demonstrates package-integrity behavior, not legal significance of any real source document. |
| Missing signing input | Cassandra records an explicit signing skip when required EATF inputs are absent. | Does the workflow avoid pretending that unsigned or under-specified packages verified? | `notes/fixture-matrix.md`; `notes/test_eatf_missing_signing_fixture.py`; `notes/eatf-missing-signing-fixture-validation-output.json` | `skipped_missing_signing_inputs` is transparent packaging telemetry, not a failed or passed trusted-list validation. |
| Dashboard multistate | Cassandra's public-index consumer can represent multiple run and receipt states without turning them into alerts. | Can dashboard data stay informative while preserving claim boundaries? | `notes/fixture-matrix.md`; `notes/fixtures/dashboard-public-index-multistate.json`; `notes/test_dashboard_public_index_fixture.py`; `notes/dashboard-public-index-fixture-validation-output.json`; `notes/test_observatory_dashboard_cards.py` | Dashboard states are method telemetry and review cues, not public alerting, supervision, or publication approval. |
| Claim safety | Cassandra can detect configured overclaiming phrases in controlled wording samples. | Is there a mechanical guard against common legal/signature/supervision overclaims? | `notes/fixture-matrix.md`; `notes/fixtures/claim-safety-wording-fixtures.json`; `notes/test_claim_safety_fixture.py`; `notes/claim-safety-fixture-validation-output.json` | Heuristic scanning reduces wording risk but does not replace operator review, legal review, or publication approval. |

## How to use this map in the paper

1. Use the fixture rows in the Results or Methods section as evidence that the implemented workflow has controlled behavior, not as empirical claims about real trusted-list actors.
2. Pair each fixture reference with at least one real observation artifact when making a full-stack claim. Example: real dated runs show the pipeline operating on public LOTL-derived artifacts; the synthetic fetch-failure fixture shows that failure modes are represented safely.
3. Keep named entities out of fixture prose. Synthetic fixtures are valuable precisely because they let the paper discuss behavior without exposing provider/service names.
4. If a reviewer asks whether Cassandra is only an XML parser, point to the combined fixture set: diff behavior, fetch/non-XML handling, package-integrity success/failure, dashboard state handling, and claim-safety scanning.
5. If a reviewer asks whether EATF proves legal validity, point to the EATF success, tamper, and missing-input fixtures together: the evidence layer distinguishes package integrity, tamper evidence, and skipped signing inputs while refusing legal interpretation.

## Reviewer-safe claim patterns

Allowed:

- "The stable no-change fixture checks that identical synthetic comparable records emit no structural diff under the configured comparison function."
- "The EATF tamper fixture checks that altered synthetic package bytes fail verification in the fixture harness."
- "The dashboard multistate fixture checks that `ok`, `verify_failed`, and `skipped_missing_signing_inputs` receipt states remain caveated data states."

Avoid:

- Saying that a fixture proves a real trusted list is valid or invalid.
- Saying that an EATF `ok` receipt validates source XML signatures.
- Saying that zero structural changes imply no legally relevant change.
- Saying that dashboard state is a public warning, compliance status, or supervisory signal.

## Maintenance rule

When adding a new fixture, update in the same commit:

1. `notes/fixture-matrix.md`.
2. This `notes/fixture-to-claim-map.md`.
3. The relevant `notes/test_*.py` fixture test and validation output.
4. Any paper/card row that cites the fixture.

This keeps the reviewer map aligned with implemented behavior instead of becoming decorative documentation.
