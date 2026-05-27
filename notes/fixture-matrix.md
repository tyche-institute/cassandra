# Cassandra fixture matrix

Purpose: controlled, synthetic fixtures that make Cassandra behavior reviewable without exposing raw trusted-list names or converting structural observation into legal/status claims.

Claim boundary: every fixture below is synthetic workflow evidence only. Passing a fixture test does not validate trusted lists, does not validate signatures, does not determine provider/service legal status, does not supervise any entity, does not issue public alerts, and does not approve publication.

| Priority | Fixture | Synthetic input shape | Expected output | Implemented artifact | Claim-safety note |
|---:|---|---|---|---|---|
| 1 | Stable no-change fixture | Two equivalent comparable baseline records with the same key, normalized hash, and summary fields. | `compare_baselines` emits zero changes. | `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py` | Zero changes means only that the synthetic structural records match; it does not prove absence of legally relevant change in any real trusted list. |
| 2 | Normalized hash change fixture | Same comparable key and same aggregate counts, but changed canonical content hash. | One `normalized_hash_changed` entry with the standard structural caveat. | `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py` | A hash change is canonical-byte churn requiring review; it is not legal effect, signature validity, or status evidence. |
| 3 | Provider inventory fixture | Hashed provider key added and removed under synthetic non-name keys. | `provider_inventory_changed` with added/removed hash-key arrays; covered by add and removal cases. | `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py` | Keys are local structural handles, not identifiers for legal prose. |
| 4 | Service inventory fixture | Hashed service key added and removed under synthetic non-name keys. | `service_inventory_changed` with added/removed hash-key arrays; covered by add and removal cases. | `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py` | Service keys must remain hash/synthetic only. |
| 5 | Provider-service-detail fixture | Same provider key with changed aggregate service details; plus service reassignment across stable global provider/service inventory. | `provider_service_detail_changed`, including per-provider service-key delta assertions. | `notes/fixtures/synthetic-diff-fixtures.json`; `notes/test_synthetic_diff_fixtures.py` | Output remains aggregate/hash-keyed and does not name entities. |
| 6 | Fetch failure fixture | Timeout, HTTP error, redirect, and unreachable pointer metadata via mocked `requests.get`. | Per-endpoint metadata preserves timeout/unreachable errors, HTTP error status/body hash, and redirect final URL/history. | `fetch.py`; `notes/test_fetch_and_non_xml_fixtures.py`; `notes/fetch-non-xml-fixture-validation-output.json` | Fetch failures are operational observations, not endpoint or legal-status judgments. |
| 7 | Non-XML fixture | Temporary workspace with valid XML, PDF, HTML, TXT, and malformed XML inputs. | Normalizer records PDF/HTML/TXT as `skipped_non_xml`, malformed XML as `xml_parse_error`, and still writes a manifest. | `parse.py`; `notes/test_fetch_and_non_xml_fixtures.py`; `notes/fetch-non-xml-fixture-validation-output.json` | Non-XML and parse-error handling is corpus-shape telemetry only. |
| 8 | EATF success fixture | Minimal package/receipt verifies `ok`. | EATF receipt status `ok`. | Planned | Receipt verifies package bytes and declared hashes only. |
| 9 | EATF tamper fixture | Altered payload or AEP. | Verification fails explicitly. | Planned | Tamper failure teaches verifier behavior, not trusted-list meaning. |
| 10 | Missing-signing-input fixture | Minimal synthetic run artifacts with no EATF root, private key, public key, or timestamp passed to the packaging wrapper. | Explicit `skipped_missing_signing_inputs`; missing input names are preserved; payload, metadata, and receipt files are still written for review. | `notes/test_eatf_missing_signing_fixture.py`; `notes/eatf-missing-signing-fixture-validation-output.json` | Skips are visible and not silently treated as verified; this is package-input telemetry, not signature validation or legal-status evidence. |
| 11 | Dashboard fixture | Small public index with multiple run states. | Dashboard/public-index consumer handles ok/skipped/failure states. | Planned | Dashboard remains method telemetry, not alerting. |
| 12 | Claim-safety fixture | Forbidden direct wording samples. | Scanner catches overclaiming. | Planned | Heuristic scan does not replace legal/operator review. |

Near-term implementation order:

1. Keep the stable no-change and normalized-hash-change fixtures small and direct, tied to `diff.compare_baselines`.
2. Add provider/service inventory fixtures next by extending the same synthetic JSON fixture file.
3. Add fetch/non-XML fixtures with temporary workspaces so they exercise manifest behavior without touching real dated runs.
4. Add EATF/dashboard/claim-safety fixtures after the core diff fixture set is stable.
