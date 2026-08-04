# Cassandra — EU/EEA Trusted-List Observatory Dataset

Cassandra is a research dataset and toolkit that records **daily structural snapshots of the
national trusted lists (TLs) published under Regulation (EU) No 910/2014 (eIDAS)** across
EU/EEA jurisdictions, together with normalized representations and day-over-day structural
diffs.

The project is a **research-only structural observation** of publicly published artefacts. It
is explicitly **not** trusted-list validation, signature validation, legal-status
determination, supervision, public alerting, or any regulated trust-service output. Legal
interpretation is kept outside the automated pipeline by design.

## Contents

| Path | What it holds |
|------|---------------|
| `snapshots/` | Raw, as-fetched national TL documents per day (XML / XTSL / PDF) |
| `normalized/` | Canonicalised representations used for stable structural comparison |
| `diffs/` | Day-over-day structural diffs (added/removed/changed listed items) |
| `baselines/` | Per-day baseline summaries |
| `bundles/` | Reproducible provenance bundles (source references + hashes) |
| `evidence/`, `observatory/` | Aggregated observation outputs and the public observatory view |
| `figures/` | Figures derived from the aggregated results |
| `paper/` | Companion research paper drafts and supporting cards |
| `fetch.py`, `parse.py`, `diff.py`, `run_daily.py`, `alert_rollup.py`, `create_bundle.py` | Pipeline tooling |
| `SOURCES.md` | The national trusted-list source endpoints |
| `CLAIMS.md` | Claims-and-evidence ledger for the companion paper |

## Data provenance & neutrality

Source snapshots are retrieved from the official national trusted-list publishers listed in
[`SOURCES.md`](SOURCES.md) and are redistributed **as published**, unmodified, for research and
reproducibility. Every trust-service provider that appears in this dataset appears exactly as it
is listed by its national scheme; inclusion is a neutral record of public-sector data and
implies nothing beyond the public listing itself.

## Reproducing

```bash
pip install -r requirements.txt
python run_daily.py        # fetch → parse → normalize → diff → aggregate
```

## Citation & contact

Anton Sokolov, Tyche Institute — ORCID [0000-0003-2452-7096](https://orcid.org/0000-0003-2452-7096) ·
`anton.sokolov@tyche.institute`. See [`CITATION.cff`](CITATION.cff).

## License

See [`LICENSE`](LICENSE). In brief: Tyche-authored code is MIT; Tyche-authored data, figures,
and text are CC BY 4.0; upstream national trusted-list source documents remain the property of
their respective national schemes and are included here as neutral public-sector records.
