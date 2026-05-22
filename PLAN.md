# Lane 16 — CASSANDRA (EU trusted-list longitudinal monitor)

## Mission

Converge on a daily, diffable, research-only snapshot history for the EU list-of-lists and national trusted-list XML documents. End-state: fetcher, parser, semantic diff engine, bundled daily snapshots, alerts JSONL, and a draft paper about structural churn observed in public lists without asserting legal effect.

## Scope

In:

- LOTL fetcher and extraction of national list pointers.
- XML snapshot store under dated directories.
- Signature-shape parser for observation only, not relying-party validation.
- Normalizer for whitespace, namespace, and attribute-order stability.
- Semantic diff classes for listed-entity additions, removals, supervisory metadata changes, and qualified-status field changes.
- EATF-bundle-style metadata per snapshot.
- Daily roll-up and longitudinal paper draft.

Out:

- Operating, supervising, or validating any trusted list.
- Asserting legal effect from a snapshot or diff.
- Claiming an entity has or lacks a legal status based on this lane.
- Performing signature verification as a relying party.
- Publishing prose that names listed entities without explicit approval.

## Inputs

- Public ETSI TS 119 612 v2.x specification fetched once into `sources/`.
- `https://ec.europa.eu/tools/lotl/eu-lotl.xml` — list-of-lists XML.
- The national XML pointers contained in the fetched list-of-lists.

## Output artifacts

| Path | Purpose |
|---|---|
| `fetch.py` | Fetch LOTL and national XML snapshots. |
| `parse.py` | Extract structural fields for observation. |
| `diff.py` | Compare normalized snapshots and emit structured diffs. |
| `snapshots/YYYY-MM-DD/<country>.xml` | Dated raw XML snapshots. |
| `diffs/YYYY-MM-DD.json` | Structured diff for one snapshot date. |
| `alerts.jsonl` | Append-only roll-up of observed structural diffs. |
| `paper/draft.md` | Companion longitudinal study draft. |

## Success criteria

| Horizon | Target |
|---:|---|
| 24h | Full snapshot of LOTL plus national XML files recorded and bundled. |
| 72h | Diff engine works against synthetic mutation and three real-world diff runs are recorded, even if empty. |
| 7d | Structured-diff alert template, paper outline plus 1000 words of background, and all snapshots bundled. |

## Claim-safety

- Never claim a trusted-list change has legal effect.
- Report “structural diff observed” and point to the XML path and timestamp.
- Use listed names inside machine-readable diff records only; aggregate in paper prose.
- Observation is not supervision, validation, or public status determination.

## FIRST 10 STEPS

1. Confirm WORKSPACE via `pwd`; create `sources/`, `snapshots/`, `diffs/`, `bundles/`, `paper/`, `notes/`.
2. Create `.venv`; install pip-only dependencies inside it.
3. Fetch the LOTL XML over HTTPS and save source metadata with sha256.
4. Parse the LOTL to extract national XML pointers and persist them in `notes/pointers.json`.
5. Fetch all national XML files into `snapshots/<today>/`.
6. Write a normalizer that canonicalizes whitespace and attribute order without changing content.
7. Write a diff that compares against a stored baseline; on day 1, record baseline and empty diff.
8. Bundle today's snapshot with source URLs, hashes, and observation caveats.
9. Append a machine-readable roll-up entry to `alerts.jsonl`.
10. Append `HERMES_PROGRESS.md` with snapshot count and next diff class to implement.

## Loop cadence

After step 10, each subsequent iteration picks one bounded action:

- Perform the daily fetch.
- Compare with the previous baseline.
- Refine one semantic diff class.
- Write one alert template or aggregation.
- Write 250–400 words into the paper.
- Review paper prose for aggregation-only naming.

## Local dependencies

- `pip install lxml signxml requests-cache`
- Do not install apt packages; use only the lane venv.

## State discipline

- Keep `PLAN.md`, `HERMES_PROGRESS.md`, `ARTIFACT_INDEX.md`, `SOURCES.md`, and `CLAIMS.md` current.
- Hash every generated artifact before listing it as verified.
- Keep downloaded sources under `sources/` or `vendor/` with metadata.
- Stop and write `BLOCKED.md` if scope, legal, credential, or publication uncertainty appears.

## Verification expectations

- Run the smallest reproducible smoke test before scaling.
- Record command lines, exit codes, and output paths in `HERMES_PROGRESS.md`.
- Treat a missing dependency as a blocker only after checking the local PATH and venv.
- Prefer deterministic seeds and dated run directories.
- Re-run the relevant verifier or parser after every code change.
- Keep public-facing wording cautious and assumption-scoped.
